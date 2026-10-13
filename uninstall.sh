#!/bin/bash
# Happy Hamzzi 제거: 앱 종료·삭제, 상태 파일, Claude Code 훅, 옛 LaunchAgent
pkill -f "Happy Hamzzi.app/Contents/MacOS/hamster" 2>/dev/null
launchctl bootout gui/$(id -u)/com.gipeum.happyhamzzi 2>/dev/null; rm -f ~/Library/LaunchAgents/com.gipeum.happyhamzzi.plist
rm -rf "/Applications/Happy Hamzzi.app" ~/.hamster.d ~/.hamster
defaults delete com.gipeum.happyhamzzi 2>/dev/null
command -v python3 >/dev/null 2>&1 && python3 - <<'PY' || echo "훅은 ~/.claude/settings.json 에서 '.hamster.d' 가 든 항목을 직접 지워 주세요"
import json, os
p=os.path.expanduser('~/.claude/settings.json')
if os.path.exists(p):
    try:
        d=json.load(open(p)); hooks=d.get('hooks',{})
        if isinstance(hooks,dict):
            for e in list(hooks): hooks[e]=[x for x in hooks[e] if not any(('.hamster.d/' in h.get('command','') or h.get('command','').endswith('> ~/.hamster')) for h in x.get('hooks',[]))]
            tmp=p+'.tmp'; json.dump(d,open(tmp,'w'),indent=2,ensure_ascii=False); open(tmp,'a').write('\n'); os.replace(tmp,p); print('hooks removed')
    except Exception as e: print('settings.json 을 읽지 못해 훅은 건너뜁니다:', e)
PY
echo "제거 완료. 로그인 항목 목록에 남아 있으면 시스템 설정 → 일반 → 로그인 항목에서 지우세요."
