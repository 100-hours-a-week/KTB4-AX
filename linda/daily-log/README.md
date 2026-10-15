# linda — 하루 기록 자동화 (daily-log)

아침에 `daily start`, 저녁에 `daily end`라고 말하면 AI 에이전트가 그날 한 일을 모아 Obsidian 볼트에 일기를 써 주는 스킬입니다. 나중에 자기소개서·면접에 쓸 경험을 **사실과 근거**로 쌓는 것이 목적입니다.

| 출처 | 모으는 것 | 필수 여부 |
|---|---|---|
| Screenpipe | 오늘 쓴 앱·창 제목·시간 (3분 단위 타임라인) | 권장 |
| GitHub | 내 담당 Project 카드, 오늘 쓴 이슈·댓글, 위키 변경 | 선택 |
| Discord | 지정한 서버 업무 채널에서 화면에 보였던 대화 | 선택 (Screenpipe 필요) |
| 작업 세션 | Claude Code·Codex·Grok과 나눈 오늘의 작업 대화 | 선택 |

에이전트는 일기를 쓰기만 합니다. 프로그램 설치와 `git commit`·`push`는 하지 않고 명령만 알려 줍니다.

---

## 폴더 구성

아래 명령은 모두 이 폴더(`KTB4-AX/linda/daily-log`)에서 실행합니다.

```sh
git clone https://github.com/100-hours-a-week/KTB4-AX.git
cd KTB4-AX/linda/daily-log
```

```
daily-log/
├── README.md              ← 지금 이 문서
├── daily-log/             ← 스킬. 에이전트의 스킬 폴더로 복사합니다
│   ├── SKILL.md           ← 에이전트가 따르는 절차
│   ├── config.example.json← 내 설정 예시 (config.json으로 복사해 채움)
│   ├── 기록-작성기준.md     ← 일기를 어떻게 쓰는지에 대한 기준
│   └── scripts/
│       ├── daily_log.py   ← 일기 파일 생성·자동 상자 채우기
│       ├── timeline.py    ← Screenpipe 기록 → 3분 타임라인
│       └── app-category.json ← 앱을 집중/중립/표류로 나누는 규칙
└── vault-starter/         ← Obsidian 볼트 시작 세트. 원하는 위치로 복사합니다
    ├── CLAUDE.md          ← 에이전트가 지킬 볼트 규칙
    ├── .obsidian/         ← 템플릿·데일리 노트 설정
    ├── _템플릿/            ← 일일노트·트러블슈팅 틀
    └── raw/일기/           ← 일기가 쌓이는 곳
```

---

## 처음 설정 — `daily setup`

아래 [사용 방법](#사용-방법) 1~5장의 설치를 마친 뒤 한 번만 합니다.

볼트에서 에이전트를 켜고 `daily setup`이라고 말하면 대화로 설정합니다. 설정 전에 `daily start`를 말해도 자동으로 이 단계부터 시작합니다.

```sh
cd ~/Documents/linda-vault
claude
```

```text
> daily setup
```

에이전트가 볼트 → Screenpipe → GitHub → Discord → 작업 세션 순서로 "쓸지, 쓴다면 값이 뭔지"를 묻습니다. 값을 받을 때마다 실제로 조회해 보고, 끝나면 `config.json`을 저장한 뒤 이런 표를 보여 줍니다.

```text
| 출처 | 상태 | 고치는 방법 |
|---|---|---|
| 볼트 | ✅ | |
| Screenpipe | ✅ | |
| GitHub | ❌ project 권한 없음 | gh auth refresh -s project |
| Discord | ⚠️ 기록에서 서버가 아직 안 보임 | Screenpipe를 켠 채 서버를 한 번 열어 두기 |
| 작업 세션 | — 끔 | |
```

- ❌는 안내된 명령을 직접 실행한 뒤 `daily setup`을 다시 하면 됩니다. 쓰지 않을 출처는 그 자리에서 끄면 됩니다.
- 값을 바꾸고 싶을 때도 `daily setup`이라고 말하면 지금 값을 보여 주고 바꿀 것만 묻습니다.
- 매일 `daily start` 때도 켜 둔 출처를 가볍게 점검해, 로그인이 풀렸거나 권한이 빠졌으면 아침에 알려 줍니다.

---

## 하루 사용법

| 때 | 어디서 | 할 일 |
|---|---|---|
| 처음 한 번 | 볼트 탭 | `daily setup` (바로 위 처음 설정) |
| 아침 | 볼트 탭 | `daily start` |
| 낮 | 작업 탭 | 평소처럼 에이전트와 일하기 |
| 저녁 | 볼트 탭 | `daily end` (+ 오늘만의 부탁) |

### 아침 — `daily start`

- 켜 둔 출처(GitHub·Discord 등) 설정이 아직 유효한지 빠르게 점검합니다. 문제가 있으면 맨 위에 한 줄로 알려 줍니다.
- 오늘 일기 파일 `raw/일기/YYYY-MM-DD.md`를 만듭니다.
- Screenpipe가 녹화 중인지 확인합니다. 꺼져 있으면 켜는 명령을 알려 줍니다(직접 켜지는 않음).
- GitHub를 켰다면 오늘 할 내 카드를 표로 보여 줍니다.

**실행 예시**

터미널에서 볼트로 이동해 에이전트를 켠 뒤 말로 부탁합니다.

```sh
cd ~/Documents/linda-vault
claude          # Codex라면 codex
```

```text
> daily start                    # 자동으로 오늘 날짜로 시작
> 오늘 daily start 해줘            # 문장으로 말해도 됩니다
> daily start 2026-10-08         # 지난 날짜를 지정
> /daily-log start               # Claude Code에서는 스킬 이름을 슬래시 명령으로도 부를 수 있습니다
```

에이전트는 대략 이렇게 답합니다.

```text
일기 파일: raw/일기/2026-10-15.md (새로 만듦)
Screenpipe: 녹화 중 — 마지막 캡처 09:12

| 카드 | 상태 |
|---|---|
| 로그인 API 리팩터링 | In Progress |
```

### 저녁 — `daily end`

- 첫 줄은 꼭 씁니다. 다음 줄부터는 **오늘만** 적용되는 부탁입니다.
- 에이전트가 자료를 모아 일기 본문(오늘의 맥락·한 일·논의·회고)을 씁니다.
- 트러블슈팅 후보가 있으면 쓰기 전에 목록을 보여 주고 멈춥니다. 번호(`1,3`)·`전부`·`없음`으로 답하세요.
- `## 내 메모`는 내 칸입니다. 에이전트는 고치지 않습니다.

**실행 예시**

```text
> daily end
```

```text
> daily end
  my-org/another-repo 레포도 봐.
  오늘 오후 회의는 Discord #회의 채널에서 했어.
```

```text
> daily end 2026-10-14           # 어제 일기를 늦게 마무리할 때
```

트러블슈팅 후보가 있으면 이렇게 묻고 멈춥니다.

```text
트러블슈팅 후보 2건 — 어떤 것을 일기에 넣을까요?
1. 배포 후 API 서버가 켜지지 않음 · GitHub 이슈 #12 · 해결
2. 검색 결과가 비어 있음 · Discord #backend · 미해결
```

```text
> 1          # 1번만
> 1,2        # 둘 다
> 전부
> 없음       # 트러블슈팅 섹션 없이 마무리
```

다 쓰고 나면 Obsidian에서 `raw/일기/2026-10-15.md`를 열어 확인하고, 필요하면 맨 아래 `## 내 메모`에 직접 적습니다.

---

# 사용 방법

## 1. 준비물

macOS 기준입니다. 이미 설치된 것은 건너뛰세요.

| 도구 | 용도 | 필수 |
|---|---|---|
| Homebrew | 아래 도구 설치 | 권장 |
| Python 3.9 이상 | 스크립트 실행 | ✅ |
| Node.js | `npx`로 Screenpipe 실행 | Screenpipe CLI 쓸 때 |
| Obsidian | 일기 보기·쓰기 | ✅ |
| AI 에이전트 CLI | 스킬 실행 (Claude Code 또는 Codex) | ✅ |
| Screenpipe | 화면 기록 | 권장 |
| Orca | 에이전트 터미널·작업 공간 | 선택 |
| GitHub CLI (`gh`) | GitHub 수집 | GitHub 쓸 때 |

### 1-1. Homebrew · Python · Node.js

Homebrew가 없다면 [brew.sh](https://brew.sh)의 설치 명령을 먼저 실행합니다.

```sh
brew install python node
python3 --version   # 3.9 이상인지 확인
```

### 1-2. GitHub CLI (GitHub 수집을 켤 때만)

```sh
brew install gh
gh auth login
gh auth refresh -s project   # Project 보드를 읽으려면 project 권한이 필요합니다
gh auth status               # Token scopes에 project가 보이면 됩니다
```

---

## 2. Obsidian

1. [obsidian.md/download](https://obsidian.md/download)에서 설치합니다. (`brew install --cask obsidian`도 됩니다.)
2. 시작 볼트를 원하는 위치로 복사합니다. 아래 예시는 `~/Documents/linda-vault`입니다.

   ```sh
   cp -R vault-starter ~/Documents/linda-vault
   ```

3. Obsidian → **Open folder as vault**(폴더를 볼트로 열기) → `~/Documents/linda-vault`를 고릅니다.
4. 설정은 `.obsidian/`에 미리 들어 있습니다. 열고 나서 **Settings(설정)**에서 아래 값이 맞는지만 확인합니다.

| 설정 위치 | 항목 | 값 |
|---|---|---|
| Core plugins | Daily notes, Templates | 켜짐 |
| Templates | Template folder location | `_템플릿` |
| Daily notes | New file location | `raw/일기` |
| Daily notes | Date format | `YYYY-MM-DD` |
| Daily notes | Template file location | `_템플릿/일일노트` |
| Files and links | Default location for new attachments | `raw/assets` |

데일리 노트의 폴더·형식이 위와 다르면 스크립트가 만든 일기와 Obsidian이 만든 노트가 따로 생깁니다. 꼭 맞춰 주세요. ([데일리 노트 공식 도움말](https://obsidian.md/help/plugins/daily-notes))

> 일기에는 개인정보가 들어갑니다. 볼트를 git으로 관리한다면 **private 저장소**를 쓰세요.

---

## 3. Screenpipe (화면 기록)

Screenpipe는 화면을 계속 기록해 두고, 나중에 "오늘 어떤 앱에서 무엇을 봤는지" 찾아볼 수 있게 해 주는 도구입니다. 모든 데이터는 내 컴퓨터의 `~/.screenpipe/`에만 저장됩니다.

### 3-1. 설치와 녹화 시작

둘 중 하나를 고릅니다.

| 방법 | 명령 | 특징 |
|---|---|---|
| 데스크톱 앱 (권장) | [screenpi.pe/onboarding](https://screenpi.pe/onboarding)에서 설치 | 권한 설정을 앱이 안내해 줌 |
| CLI | `SCREENPIPE_NO_REMINDERS=1 npx -y screenpipe@latest record` | 터미널에서 백그라운드로 녹화 |

### 3-2. macOS 권한

처음 실행하면 권한을 묻습니다. 허용하지 않으면 기록이 비어 있습니다.
**시스템 설정 → 개인정보 보호 및 보안**에서 아래 항목에 Screenpipe(또는 CLI를 띄운 터미널 앱)를 켭니다.

- 화면 및 시스템 오디오 녹음
- 손쉬운 사용
- 마이크 (음성까지 기록할 때만)

CLI가 "손상된 앱"이나 "permission denied"로 막히면 공식 문서의 안내대로 격리 속성을 지웁니다.

```sh
xattr -d com.apple.quarantine ~/.npm/_npx/*/node_modules/screenpipe*/bin/screenpipe
```

### 3-3. 잘 기록되는지 확인

```sh
npx -y screenpipe@latest status          # running인지, 마지막 캡처가 오늘인지
npx -y screenpipe@latest doctor          # 권한·의존성 점검
```

`/health`가 200이라고 해서 오늘 녹화 중인 것은 아닙니다. 위 `status`의 마지막 캡처 시각을 보세요.

### 3-4. API 토큰

타임라인 스크립트는 Screenpipe 로컬 API(기본 포트 3030)를 씁니다. 토큰은 저장하지 말고 쓸 때마다 받아 환경변수로 넘깁니다. 에이전트도 같은 방식으로 받습니다.

```sh
export SCREENPIPE_API_KEY=$(npx -y screenpipe@latest auth token)
```

> 토큰을 URL·로그·스크린샷에 남기지 마세요.

### 3-5. 개인정보 주의

- Screenpipe는 화면에 보인 모든 것(메신저·메일·비밀번호 입력 화면 포함)을 기록합니다. 민감한 작업 중에는 녹화를 멈추세요.
- daily-log는 원문을 볼트로 복사하지 않습니다. 앱·창 제목·시간 표와 업무 요약만 일기에 남깁니다.
- Discord 수집은 config에 적은 **서버 하나의 업무 채널**만 봅니다. DM은 항상 뺍니다.

---

## 4. 에이전트 터미널 — Orca 또는 일반 터미널

### 4-1. AI 에이전트 CLI

둘 중 하나 이상을 설치하고 로그인합니다. 설치 명령은 공식 문서를 따르세요.

| 에이전트 | 공식 문서 | 스킬 설치 위치 | 볼트 규칙 파일 |
|---|---|---|---|
| Claude Code | [code.claude.com/docs](https://code.claude.com/docs/en/overview) | `~/.claude/skills/daily-log/` | `CLAUDE.md` |
| Codex | [Codex 스킬 문서](https://learn.chatgpt.com/docs/build-skills) | `~/.agents/skills/daily-log/` | `AGENTS.md` |

### 4-2. Orca (선택)

[Orca](https://onorca.dev)는 여러 AI 에이전트를 탭·분할 터미널로 띄워 두고 프로젝트별로 관리하는 데스크톱 앱입니다.

```sh
brew install --cask stablyai/orca/orca
```

또는 [onorca.dev/download](https://onorca.dev/download)에서 받습니다.

권장 사용 방식은 다음과 같습니다.

| 탭 | 폴더 | 하는 일 |
|---|---|---|
| 볼트 탭 | `~/Documents/linda-vault` | 아침 `daily start`, 저녁 `daily end` |
| 작업 탭 | 내 프로젝트 레포·worktree | 낮에 에이전트와 일하기 |

1. Orca에서 볼트 폴더와 작업 레포를 각각 프로젝트로 추가합니다.
2. 볼트 프로젝트에서 터미널을 열고 `claude`(또는 `codex`)를 실행합니다.
3. 낮에는 작업 프로젝트 탭에서 일합니다. **이 폴더 경로를 `config.json`의 `sessions.allowed_cwds`에 적어 두면** 저녁에 그날 대화를 찾아 일기에 반영합니다.

### 4-3. Orca 없이

어떤 터미널(Terminal, iTerm, Ghostty 등)이든 됩니다.

```sh
cd ~/Documents/linda-vault && claude     # 볼트에서 에이전트 실행
```

작업은 다른 창에서 프로젝트 폴더로 이동해 에이전트를 띄우면 됩니다.

---

## 5. 스킬 설치와 설정

### 5-1. 스킬 복사

```sh
# Claude Code
mkdir -p ~/.claude/skills && cp -R daily-log ~/.claude/skills/daily-log

# Codex
mkdir -p ~/.agents/skills && cp -R daily-log ~/.agents/skills/daily-log
cp ~/Documents/linda-vault/CLAUDE.md ~/Documents/linda-vault/AGENTS.md   # Codex는 AGENTS.md를 읽습니다
```

스킬 폴더를 업데이트하기 쉽게 두고 싶다면 `cp -R` 대신 `ln -s "$PWD/daily-log" ~/.claude/skills/daily-log`로 링크해도 됩니다.

### 5-2. config.json 직접 쓰기 (선택)

보통은 [처음 설정](#처음-설정--daily-setup)의 `daily setup`으로 충분합니다. 직접 파일로 쓰고 싶다면 `config.example.json`을 `config.json`으로 복사해 아래 표대로 채웁니다. 쓰지 않는 출처는 `"enabled": false`로 둡니다.

```sh
cd ~/.claude/skills/daily-log      # Codex라면 ~/.agents/skills/daily-log
cp config.example.json config.json
```

| 키 | 뜻 | 예시 |
|---|---|---|
| `vault` | 볼트 경로 | `~/Documents/linda-vault` |
| `timezone` | 날짜 기준 시간대 | `Asia/Seoul` |
| `screenpipe.enabled` | 화면 기록 수집 | `true` |
| `github.user` | 내 GitHub 아이디 | `my-github-id` |
| `github.project_owner` / `project_number` | Project 보드 주인(org/계정)과 번호. 보드 URL `github.com/orgs/<owner>/projects/<number>`에서 확인 | `my-org` / `1` |
| `github.start_statuses` | 아침에 보여줄 카드 상태 이름. 보드의 Status 필드 값 그대로 | `["In Progress", "Todo"]` |
| `github.repos` | 이슈를 볼 레포 목록 | `["my-org/my-repo"]` |
| `github.wiki_repo` | 위키 변경을 볼 레포 (없으면 빈칸) | `my-org/my-repo` |
| `discord.server_id` | Discord 서버 ID. 브라우저 주소 `discord.com/channels/<서버ID>/<채널ID>`의 첫 숫자 | |
| `discord.server_name` | 창 제목에 보이는 서버 이름 (주소가 기록되지 않는 앱용) | |
| `discord.priority_channel_ids` | 먼저 볼 업무 채널 ID들 | |
| `discord.exclude_channels` | 뺄 채널 이름 | `["#잡담"]` |
| `sessions.allowed_cwds` | 일기에 반영할 작업 폴더 | `["~/work/my-project"]` |
| `sessions.sessions_file` | (선택) 세션 목록 파일. 비우면 폴더·날짜로 찾음 | |

`sessions_file`을 쓰면 아래처럼 첫 열에 세션 ID, 아무 열에 날짜(월/일)를 적은 마크다운 표로 만듭니다.

```md
| 세션 ID | 날짜 | 한 일 |
|---|---|---|
| 3f2a9c1e-... (codex) | 10/15 | 로그인 API 리팩터링 |
```

### 5-3. 앱 분류 규칙 (선택)

`scripts/app-category.json`의 `window`에 내 프로젝트 폴더·레포 이름을 넣으면 그 창은 "집중"으로 칠해집니다. 처음 `daily end`를 하면 분류되지 않은 앱 목록을 보여 주니, 그때 추가해도 됩니다.

### 5-4. 설치 확인

```sh
python3 ~/.claude/skills/daily-log/scripts/daily_log.py --self-test   # daily_log self-test: ok
python3 ~/.claude/skills/daily-log/scripts/timeline.py --selftest     # selftest ok
```



---

## 6. 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| `daily start`를 했는데 설정부터 묻는다 | `config.json`이 없거나 예시 값이 남아 있어서입니다. 질문에 답하면 설정 후 원래 요청을 이어서 합니다 ([처음 설정](#처음-설정--daily-setup)) |
| 아침에 "GitHub 점검 실패" 알림 | 로그인이 풀렸거나 권한이 빠졌습니다. 안내된 명령을 실행하고 `daily setup`으로 다시 점검합니다 |
| 타임라인에 "recorder가 꺼져 있습니다" | Screenpipe가 꺼져 있습니다. 3-1의 녹화 명령을 실행하거나 데스크톱 앱을 켭니다 |
| "SCREENPIPE_API_KEY가 없습니다" | 3-4의 `export` 명령을 실행합니다 |
| HTTP 401/403 | 토큰이 지금 실행 중인 Screenpipe와 맞지 않습니다. `auth token`으로 다시 받습니다 |
| `search`가 code 5(database is locked) | 녹화 중 DB 잠금입니다. 에이전트가 자동으로 HTTP API로 다시 조회합니다 |
| 화면 기록이 비어 있음 | 3-2 권한을 확인하고 `doctor`를 실행합니다 |
| 포트 3030 사용 중 | `lsof -i :3030`으로 무엇이 쓰는지 확인합니다 |
| `gh project`가 권한 오류 | `gh auth refresh -s project` |
| 일기가 두 개 생김 | Obsidian 데일리 노트 폴더·형식이 2장 표와 다릅니다 |
| Discord 내용이 안 들어옴 | 브라우저가 주소를 넘기지 않으면 `discord.server_name`으로 찾습니다. 창 제목에 보이는 서버 이름과 같은지 확인합니다 |

---

## 참고한 공식 문서

- Screenpipe 시작하기 — <https://docs.screenpipe.com/getting-started>
- Orca — <https://onorca.dev> · <https://github.com/stablyai/orca>
- Obsidian 데일리 노트 — <https://obsidian.md/help/plugins/daily-notes>
- Claude Code 스킬 — <https://code.claude.com/docs/en/skills>
- Codex 스킬 — <https://learn.chatgpt.com/docs/build-skills>
- `gh project item-list` — <https://cli.github.com/manual/gh_project_item-list>
- GitHub Projects 필터 — <https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects>
