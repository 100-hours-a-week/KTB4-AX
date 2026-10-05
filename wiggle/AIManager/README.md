<h1 align="center">AIManager</h1>

<p align="center"><b>팀 AI 스킬·MCP·플러그인 관리·공유 도구</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Codex-555.svg" alt="Claude Code | Codex">
</p>

관리자가 팀 GitHub 저장소에 팀에서 사용할 스킬과 MCP 서버를 모아두면, 팀원은 AI 도구를 열 때마다 최신 상태를 자동으로 다운받아 사용할 수 있습니다.

## 빠른 시작

아래 문장 중 하나를 **Claude Code나 Codex에 그대로 보내세요.** AI가 이 README를 읽고 설치를 진행합니다.

**팀을 처음 만든다면 (팀장)**

```text
AIManager를 설치하고 우리 팀 저장소를 새로 만들어줘. 방법은 https://github.com/SungjinWi99/AIManager 를 읽고 따라 해.
```

**이미 있는 팀에 참여한다면 (팀원)**

```text
AIManager를 설치하고 우리 팀에 참여시켜줘. 방법은 https://github.com/SungjinWi99/AIManager 를 읽고 따라 해. 팀 저장소는 https://github.com/<조직>/<저장소>
```

설치가 끝나면 AI 도구를 **새로 여세요.** 그다음부터는 말로 요청하면 됩니다.

| 하고 싶은 것 | 이렇게 말하세요 |
|---|---|
| 내 스킬을 팀에 공유 | "`my-skill` 스킬 팀에 공유해줘" |
| 팀 스킬 고치기 | "팀 `adr` 스킬에서 ○○ 부분 고쳐서 올려줘" |
| 팀 MCP 서버 추가 | "Notion MCP를 팀 MCP로 추가해줘" |
| 팀 플러그인 추가·설치 | "`code-review` 플러그인을 팀 플러그인으로 추가해줘", "팀 플러그인 설치해줘" |
| 팀원 초대 (팀장) | "`github-id1`, `github-id2`를 팀에 초대해줘" |
| 사용 통계 | "이번 주 팀 스킬 사용 통계 보여줘" |
| 문제 확인 | "AIManager 점검해줘" |

## 준비물

- macOS 또는 Linux
- Python 3.9 이상 (`python3 --version`), git
- [GitHub CLI](https://cli.github.com) 로그인: `gh auth login` (팀 저장소 만들기, 공유 PR, 초대에 사용)
- Claude Code 또는 Codex (둘 다 써도 됩니다)

## 무엇을 공유하나요

| 대상 | 팀장이 하는 일 | 팀원 PC에서 일어나는 일 |
|---|---|---|
| **스킬** | PR 리뷰 후 머지 | AI 도구를 열 때 자동으로 받아 `~/.claude/skills`, `~/.agents/skills`에 연결 |
| **MCP 서버** | PR 리뷰 후 머지 | Claude Code·Codex 설정에 자동으로 추가·제거. 로그인이 필요하면 한 번 안내 |
| **플러그인·npm 도구** | PR 리뷰 후 머지 | 바뀌면 한 번 안내. 설치는 확인 후 `aimanager packages`로 직접 |
| **사용 통계** | `aimanager digest`로 확인 | 팀 스킬을 쓴 기록을 하루 한 번 팀 저장소에 보고 |

<details>
<summary><b>명령줄로 직접 설치하기</b></summary>

### 팀장: 팀 만들기

```sh
git clone https://github.com/SungjinWi99/AIManager.git ~/.aimanager/tool
python3 ~/.aimanager/tool/aimanager.py create <저장소 이름>      # 기본 비공개. --public, --team <팀 이름>
aimanager invite <팀원 GitHub 아이디> ...                         # 초대 + 팀원에게 보낼 안내문 출력
```

`create`는 GitHub에 팀 저장소를 만들고 기본 구조(`skills/`, `mcp/mcp.json`, `aimanager.json`, `stats` 브랜치)를 올린 뒤 이 PC에 연결합니다.

### 팀원: 참여하기

```sh
git clone https://github.com/SungjinWi99/AIManager.git ~/.aimanager/tool
python3 ~/.aimanager/tool/aimanager.py init https://github.com/<조직>/<저장소>.git
```

### 공통: 마무리

- **Codex를 쓴다면** Codex에서 `/hooks`를 열고 AIManager 훅 3개를 신뢰(trust)하세요. 신뢰하기 전에는 Codex에서 동기화와 기록이 동작하지 않습니다.
- `~/.local/bin`이 PATH에 없으면 추가하세요. 그래야 어디서든 `aimanager`를 쓸 수 있습니다.
- `aimanager doctor`로 모두 ✔인지 확인하세요.

</details>

## 명령

| 명령 | 하는 일 |
|---|---|
| `aimanager create <이름>` | (팀장) 새 팀 저장소를 만들고 연결 |
| `aimanager invite <아이디...>` | (팀장) 팀원을 저장소에 초대하고 안내문 출력 |
| `aimanager init <URL>` | 팀 저장소에 연결, 훅 등록, 첫 동기화 (다시 실행해도 안전) |
| `aimanager pull` | 지금 바로 동기화 (AI 도구를 열 때 자동 실행) |
| `aimanager push <스킬>` | 스킬을 팀 저장소에 PR로 올리기 |
| `aimanager mcp list` / `add` / `remove` | 팀 MCP 서버 보기, 추가·제거 PR |
| `aimanager packages [--dry-run]` / `packages add <대상>` | 팀 플러그인·npm 도구 설치, 선언 추가 PR |
| `aimanager digest [일수]` | 팀 스킬 사용 통계 (기본 7일) |
| `aimanager doctor` | 설치 상태 점검 |
| `aimanager uninstall [--purge]` | 이 PC에서 제거 (`--purge`는 `~/.aimanager`까지 삭제) |

## 자주 묻는 질문

<details>
<summary><b>새 팀 스킬은 언제 보이나요?</b></summary>

PR이 머지된 뒤 **AI 도구를 새로 열면** 보입니다. 바로 받고 싶으면 `aimanager pull`을 실행하세요.
</details>

<details>
<summary><b>내 개인 스킬과 팀 스킬 이름이 같으면요?</b></summary>

개인 스킬이 우선하고 팀 스킬은 건너뜁니다. `aimanager doctor`에 어떤 스킬을 건너뛰었는지 나옵니다. MCP 서버도 같은 이름의 개인 서버가 있으면 건드리지 않습니다.
</details>

<details>
<summary><b>팀 스킬을 고치고 싶어요.</b></summary>

`~/.aimanager/team`에서 직접 커밋하지 말고 "팀 ○○ 스킬 고쳐서 올려줘"라고 요청하세요(`aimanager push`). 고친 내용은 PR로 올라가고, 로컬 사본은 원래대로 돌아갑니다.
</details>

<details>
<summary><b>무엇이 기록되나요?</b></summary>

팀 스킬을 쓴 **시각, 도구(claude/codex), 스킬 이름, 세션 ID**만 기록합니다. 프롬프트, 코드, 파일 내용은 기록하지 않습니다. 기록은 하루 한 번 팀 저장소의 `stats` 브랜치에 `<GitHub 아이디>.tsv`로 올라가므로, **팀 저장소를 비공개로 두는 것을 권장합니다.**
</details>

<details>
<summary><b>MCP 서버에 API 키가 필요하면요?</b></summary>

키 값은 팀 저장소에 넣지 말고 환경 변수 이름만 적으세요. 예: `aimanager mcp add my-api --url https://example.com/mcp --header "Authorization=Bearer \${MY_API_TOKEN}"`. 각자 자기 PC에 `MY_API_TOKEN`을 설정하면 됩니다. OAuth를 쓰는 서버(Notion 등)는 추가된 뒤 각자 로그인합니다: Claude Code는 `/mcp`, Codex는 `codex mcp login <이름>`.
</details>

<details>
<summary><b>다른 팀으로 옮기거나 지우고 싶어요.</b></summary>

`aimanager uninstall`은 훅, 팀 스킬 링크, AIManager가 추가한 MCP 서버를 지웁니다. 개인 스킬과 개인 MCP 서버는 남습니다. 다른 팀에 참여하려면 `aimanager uninstall --purge` 후 새 저장소로 `init` 하세요.
</details>

## 팀 저장소 구조

```text
skills/<이름>/SKILL.md   팀 스킬
mcp/mcp.json             팀 MCP 서버
aimanager.json           팀 이름, 플러그인·npm 도구 선언
stats (브랜치)            팀원별 스킬 사용 기록
```

<details>
<summary><b>파일 형식</b> (TeamAI의 <code>mcp.yaml</code>, <code>packages</code>와 같은 필드를 JSON으로)</summary>

`mcp/mcp.json`

```json
{ "servers": [
  { "name": "notion", "transport": "http", "url": "https://mcp.notion.com/mcp" },
  { "name": "fmt", "transport": "stdio", "command": "npx", "args": ["-y", "@acme/fmt-mcp"],
    "env": { "MODE": "strict" }, "requires": ["npx"], "tools": ["claude"] }
] }
```

- `transport`: `stdio`, `http`, `sse` (Codex는 `sse` 미지원, 헤더는 `Bearer ${ENV}`만 지원)
- `requires`: PATH에 없으면 그 PC에서는 건너뜀. `tools`: 일부 도구에만 적용

`aimanager.json`

```json
{ "team": "my-team",
  "packages": {
    "npm": [{ "name": "eslint", "version": "latest", "global": true }],
    "claude": {
      "marketplaces": [{ "name": "claude-plugins-official", "repo": "anthropics/claude-plugins-official" }],
      "plugins": [{ "name": "code-review@claude-plugins-official" }] } } }
```

</details>

## 에이전트용 설치 안내

> 이 절은 "빠른 시작" 문장을 받은 AI 도구가 따라 하는 절차입니다. 명령은 에이전트가 직접 실행하고, 결과는 사용자 언어로 짧게 알려줍니다. 사용자에게 물어야 하는 것은 **표시된 곳에서만** 묻습니다.

1. **준비물 확인:** `python3 --version`(3.9 이상), `git --version`, `gh auth status`를 확인한다. `gh`가 로그인되어 있지 않으면 `gh auth login --web --git-protocol https`를 실행하고, 출력된 코드와 URL을 사용자에게 보여주며 브라우저에서 승인하게 한다.
2. **도구 받기:** `~/.aimanager/tool`이 없으면 `git clone https://github.com/SungjinWi99/AIManager.git ~/.aimanager/tool`. 있으면 `git -C ~/.aimanager/tool pull`.
3. **팀 만들기 또는 참여하기:**
   - 팀원(저장소 URL이 있음): `python3 ~/.aimanager/tool/aimanager.py init <URL>`. 권한 오류가 나면 팀장에게 GitHub 초대를 받고 수락해야 한다고 알린다. **URL이 없으면 새 저장소를 만들지 말고** 팀장에게 URL을 받아오라고 안내한다.
   - 팀장(새로 만들기): **저장소 이름을 묻는다**(예: `<팀>-ai`). 기본은 비공개. `python3 ~/.aimanager/tool/aimanager.py create <이름>`.
4. **결과 알리기:** 출력에 나온 팀 스킬 목록을 알려준다. Codex가 설치되어 있으면 "Codex에서 `/hooks`를 열고 AIManager 훅 3개를 신뢰하세요"라고 안내한다. `~/.local/bin`이 PATH에 없다는 안내가 나왔다면 그대로 전달한다.
5. **점검:** `python3 ~/.aimanager/tool/aimanager.py doctor`를 실행하고, ✖ 항목이 있으면 안내된 방법으로 해결한다.
6. **팀장이라면:** 팀원 GitHub 아이디를 **묻고** `aimanager invite <아이디...>`를 실행한 뒤, 출력된 안내문을 사용자에게 전달한다.
7. 마지막으로 "AI 도구를 새로 열면 팀 스킬이 보입니다. 이후에는 말로 요청하세요(예: '이 스킬 팀에 공유해줘')."라고 알린다.

## 개발

```sh
python3 -m unittest discover tests
```

`aimanager.py` 한 파일에 모든 기능이 있습니다. 이슈와 PR 환영합니다.

## 라이선스

[MIT](LICENSE)
