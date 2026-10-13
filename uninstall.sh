#!/bin/bash
# Happy Hamzzi 제거: 앱 종료·삭제, 상태 파일, Claude Code 훅, 옛 LaunchAgent
pkill -f "Happy Hamzzi.app/Contents/MacOS/hamster" 2>/dev/null
launchctl bootout gui/$(id -u)/com.gipeum.happyhamzzi 2>/dev/null; rm -f ~/Library/LaunchAgents/com.gipeum.happyhamzzi.plist
rm -rf "/Applications/Happy Hamzzi.app" ~/.hamster.d ~/.hamster
defaults delete com.gipeum.happyhamzzi 2>/dev/null
python3 - <<'PY'
import json, os
p=os.path.expanduser('~/.claude/settings.json')
if os.path.exists(p):
    d=json.load(open(p))
    for e in list(d.get('hooks',{})): d['hooks'][e]=[x for x in d['hooks'][e] if not any('.hamster' in h.get('command','') for h in x.get('hooks',[]))]
    json.dump(d,open(p,'w'),indent=2,ensure_ascii=False); open(p,'a').write('\n'); print('hooks removed')
PY
echo "제거 완료. 로그인 항목 목록에 남아 있으면 시스템 설정 → 일반 → 로그인 항목에서 지우세요."
