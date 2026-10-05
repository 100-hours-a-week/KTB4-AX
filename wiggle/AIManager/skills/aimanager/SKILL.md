---
name: aimanager
description: AIManager로 팀의 AI 스킬·플러그인·MCP를 공유하고 관리한다. "팀 저장소 새로 만들어줘", "팀원 초대해줘", "이 스킬 팀에 공유해줘", "팀 스킬 수정 올려줘", "팀 MCP 추가해줘", "팀 플러그인 추가/설치해줘", "팀 스킬 사용 통계 보여줘", "AIManager 점검/제거해줘" 같은 요청에 사용한다.
---

# aimanager

명령은 `aimanager`(없으면 `python3 ~/.aimanager/tool/aimanager.py`)로 실행한다. 사용자가 직접 명령을 칠 필요가 없도록 에이전트가 실행하고, 결과를 사용자 언어로 짧게 알려준다.

## 팀 만들기·초대·참여

- 새 팀(팀장): 저장소 이름을 묻고 `aimanager create <이름>` (기본 비공개, `--public`, `--team <팀 이름>`). 이어서 팀원 GitHub 아이디를 묻고 `aimanager invite <아이디...>` → 출력된 안내문을 사용자에게 전달한다.
- 참여(팀원): `aimanager init <팀 저장소 URL>`. URL이 없으면 새로 만들지 말고 팀장에게 받아오라고 안내한다.
- 끝나면 Codex 사용자에게 `/hooks`에서 AIManager 훅 신뢰를 안내하고, `aimanager doctor`로 확인한다.

## 스킬 공유 (새 스킬, 팀 스킬 수정)

1. 올릴 폴더를 정한다. 사용자가 경로를 주면 그 경로, 이름만 주면 `~/.claude/skills/<이름>` 또는 `~/.agents/skills/<이름>`. 애매하면 묻는다.
2. 폴더 전체를 읽고 다음이 있으면 알리고 어떻게 할지 묻는다: 비밀값(API 키, 토큰), 개인 절대 경로, 개인만 쓰는 도구·위키 의존, 외부 출처(라이선스가 있으면 팀 저장소 `THIRD_PARTY_NOTICES.md`에 추가 필요).
3. `aimanager push <이름 또는 경로>` → PR 링크를 알려준다. 머지 후 팀원이 AI 도구를 새로 열면 적용된다.

## MCP 서버 공유

- 추가: `aimanager mcp add <이름> --url <URL>` (HTTP), `aimanager mcp add <이름> -- <명령> <인자...>` (stdio)
  - 비밀값은 값 대신 환경 변수로: `--header "Authorization=Bearer \${TOKEN_ENV}"`, `--env KEY=VALUE`
  - 일부 도구만: `--tools claude` 또는 `--tools codex`
- 제거: `aimanager mcp remove <이름>`
- 상태: `aimanager mcp list`

추가·제거는 PR로 올라가고, 머지되면 팀원 PC의 Claude Code·Codex 설정에 자동 반영된다. 이름이 같은 개인 서버가 있으면 건드리지 않는다.

## 플러그인·도구 공유

- 선언 추가(PR): `aimanager packages add <플러그인>@<마켓플레이스>` (공식 외 마켓플레이스는 `--marketplace-repo owner/repo`), npm 도구는 `aimanager packages add <이름>[@버전] --npm`
- 설치: `aimanager packages --dry-run`으로 명령을 보여주고, 사용자가 동의하면 `aimanager packages`

"[AIManager] 팀 플러그인·패키지 선언이 바뀌었습니다" 안내가 보이면 자동으로 설치하지 말고 위 순서대로 사용자에게 확인받는다.

## 그 밖에

- 사용 통계: `aimanager digest [일수]`
- 점검: `aimanager doctor` (Codex 훅은 Codex `/hooks`에서 신뢰해야 동작)
- 지금 동기화: `aimanager pull`
- 제거: `aimanager uninstall` (`--purge`는 `~/.aimanager`까지 삭제)
