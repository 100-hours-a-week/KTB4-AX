---
name: session-record
description: Write a decision-record markdown document for the current Claude Code session (decisions with rationale, reversals, corrections, verified vs unverified, open items) with metadata that lets the transcript be found again. Use when the user asks to summarize or record the conversation, "세션 기록", "대화 정리", "결정 기록", or wants a reusable record of what was decided and why.
---

# session-record

현재 세션을 **결정 기록 문서**로 정리한다. 대화 전사가 아니라 "무엇을 왜 결정했고, 무엇이 번복되었고, 무엇이 아직 남았는지"를 남기는 문서다. 나중에 사람이나 다른 세션의 Claude가 같은 결정을 다시 제안하거나 뒤집지 않게 하는 것이 목적이다.

## 1. 작성 전에 질문한다 (grill-me 방식)

바로 쓰지 말고 아래를 **한 번에 하나씩**, 추천 답변과 함께 묻는다. 사용자가 이미 답한 항목은 다시 묻지 않는다.

1. **독자와 용도**: 추천은 "본인과 이후 세션의 Claude용 결정 기록". 팀 공유용이면 개인 정보와 내부 논의를 빼야 하므로 반드시 확인한다.
2. **메타데이터 범위**: 추천은 이 세션만 기록. 다른 세션을 함께 넣으려면 해당 세션 기록을 직접 읽고 확인한 뒤에만 넣는다(읽지 않은 세션의 내용을 추측해 쓰지 않는다).
3. **개인 정보 처리**: 추천은 이메일 주소는 본문에 넣지 않고, 나머지는 사용자 지시에 따른다.
4. **저장 위치**: 기본값은 현재 프로젝트 폴더의 `sessions/`. 다른 위치를 원하면 따른다.

## 2. 메타데이터를 수집한다 (추측하지 않고 확인한다)

- **세션 ID**: 현재 세션의 scratchpad 경로(`.../<세션 ID>/scratchpad`)에 들어 있다. 또는 `~/.claude/projects/<작업 폴더 경로에서 / 를 - 로 바꾼 이름>/` 안의 `.jsonl` 중 가장 최근에 수정된 파일명이다.
- **시작과 마지막 시각**: 이력 파일의 `timestamp` 필드만 읽어 KST로 변환한다. 대화 내용은 읽지 않는다. `python3 -I`로 실행한다.
  ```bash
  python3 -I - <<'EOF'
  import json
  from datetime import datetime
  from zoneinfo import ZoneInfo
  stamps = []
  for line in open("<이력 파일 경로>", encoding="utf-8"):
      try: stamps.append(json.loads(line).get("timestamp"))
      except Exception: pass
  stamps = [s for s in stamps if s]
  kst = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Seoul"))
  print(kst(min(stamps)), kst(max(stamps)))
  EOF
  ```
- **모델**: 시스템 프롬프트에 나온 모델 이름과 ID를 쓴다.
- **산출물**: `git log`로 이 세션에서 만든 커밋 해시와 브랜치를, PR이 있으면 `gh pr list`로 번호와 URL을 확인해서 적는다. 확인하지 않은 해시나 URL은 쓰지 않는다.
- **마지막 시각의 의미**: 문서를 쓰는 시점까지의 대화만 반영된다. 그 이후 대화는 포함되지 않는다고 프론트매터에 밝힌다.

## 3. 파일 이름

`sessions/YYYY-MM-DD_HHMM_<슬러그>.md`

- 날짜와 시각은 **세션 시작 시각(KST)** 이다. 파일 목록이 시계열로 정렬된다.
- 슬러그는 영어 소문자와 하이픈으로 주제를 요약한다.
- 같은 폴더에 이미 파일이 있으면 읽지 말고 이름만 확인해서 충돌을 피한다.

## 4. 문서 구조 (이 순서와 제목을 유지한다)

````markdown
---
title: <세션 주제>
type: session-decision-record
audience: <독자>
date: <YYYY-MM-DD>
session:
  id: <세션 ID>
  started: <YYYY-MM-DD HH:MM:SS KST>
  last_record: <YYYY-MM-DD HH:MM:SS KST>   # 문서를 쓴 시점까지 반영
  model: <모델 ID> (<모델 이름>)
  entry_skill: </사용한 스킬, 없으면 생략>
  transcript: ~/.claude/projects/<폴더>/<세션 ID>.jsonl
  resume: "<작업 폴더>에서 `claude --resume <세션 ID>`"
  transcript_note: 이 컴퓨터에만 있고 보관 정책에 따라 지워질 수 있음. 본문의 결정과 근거를 우선 기준으로 삼고, 이력 파일은 보조 수단으로만 씀.
repos:
  <이름>: {path: "<경로>", remote: "<owner/repo>", branch: "<브랜치>"}
artifacts:
  - {what: <산출물>, repo: <이름>, commit: <해시>, pr: "<URL>"}
related_sessions:
  - {id: <ID>, started: <시각>, status: "아직 이 기록에 포함하지 않음"}
sort_key: <YYYY-MM-DD_HHMM>
---

# <제목>

<한두 문장: 이 문서의 용도와, 결과물 문서가 따로 있다면 그 관계>

## 1. 한눈에 보기
목표, 현재 상태, 가장 중요한 한계(검증하지 못한 것)를 불릿 3~5개로.

## 2. 용어
대화 중 정정을 거쳐 확정된 용어만. 모호한 표현이 정정된 적이 있으면 그 사실도 적는다.

## 3. 결정 기록
소제목으로 주제를 나누고, 각 표는 `# | 결정 | 근거 | 상태`.
- 번호는 문서 전체에서 D1, D2…로 이어서 붙인다.
- 상태는 `유효`, `대체됨(Dn)`, `철회됨(Dn)`, `유효(사용자 책임)` 중 하나로 쓰고, 번복된 결정도 지우지 말고 남긴다.
- 작업 중 발견해 설계를 바꾼 사실은 별도 표 `# | 발견 | 조치`로 F1, F2…로 적는다.

## 4. 대화 중 정정된 오해
Claude나 사용자가 처음에 잘못 가정했다가 바로잡은 것들. "A로 가정함 → 실제는 B" 형식. 같은 실수를 반복하지 않게 하는 용도다.

## 5. 구현 요약 (코드를 만든 세션만)
모듈별 역할, 실행 명령어, 기준 코드가 어느 저장소인지.

## 6. 검증한 것과 못 한 것
- **검증함**: 실제로 실행해서 확인한 것과 그 방법.
- **검증하지 못함**: 실행하지 못했거나 가짜로만 검증한 것. 숨기지 않는다.

## 7. 미해결 사항과 다음 행동
`순서 | 할 일 | 담당 | 비고` 표. 외부 대기(승인, 권한, 키 등)는 담당자를 명시한다.

## 8. 이 문서를 쓰게 된 결정
형식, 메타데이터 범위, 개인 정보 처리처럼 4번에서 합의한 내용.
````

## 5. 작성 규칙

- **근거를 적는다.** 결정만 쓰고 이유를 빼면 이 문서의 가치가 없다.
- **번복을 지우지 않는다.** 철회된 결정은 상태만 바꿔 남긴다.
- **사실만 쓴다.** 실행해서 확인한 것과 추측을 구분한다. 확인하지 못한 항목은 6절의 "검증하지 못함"에 둔다.
- **사용자의 결정은 사용자의 결정으로 쓴다.** 사용자가 위험을 감수하기로 한 결정은 `유효(사용자 책임)`로 표시하고 평가를 덧붙이지 않는다.
- **비밀 값은 쓰지 않는다.** API 키, 토큰, 비밀번호가 대화에 나왔더라도 문서에는 쓰지 않는다. 이력 파일에 남아 있다는 사실만 적는다.
- **전사를 만들지 않는다.** 대화 문장을 길게 옮기지 말고 결정 단위로 요약한다.
- **다른 세션의 이력 파일은 사용자가 요청할 때만 읽는다.**

## 6. 마무리

1. 프론트매터가 유효한 YAML인지 확인한다(`ruby -ryaml -rdate -e 'YAML.safe_load(...)'` 등).
2. 본문에서 결정 번호(Dn, Fn) 참조가 맞는지 확인한다.
3. 파일 경로와 요약(결정 개수, 검증하지 못한 항목)을 사용자에게 보고한다.
4. **커밋하지 않는다.** 사용자가 요청할 때만 커밋한다.
