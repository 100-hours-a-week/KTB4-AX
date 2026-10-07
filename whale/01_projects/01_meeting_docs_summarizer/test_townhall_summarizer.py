import pytest

from townhall_summarizer import (
    SECTION_ONE_HEADING,
    SECTION_TWO_HEADING_IN_PROGRESS,
    SECTION_TWO_HEADING_RESOLVED,
    extract_title,
    remove_retrospective_section,
    summarize_issue_for_townhall,
    validate_townhall_format,
)

SAMPLE_ISSUE_MARKDOWN = """# 2026-09-29 부하테스트와 AI 개발을 위한 테스트 환경 분리 필요

## 🐞 에러 내용
- 운영 서버에서 부하테스트를 진행하면 응답 지연이나 장애로 실제 사용자가 서비스를 이용하지 못할 수 있다는 우려가 제기되었다.

## 🔍 원인 분석
- 현재 운영 환경과 개발, 테스트 환경이 분리되어 있지 않다.

## ✅ 해결 방법
- 운영 서버와 유사한 환경의 EC2 한 대를 추가해 테스트 환경을 구성하는 방향을 결정했다.

## 회고
- EC2를 추가하는 것만으로 격리가 완성되는 것은 아니다.
"""

TITLE = "부하테스트와 AI 개발을 위한 테스트 환경 분리 필요"

VALID_IN_PROGRESS_OUTPUT = f"""# {TITLE}

{SECTION_ONE_HEADING}
- 운영 서버 부하테스트 시 실제 사용자 장애 우려가 있었음.

{SECTION_TWO_HEADING_IN_PROGRESS}
- EC2 한 대를 추가해 테스트 환경을 구성하는 방향으로 결정함.
"""

VALID_RESOLVED_OUTPUT = VALID_IN_PROGRESS_OUTPUT.replace(
    SECTION_TWO_HEADING_IN_PROGRESS, SECTION_TWO_HEADING_RESOLVED
)


class RecordingTextGenerator:
    def __init__(self, response_text):
        self.response_text = response_text
        self.received_prompt = None

    def __call__(self, prompt):
        self.received_prompt = prompt
        return self.response_text


def test_extract_title_removes_date_prefix():
    assert extract_title(SAMPLE_ISSUE_MARKDOWN) == TITLE


def test_extract_title_raises_when_title_line_is_missing():
    with pytest.raises(ValueError):
        extract_title("## 에러 내용\n- 내용")


def test_remove_retrospective_section_keeps_other_sections():
    result_text = remove_retrospective_section(SAMPLE_ISSUE_MARKDOWN)
    assert "회고" not in result_text
    assert "격리가 완성" not in result_text
    assert "## 🐞 에러 내용" in result_text
    assert "## 🔍 원인 분석" in result_text
    assert "## ✅ 해결 방법" in result_text


def test_validate_accepts_in_progress_and_resolved_headings():
    validate_townhall_format(VALID_IN_PROGRESS_OUTPUT, TITLE)
    validate_townhall_format(VALID_RESOLVED_OUTPUT, TITLE)


def test_validate_rejects_title_with_date_prefix():
    output_text = VALID_IN_PROGRESS_OUTPUT.replace(TITLE, f"2026-09-29 {TITLE}", 1)
    with pytest.raises(ValueError):
        validate_townhall_format(output_text, TITLE)


def test_validate_rejects_missing_section_two():
    output_text = VALID_IN_PROGRESS_OUTPUT.split(SECTION_TWO_HEADING_IN_PROGRESS)[0]
    with pytest.raises(ValueError):
        validate_townhall_format(output_text, TITLE)


def test_validate_rejects_both_section_two_headings():
    output_text = (
        VALID_IN_PROGRESS_OUTPUT + f"\n{SECTION_TWO_HEADING_RESOLVED}\n- 추가 내용\n"
    )
    with pytest.raises(ValueError):
        validate_townhall_format(output_text, TITLE)


def test_summarize_sends_prompt_without_retrospective_and_returns_output():
    fake_text_generator = RecordingTextGenerator(VALID_IN_PROGRESS_OUTPUT)

    summary_text = summarize_issue_for_townhall(SAMPLE_ISSUE_MARKDOWN, fake_text_generator)

    sent_prompt = fake_text_generator.received_prompt
    assert "격리가 완성" not in sent_prompt
    assert f"# {TITLE}" in sent_prompt
    assert "2026-09-29" not in sent_prompt.split("[이슈 본문]")[0]
    assert summary_text == VALID_IN_PROGRESS_OUTPUT.strip()


def test_summarize_raises_when_model_output_breaks_format():
    fake_text_generator = RecordingTextGenerator("형식과 무관한 응답")
    with pytest.raises(ValueError):
        summarize_issue_for_townhall(SAMPLE_ISSUE_MARKDOWN, fake_text_generator)
