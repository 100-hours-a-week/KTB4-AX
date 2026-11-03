#!/usr/bin/env python3
"""config.json 생성. 네 가지(과정 · 팀 번호 · 이름 · GitHub 계정)를 받아서 쓴다.

gh 활동 기록으로 '제안값'을 만들어 주지만, 네 값은 항상 명시적으로 확정해야 한다.

  bootstrap.py                 # 터미널이면 네 가지를 차례로 물어본다
  bootstrap.py --suggest       # 제안값만 JSON 으로 출력 (파일 안 씀)
  bootstrap.py --github-username kkkk2058 --team 13 \
               --course 인공지능 --name "sevan.kim (김세훈)/인공지능"

비터미널(에이전트)에서 네 값이 다 안 들어오면 아무것도 쓰지 않고 종료 코드 3 과
함께 제안값을 돌려준다 — 에이전트가 사용자에게 물어본 뒤 인자로 넘기라는 뜻이다.

종료 코드: 0 정상 / 2 gh 준비 안 됨 / 3 네 값이 확정되지 않음
"""
import argparse, json, os, re, shutil, subprocess, sys

ORG = "100-hours-a-week"
# 레포 접미사 → (과정명, 담당 강사)
PARTS = {"AI": ("인공지능", "알렉스"), "FE": ("풀스택", "케빈"),
         "BE": ("풀스택", "케빈"), "CLOUD": ("클라우드", "찰리")}
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def ensure_gh():
    """gh 설치·인증 확인. 없으면 brew 로 설치까지 시도한다."""
    if not shutil.which("gh"):
        if not shutil.which("brew"):
            print("gh CLI 가 없고 Homebrew 도 없습니다.\n"
                  "  https://cli.github.com 에서 설치한 뒤 다시 실행하세요.", file=sys.stderr)
            sys.exit(2)
        print("gh CLI 가 없어 설치합니다 (brew install gh)... 몇 분 걸릴 수 있습니다.", file=sys.stderr)
        if subprocess.run(["brew", "install", "gh"]).returncode != 0:
            print("brew install gh 실패. 직접 설치해주세요: https://cli.github.com", file=sys.stderr)
            sys.exit(2)
    if sh("gh", "auth", "status")[0] != 0:
        print("gh 인증이 필요합니다. 아래를 실행한 뒤 다시 시도하세요:\n\n  gh auth login\n",
              file=sys.stderr)
        sys.exit(2)


def my_repos(login):
    """내가 이슈·코멘트를 남긴 org 레포 이름들."""
    names = set()
    for q in (f"author:{login}", f"commenter:{login}"):
        code, out, _ = sh("gh", "api", "--paginate",
                          f"search/issues?q={q}+org:{ORG}&per_page=100",
                          "--jq", ".items[].repository_url")
        if code == 0:
            names |= {u.rsplit("/", 1)[-1] for u in out.splitlines() if u}
    return names


def detect(override=None):
    override = override or {}
    ensure_gh()
    code, login, _ = sh("gh", "api", "user", "--jq", ".login")
    if code != 0 or not login:
        print("GitHub 계정을 못 읽었습니다. 'gh auth login' 을 확인하세요.", file=sys.stderr)
        sys.exit(2)
    _, gh_name, _ = sh("gh", "api", "user", "--jq", ".name // empty")
    login = override.get("github_username") or login

    repos = my_repos(login)
    out = {"github_username": login, "_detected_from": sorted(repos)}

    teams = {int(m.group(1)) for r in repos
             if (m := re.fullmatch(r"KTB4-(\d+)th-wiki", r, re.I))}
    if override.get("team") and str(override["team"]).isdecimal():
        teams = {int(override["team"])}
    if len(teams) == 1:
        t = teams.pop()
        out["team_number"] = t
        out["github_daily_scrum_repo"] = f"{ORG}/KTB4-{t}th-wiki"
        out["github_troubleshooting_repo"] = f"{ORG}/KTB4-{t}th-wiki"
    else:
        out["_unresolved_team"] = sorted(teams)

    parts = {m.group(1).upper() for r in repos
             if (m := re.fullmatch(r"KTB4-\d+th-(AI|FE|BE|Cloud)", r, re.I))}
    courses = {PARTS[p] for p in parts if p in PARTS}
    if override.get("course"):
        want = override["course"]
        courses = {v for v in PARTS.values() if want in v} or {(want, want)}
    if len(courses) == 1:
        course, teacher = courses.pop()
        out["course"] = f"카카오테크 부트캠프 판교 - {teacher} 과정"
        out["_course_part"] = course
    else:
        out["_unresolved_course"] = sorted(parts)

    # 이름은 GitHub 에서 알 수 없다 (닉네임·한글이름 매핑이 아무 데도 없음).
    # 커밋 author 이름으로 후보만 제시한다.
    _, commit_name, _ = sh("gh", "search", "commits", "--author", login, "--owner", ORG,
                           "--limit", "1", "--json", "commit",
                           "--jq", ".[0].commit.author.name // empty")
    cand = (commit_name or gh_name or login).lower()
    if "_course_part" in out:
        out["_name_suggestion"] = f"{cand} (한글이름)/{out['_course_part']}"
    return out


STARTER_DEFAULTS = {
    "_주의": "의견은 기본적으로 긍정 문구를 무작위 선택합니다. 제출 전에 확인하세요. 고정 문구는 feedback_mode를 fixed로 바꾸고 아래에 적습니다.",
    "아쉬웠던 점": "",
    "좋았던 점": "",
    "강사에 대한 피드백": "",
    "교육/세미나에 대한 평점": "10",
    "교육/세미나 평점을 남기신 이유": "",
    "오늘의 본인의 성과에 대한 평점": "10",
    "스스로 개선하거나": "",
    "비고": "",
}


PLACEHOLDER = "한글이름"
COURSES = ["인공지능", "풀스택", "클라우드"]
TEACHER = {"인공지능": "알렉스", "풀스택": "케빈", "클라우드": "찰리"}


def interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


def prompt(label, hint, suggestion, validate):
    """suggestion 을 Enter 기본값으로 제시하고 답을 받는다. 못 받으면 None."""
    print(f"\n{label}")
    if hint:
        print(f"  {hint}")
    ok = suggestion and validate(suggestion) and PLACEHOLDER not in str(suggestion)
    if ok:
        print(f"  Enter = {suggestion}")
    elif suggestion:
        print(f"  예시: {str(suggestion).replace(PLACEHOLDER, '김세훈')}")
    for _ in range(3):
        try:
            a = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if not a and ok:
            return suggestion
        if a and PLACEHOLDER not in a and validate(a):
            return a
        print("  값을 다시 확인해주세요.")
    return None


def resolve(a, d):
    """네 값을 확정한다. 확정 못 하면 (None, 안내문) 을 돌려준다."""
    sug = {
        "github_username": d.get("github_username"),
        "team": d.get("team_number"),
        "course": d.get("_course_part"),
        "name": d.get("_name_suggestion"),
    }
    got = {"github_username": a.github_username, "team": a.team,
           "course": a.course, "name": a.name}

    checks = {
        "github_username": lambda v: bool(str(v).strip()),
        "team": lambda v: str(v).isdecimal() and 1 <= int(v) <= 20,
        "course": lambda v: v in COURSES,
        "name": lambda v: bool(str(v).strip()) and PLACEHOLDER not in str(v),
    }
    labels = {
        "github_username": ("GitHub 계정을 알려주세요.", "Daily Scrum 코멘트를 찾을 때 씁니다."),
        "team": ("팀 번호는 몇 번인가요?", "1~20. 월·금 분단 강사 폼을 고르는 기준입니다."),
        "course": ("소속 과정은 무엇인가요?", " / ".join(COURSES)),
        "name": ("폼에 쓰는 이름을 알려주세요.", "영어닉네임 (한글이름)/과정 형식입니다."),
    }
    for k in ("github_username", "team", "course", "name"):
        if got[k] is None and interactive():
            got[k] = prompt(*labels[k], sug[k], checks[k])
        if got[k] is None:
            continue
        if not checks[k](got[k]):
            return None, f"{k} 값이 올바르지 않습니다: {got[k]!r}"

    missing = [k for k in got if got[k] is None]
    if missing:
        return None, missing
    got["team"] = int(got["team"])
    return got, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="폼에 쓸 이름. 예: 'sevan.kim (김세훈)/인공지능'")
    ap.add_argument("--github-username", help="본인 GitHub 계정")
    ap.add_argument("--team", help="팀 번호 (1~20)")
    ap.add_argument("--course", help=" / ".join(COURSES))
    ap.add_argument("--suggest", action="store_true", help="제안값만 출력")
    ap.add_argument("--json", dest="suggest", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--force", action="store_true", help="기존 config.json 덮어쓰기")
    a = ap.parse_args()

    path = os.path.join(HERE, "config.json")
    if os.path.exists(path) and not a.force and not a.suggest:
        print(f"이미 있습니다: {path}\n덮어쓰려면 --force", file=sys.stderr)
        return

    d = detect({"github_username": a.github_username, "team": a.team, "course": a.course})
    if a.suggest:
        print(json.dumps({
            "github_username": d.get("github_username"),
            "team": d.get("team_number"),
            "course": d.get("_course_part"),
            "name": d.get("_name_suggestion"),
            "_detected_from": d.get("_detected_from", []),
        }, ensure_ascii=False, indent=2))
        return

    got, problem = resolve(a, d)
    if got is None:
        print("설정을 만들지 않았습니다 — 아래 네 가지를 사용자에게 확인한 뒤 "
              "인자로 넘겨서 다시 실행하세요.", file=sys.stderr)
        if isinstance(problem, str):
            print(f"  {problem}", file=sys.stderr)
        print(json.dumps({
            "필요한 값": ["--github-username", "--team", "--course", "--name"],
            "제안값": {
                "github_username": d.get("github_username"),
                "team": d.get("team_number"),
                "course": d.get("_course_part"),
                "name": d.get("_name_suggestion"),
            },
            "과정 선택지": COURSES,
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)

    t, course = got["team"], got["course"]
    cfg = {
        "course": f"카카오테크 부트캠프 판교 - {TEACHER[course]} 과정",
        "name": got["name"],
        "team_number": t,
        "github_daily_scrum_repo": f"{ORG}/KTB4-{t}th-wiki",
        "github_troubleshooting_repo": f"{ORG}/KTB4-{t}th-wiki",
        "github_username": got["github_username"],
        "form_urls": {},
        "feedback_mode": "positive_random",
        "defaults": STARTER_DEFAULTS,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"생성: {path}")
    for k in ("github_username", "team_number", "course", "name", "github_daily_scrum_repo"):
        print(f"  {k} = {cfg[k]}")


if __name__ == "__main__":
    main()
