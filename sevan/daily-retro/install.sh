#!/usr/bin/env bash
# 이 레포의 skills/ 아래 모든 스킬을 Claude Code 와 Codex 양쪽에 링크한다.
# 사용법: bash install.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")
[ -d "$HOME/.codex" ] && DESTS+=("$HOME/.codex/skills")   # Codex 구버전 경로

for SKILL in "$ROOT"/.claude/skills/*/; do
  NAME="$(basename "$SKILL")"
  for DEST in "${DESTS[@]}"; do
    mkdir -p "$DEST"
    ln -sfn "${SKILL%/}" "$DEST/$NAME"
    echo "링크: $DEST/$NAME"
  done
done

command -v gh >/dev/null || echo "경고: gh CLI 없음 → https://cli.github.com 설치 후 'gh auth login'"
gh auth status >/dev/null 2>&1 || echo "경고: gh 인증 필요 → 'gh auth login'"
command -v python3 >/dev/null || echo "경고: python3 없음"
echo "완료. Claude Code 나 Codex 를 새로 띄우면 스킬이 잡힙니다."
echo "개인 config.json 은 첫 실행에 네 가지 정보를 확인한 뒤 생성합니다."
