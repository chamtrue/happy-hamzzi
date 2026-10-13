#!/bin/bash
# 배포 패키지: dist/HappyHamzzi-<ver>.zip ("Happy Hamzzi.app" + install.sh + uninstall.sh + README)
set -e; cd "$(dirname "$0")"; ./build.sh >/dev/null
V=$(/usr/libexec/PlistBuddy -c 'Print CFBundleShortVersionString' app/Info.plist)
rm -rf dist/pkg; mkdir -p dist/pkg; cp -R "Happy Hamzzi.app" dist/pkg/
cat > dist/pkg/install.sh <<'IN'
#!/bin/bash
# 햄스터 설치: Applications 복사 → 로그인 자동 실행 → Claude Code 훅(있으면) → 실행
set -e; cd "$(dirname "$0")"
major=$(sw_vers -productVersion | cut -d. -f1); if [ "$major" -lt 14 ]; then echo "macOS 14 이상이 필요해요 (지금 $(sw_vers -productVersion))"; exit 1; fi
pkill -f "Happy Hamzzi.app/Contents/MacOS/hamster" 2>/dev/null || true; sleep 0.5
rm -rf "/Applications/Happy Hamzzi.app"; cp -R "Happy Hamzzi.app" /Applications/
xattr -dr com.apple.quarantine "/Applications/Happy Hamzzi.app" 2>/dev/null || true
if [ -f ~/.claude/settings.json ] && command -v python3 >/dev/null 2>&1; then
python3 - <<'PY' || echo "Claude Code 훅은 나중에 앱 설정 → 시스템에서 연결할 수 있어요"
import json, os, sys
p=os.path.expanduser('~/.claude/settings.json')
try: d=json.load(open(p))
except Exception as e: print('settings.json 을 읽지 못해 훅은 건너뜁니다:', e); sys.exit(1)
if not isinstance(d.get('hooks',{}),dict): print('hooks 형식이 달라 건너뜁니다'); sys.exit(1)
d.setdefault('hooks',{})
SID="sid=$(grep -o '\"session_id\" *: *\"[^\"]*\"' | head -1 | sed 's/.*\"\\([^\"]*\\)\"$/\\1/' | tr -cd 'A-Za-z0-9_-' | cut -c1-64); mkdir -p ~/.hamster.d; chmod 700 ~/.hamster.d; "
ev={'UserPromptSubmit':'working','PostToolUse':'working','Stop':'done','StopFailure':'faint','PostToolUseFailure':'faint','PermissionRequest':'surprised','SessionEnd':None}
for e,s in ev.items():
    lst=d['hooks'].setdefault(e,[])
    if any('.hamster.d/${sid' in h.get('command','') for x in lst for h in x.get('hooks',[])): continue
    c=SID+(f'echo {s} > "$HOME/.hamster.d/${{sid:-default}}"' if s else 'rm -f "$HOME/.hamster.d/${sid:-default}"')
    entry={'hooks':[{'type':'command','command':c}]}
    if e in ('PostToolUse','PostToolUseFailure','PermissionRequest'): entry={'matcher':'*',**entry}
    lst.append(entry)
import shutil; shutil.copy(p, p+'.bak-hamzzi')
tmp=p+'.tmp'; json.dump(d,open(tmp,'w'),indent=2,ensure_ascii=False); open(tmp,'a').write('\n'); os.replace(tmp,p); print('Claude Code 훅 등록')
PY
fi
open "/Applications/Happy Hamzzi.app"
echo "설치 완료. 앱이 로그인 항목에 스스로 등록돼요(설정에서 끌 수 있음). 메뉴바 햄스터 우클릭 → 설정…"
echo "권한: 캘린더(회의), 자동화·손쉬운 사용(슬랙·카톡 배지)은 처음 뜨는 팝업에서 허용. 노치 맥북은 ⌘+드래그로 시계 쪽에 옮기세요."
IN
cp uninstall.sh LICENSE LICENSE-ART.md dist/pkg/
cat > dist/pkg/README.md <<'RM'
# Happy Hamzzi — 메뉴바에 사는 픽셀 햄스터

맥 메뉴바(노치 맥북이면 노치 아래)에 햄스터가 살면서 Claude Code 작업, 회의, 알림, 시간, 날씨에 반응해요.

## 설치 (둘 중 하나)

**A. DMG** — `HappyHamzzi.dmg`를 열고 앱을 Applications로 끌어다 놓은 뒤 더블클릭.
처음 열 때 "확인되지 않은 개발자" 경고가 뜨면 **앱을 우클릭 → 열기**로 한 번만 통과하면 돼요(Apple 공증 없이 자체 서명한 앱이라 그래요).

**B. zip** — 압축을 풀고 터미널에서 `bash install.sh`. Applications 복사, 경고 해제, Claude Code 훅까지 한 번에.

둘 다 첫 실행에 **로그인 항목**으로 스스로 등록돼요(설정 → 시스템에서 끌 수 있음). 요구 사양: macOS 14 이상.

## 처음 켜면

"시작하기" 창이 한 번 떠요. 권한은 **필요한 것만** 켜면 되고 안 켜도 햄스터는 돌아가요. 우클릭 → "시작 안내 다시 보기"로 언제든 다시 볼 수 있어요.

| 권한 | 쓰는 곳 | 안 켜면 |
| --- | --- | --- |
| 캘린더 | 회의 5분 전 알람시계, 회의 중 헤드폰, 좌클릭 일정 보기 | 회의 반응·일정 탭 없음 |
| 손쉬운 사용 | Dock 배지(슬랙·카톡·아웃룩 알림), 타자 반응 | 알림 봉투·봉고 없음 |
| 위치 | 날씨 코스튬(비·눈·더위) | 날씨 없음 |
| 자동화(System Events) | Dock 배지 읽기 | 알림 봉투 없음 |

**아웃룩 일정 연결:** 시스템 설정 → 인터넷 계정 → 계정 추가 → Microsoft Exchange → 회사 메일로 로그인 → **캘린더만** 켜기. 그러면 맥 캘린더에 일정이 들어오고 햄스터가 읽어요. 토큰·IT 요청 없음.

**Claude Code 훅:** 설정 → 시스템 → Claude Code → **연결**. `~/.claude/settings.json`에 훅 7개를 넣어요(먼저 `settings.json.bak-hamzzi`로 백업, 다른 훅은 안 건드림). 연결 안 돼 있으면 우클릭 메뉴 맨 위에 안내가 떠요.

## 쓰는 법

- **좌클릭** 쓰다듬기 + 팝오버(일정 · 볼주머니(클립보드 최근 5개) · 활동 잔디 · 집중 세션 시작)
- **우클릭** 지금 상태 설명, 다음 회의, 스킨(디자인 A 클래식 34종 · 디자인 B 햄찌 2종), 레이아웃, 상태·코스튬 테스트, 설정
- **마우스 올리기** 지금 왜 이 표정인지 툴팁
- **설정(⌘,)** 모습(스킨·액세서리·레이아웃·타자 반응) · 하루 리듬(점심·퇴근·잘 시간·금요일·계절·생일) · 건강(쉬기·물·집중) · 알림(감시 앱) · 시스템(로그인·권한·Claude 훅·클립보드)

**레이아웃:** 22px 단독 / 44px 햄스터+소품 / 66px +장면 / **노치 모드**(노치 아래 검은 트레이에 32px, 노치 화면이 없으면 자동으로 메뉴바).

**노치 맥북 주의:** 메뉴바 아이콘이 많으면 새 아이콘이 노치 밑에 숨어요. 안 보이면 **⌘를 누른 채 시계 쪽으로 끌어** 옮기세요. 한 번 옮기면 기억해요.

## 햄스터가 하는 것

| 상태 | 언제 |
| --- | --- |
| 쳇바퀴 | Claude가 일하는 중 (키 치면 귀 쫑긋) |
| 체크 | Claude 답변 끝 |
| 사이렌 | Claude가 승인을 기다림 (풀릴 때까지) |
| 기절 | Claude 작업 실패 |
| 봉투/로고 | 슬랙·카톡·아웃룩 배지 변화 |
| 알람시계 / 헤드폰 | 회의 5분 전 / 회의 중 |
| 도시락 · 가방 · 잠옷 · 파티 모자 | 점심 · 퇴근 · 밤 · 금요일 오후 (시간은 설정) |
| 커피 · 물병 | 오래 일함 · 물 마실 시간 (물병 든 채 클릭 = 마셨다) |
| 배터리 · 불 | 배터리 20% 이하 · CPU 과부하 |
| 우산 · 눈사람 · 선풍기 | 비 · 눈 · 30도 이상 |
| 산타 · 호박 · 호건 · 튜브 | 12월 · 핼러윈 · 설·추석 · 7~8월 |
| 케이크 | 생일(설정) |
| 하트 · 짜증 · 전력질주 · 부활 | 클릭 (상태에 따라 반응이 달라요) |
| 봉고 | 빠르게 타자 치면 같이 쳐요 (기본 꺼짐, 키 내용은 안 읽음) |
| 세수 · 볼 채우기 · 구르기 · 빼꼼 | 심심할 때 무작위 |

## 프라이버시

- 모든 데이터는 이 맥 안에만 있어요. 서버 없음, 계정 없음.
- 밖으로 나가는 요청은 두 가지예요. 날씨(Open-Meteo, 약 1km로 뭉갠 좌표만, 위치 권한 없으면 안 보냄)와 GitHub 릴리스 페이지의 버전 확인(하루 한 번, 설정에서 끌 수 있음). 업데이트 설치 때만 GitHub에서 zip을 받아요.
- 타자 반응은 "눌렸다"는 횟수만 세고 어떤 키인지는 읽지 않아요. 기본은 꺼짐.
- 볼주머니(클립보드)는 메모리에만 두고 앱을 끄면 사라져요. 설정에서 끌 수 있어요.
- 상태 파일은 `~/.hamster.d/`(세션 상태·활동 횟수)뿐이에요.

## 제거

`bash uninstall.sh` — 앱, 상태 파일, Claude Code 훅, 저장된 설정을 지워요. 로그인 항목 목록에 남으면 시스템 설정 → 일반 → 로그인 항목에서 지우세요.

## 문제가 생기면

- **햄스터가 안 보여요** → 노치 맥북이면 ⌘+드래그로 시계 쪽으로. 또는 우클릭이 안 되면 앱을 다시 열어 보세요(두 번 열어도 하나만 떠요).
- **슬랙 알림이 안 와요** → 시스템 설정 → 손쉬운 사용에 Happy Hamzzi가 켜져 있는지, 설정 → 알림에서 앱이 켜져 있는지.
- **회의 반응이 없어요** → 맥 캘린더 앱에 Exchange 일정이 보이는지 먼저 확인.
- **Claude 반응이 없어요** → 설정 → 시스템 → Claude Code가 "훅 연결됨"인지. 연결 후 새로 연 세션부터 반영돼요.

---
© 2026 moon.gipeum · 코드 MIT(LICENSE) · 그림 CC BY-NC 4.0(LICENSE-ART.md)
RM
chmod +x dist/pkg/*.sh; rm -f "dist/HappyHamzzi-$V.zip"; (cd dist/pkg && zip -qr "../HappyHamzzi-$V.zip" .)
# DMG: 앱 + Applications 바로가기 (끌어다 놓기 설치)
rm -rf dist/dmg "dist/HappyHamzzi-$V.dmg"; mkdir -p dist/dmg; cp -R "Happy Hamzzi.app" dist/dmg/; ln -s /Applications dist/dmg/Applications
cp dist/pkg/README.md dist/dmg/; cp dist/pkg/install.sh dist/pkg/uninstall.sh dist/dmg/; cp LICENSE LICENSE-ART.md dist/dmg/
hdiutil create -quiet -volname "Happy Hamzzi" -srcfolder dist/dmg -ov -format UDZO "dist/HappyHamzzi-$V.dmg"; rm -rf dist/dmg
ls -la "dist/HappyHamzzi-$V.zip" "dist/HappyHamzzi-$V.dmg"
