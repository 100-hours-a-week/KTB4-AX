#!/usr/bin/env python3
"""긍정 피드백 초안 생성. 항목마다 직전 문장을 제외하고 무작위로 고른다.

기본값은 positive_random. 기존 설정에도 적용하며, fixed 모드에서는 defaults를 쓴다.
직접 받은 --overrides 값이 가장 우선한다. 사실 기반 학습 요약과 성과는 생성하지 않는다.
"""
import argparse
import json
from pathlib import Path
import secrets


HERE = Path(__file__).resolve().parents[1]


def read_object(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 객체가 필요합니다: {path}")
    return value


def generate(config, bank, previous, overrides):
    mode = config.get("feedback_mode", "positive_random")
    if mode not in ("positive_random", "fixed"):
        raise ValueError("feedback_mode는 positive_random 또는 fixed여야 합니다.")
    defaults = config.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("config.defaults는 JSON 객체여야 합니다.")
    answers = {k: v for k, v in defaults.items() if not k.startswith("_")}
    sources = {k: "config.defaults" for k in answers}
    selected = {}
    if mode == "positive_random":
        for key, candidates in bank.items():
            choices = [v for v in candidates if v != previous.get(key)]
            if not choices:
                raise ValueError(f"서로 다른 긍정 문구가 필요합니다: {key}")
            answers[key] = secrets.choice(choices)
            sources[key] = "positive_random"
            selected[key] = answers[key]
    for key, value in overrides.items():
        if not key.startswith("_"):
            answers[key] = value
            sources[key] = "user"
    answers["_sources"] = sources
    return answers, selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    parser.add_argument("--overrides", type=Path, help="사용자가 직접 지정한 값의 JSON 파일")
    parser.add_argument("--output", type=Path, help="생성할 JSON 파일. 생략하면 표준 출력")
    args = parser.parse_args()
    state_path = args.config.parent / ".feedback-state.json"
    try:
        config = read_object(args.config)
        bank = read_object(HERE / "assets/positive-feedback.json")
        overrides = read_object(args.overrides) if args.overrides else {}
        try:
            previous = read_object(state_path)
        except (OSError, ValueError):
            previous = {}
        answers, selected = generate(config, bank, previous, overrides)
        text = json.dumps(answers, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        if selected:
            state_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.exit(2, f"긍정 피드백 생성 실패: {error}\n")


if __name__ == "__main__":
    main()
