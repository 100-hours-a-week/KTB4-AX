# 프로젝트 미팅 문서 요약

## 기능 요약

이슈 본문을 저장한 트러블슈팅 markdown(에러 내용, 원인 분석, 해결 방법, 회고)을 입력받아 타운홀 미팅 양식의 markdown으로 요약함. 출력 양식이 맞지 않으면 에러로 종료함.

## 실행 명령어

```bash
uv sync
uv run python townhall_summarizer.py issue.md townhall.md
```
