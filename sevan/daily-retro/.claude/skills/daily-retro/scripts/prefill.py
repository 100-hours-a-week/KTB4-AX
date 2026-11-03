#!/usr/bin/env python3
"""구글폼 사전채움(prefill) 링크 생성기.

폼 HTML에서 entry ID를 직접 뽑아 라벨로 매칭하므로 entry ID를 하드코딩하지 않는다.
사용법:
  prefill.py --form <URL> --list                      # 질문 라벨 + entry ID + 타입 확인
  prefill.py --form <URL> --answers a.json [--open]   # 링크 생성 (기본으로 브라우저에서 염)

answers.json 은 {"라벨의 일부": "값"} 형태. 키는 질문 라벨의 고유한 부분 문자열이면 된다.
  - 라벨 매칭에서는 폼마다 다른 띄어쓰기를 무시한다.
  - 날짜 문항(타입 9)은 값을 "YYYY-MM-DD" 로 준다.
  - 값이 빈 문자열이면 그 문항은 링크에서 빼서 사람이 직접 채우게 남긴다.
  - _ 로 시작하는 키는 config.defaults 의 안내용 메타데이터라 무시한다.
  - 키가 0개 또는 2개 이상의 라벨에 걸리면 에러로 멈춘다(조용히 틀리지 않게).
"""
import argparse, json, re, subprocess, sys, urllib.request
from urllib.parse import quote

TYPES = {0: "단답형", 1: "장문형", 2: "객관식", 3: "드롭다운", 4: "체크박스",
         5: "선형배율", 9: "날짜", 18: "평점(선형배율)"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8", "replace")


def parse_questions(html: str):
    m = re.search(r"FB_PUBLIC_LOAD_DATA_ = (.*?);</script>", html, re.S)
    if not m:
        sys.exit("FB_PUBLIC_LOAD_DATA_ 를 찾지 못했습니다. 폼 URL이 맞는지, 로그인이 필요한 폼은 아닌지 확인하세요.")
    data = json.loads(m.group(1))
    out = []
    for q in data[1][1]:
        label, qtype, subs = q[1], q[3], (q[4] or [])
        for s in subs:
            out.append({"entry": s[0], "label": label, "type": qtype,
                        "options": [o[0] for o in (s[1] or [])] if s[1] else None})
    return out


def resolve(questions, key):
    normalized_key = re.sub(r"\s+", "", key)
    hits = [q for q in questions if normalized_key in re.sub(r"\s+", "", q["label"])]
    if not hits:
        sys.exit(f"[에러] 라벨에 '{key}' 를 포함하는 문항이 없습니다. --list 로 실제 라벨을 확인하세요.")
    if len(hits) > 1:
        labels = " / ".join(q["label"] for q in hits)
        sys.exit(f"[에러] '{key}' 가 여러 문항에 걸립니다 → {labels}\n더 구체적인 키를 쓰세요.")
    return hits[0]


def build(form_url, questions, answers):
    parts = ["usp=pp_url"]
    skipped = []
    for key, value in answers.items():
        if key.startswith("_"):
            continue
        q = resolve(questions, key)
        value = str(value).strip()
        if not value:
            skipped.append(q["label"])
            continue
        if q["type"] == 9:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                sys.exit(f"[에러] 날짜 문항 '{q['label']}' 값은 YYYY-MM-DD 여야 합니다 (받은 값: {value})")
            y, mo, d = value.split("-")
            e = q["entry"]
            parts += [f"entry.{e}_year={y}", f"entry.{e}_month={int(mo)}", f"entry.{e}_day={int(d)}"]
        else:
            if q["options"] and value not in q["options"]:
                sys.exit(f"[에러] '{q['label']}' 의 값 '{value}' 은 선택지에 없습니다 → {q['options']}")
            parts.append(f"entry.{q['entry']}={quote(value)}")
    base = form_url.split("?")[0]
    return base + "?" + "&".join(parts), skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", required=True)
    ap.add_argument("--answers")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--open", dest="do_open", action="store_true", default=True)
    ap.add_argument("--no-open", dest="do_open", action="store_false")
    a = ap.parse_args()

    questions = parse_questions(fetch(a.form))

    if a.list or not a.answers:
        for q in questions:
            print(f"entry.{q['entry']:<12} [{TYPES.get(q['type'], q['type'])}] {q['label']}")
            if q["options"]:
                print(f"{'':<20}  선택지: {q['options']}")
        return

    with open(a.answers, encoding="utf-8") as f:
        answers = json.load(f)
    url, skipped = build(a.form, questions, answers)

    if skipped:
        print("[빈 채로 남김 — 사람이 직접 입력]", file=sys.stderr)
        for s in skipped:
            print("  -", s, file=sys.stderr)
    print(url)
    if a.do_open:
        subprocess.run(["open", url], check=False)


if __name__ == "__main__":
    main()
