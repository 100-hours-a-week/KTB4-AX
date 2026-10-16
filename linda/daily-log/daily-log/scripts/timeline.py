#!/usr/bin/env python3
"""하루치 screenpipe 기록을 3분 블록 타임라인 HTML로 만든다.

    python3 timeline.py 2026-09-23     # 그날 타임라인을 stdout으로
    python3 timeline.py --selftest     # 네트워크 없이 로직만 검증

출력을 그대로 일기(raw/일기/YYYY-MM-DD.md)의 `## 타임라인` 자리에 붙인다.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

API = os.environ.get("SCREENPIPE_LOCAL_API_URL", "http://localhost:3030")
KEY = os.environ.get("SCREENPIPE_LOCAL_API_KEY") or os.environ.get("SCREENPIPE_API_KEY", "")
HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(HERE, "app-category.json")

BUCKET = 3  # 분
ROWS = 60 // BUCKET
SQL_MAX = 10000  # screenpipe /raw_sql이 허용하는 최대 LIMIT (0.4.x에서 확인)
COLORS = {"focus": "#8aa870", "neutral": "#7e8a99", "drift": "#c4826b"}
LABELS = {"focus": "집중", "neutral": "중립", "drift": "표류"}


# ---------- screenpipe ----------

def sql(query):
    """읽기 전용 SQL. 라이브 db.sqlite에 직접 붙지 않고 데몬을 거친다."""
    capped = "limit" not in query.lower()
    if capped:
        query += " LIMIT %d" % SQL_MAX  # /raw_sql은 LIMIT 없는 조회를 400으로 거절한다
    req = urllib.request.Request(
        API + "/raw_sql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": "Bearer " + KEY,
            "Content-Type": "application/json",
            "X-Screenpipe-Client": "api",
            "X-Screenpipe-Agent": "claude",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        rows = rows_of(json.loads(r.read().decode()))
    if capped and len(rows) >= SQL_MAX:
        print("[경고] 조회가 상한 %d행에 걸렸습니다. 결과가 잘렸을 수 있습니다." % SQL_MAX,
              file=sys.stderr)
    return rows


def rows_of(payload):
    """raw_sql 응답 형태가 버전마다 달라서 흔한 셋을 모두 받아넘긴다."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for k in ("data", "rows", "results"):
            if isinstance(payload.get(k), list):
                return payload[k]
    raise SystemExit("raw_sql 응답 형태를 모르겠습니다: " + repr(payload)[:300])


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


# ---------- 시간 ----------

def parse_ts(raw):
    """screenpipe timestamp를 로컬 시각으로. 타임존 표기가 없으면 UTC로 본다."""
    s = str(raw).strip().replace(" ", "T")
    s = re.sub(r"(\.\d{1,6})\d*", r"\1", s)  # 나노초 절삭
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone()


def bucket_key(dt):
    return dt.hour, (dt.minute // BUCKET) * BUCKET


# ---------- 분류 ----------

def load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        r = json.load(f)
    return r.get("window", {}), r.get("app", {})


def classify(app, window, win_rules, app_rules):
    """창 제목 키워드 우선, 없으면 앱 이름. 어느 쪽에도 없으면 None(미분류)."""
    hay = (window or "").lower()
    for kw, cat in win_rules.items():
        if kw.lower() in hay:
            return cat
    hay = (app or "").lower()
    for kw, cat in app_rules.items():
        if kw.lower() in hay:
            return cat
    return None


# ---------- 수집 ----------

def frame_columns():
    rows = sql("SELECT * FROM frames LIMIT 1")
    if not rows or not isinstance(rows[0], dict):
        raise SystemExit("frames 테이블의 컬럼명을 읽지 못했습니다. 스키마를 먼저 확인해 주세요.")
    return set(rows[0].keys())


def input_table():
    """입력 이벤트 테이블이 있으면 이름을 준다. 없으면 대기 구간 구분을 끈다."""
    rows = sql("SELECT name FROM sqlite_master WHERE type='table'")
    names = [r.get("name", "") for r in rows if isinstance(r, dict)]
    for n in names:
        if "input" in n.lower() or "ui_monitoring" in n.lower():
            return n
    return None


def collect(day):
    """하루치를 (시,분) 버킷 → 최다 점유 (앱, 창)으로 접는다."""
    cols = frame_columns()
    lo = (day - timedelta(days=1)).isoformat()
    hi = (day + timedelta(days=2)).isoformat()  # 타임존 차이를 양쪽으로 여유

    win = "window_name" if "window_name" in cols else "NULL AS window_name"
    where = "timestamp >= %s AND timestamp < %s" % (q(lo), q(hi))
    if "focused" in cols:
        where += " AND focused = 1"  # 활성 창만

    rows = sql(
        "SELECT substr(timestamp,1,16) AS m, app_name, %s, COUNT(*) AS c "
        "FROM frames WHERE %s GROUP BY m, app_name, window_name" % (win, where)
    )

    tally = defaultdict(Counter)
    for r in rows:
        dt = parse_ts(r.get("m"))
        if dt is None or dt.date() != day:
            continue
        tally[bucket_key(dt)][(r.get("app_name") or "?", r.get("window_name") or "")] += int(r.get("c") or 1)

    return {k: v.most_common(1)[0][0] for k, v in tally.items() if v}


def collect_input(day, table):
    """사람이 실제로 조작한 버킷 집합."""
    lo = (day - timedelta(days=1)).isoformat()
    hi = (day + timedelta(days=2)).isoformat()
    try:
        rows = sql(
            "SELECT DISTINCT substr(timestamp,1,16) AS m FROM %s "
            "WHERE timestamp >= %s AND timestamp < %s" % (table, q(lo), q(hi))
        )
    except Exception:
        return None
    out = set()
    for r in rows:
        dt = parse_ts(r.get("m"))
        if dt is not None and dt.date() == day:
            out.add(bucket_key(dt))
    return out


# ---------- 렌더 ----------

def cell(cat, active):
    style = "background:" + (COLORS[cat] if cat else "#c9c6c0")
    if active is False:
        style += ";opacity:.35"  # 입력이 없던 블록 = 에이전트 실행/대기
    return '<td style="%s"></td>' % style


def render(day, blocks, typed, win_rules, app_rules):
    hours = sorted({h for h, _ in blocks})
    if not hours:
        return "> [!warning] 이 날짜의 화면 기록이 없습니다.\n"
    hours = list(range(hours[0], hours[-1] + 1))

    cat_of, mins = {}, Counter()
    for key, (app, window) in blocks.items():
        c = classify(app, window, win_rules, app_rules)
        cat_of[key] = c
        mins[c] += BUCKET

    out = ['<div style="font:11px/1.4 var(--font-monospace);overflow-x:auto">']
    legend = []
    for c in ("focus", "neutral", "drift"):
        if mins[c]:
            legend.append(
                '<span style="display:inline-block;width:10px;height:10px;background:%s;'
                'border-radius:2px;vertical-align:-1px"></span> %s %s'
                % (COLORS[c], LABELS[c], hhmm(mins[c]))
            )
    if mins[None]:
        legend.append(
            '<span style="display:inline-block;width:10px;height:10px;background:#c9c6c0;'
            'border-radius:2px;vertical-align:-1px"></span> 미분류 %s' % hhmm(mins[None])
        )
    legend.append(
        '<span style="display:inline-block;width:10px;height:10px;'
        'border:1px solid var(--background-modifier-border);border-radius:2px;'
        'vertical-align:-1px"></span> 미기록'
    )
    out.append("\n".join(legend))

    out.append('<table style="border-collapse:separate;border-spacing:2px;'
               'table-layout:fixed;margin-top:8px">')
    head = ['<td style="width:26px"></td>']
    head += ['<td style="width:24px">%d시</td>' % h for h in hours]
    out.append('<tr style="height:11px;color:var(--text-muted)">' + "".join(head) + "</tr>")

    for m in range(0, 60, BUCKET):
        tds = ['<td style="color:var(--text-muted)">:%02d</td>' % m]
        for h in hours:
            key = (h, m)
            if key not in blocks:
                tds.append("<td></td>")
                continue
            app, window = blocks[key]
            active = None if typed is None else (key in typed)
            td = cell(cat_of[key], active)
            title = (window or app).replace('"', "&quot;")[:80]
            tds.append(td.replace("></td>", ' title="%s"></td>' % title))
        out.append('<tr style="height:11px">' + "".join(tds) + "</tr>")

    out.append("</table>")
    out.append("</div>")
    out.append("")
    out.append(app_table(blocks, cat_of))
    return "\n".join(out)


def hhmm(minutes):
    h, m = divmod(minutes, 60)
    return ("%dh%02dm" % (h, m)) if h else ("%dm" % m)


def app_table(blocks, cat_of):
    per = Counter()
    cat_per = {}
    for key, (app, _) in blocks.items():
        per[app] += BUCKET
        cat_per[app] = cat_of[key] or "미분류"
    lines = ["| 앱 | 시간 | 분류 |", "|---|---|---|"]
    for app, m in per.most_common(8):
        lines.append("| %s | %s | %s |" % (app, hhmm(m), LABELS.get(cat_per[app], cat_per[app])))
    return "\n".join(lines)


# ---------- 검증 ----------

def selftest():
    assert bucket_key(datetime(2026, 9, 23, 10, 0)) == (10, 0)
    assert bucket_key(datetime(2026, 9, 23, 10, 2)) == (10, 0)
    assert bucket_key(datetime(2026, 9, 23, 10, 3)) == (10, 3)
    assert bucket_key(datetime(2026, 9, 23, 10, 59)) == (10, 57)

    assert parse_ts("2026-09-23T01:00:00Z").tzinfo is not None
    assert parse_ts("2026-09-23 01:00:00") is not None
    assert parse_ts("2026-09-23T01:00:00.123456789Z") is not None
    assert parse_ts("깨진값") is None

    w = {"myproject": "focus"}
    a = {"Discord": "neutral"}
    assert classify("Cursor", "~/myproject/api.py", w, a) == "focus"   # 창 제목이 앱보다 우선
    assert classify("Discord", "일반대화", w, a) == "neutral"
    assert classify("Chrome", "유튜브", w, a) is None                     # 미분류는 None
    assert classify(None, None, w, a) is None

    assert hhmm(0) == "0m" and hhmm(59) == "59m" and hhmm(261) == "4h21m"

    assert "기록이 없습니다" in render(datetime(2026, 9, 23).date(), {}, None, w, a)

    blocks = {(10, 0): ("Cursor", "~/myproject/x.py"), (10, 3): ("Chrome", "유튜브")}
    html = render(datetime(2026, 9, 23).date(), blocks, {(10, 0)}, w, a)
    assert COLORS["focus"] in html and "#c9c6c0" in html
    assert "opacity:.35" in html          # 입력 없던 블록은 흐리게
    assert html.count("<tr") == ROWS + 1  # 헤더 + 20행
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    day = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    if not KEY:
        raise SystemExit("SCREENPIPE_API_KEY가 없습니다. 다음처럼 받아 넣어 주세요.\n"
                         "  export SCREENPIPE_API_KEY=$(npx -y screenpipe@latest auth token)")

    win_rules, app_rules = load_rules()
    try:
        blocks = collect(day)
    except urllib.error.HTTPError as e:
        raise SystemExit(
            "screenpipe API(%s)가 조회를 거절했습니다: HTTP %s %s\n%s"
            % (API, e.code, e.reason, e.read().decode(errors="replace")[:300])
        )
    except urllib.error.URLError as e:
        raise SystemExit(
            "screenpipe API(%s)에 붙지 못했습니다: %s\n"
            "recorder가 꺼져 있습니다. 다음 중 하나를 먼저 실행하세요.\n"
            "  SCREENPIPE_NO_REMINDERS=1 npx -y screenpipe@latest record   (기록 재개)\n"
            "  또는 Screenpipe 데스크톱 앱을 켭니다."
            % (API, e)
        )
    if not blocks:
        print("> [!warning] %s 화면 기록이 없습니다." % day)
        return

    table = input_table()
    typed = collect_input(day, table) if table else None

    print(render(day, blocks, typed, win_rules, app_rules))

    unknown = Counter()
    for app, window in blocks.values():
        if classify(app, window, win_rules, app_rules) is None:
            unknown[(app, (window or "")[:60])] += BUCKET
    if unknown:
        print("\n--- 미분류 (app-category.json에 추가하세요) ---", file=sys.stderr)
        for (app, window), m in unknown.most_common(30):
            print("%6s  %-22s %s" % (hhmm(m), app, window), file=sys.stderr)
    if table is None:
        print("\n[알림] 입력 이벤트 테이블이 없어 대기 구간을 구분하지 않았습니다.", file=sys.stderr)


if __name__ == "__main__":
    main()
