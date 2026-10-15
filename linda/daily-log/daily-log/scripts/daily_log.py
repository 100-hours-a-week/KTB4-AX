#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SEOUL = ZoneInfo("Asia/Seoul")
SECTIONS = ("screenpipe", "github")
FALLBACK = "오늘 자동 로그 없음"


def today_date():
    return datetime.now(SEOUL).date().isoformat()


def validate_date(value):
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("날짜는 YYYY-MM-DD 형식이어야 합니다.") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("날짜는 YYYY-MM-DD 형식이어야 합니다.")
    return value


def diary_path(vault, day):
    return Path(vault).expanduser() / "raw" / "일기" / f"{day}.md"


def marker(section, edge):
    return f"<!-- auto:{section}:{edge} -->"


def marker_block(section):
    return f"{marker(section, 'start')}\n{marker(section, 'end')}\n"


def section_bounds(text, section):
    start_marker = marker(section, "start")
    end_marker = marker(section, "end")
    start = text.rfind(start_marker)
    if start < 0:
        return None
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        return None
    return start + len(start_marker), end


def ensure_markers(text):
    missing = [section for section in SECTIONS if section_bounds(text, section) is None]
    if not missing:
        return text
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    for index, section in enumerate(missing):
        text += marker_block(section)
        if index < len(missing) - 1:
            text += "\n"
    return text


def read_template(vault, day):
    template = Path(vault).expanduser() / "_템플릿" / "일일노트.md"
    return ensure_markers(template.read_text(encoding="utf-8").replace("YYYY-MM-DD", day))


def start(vault, day):
    path = diary_path(vault, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(read_template(vault, day), encoding="utf-8")
        return path
    current = path.read_text(encoding="utf-8")
    updated = ensure_markers(current)
    if updated != current:
        path.write_text(updated, encoding="utf-8")
    return path


def splice_body(vault, day, section, body, keep_if_empty=False):
    if section not in SECTIONS:
        raise ValueError(f"알 수 없는 섹션: {section}")
    path = start(vault, day)
    current = path.read_text(encoding="utf-8")
    body = body.rstrip("\r\n")
    if section == "screenpipe" and keep_if_empty and not body:
        body = FALLBACK
    bounds = section_bounds(current, section)
    if bounds is None:
        raise ValueError(f"마커를 만들 수 없습니다: {section}")
    start_end, end_start = bounds
    updated = current[:start_end] + "\n" + body + "\n" + current[end_start:]
    path.write_text(updated, encoding="utf-8")
    return path


def read_body(path):
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def self_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        vault = Path(temp_dir)
        template = vault / "_템플릿" / "일일노트.md"
        template.parent.mkdir(parents=True)
        template.write_text(
            "---\ntype: daily\ndate: YYYY-MM-DD\ntags: [일기]\n---\n\n"
            "# YYYY-MM-DD\n\n## 오늘 한 일\n\n-\n\n"
            "<!-- auto:screenpipe:start -->\n<!-- auto:screenpipe:end -->\n\n"
            "<!-- auto:github:start -->\n<!-- auto:github:end -->\n",
            encoding="utf-8",
        )

        path = start(vault, "2026-09-15")
        skeleton = path.read_text(encoding="utf-8")
        assert "## 오늘 한 일" in skeleton
        for section in SECTIONS:
            assert marker(section, "start") in skeleton
            assert marker(section, "end") in skeleton

        human = "## 오늘 한 일\n\n- 아이가 쓴 내용\n"
        path.write_text(human, encoding="utf-8")
        start(vault, "2026-09-15")
        before_github = path.read_text(encoding="utf-8")
        splice_body(vault, "2026-09-15", "screenpipe", "| 앱 | 창 | 시간 |\n|---|---|---|\n| Terminal | 작업 | 09:00 |")
        spliced = path.read_text(encoding="utf-8")
        assert human in spliced
        assert "| Terminal | 작업 | 09:00 |" in spliced
        assert before_github.split(marker("github", "start"))[1] == spliced.split(marker("github", "start"))[1]

        missing = vault / "raw" / "일기" / "2026-09-16.md"
        missing.parent.mkdir(parents=True, exist_ok=True)
        missing.write_text("# 2026-09-16\n\n## 오늘 한 일\n\n- 보존할 내용\n", encoding="utf-8")
        start(vault, "2026-09-16")
        repaired = missing.read_text(encoding="utf-8")
        assert repaired.startswith("# 2026-09-16\n\n## 오늘 한 일\n\n- 보존할 내용\n")
        assert marker("screenpipe", "start") in repaired
        assert marker("github", "start") in repaired

        splice_body(vault, "2026-09-15", "screenpipe", "", keep_if_empty=True)
        empty_spliced = path.read_text(encoding="utf-8")
        screen_start = empty_spliced.index(marker("screenpipe", "start")) + len(marker("screenpipe", "start"))
        screen_end = empty_spliced.index(marker("screenpipe", "end"))
        assert empty_spliced[screen_start:screen_end] == f"\n{FALLBACK}\n"

    print("daily_log self-test: ok")


def build_parser():
    parser = argparse.ArgumentParser(description="Create and update daily diary markers.")
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--date", default=today_date(), type=validate_date)
    start_parser.add_argument("--vault", required=True)

    splice_parser = subparsers.add_parser("splice")
    splice_parser.add_argument("--date", default=today_date(), type=validate_date)
    splice_parser.add_argument("--vault", required=True)
    splice_parser.add_argument("--section", choices=SECTIONS, required=True)
    splice_parser.add_argument("--body-file", required=True)
    splice_parser.add_argument("--keep-if-empty", action="store_true")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if args.command is None:
        parser.error("명령을 지정하세요: start 또는 splice")
    try:
        if args.command == "start":
            print(start(args.vault, args.date))
        else:
            print(splice_body(args.vault, args.date, args.section, read_body(args.body_file), args.keep_if_empty))
    except (OSError, ValueError) as exc:
        print(f"daily-log: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
