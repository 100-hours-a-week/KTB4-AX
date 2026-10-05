"""임시 HOME과 로컬 bare 원격으로 설치부터 통계까지 확인한다. 실제 설정은 건드리지 않는다."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import aimanager  # noqa: E402

SCRIPT = str(ROOT / "aimanager.py")


def sh(*cmd, cwd=None, env=None, stdin=None):
    return subprocess.run(cmd, cwd=cwd, env=env, input=stdin, capture_output=True, text=True, check=True).stdout


class Pure(unittest.TestCase):
    def test_skills_used(self):
        team = {"adr": None, "grilling": None, "domain-modeling": None}
        with mock.patch.object(aimanager, "team_skills", return_value=team):
            used = aimanager.skills_used
            self.assertEqual(used({"tool_name": "Skill", "tool_input": {"skill": "grilling"}}), {"grilling"})
            self.assertEqual(used({"prompt": "/adr DB 고르자"}), {"adr"})
            self.assertEqual(used({"prompt": "$domain-modeling 정리, $HOME 말고"}), {"domain-modeling"})
            self.assertEqual(used({"tool_input": {"command": "cat ~/.agents/skills/adr/SKILL.md"}}), {"adr"})
            self.assertEqual(used({"prompt": "파일 /x/skills/adr 봐줘"}), set())  # 경로 속 /adr는 호출이 아님
            self.assertEqual(used({"tool_name": "Skill", "tool_input": {"skill": "orca-cli"}}), set())  # 팀 스킬 아님

    def test_repo_id(self):
        same = {"https://github.com/A/b.git", "git@github.com:a/B.git", "https://github.com/a/b/"}
        self.assertEqual({aimanager._repo_id(u) for u in same}, {"a/b"})

    def test_mcp_add_cmd(self):
        http = {"name": "n", "transport": "http", "url": "https://x/mcp", "headers": {"Authorization": "Bearer ${T}"}}
        self.assertEqual(aimanager.codex_http_toml(http),
                         '[mcp_servers."n"]\nurl = "https://x/mcp"\nbearer_token_env_var = "T"\n')
        self.assertIsNone(aimanager.codex_http_toml({**http, "headers": {"X-Key": "1"}}))
        self.assertIsNone(aimanager.mcp_add_cmd("codex", {**http, "transport": "sse"}))
        stdio = {"name": "f", "command": "npx", "args": ["-y", "p"], "env": {"A": "1"}}
        self.assertEqual(aimanager.mcp_add_cmd("codex", stdio), ["codex", "mcp", "add", "f", "--env", "A=1", "--", "npx", "-y", "p"])
        spec = json.loads(aimanager.mcp_add_cmd("claude", http)[-1])
        self.assertEqual(spec["type"], "http")


class EndToEnd(unittest.TestCase):
    def test_install_track_report_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            home, remote, work = tmp / "home", tmp / "remote.git", tmp / "work"
            home.mkdir()
            env = {**os.environ, "HOME": str(home), "GIT_CONFIG_GLOBAL": "/dev/null",
                   "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            # 팀 저장소: 스킬 2개 + 빈 stats 브랜치
            sh("git", "init", "-q", "--bare", "-b", "main", str(remote))
            sh("git", "clone", "-q", str(remote), str(work), env=env)
            for n in ("adr", "grilling"):
                (work / "skills" / n).mkdir(parents=True)
                (work / "skills" / n / "SKILL.md").write_text(f"---\nname: {n}\n---\n")
            (work / "mcp").mkdir()
            (work / "mcp" / "mcp.json").write_text('{"servers": []}')
            (work / "aimanager.json").write_text('{"team": "t"}')
            sh("git", "add", "-A", cwd=work, env=env)
            sh("git", "commit", "-qm", "init", cwd=work, env=env)
            sh("git", "push", "-q", "origin", "main", cwd=work, env=env)
            sh("git", "checkout", "-q", "--orphan", "stats", cwd=work, env=env)
            sh("git", "rm", "-rqf", ".", cwd=work, env=env)
            sh("git", "commit", "-q", "--allow-empty", "-m", "stats", cwd=work, env=env)
            sh("git", "push", "-q", "origin", "stats", cwd=work, env=env)
            # 같은 이름의 개인 스킬
            personal = home / ".claude" / "skills" / "adr"
            personal.mkdir(parents=True)
            (personal / "SKILL.md").write_text("personal")

            sh(sys.executable, SCRIPT, "init", str(remote), env=env)
            sh(sys.executable, SCRIPT, "init", str(remote), env=env)  # 다시 실행해도 안전해야 한다

            claude, agents = home / ".claude" / "skills", home / ".agents" / "skills"
            self.assertFalse((claude / "adr").is_symlink())  # 개인 스킬 우선
            self.assertTrue((agents / "adr").is_symlink())
            self.assertTrue((claude / "grilling").is_symlink())
            self.assertTrue((claude / "aimanager").is_symlink())  # 도구 기본 스킬
            hooks = json.loads((home / ".claude" / "settings.json").read_text())["hooks"]
            self.assertEqual({k: len(v) for k, v in hooks.items()},
                             {"SessionStart": 1, "UserPromptSubmit": 1, "PostToolUse": 1})
            self.assertEqual(len(json.loads((home / ".codex" / "hooks.json").read_text())["hooks"]), 3)

            def hook(event, tool, payload):
                return sh(sys.executable, SCRIPT, "hook", event, tool, env=env, stdin=json.dumps(payload))

            hook("post-tool-use", "claude", {"session_id": "c1", "tool_name": "Skill", "tool_input": {"skill": "grilling"}})
            hook("prompt-submit", "claude", {"session_id": "c1", "prompt": "/adr"})
            hook("prompt-submit", "codex", {"session_id": "x1", "prompt": "$grilling 해줘"})
            hook("post-tool-use", "codex", {"session_id": "x1", "tool_name": "Bash",
                                             "tool_input": {"command": "cat ~/.agents/skills/grilling/SKILL.md"}})
            state = home / ".aimanager" / "state"
            self.assertEqual(len((state / "usage.tsv").read_text().splitlines()), 4)

            sh(sys.executable, SCRIPT, "pull", "--quiet", env=env)
            self.assertFalse((state / "usage.tsv").exists())  # 보고 후 비워짐
            self.assertIn("stats:", sh("git", "-C", str(remote), "log", "--oneline", "stats"))

            out = sh(sys.executable, SCRIPT, "digest", env=env)
            self.assertIn("3회", out)  # codex 같은 세션의 grilling 두 번은 한 번으로

            # 패키지 선언이 바뀌면 다음 프롬프트에 한 번만 안내
            sh("git", "checkout", "-q", "main", cwd=work, env=env)
            (work / "aimanager.json").write_text(json.dumps({"team": "t", "packages": {
                "npm": [{"name": "eslint", "version": "latest", "global": True}],
                "claude": {"marketplaces": [], "plugins": []}}}))
            (work / "skills" / "grilling" / "SKILL.md").unlink()
            (work / "skills" / "grilling").rmdir()
            sh("git", "commit", "-qam", "change", cwd=work, env=env)
            sh("git", "push", "-q", "origin", "main", cwd=work, env=env)
            sh(sys.executable, SCRIPT, "pull", "--quiet", env=env)
            self.assertFalse((claude / "grilling").exists() or (claude / "grilling").is_symlink())  # 삭제 반영
            self.assertIn("[AIManager]", hook("prompt-submit", "claude", {"prompt": "hi"}))
            self.assertEqual(hook("prompt-submit", "claude", {"prompt": "hi"}), "")

            # 다른 팀 저장소로 init하면 멈춘다
            r = subprocess.run([sys.executable, SCRIPT, "init", "https://github.com/other/team.git"],
                               env=env, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("이미 다른 팀", r.stderr)

            sh(sys.executable, SCRIPT, "uninstall", env=env)
            self.assertNotIn("hooks", {k for k, v in json.loads((home / ".claude" / "settings.json").read_text()).items() if v})
            self.assertFalse((agents / "adr").is_symlink())
            self.assertTrue((claude / "adr").exists())  # 개인 스킬은 남는다


if __name__ == "__main__":
    unittest.main()
