---
name: daily-log
description: >
  하루 시작/끝 일기 파이프라인. Screenpipe 화면 기록과 (설정에 따라) GitHub Project·레포,
  Discord 업무 채널, AI 에이전트 작업 세션을 모아 Obsidian 볼트의 raw/일기/DATE.md에 쓴다.
  Use when the user says daily setup, daily start, daily end, 하루 시작, 하루 끝, 오늘 일기, 하루 기록, 일기 설정.
---

# daily-log

## 0. 먼저 읽을 것

- `SKILL_DIR`은 이 SKILL.md가 들어 있는 폴더다. 아래 명령의 `$SKILL_DIR`은 그 절대경로로 바꿔 실행한다.
- `$SKILL_DIR/config.json`을 읽는다. 없거나, `enabled: true`인 출처에 예시 값(`my-github-id`, `my-org`, `my-org/my-repo`, `~/work/my-project`)이나 빈 필수 값이 남아 있으면 요청이 무엇이든 먼저 **daily setup**을 진행한다.
- `VAULT`는 config의 `vault` 값이다(`~`는 홈으로 펼친다). 볼트에 `CLAUDE.md`가 있으면 그 규칙을 먼저 적용한다.
- **일기 본문을 쓰기 전에 `$SKILL_DIR/기록-작성기준.md`를 반드시 읽는다.** 이 문서는 실행 순서와 명령만 정하고, 글을 어떻게 쓰는지는 기록-작성기준이 정한다.
- 날짜 기본값은 config `timezone`(기본 Asia/Seoul)의 오늘이다.
- config에서 `enabled: false`인 출처는 조회하지도, 언급하지도 않는다.

### 문서 작성 공통 지침

스킬로 일기나 raw 파일을 만들거나 고칠 때 **첫 줄**에 작성 모델과 일시를 인용구로 적는다. 모델 이름은 지금 실행 중인 모델의 실제 이름을 쓴다.

    > **작성 모델:** <모델 이름> | **작성 일시:** YYYY-MM-DD HH:MM KST

이 일기의 목적은 나중에 자기소개서·면접에 쓸 경험을 사실과 근거로 모으는 것이다. 자동 자료를 붙이는 데서 끝내지 말고, **그 글만 읽어도 그날 무슨 일이 있었고, 어떤 문제가 어디서 생겨, 어떻게 해결하거나 논의했는지 알 수 있게** 쉬운 문장으로 자세히 쓴다. 요약으로 줄이지 않는다.

일기 본문은 에이전트가 쓰는 글이다. 사용자가 직접 쓴 `## 내 메모`는 고치지 않는다. 수치는 기록-작성기준 §4의 판별 질문 — *"시스템을 잰 값인가, 내가 일한 양을 센 값인가?"* — 을 통과한 값만 쓴다.

자동 상자 마커는 다음 네 줄이다. 스크립트가 만들고 채운다.

    <!-- auto:screenpipe:start -->
    <!-- auto:screenpipe:end -->
    <!-- auto:github:start -->
    <!-- auto:github:end -->

## daily setup

처음 한 번, 그리고 사용자가 `daily setup`·"설정 다시"라고 할 때 실행한다. 사용자가 JSON을 직접 고치지 않게 대화로 값을 받아 `$SKILL_DIR/config.json`을 대신 쓴다.

1. `config.json`이 없으면 `config.example.json`을 복사해 시작한다. 있으면 지금 값을 보여 주고 바꿀 것만 묻는다.
2. 아래 순서로 한 출처씩 묻는다. "쓸까요?"에 아니오면 `enabled: false`로 두고 다음으로 넘어간다.

    | 순서 | 출처 | 물어볼 값 |
    |---|---|---|
    | 1 | 볼트 | 볼트 경로 (`vault`), 시간대 (기본 `Asia/Seoul`) |
    | 2 | Screenpipe | 쓸지 여부 |
    | 3 | GitHub | 아이디, Project 보드 URL(여기서 owner·번호를 뽑는다), 아침에 보여줄 Status 이름, 이슈를 볼 레포, 위키 레포 |
    | 4 | Discord | 서버 주소(`discord.com/channels/<서버ID>/...`)나 서버 ID, 서버 이름, 업무 채널, 뺄 채널 |
    | 5 | 작업 세션 | 낮에 에이전트와 일하는 폴더들, 세션 목록 파일(선택) |

    GitHub 아이디는 사용자가 비워 두면 `gh api user --jq .login` 결과를 제안한다. Status 이름은 보드를 한 번 조회해 실제 값 목록을 보여 주고 고르게 한다.
3. 값을 받을 때마다 바로 아래 점검을 돌린다. 출력에 토큰이 보이면 기록하지 않는다.

    | 출처 | 점검 | 통과 조건 |
    |---|---|---|
    | 볼트 | `vault` 경로와 `<vault>/_템플릿/일일노트.md` 존재 | 둘 다 있음 |
    | Screenpipe | `$SP status --json` | running이고 마지막 캡처가 오늘 |
    | GitHub | `gh auth status` | 로그인 계정이 `github.user`와 같고 scopes에 `project`가 있음 |
    | GitHub | `gh project item-list <number> --owner <owner> --limit 1 --format json` · 레포마다 `gh repo view <repo> --json name` | 모두 성공 |
    | Discord | `$SP search "<server_name>" --start <7일 전> --json -n 5`로 창 제목·주소에 서버 이름이나 ID가 보이는지 | 1건 이상 |
    | 작업 세션 | `allowed_cwds` 폴더 존재, `sessions_file`(있으면) 존재 | 모두 있음 |

4. 끝나면 `config.json`을 저장하고 결과를 표로 보여준다. 표의 열은 `출처 | 상태(✅ 통과 · ⚠️ 확인 필요 · ❌ 실패 · — 끔) | 고치는 방법`이다.
    - ❌는 원인과 고치는 명령을 안내하고, 지금 끌지(`enabled: false`) 묻는다. 설치·로그인 명령은 안내만 하고 실행하지 않는다.
    - Discord가 기록에서 안 보이면 ⚠️로 두고 "Screenpipe가 켜진 상태에서 그 서버를 한 번 열어 두면 다음 점검에서 확인된다"고 안내한다.
    - Screenpipe가 꺼져 있으면 ⚠️로 두고 녹화 명령을 보여준다.
5. setup이 다른 요청(`daily start` 등) 때문에 시작됐다면, 끝난 뒤 원래 요청을 이어서 실행한다.

## daily start [DATE]

1. 입력한 DATE를 쓰고, 없으면 오늘을 쓴다.
   켜져 있는 출처만 빠르게 점검한다: GitHub는 `gh auth status`, Discord·작업 세션은 설정 값이 비어 있지 않은지, 볼트는 경로 존재. Screenpipe는 2단계에서 본다. 실패한 출처가 있으면 채팅 맨 위에 한 줄로 알리고 `daily setup`으로 고칠 수 있다고 안내한다. 점검 실패가 있어도 start는 계속한다.
2. `screenpipe.enabled`이면 녹화 상태를 **조회만** 한다. 직접 켜지 않는다.

        if command -v screenpipe >/dev/null; then SP=screenpipe; else SP="npx -y screenpipe@latest"; fi
        $SP status --json

    `running`이고 마지막 캡처 날짜가 오늘일 때만 녹화 중으로 본다. 아니면 아래 명령을 보여주기만 한다.

        SCREENPIPE_NO_REMINDERS=1 npx -y screenpipe@latest record

    `/health` 200만으로 오늘 녹화 중이라고 판단하지 않는다.
3. 일기 파일을 만들거나 마커만 보충한다. 이미 있는 본문과 `## 내 메모`는 start에서 건드리지 않는다.

        python3 "$SKILL_DIR/scripts/daily_log.py" start --date DATE --vault "$VAULT"

4. `github.enabled`이면 내 담당 카드 중 상태가 `github.start_statuses`에 든 것만 채팅 표로 보여준다. 일기에는 쓰지 않는다.

        gh project item-list <project_number> --owner <project_owner> --query "assignee:@me" --limit 50 --format json

5. 볼트가 git 저장소면 `git status`를 표로 보여준다. 커밋하지 않고, 사용자가 직접 입력할 명령만 보여준다.

시작 때는 GitHub 댓글·Screenpipe 이력·세션 전문을 읽지 않는다.

## daily end [추가 부탁...]

`daily end` 다음 줄은 그날만의 추가 부탁으로 읽는다. 다음 날 기본값으로 저장하지 않는다.

| 출처 | 켜는 설정 | 가져올 것 | 가져오지 않을 것 |
|---|---|---|---|
| Screenpipe | `screenpipe.enabled` | 오늘의 앱·창 제목·시간 | 전체 OCR·오디오 전사 원문 |
| Discord | `discord.enabled` | 지정 서버 업무 채널의 화면 내용(Screenpipe OCR) | 서버 밖·DM·잡담 채널 |
| GitHub | `github.enabled` | 내 담당 카드, 오늘 내가 쓴 댓글·본문, 오늘 연 이슈 | 남이 쓴 댓글만 있는 이슈, 관련 없는 옛 이슈 |
| 작업 세션 | `sessions.enabled` | 오늘 허용 폴더에서 한 에이전트 대화 | 허용 폴더 밖 대화 |

### 1. Screenpipe

Screenpipe 상자는 3분 블록 타임라인으로 시작한다. API 토큰은 환경변수로만 넘기고 출력·기록하지 않는다.

    export SCREENPIPE_API_KEY=$(npx -y screenpipe@latest auth token)
    python3 "$SKILL_DIR/scripts/timeline.py" DATE

stdout으로 격자 HTML과 앱별 표가 나온다. 그 아래에 앱·창 제목·시간을 요약한 작은 한국어 표를 붙여 한 본문으로 만든다. 분류 규칙은 `$SKILL_DIR/scripts/app-category.json`에 있다. 미분류 앱이 stderr로 나오면 그 목록을 사용자에게 보여주고 규칙에 추가할지 묻는다. 타임라인이 실패하면 표만 넣고 실패 원인을 상자 첫 줄에 적는다.

창 목록 조회는 CLI로 한다. 녹화 중 SQLite 잠금(code 5)으로 실패하면 같은 조건으로 `http://localhost:3030/search`를 토큰과 함께 호출한다.

    $SP search --start '<DATE>T00:00:00+09:00' --end now --json -n 80 --content-type ocr --max-content-length 80

조회 결과가 없으면 상자를 비우지 말고 `오늘 자동 로그 없음`만 넣는다(`--keep-if-empty`가 처리한다).

    printf '%s\n' "$BODY" | python3 "$SKILL_DIR/scripts/daily_log.py" splice --date DATE --vault "$VAULT" --section screenpipe --body-file - --keep-if-empty

요약 중 오류가 나면 splice를 하지 않아 이전 상자를 보존한다. Screenpipe DB와 화면 파일은 `~/.screenpipe/`에 두고 볼트로 복사하지 않는다.

### 2. Discord 업무 내용 (`discord.enabled`)

Discord 내용은 Screenpipe 화면 OCR에서 **config의 서버 하나**로만 가져온다. 서버를 확인하는 수단은 두 가지이고 있는 것을 쓴다.

| 순서 | 확인 수단 | 통과 조건 |
|---|---|---|
| ① | `browser_url` | `discord.server_id`가 포함된 기록 |
| ② | `window_name` (①이 비었을 때) | `discord.server_name`이 포함되고 채널이 `#이름` 형태인 기록 |

일부 브라우저와 데스크톱 앱은 주소를 넘기지 않아 ①이 비어 있다. **①이 비었다는 이유로 Discord를 통째로 빼지 않는다.** 둘 다 서버를 특정하지 못할 때만 뺀다.

- DM은 뺀다. 창 제목이 `#이름` 대신 `@이름`이거나 사람 이름 목록이면 DM이다.
- `discord.exclude_channels`와 잡담·링크·식사 채널은 뺀다. `priority_channel_ids`를 먼저 보고, 다른 채널은 그날 내 메시지나 업무 활동이 보일 때만 더한다.
- 날짜는 화면에 보인 **날짜 구분선**(`YYYY년 M월 D일`)으로 가린다. 스크롤백 때문에 다른 날 메시지가 같은 프레임에 찍힌다.
- OCR 양이 많으므로 **채널×20분마다 가장 긴 프레임 하나만** 고르고 줄 단위로 중복을 지운 뒤 읽는다. 사이드바·멤버 목록·버튼 같은 화면 장식은 버린다.
- 업무와 직접 관련된 내용만 요약하고 **누가 말했는지** 함께 적는다. 화면에 안 보였거나 OCR이 잘린 부분은 추정하지 않고, 못 본 구간이 있으면 보고에 밝힌다.
- 음성 전사는 화면으로 확인되지 않는 회의 내용의 보조 근거로만 쓴다. 전사 원문은 볼트에 복사하지 않는다.

### 3. GitHub (`github.enabled`)

    gh project item-list <project_number> --owner <project_owner> --limit 100 --format json
    gh issue list -R <repo> --state all --limit 50 --json number,title,state,author,assignees,createdAt,updatedAt,url

`repos`의 레포마다 이슈 목록을 본다. 댓글은 보드 항목의 `content.repository`와 `content.number`로 가져온다.

    gh api repos/<content.repository>/issues/<content.number>/comments

**수집 대상**
- 보드 카드 중 담당자가 `github.user`인 카드, 또는 연결 이슈에 `github.user`가 DATE에 쓴 댓글·본문이 있는 카드
- `repos`의 이슈 중 담당자가 `github.user`이거나 DATE에 내가 연 이슈(보드에 아직 없어도)
- 담당자라는 사실만으로 그날 일했다고 단정하지 않는다. 그날 쓴 댓글·커밋·이슈 활동으로 확인한다.

`wiki_repo`가 있으면 위키 변경도 본다. GitHub Wiki는 별도 git 저장소라 `gh issue`·`gh project`에 잡히지 않는다. `https://github.com/<wiki_repo>/wiki/_history`에서 DATE의 리비전을 확인한다. 팀원이 내 결정을 대신 반영하는 경우가 있으므로 **작성자로 거르지 말고 내용으로 내 작업인지 판단한다.**

auto 상자의 표 열은 `출처 | 항목 | 상태 | 근거(URL)`이다.

    printf '%s\n' "$BODY" | python3 "$SKILL_DIR/scripts/daily_log.py" splice --date DATE --vault "$VAULT" --section github --body-file -

조회가 실패하면 기존 GitHub 상자를 보존하고 채팅에 실패를 말한다. GitHub가 꺼져 있어도 다른 출처의 근거 표가 있으면 이 상자에 넣는다.

### 4. 작업 세션 (`sessions.enabled`)

세션은 추측해서 고르지 않는다.

1. `sessions.sessions_file`이 있으면 그 파일의 표에서 DATE(월/일)가 들어 있는 행의 첫 열(세션 ID)을 읽는다. 뒤에 붙은 `(codex)` 같은 괄호는 떼고 ID만 쓴다.
2. 파일이 없으면 `sessions.allowed_cwds` 아래에서 DATE에 수정된 세션만 찾는다.
3. 목록에 없는 세션은 수집할지 사용자에게 먼저 묻는다.

세션 저장 위치(에이전트별 기본값):

- Claude Code: `~/.claude/projects/<cwd의 /를 -로 바꾼 이름>/*.jsonl`
- Codex: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (`session_meta`의 cwd 확인)
- Grok: `~/.grok/sessions/<urlencode한 cwd>/`

일기에는 세션 ID를 **앞 8자**로 적는다. 이어받기로 기록 파일이 갈렸으면 두 ID를 모두 적는다. 대화에 실제로 나온 사실만 적고 지어내지 않는다.

### 5. 일기 본문

auto 표는 근거일 뿐 일기가 아니다. 본문은 볼트의 `_템플릿/일일노트.md` 섹션을 기록-작성기준 §3에 따라 채운다.

| 섹션 | 규칙 |
|---|---|
| `## 오늘의 맥락` | 필수. 어느 프로젝트의 어느 단계인지, 오늘 무엇을 하려 했는지 |
| `## 오늘 한 일` | 필수. 일마다 `###` 소제목 + 무엇을·왜·어떻게·결과. **빈칸 금지** |
| `## 논의한 것` | 있으면. 누가 무엇을 제안했고 무엇으로 정했나. 팀원 발언은 팀원 것으로 표시 |
| `## 오늘의 트러블슈팅` | 아래 **후보 제시 → 선택**을 거친 것만, `_템플릿/트러블슈팅.md` 구조 그대로 |
| `## 수치` | 실측 값이 있을 때만. 없으면 섹션을 만들지 않는다 |
| `## 회고` | 필수. **하루에 한 번만** |
| `## 이어서 확인할 일` | 있으면 |
| `## 내 메모` | 사용자 전용. 고치지 않는다 |

#### 트러블슈팅 후보 제시 → 선택

기술 사건에 한정하지 않는다. 설계·구현 판단, 논의, 회고에서 나온 사건도 같은 틀로 다룬다. 아래 신호가 하나라도 있으면 후보로 올린다. **해결됐는지로 거르지 않는다.**

| 소스 | 신호 |
|---|---|
| 오늘 한 일 초안 | "안 됐다/못 썼다" · "발견했다/확인했다" + 문제 명사(불일치·에러·버그·미반영) · "~대신 ~로 바꿨다" · "원인 모름" |
| GitHub | 제목·본문에 버그·에러·실패·fix·트러블슈팅, `bug` 라벨 |
| Discord | "문제", "안 되는데", "에러", 팀원이 올린 트러블슈팅 글 |
| Screenpipe | Error·Exception·스택트레이스가 보이는 구간 |
| 작업 세션 | "발견", "실패", "안 됨" 같은 동사가 붙은 항목 |

후보가 있으면 본문에 쓰기 전에 **채팅으로 먼저 보여주고 멈춘다.** 형식은 번호 · 한 줄 제목 · 출처 · 상태(해결·진행중·미해결)다. 사용자가 번호(`1,3`)·`전부`·`없음`으로 답하면 고른 것만 쓴다. 후보가 0개면 섹션을 만들지 않는다.

트러블슈팅은 일기 안에서 혼자 읽히게 전부 쓴다. 다른 파일로 넘기지 않는다.

`## 수치`에는 응답 시간·처리량·정확도·메모리·이미지 크기·기동 시간·비용처럼 **시스템을 잰 값**만 출처와 함께 쓴다. 커밋·PR 개수, 줄 수, 파일 수, 테스트 개수, 커밋 해시는 작업량이므로 넣지 않는다.

본문을 다 쓴 뒤 기록-작성기준 §5 체크리스트를 돌린다.

### 6. 마무리

- 모든 자동 상자는 표로 요약한다. 화면 본문이나 대화 원문을 덤프하지 않는다. 덤프하지 않는다는 것은 원문을 복사하지 않는다는 뜻이지 본문을 짧게 쓴다는 뜻이 아니다.
- 볼트가 git 저장소면 끝에 `git status`를 표로 보여준다. 커밋·푸시는 사용자가 직접 한다.
- 프로그램 설치와 `git add`·`commit`·`push`는 실행하지 않고 명령만 안내한다.

## 자체 점검

    python3 "$SKILL_DIR/scripts/daily_log.py" --self-test
    python3 "$SKILL_DIR/scripts/timeline.py" --selftest
