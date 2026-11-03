# daily-retro

카카오테크 부트캠프 일일회고 폼을 채워주는 Agent Skill. **Claude Code 와 Codex 양쪽에서 동작합니다.**

## 쓰는 법

```bash
git clone https://github.com/100-hours-a-week/KTB4-AX.git
cd KTB4-AX/sevan/daily-retro
claude
```

이 폴더(`sevan/daily-retro`)에서 Claude Code 를 띄우면 **설치 과정 없이 바로 스킬이 잡힙니다** (`.claude/skills/` 가 레포 안에 있어서). Codex 도 같은 폴더에서 그냥 실행하면 됩니다 (`.agents/skills/` 링크가 같이 들어 있습니다).

그리고 한 줄:

```
오늘 회고 폼 작성해줘
```

첫 실행 때 설정이 없으면 스킬이 **네 가지를 한 번에 물어봅니다.** GitHub 활동 기록으로 추측값을 미리 채워주니, 맞으면 그대로 확인만 하면 됩니다.

> 1. GitHub 계정 — `kkkk2058` 맞나요?
> 2. 팀 번호 — `13` 맞나요?
> 3. 소속 과정 — 인공지능 / 풀스택 / 클라우드
> 4. 폼에 쓰는 이름 — `영어닉네임 (한글이름)/과정` 형식

`gh` 가 없으면 설치까지 해줍니다 (인증만 `gh auth login` 으로 직접). 이 네 가지는 **최초 1회**뿐이고, 이후로는 매일 `오늘 회고 폼 작성해줘` 한 줄이면 폼이 다 채워진 채로 브라우저에 뜹니다. **제출 버튼은 항상 본인이** 누릅니다.

터미널에서 직접 설정만 만들고 싶으면:

```bash
python3 .claude/skills/daily-retro/scripts/bootstrap.py
```

### 어디서나 쓰고 싶으면

레포 폴더 밖에서도 쓰려면 한 번만:

```bash
bash install.sh
```

`~/.claude/skills/` 와 `~/.agents/skills/` 에 링크를 걸어줍니다. `git pull` 하면 업데이트가 바로 반영됩니다.

## 스킬: `daily-retro`

GitHub Daily Scrum · Troubleshooting 이슈를 읽어서 교육 과정 후기 구글폼을 채운 링크를 만들고 브라우저에 띄웁니다.

**동작 순서**

1. 오늘 요일로 폼을 고릅니다 — 화·수·목은 과정 강사, 월·금은 팀 번호 기준 분단 강사. 폼 주소는 공개 레포에 두지 않으므로, 강사 폼을 처음 쓸 때 스킬이 물어보면 부트캠프 공지의 후기 폼 링크를 붙여 넣으세요 (본인 `config.json` 에만 저장됩니다)
2. `gh` 로 그날 Daily Scrum 이슈에서 본인 코멘트를 읽습니다
3. 학습 요약·개선점을 **그 기록에서만** 뽑습니다. Daily Scrum 회고가 비어 있으면 같은 날짜 Troubleshooting 이슈의 회고를 봅니다. 없는 내용은 만들지 않습니다
4. 의견 항목(강사 피드백·평점 등)은 `config.json` 의 `defaults` 값으로 채웁니다
5. 사전채움 링크를 만들어 기본 브라우저로 엽니다
6. 채운 값을 출처와 함께 표로 보여줍니다 — **제출은 직접**

**사용 예**

```
오늘 회고 폼 작성해줘
9/17 회고 폼 작성해줘
오늘 회고 써줘, 좋았던 점은 실습 시간이 넉넉했던 거로
```

마지막 예처럼 그날 할 말을 같이 주면 기본값 대신 그 값이 들어갑니다.

### `defaults` 는 꼭 본인 말로 고치세요

`config.json` 의 `defaults` 는 **매일 그대로 제출되는 문장**입니다. 팀원 전원이 기본값을 그대로 두면 강사가 똑같은 후기 20장을 받게 되고, 피드백으로서 아무 의미가 없어집니다. 첫 실행 후 한 번만 손봐주세요.

`config.json` 은 `.gitignore` 에 있어 커밋되지 않습니다 (사람마다 다르고 개인정보가 들어갑니다).

## 폼만 따로 다루기

```bash
# 폼의 질문 라벨과 entry ID 확인
python3 .claude/skills/daily-retro/scripts/prefill.py --form "<폼 URL>" --list

# answers.json 으로 링크 생성 + 브라우저 열기
python3 .claude/skills/daily-retro/scripts/prefill.py --form "<폼 URL>" --answers answers.json

# 설정 자동 감지 결과만 보기
python3 .claude/skills/daily-retro/scripts/bootstrap.py --json
```

`prefill.py` 는 entry ID 를 하드코딩하지 않고 폼 HTML 에서 뽑아 **질문 라벨로 매칭**합니다. 키가 0개 또는 2개 이상 문항에 걸리면 에러로 멈추므로, 조용히 엉뚱한 칸에 값이 들어가는 일이 없습니다.

## 필요한 것

- macOS, `python3` (기본 포함)
- `gh` CLI — 없으면 스킬이 `brew install gh` 로 설치합니다. 인증만 직접: `gh auth login`

## 스킬 추가하기

`.claude/skills/<이름>/SKILL.md` 를 만들면 됩니다. 프론트매터는 `name` 과 `description` 두 개만 필수이고, 이 포맷([Agent Skills](https://agentskills.io))은 Claude Code 와 Codex 가 공통으로 읽습니다.
