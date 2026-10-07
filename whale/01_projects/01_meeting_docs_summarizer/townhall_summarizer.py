"""GitHub issue 트러블슈팅 markdown을 타운홀 미팅 양식으로 요약하는 모듈."""

import argparse
import re
from pathlib import Path
from typing import Callable

TextGenerator = Callable[[str], str]

DEFAULT_PROVIDER_NAME = "gemini-3.1-flash-lite"
MAXIMUM_OUTPUT_TOKENS = 1500

SECTION_ONE_HEADING = "## 1. 어떤 어려움이 있었나?"
SECTION_TWO_HEADING_IN_PROGRESS = "## 2. 어떻게 해결 중인가?"
SECTION_TWO_HEADING_RESOLVED = "## 2. 어떻게 해결했나?"

DATE_PREFIX_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\s+")
RETROSPECTIVE_HEADING_KEYWORD = "회고"


def extract_title(issue_markdown_text: str) -> str:
    """'# 2026-09-29 제목' 형태의 첫 제목 줄에서 날짜 접두사를 제외한 제목을 반환함."""
    for line in issue_markdown_text.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("# "):
            title_text = stripped_line[2:].strip()
            return DATE_PREFIX_PATTERN.sub("", title_text)
    raise ValueError("제목 줄('# ...')을 찾을 수 없음.")


def remove_retrospective_section(issue_markdown_text: str) -> str:
    """'## ...회고' 섹션을 제거한 본문을 반환함."""
    kept_lines = []
    is_inside_retrospective = False
    for line in issue_markdown_text.splitlines():
        if line.startswith("## "):
            is_inside_retrospective = RETROSPECTIVE_HEADING_KEYWORD in line
        if not is_inside_retrospective:
            kept_lines.append(line)
    return "\n".join(kept_lines)


def build_prompt(title: str, issue_body_without_retrospective: str) -> str:
    """요약 지시문, 출력 양식, 이슈 본문을 하나의 prompt로 합침."""
    return f"""아래 이슈 본문을 타운홀 미팅 발표 양식으로 요약한다.

[핵심 메시지]
각 이슈를 '어려움(에러 내용과 원인)'과 '해결(해결 방법)' 두 질문으로 압축하여, 청중이 문제 상황과 대응 방향을 바로 파악하게 한다.

[규칙]
1. 첫 줄은 "# {title}" 그대로 작성한다.
2. "{SECTION_ONE_HEADING}" 섹션에는 '에러 내용'을 요약하고, 말미에 '원인 분석'을 1~2줄로 압축하여 포함한다.
3. 섹션 2의 제목은 해결 방법의 상태에 따라 둘 중 하나만 사용한다.
   - 완료 시제(구성했다, 적용했다 등)로 기록되어 있으면 "{SECTION_TWO_HEADING_RESOLVED}"를 사용한다.
   - 방향 결정이나 계획 단계(결정했다, 활용한다 등)이면 "{SECTION_TWO_HEADING_IN_PROGRESS}"를 사용한다.
4. 섹션 2에는 '해결 방법'의 핵심 조치만 요약한다.
5. 입력에 없는 원인, 해결책, 인사이트는 추가하지 않는다.
6. 각 섹션은 bullet (글머리 기호) 목록으로, 최대한 짧게 작성한다.
7. 설명, 서문, 코드 블록 표시 없이 markdown 본문만 출력한다.

[출력 양식]
# {title}

{SECTION_ONE_HEADING}
- ...

(섹션 2 제목은 규칙 3에 따라 선택)
- ...

[이슈 본문]
{issue_body_without_retrospective}
"""


def validate_townhall_format(output_text: str, expected_title: str) -> None:
    """출력이 타운홀 양식(제목, 섹션 1, 섹션 2 순서)을 만족하는지 검증함."""
    lines = [line.strip() for line in output_text.strip().splitlines()]
    if not lines or lines[0] != f"# {expected_title}":
        raise ValueError(f"첫 줄이 '# {expected_title}'와 일치하지 않음.")
    if SECTION_ONE_HEADING not in lines:
        raise ValueError(f"'{SECTION_ONE_HEADING}' 섹션이 없음.")
    section_two_headings_found = [
        heading
        for heading in (SECTION_TWO_HEADING_IN_PROGRESS, SECTION_TWO_HEADING_RESOLVED)
        if heading in lines
    ]
    if len(section_two_headings_found) != 1:
        raise ValueError("섹션 2 제목이 정확히 하나여야 함.")
    if lines.index(SECTION_ONE_HEADING) > lines.index(section_two_headings_found[0]):
        raise ValueError("섹션 1이 섹션 2보다 앞에 있어야 함.")


def create_gemini_text_generator(model_name: str) -> TextGenerator:
    """Gemini API로 텍스트를 생성하는 함수를 반환함. 환경변수 GEMINI_API_KEY를 사용함."""
    from google import genai  # 단위 테스트에서 SDK 없이 실행할 수 있도록 지연 import 함.

    client = genai.Client()

    def generate_text(prompt: str) -> str:
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text or ""

    return generate_text


def summarize_issue_for_townhall(
    issue_markdown_text: str,
    generate_text: TextGenerator,
) -> str:
    """이슈 markdown을 타운홀 양식으로 요약하여 반환함."""
    title = extract_title(issue_markdown_text)
    issue_body_without_retrospective = remove_retrospective_section(issue_markdown_text)
    prompt = build_prompt(title, issue_body_without_retrospective)
    output_text = generate_text(prompt).strip()
    validate_townhall_format(output_text, title)
    return output_text


def main() -> None:
    # API 환경 변수 호출
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # 터미널 명령어 구성(Terminal Command)
    argument_parser = argparse.ArgumentParser(description="이슈 트러블슈팅 markdown을 타운홀 양식으로 요약함.")
    argument_parser.add_argument("input_path", help="입력 이슈 markdown 파일 경로")
    argument_parser.add_argument("output_path", help="출력 markdown 파일 경로")
    argument_parser.add_argument("--model", default="gemini-3.1-flash-lite", help="미지정 시 provider 기본 모델 사용")
    parsed_arguments = argument_parser.parse_args()

    generate_text = create_gemini_text_generator(parsed_arguments.model)
    issue_markdown_text = Path(parsed_arguments.input_path).read_text(encoding="utf-8")
    summary_text = summarize_issue_for_townhall(issue_markdown_text, generate_text)
    Path(parsed_arguments.output_path).write_text(summary_text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
