"""Fresh-copy checks. GitHub, browser, and global install paths are isolated."""
import json
import os
from pathlib import Path
import pty
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit


PACKAGE = Path(__file__).resolve().parents[1]


class FirstRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="daily-retro-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / "daily-retro"
        shutil.copytree(PACKAGE, self.package, symlinks=True,
                        ignore=shutil.ignore_patterns("config.json", "__pycache__"))
        self.skill = self.package / ".claude/skills/daily-retro"
        self.config = self.skill / "config.json"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        PYTHONDONTWRITEBYTECODE="1",
                        DAILY_RETRO_TEST_DIR=str(self.root / "global-skills"))
        self.executable("gh", '''import os, sys
args = sys.argv[1:]
if args[:2] == ["auth", "status"]:
    sys.exit(2 if os.environ.get("TEST_GH_UNAUTHENTICATED") else 0)
if args[:2] == ["api", "user"]:
    print("fixture-user" if args[-1] == ".login" else "Fixture User")
elif args[:2] == ["api", "--paginate"]:
    print("https://api.github.com/repos/100-hours-a-week/KTB4-13th-wiki")
    print("https://api.github.com/repos/100-hours-a-week/KTB4-13th-AI")
elif args[:2] == ["search", "commits"]:
    print("fixture.author")
else:
    sys.exit("Unexpected gh arguments: " + repr(args))
''')
        # Redirect only mkdir/ln destinations; the real HOME is never changed.
        for name in ("mkdir", "ln"):
            self.executable(name, '''import os, subprocess, sys
name = os.path.basename(sys.argv[0])
original = os.path.expanduser("~")
target = os.environ["DAILY_RETRO_TEST_DIR"]
args = [target + a[len(original):] if a.startswith(original + "/") else a
        for a in sys.argv[1:]]
sys.exit(subprocess.call(["/bin/" + name, *args]))
''')

    def executable(self, name, source):
        path = self.bin / name
        path.write_text("#!" + sys.executable + "\n" + source)
        path.chmod(0o755)

    def run_script(self, script, *args, env=None):
        return subprocess.run([sys.executable, str(self.skill / "scripts" / script), *args],
                              cwd=self.package, env=env or self.env, input="",
                              text=True, capture_output=True, timeout=15)

    def bootstrap(self, *args, **kwargs):
        return self.run_script("bootstrap.py", *args, **kwargs)

    def confirmed(self, *extra):
        return self.bootstrap("--github-username", "fixture-user", "--team", "13",
                              "--course", "인공지능", "--name",
                              "fixture.kim (테스트)/인공지능", *extra)

    def test_bundled_skill_links_resolve(self):
        linked = self.package / ".agents/skills/daily-retro/SKILL.md"
        self.assertEqual(linked.resolve(), (self.skill / "SKILL.md").resolve())
        self.assertTrue(linked.is_file())

    def test_suggest_does_not_create_config(self):
        result = self.bootstrap("--suggest")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout)
        self.assertEqual((values["github_username"], values["team"], values["course"]),
                         ("fixture-user", 13, "인공지능"))
        self.assertFalse(self.config.exists())

    def test_agent_requires_four_confirmed_values(self):
        result = self.bootstrap()
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertFalse(self.config.exists())

    def test_terminal_prompts_create_confirmed_config(self):
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        process = subprocess.Popen(
            [sys.executable, str(self.skill / "scripts/bootstrap.py")],
            stdin=slave, stdout=slave, stderr=slave, cwd=self.package, env=self.env)
        os.close(slave)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        os.write(master, "\n\n\nfixture.kim (테스트)/인공지능\n".encode())
        self.assertEqual(process.wait(timeout=15), 0)
        config = json.loads(self.config.read_text())
        self.assertEqual(config["github_username"], "fixture-user")
        self.assertEqual(config["team_number"], 13)
        self.assertEqual(config["name"], "fixture.kim (테스트)/인공지능")

    def test_confirmed_setup_creates_personal_config(self):
        result = self.confirmed()
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(self.config.read_text())
        self.assertEqual(config["github_username"], "fixture-user")
        self.assertEqual(config["team_number"], 13)
        self.assertEqual(config["course"], "카카오테크 부트캠프 판교 - 알렉스 과정")
        self.assertEqual(config["form_urls"], {})
        self.assertEqual(config["github_daily_scrum_repo"], "100-hours-a-week/KTB4-13th-wiki")

    def test_placeholder_name_is_rejected(self):
        result = self.confirmed("--name", "fixture.kim (한글이름)/인공지능")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertFalse(self.config.exists())

    def test_invalid_team_reports_validation_error(self):
        result = self.confirmed("--team", "abc")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.config.exists())

    def test_unauthenticated_first_run_stops_without_config(self):
        env = dict(self.env, TEST_GH_UNAUTHENTICATED="1")
        result = self.bootstrap("--suggest", env=env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("gh auth login", result.stderr)
        self.assertFalse(self.config.exists())

    def test_existing_config_is_preserved_without_detection(self):
        self.assertEqual(self.confirmed().returncode, 0)
        before = self.config.read_bytes()
        result = self.bootstrap(env=dict(self.env, TEST_GH_UNAUTHENTICATED="1"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.config.read_bytes(), before)

    def test_install_keeps_first_run_unconfigured(self):
        for _ in range(2):
            result = subprocess.run(["bash", "install.sh"], cwd=self.package,
                                    env=self.env, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.config.exists(), "Installer must not activate example placeholders")
        for tool in (".claude", ".agents"):
            link = self.root / "global-skills" / tool / "skills/daily-retro"
            self.assertEqual(link.resolve(), self.skill.resolve())
        self.assertEqual(self.bootstrap().returncode, 3)

    def form_fixture(self):
        defaults = json.loads((self.skill / "config.example.json").read_text())["defaults"]
        labels = [k for k in defaults if not k.startswith("_")]
        labels += ["이름", "수업일", "오늘 학습한 내용"]
        questions = [[i, label, None, 9 if label == "수업일" else 0,
                      [[100 + i, None]]] for i, label in enumerate(labels)]
        fixture = self.root / "form.html"
        fixture.write_text("<script>var FB_PUBLIC_LOAD_DATA_ = " +
                           json.dumps([None, [None, questions]], ensure_ascii=False) + ";</script>")
        answers = dict(defaults, 이름="fixture.kim (테스트)/인공지능", 수업일="2026-11-03",
                       **{"오늘 학습한 내용": "설치 & 첫 실행 검증"})
        answer_file = self.root / "answers.json"
        answer_file.write_text(json.dumps(answers, ensure_ascii=False))
        return fixture, answer_file, labels

    def test_prefill_handles_defaults_metadata_and_date(self):
        fixture, answers, labels = self.form_fixture()
        marker = self.root / "browser-called"
        self.executable("open", f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        result = self.run_script("prefill.py", "--form", fixture.as_uri(),
                                 "--answers", str(answers), "--no-open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        query = parse_qs(urlsplit(result.stdout.strip()).query)
        date_id = 100 + labels.index("수업일")
        self.assertEqual(query[f"entry.{date_id}_year"], ["2026"])
        self.assertEqual(query[f"entry.{date_id}_month"], ["11"])
        self.assertEqual(query[f"entry.{date_id}_day"], ["3"])
        text_id = 100 + labels.index("오늘 학습한 내용")
        self.assertEqual(query[f"entry.{text_id}"], ["설치 & 첫 실행 검증"])

    def test_prefill_default_opens_generated_link(self):
        fixture, answers, _ = self.form_fixture()
        marker = self.root / "browser-args.json"
        self.executable("open", f'import json, sys\nfrom pathlib import Path\n'
                                f'Path({str(marker)!r}).write_text(json.dumps(sys.argv[1:]))\n')
        result = self.run_script("prefill.py", "--form", fixture.as_uri(),
                                 "--answers", str(answers))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(marker.read_text()), [result.stdout.strip()])

    def test_prefill_matches_form_with_different_spacing(self):
        fixture, answers, _ = self.form_fixture()
        fixture.write_text(fixture.read_text().replace("교육/세미나 평점을", "교육/세미나평점을"))
        result = self.run_script("prefill.py", "--form", fixture.as_uri(),
                                 "--answers", str(answers), "--no-open")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unknown_answer_label_stops_prefill(self):
        fixture, answers, _ = self.form_fixture()
        answers.write_text(json.dumps({"없는 질문": "값"}))
        result = self.run_script("prefill.py", "--form", fixture.as_uri(),
                                 "--answers", str(answers), "--no-open")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("없는 질문", result.stderr)

    def test_ambiguous_answer_label_stops_prefill(self):
        fixture, answers, _ = self.form_fixture()
        answers.write_text(json.dumps({"평점": "10"}))
        result = self.run_script("prefill.py", "--form", fixture.as_uri(),
                                 "--answers", str(answers), "--no-open")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("여러 문항", result.stderr)


if __name__ == "__main__":
    unittest.main()
