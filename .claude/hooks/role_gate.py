#!/usr/bin/env python3
"""Review gate for pull requests opened from Claude Code.

Two modes, both called by the hooks in .claude/settings.json:

  record  when a subagent finishes (SubagentStop): note which role ran, and when.
  check   before a shell command: if the command opens a pull request or marks
          one ready, refuse unless every gate role ran after the last code edit.

The gate judges the branch being proposed, not just the session's directory:
a `cd`/`Set-Location`/`pushd` before `gh pr` moves the judged directory,
`--head <branch>` selects the worktree that has that branch checked out (or the
branch's commits when no worktree has it), and `gh pr ready <n>` run from a
clean main checkout looks up the pull request's head branch.

The ledger lives in the repository's common git dir (claude-role-runs.jsonl),
so the main checkout and every worktree share it. The older per-checkout
.claude/state/role-runs.jsonl is still read.

A change that touches only documentation or agent configuration passes without
a review. The owner can switch the gate off for a session by starting Claude
Code with ROLE_GATE=off in the environment.

Standard library only. Exit code 2 blocks the tool call; the text on stderr is
shown to Claude as the reason.
"""
import json
import os
import re
import subprocess
import sys
import time

GATE_ROLES = ["Code Reviewer", "Reality Checker"]  # GATE_ROLES_MARKER
LEDGER = os.path.join(".claude", "state", "role-runs.jsonl")  # legacy, read only
SHARED_LEDGER = "claude-role-runs.jsonl"  # in the common git dir
PR_COMMAND = re.compile(r"(?:^|[\s;&|(])gh(?:\.exe)?\s+pr\s+(create|ready)\b")
ARG = r"(?:\"([^\"]*)\"|'([^']*)'|([^\s;&|()]+))"
CD_COMMAND = re.compile(
    r"(?:^|[\s;&|(])(?:cd|chdir|pushd|Set-Location|Push-Location|sl)\s+"
    r"(?:(?:-Path|-LiteralPath|-L|-P|/d)\s+)?" + ARG,
    re.IGNORECASE,
)
HEAD_OPTION = re.compile(r"(?:^|\s)(?:--head|-H)(?:=|\s+)" + ARG)
DOC_ONLY = re.compile(
    r"(^|/)(\.claude|\.github|docs)/|\.(md|txt|rst)$|(^|/)(LICENSE|\.gitignore|\.gitattributes)$",
    re.IGNORECASE,
)
SLACK_SECONDS = 2  # file-system timestamp granularity


def git(root, *args):
    try:
        out = subprocess.run(
            ["git", "-C", root] + list(args),
            capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    # keep leading spaces: `git status --porcelain` lines start with them
    return out.stdout.rstrip() if out.returncode == 0 else None


def repo_root(cwd):
    return git(cwd or ".", "rev-parse", "--show-toplevel")


def base_ref(root):
    head = git(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    for ref in [head, "origin/main", "origin/master", "main", "master"]:
        if ref and git(root, "rev-parse", "--verify", "--quiet", ref) is not None:
            return ref
    return None


def same_path(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def common_dir(root):
    """Absolute path of the git dir shared by the main checkout and all worktrees."""
    out = git(root, "rev-parse", "--git-common-dir")
    if not out:
        return None
    return os.path.abspath(out if os.path.isabs(out) else os.path.join(root, out))


def worktrees(root):
    """[(path, branch name or None)] from `git worktree list --porcelain`; the main checkout is first."""
    out = git(root, "worktree", "list", "--porcelain")
    trees = []
    for line in (out or "").splitlines():
        if line.startswith("worktree "):
            trees.append([line[len("worktree "):], None])
        elif line.startswith("branch refs/heads/") and trees:
            trees[-1][1] = line[len("branch refs/heads/"):]
    return [tuple(tree) for tree in trees]


def current_branch(root):
    return git(root, "symbolic-ref", "--quiet", "--short", "HEAD")


def is_main_checkout(root):
    trees = worktrees(root)
    return bool(trees) and same_path(trees[0][0], root)


def first_arg(match):
    return next((group for group in match.groups() if group is not None), "")


def local_path(raw, current):
    raw = os.path.expanduser(raw)
    if os.name == "nt":
        drive = re.match(r"^/([a-zA-Z])(?:/|$)", raw)  # Git Bash style /d/Projects
        if drive:
            raw = drive.group(1) + ":/" + raw[3:]
    if not os.path.isabs(raw):
        raw = os.path.join(current, raw)
    return os.path.normpath(raw)


def target_dir(command, match, cwd):
    """Directory the `gh pr` part runs in: cwd, moved by any cd/Set-Location/pushd before it."""
    current = cwd
    for cd in CD_COMMAND.finditer(command[:match.start()]):
        raw = first_arg(cd).strip()
        if raw in ("", "-"):
            continue
        candidate = local_path(raw, current)
        if os.path.isdir(candidate):  # a cd that would fail leaves the directory unchanged
            current = candidate
    return current


def head_branch(rest):
    found = HEAD_OPTION.search(rest)
    if not found:
        return None
    branch = first_arg(found).strip()
    return branch.split(":", 1)[1] if ":" in branch else (branch or None)  # owner:branch


def ready_target(rest):
    segment = re.split(r"[;&|]", rest, maxsplit=1)[0]
    for token in re.findall(r"\"[^\"]*\"|'[^']*'|\S+", segment):
        token = token.strip("\"'")
        if token and not token.startswith("-"):
            return token
    return None


def pr_head(root, target):
    try:
        out = subprocess.run(
            ["gh", "pr", "view", target, "--json", "headRefName", "--jq", ".headRefName"],
            capture_output=True, text=True, timeout=20, cwd=root,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def locate_branch(root, branch):
    """(directory, ref): the worktree that has the branch checked out, or the repo plus a ref to judge by commits."""
    for path, name in worktrees(root):
        if name == branch and os.path.isdir(path):
            return path, None
    for ref in ["refs/heads/" + branch, "refs/remotes/origin/" + branch]:
        if git(root, "rev-parse", "--verify", "--quiet", ref) is not None:
            return root, ref
    return root, branch  # unknown branch: judged as "cannot tell what changed"


def changed_files(root):
    """Files that differ from the default branch, committed or not. None = unknown."""
    names = set()
    base = base_ref(root)
    if base is None:
        return None
    merge_base = git(root, "merge-base", base, "HEAD")
    if merge_base is None:
        return None
    committed = git(root, "diff", "--name-only", merge_base, "HEAD")
    working = git(root, "status", "--porcelain", "--untracked-files=all")
    if committed is None or working is None:
        return None
    names.update(line for line in committed.splitlines() if line)
    for line in working.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        names.add(path.strip('"'))
    return sorted(names)


def is_code(path):
    return not DOC_ONLY.search(path.replace("\\", "/"))


def last_code_change(root, files):
    """(timestamp, path) of the most recently modified changed code file."""
    newest, newest_path = 0.0, None
    for rel in files:
        full = os.path.join(root, rel)
        try:
            stamp = os.path.getmtime(full)
        except OSError:
            continue  # deleted file: nothing left to review in it
        if stamp > newest:
            newest, newest_path = stamp, rel
    return newest, newest_path


def assess_checkout(root):
    """None when nothing needs a review, else (timestamp, path) of the last code change."""
    files = changed_files(root)
    if files is None:
        return time.time(), None  # cannot tell what changed: require the gate
    code = [name for name in files if is_code(name)]
    if not code:
        return None  # documentation or agent configuration only
    stamp, newest = last_code_change(root, code)
    if not newest:
        # every changed code file was deleted: a review any time after the branch point counts
        branch_point = git(root, "log", "-1", "--format=%ct", git(root, "merge-base", base_ref(root), "HEAD") or "HEAD")
        stamp, newest = float(branch_point or 0), "(deleted files only)"
    return stamp, newest


def assess_branch(root, ref):
    """Like assess_checkout, for a branch that is not checked out: judged by its commits."""
    base = base_ref(root)
    merge_base = git(root, "merge-base", base, ref) if base else None
    files = git(root, "diff", "--name-only", "%s..%s" % (merge_base, ref)) if merge_base else None
    if files is None:
        return time.time(), None  # cannot tell what changed: require the gate
    if not [name for name in files.splitlines() if name and is_code(name)]:
        return None
    log = git(root, "log", "--format=%x00%ct", "--name-only", "%s..%s" % (merge_base, ref)) or ""
    newest, newest_path = 0.0, None
    for chunk in log.split("\x00")[1:]:
        lines = [line for line in chunk.splitlines() if line.strip()]
        code = [name for name in lines[1:] if is_code(name)]
        if lines and code and float(lines[0]) > newest:
            newest, newest_path = float(lines[0]), code[0]
    if not newest_path:
        return time.time(), None
    return newest, newest_path


def ledger_paths(root):
    paths = []
    shared = common_dir(root)
    if shared:
        paths.append(os.path.join(shared, SHARED_LEDGER))
    paths.append(os.path.join(root, LEDGER))
    trees = worktrees(root)
    if trees:
        paths.append(os.path.join(trees[0][0], LEDGER))
    unique = []
    for path in paths:
        if not any(same_path(path, seen) for seen in unique):
            unique.append(path)
    return unique


def read_ledger(paths):
    runs = {}
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                for line in handle:
                    try:
                        entry = json.loads(line)
                        role = str(entry.get("role", "")).strip().lower()
                        stamp = float(entry.get("ts", 0))
                    except (ValueError, TypeError, AttributeError):
                        continue
                    if stamp > 1e11:
                        stamp /= 1000.0  # written in milliseconds by role-gate.mjs
                    if role and stamp > runs.get(role, 0):
                        runs[role] = stamp
        except OSError:
            pass
    return runs


def record(event):
    tool_input = event.get("tool_input")
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    # SubagentStop events carry agent_type; a tool event carries tool_input.subagent_type
    role = event.get("agent_type") or tool_input.get("subagent_type") or ""
    role = str(role).strip()
    if not role:
        return 0
    root = repo_root(event.get("cwd"))
    if not root:
        return 0
    shared = common_dir(root)
    path = os.path.join(shared, SHARED_LEDGER) if shared else os.path.join(root, LEDGER)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "role": role,
            "ts": time.time(),
            "session": event.get("session_id", ""),
        }) + "\n")
    return 0


def check(event):
    tool_input = event.get("tool_input")
    command = str(tool_input.get("command", "")) if isinstance(tool_input, dict) else ""
    match = PR_COMMAND.search(command)
    if not match:
        return 0
    if os.environ.get("ROLE_GATE", "").lower() == "off":
        sys.stderr.write("role gate: switched off by ROLE_GATE=off for this session\n")
        return 0
    root = repo_root(target_dir(command, match, str(event.get("cwd") or os.getcwd())))
    if not root:
        return 0  # not a git checkout: nothing to gate
    rest = command[match.end():]
    head = head_branch(rest)
    ref = None
    if head and head != current_branch(root):
        root, ref = locate_branch(root, head)
    verdict = assess_branch(root, ref) if ref else assess_checkout(root)
    if verdict is None and match.group(1) == "ready" and not head and is_main_checkout(root):
        target = ready_target(rest)
        looked_up = pr_head(root, target) if target else None
        if looked_up and looked_up != current_branch(root):
            root, ref = locate_branch(root, looked_up)
            verdict = assess_branch(root, ref) if ref else assess_checkout(root)
    if verdict is None:
        return 0
    stamp, newest = verdict
    runs = read_ledger(ledger_paths(root))
    missing = [role for role in GATE_ROLES if runs.get(role.lower(), 0) + SLACK_SECONDS < stamp]
    if not missing:
        return 0
    when = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stamp))
    seen = ", ".join(
        "%s at %s" % (role, time.strftime("%H:%M:%S", time.localtime(runs[role.lower()])))
        for role in GATE_ROLES if role.lower() in runs
    ) or "none"
    sys.stderr.write(
        "Blocked by .claude/hooks/role_gate.py: this pull request changes code and the review gate has not "
        "run on the current state of it.\n"
        "Run these project subagents on the full diff, fix what they find, then try again: %s.\n"
        "Last code change: %s at %s. Gate runs recorded: %s.\n"
        "A review counts only if it ran after the last code edit. Documentation-only changes pass without one.\n"
        "The steps are in .claude/skills/implement-ticket/SKILL.md.\n"
        % (", ".join(missing), newest or "unknown", when, seen)
    )
    return 2


def self_test():
    import shutil
    import stat
    import tempfile

    def run(root, mode, event, env=None):
        full_env = dict(os.environ)
        full_env.pop("ROLE_GATE", None)
        full_env.update(env or {})
        event = dict(event, cwd=root)
        proc = subprocess.run(
            [sys.executable, os.path.abspath(__file__), mode],
            input=json.dumps(event), capture_output=True, text=True, env=full_env,
        )
        return proc.returncode

    def sh(root, *args):
        subprocess.run(["git", "-C", root] + list(args), check=True, capture_output=True)

    def write(path, text):
        with open(path, "w") as handle:
            handle.write(text)

    def remove(path):
        def retry(func, target, _exc):
            os.chmod(target, stat.S_IWRITE)  # git object files are read-only on Windows
            func(target)
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=retry)
        else:
            shutil.rmtree(path, onerror=retry)

    def gh(command):
        return {"tool_name": "Bash", "tool_input": {"command": command}}

    def stop(role):
        return {"hook_event_name": "SubagentStop", "agent_type": role}

    def new_repo(root):
        os.makedirs(root, exist_ok=True)
        sh(root, "init", "-q", "-b", "main")
        sh(root, "config", "user.email", "test@example.invalid")
        sh(root, "config", "user.name", "test")
        write(os.path.join(root, "app.py"), "x = 1\n")
        sh(root, "add", "-A")
        sh(root, "commit", "-q", "-m", "base")

    pr = gh("gh pr create --draft --title x --body y")
    failures = []

    def expect(label, got, want):
        if got != want:
            failures.append("%s: got %s, expected %s" % (label, got, want))

    temp = tempfile.mkdtemp(prefix="role-gate-")
    try:
        root = os.path.join(temp, "single")
        new_repo(root)
        sh(root, "checkout", "-q", "-b", "feature")

        expect("other command passes", run(root, "check", gh("git status")), 0)
        expect("no change passes", run(root, "check", pr), 0)

        write(os.path.join(root, "README.md"), "docs\n")
        expect("docs-only change passes", run(root, "check", pr), 0)

        write(os.path.join(root, "app.py"), "x = 2\n")
        expect("code change without review is blocked", run(root, "check", pr), 2)
        expect("gh pr ready is gated too", run(root, "check", gh("cd x && gh pr ready 12")), 2)
        expect("owner switch passes", run(root, "check", pr, {"ROLE_GATE": "off"}), 0)

        time.sleep(SLACK_SECONDS + 1)
        for role in GATE_ROLES[:-1]:
            run(root, "record", stop(role))
        if len(GATE_ROLES) > 1:
            expect("one gate role missing is blocked", run(root, "check", pr), 2)
        run(root, "record", stop(GATE_ROLES[-1].upper()))
        expect("all gate roles after the edit pass", run(root, "check", pr), 0)

        sh(root, "add", "-A")
        sh(root, "commit", "-q", "-m", "change")
        expect("committing does not invalidate the review", run(root, "check", pr), 0)

        time.sleep(SLACK_SECONDS + 1)
        write(os.path.join(root, "app.py"), "x = 3\n")
        expect("code edited after the review is blocked again", run(root, "check", pr), 2)

        legacy = os.path.join(root, LEDGER)
        os.makedirs(os.path.dirname(legacy), exist_ok=True)
        write(legacy, "".join(json.dumps({"role": r, "ts": time.time() + 1}) + "\n" for r in GATE_ROLES))
        expect("old .claude/state ledger still counts", run(root, "check", pr), 0)

        # main checkout clean on main, ticket work in a worktree
        main = os.path.join(temp, "main")
        tree = os.path.join(temp, "wt")
        new_repo(main)
        sh(main, "worktree", "add", "-q", "-b", "wt-feature", tree)
        time.sleep(SLACK_SECONDS + 1)
        write(os.path.join(tree, "app.py"), "x = 2\n")

        expect("clean main checkout alone passes", run(main, "check", pr), 0)
        cd_create = gh('cd "%s" && gh pr create --draft --title x --body y' % tree)
        expect("(a) cd <worktree> && gh pr create is blocked", run(main, "check", cd_create), 2)
        expect("(a) relative cd ../wt is blocked", run(main, "check", gh("cd ../wt && gh pr create --fill")), 2)
        if os.name == "nt":  # backslash paths only exist on Windows
            expect("(a) Set-Location with backslashes is blocked",
                   run(main, "check", gh("Set-Location '%s'; gh pr create --fill" % tree.replace("/", "\\"))), 2)
        head_create = gh("gh pr create --head wt-feature --title x --body y")
        expect("(b) gh pr create --head <branch> from main is blocked", run(main, "check", head_create), 2)
        expect("(b) -R does not change the directory",
               run(main, "check", gh("gh pr create -R owner/repo -H wt-feature --fill")), 2)

        time.sleep(SLACK_SECONDS + 1)
        run(main, "record", stop(GATE_ROLES[0]))
        if len(GATE_ROLES) > 1:
            expect("(c) one role recorded from main, check in worktree is blocked", run(tree, "check", pr), 2)
        for role in GATE_ROLES[1:]:
            run(main, "record", stop(role))
        expect("(c) roles recorded from main count in the worktree", run(tree, "check", pr), 0)
        expect("(c) cd <worktree> passes after review", run(main, "check", cd_create), 0)
        expect("(c) --head <branch> passes after review", run(main, "check", head_create), 0)
        expect("(c) ledger is in the common git dir",
               os.path.isfile(os.path.join(main, ".git", SHARED_LEDGER)), True)

        # a branch that no worktree has checked out: judged by its commits
        time.sleep(SLACK_SECONDS + 1)
        side = os.path.join(temp, "side")
        sh(main, "worktree", "add", "-q", "-b", "side", side, "main")
        write(os.path.join(side, "lib.py"), "y = 1\n")
        sh(side, "add", "-A")
        sh(side, "commit", "-q", "-m", "side change")
        sh(main, "worktree", "remove", side)
        side_create = gh("gh pr create --head side --fill")
        expect("(d) branch judged by commits is blocked before review", run(main, "check", side_create), 2)
        time.sleep(1)
        for role in GATE_ROLES:
            run(tree, "record", stop(role))
        expect("(d) branch judged by commits passes after review", run(main, "check", side_create), 0)
    finally:
        remove(temp)

    if failures:
        print("role_gate self-test FAILED:\n  " + "\n  ".join(failures))
        return 1
    print("role_gate self-test passed (gate roles: %s)" % ", ".join(GATE_ROLES))
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--self-test":
        return self_test()
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0  # no readable event: never block on a malformed call
    if not isinstance(event, dict):
        return 0
    if mode == "record":
        return record(event)
    if mode == "check":
        return check(event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
