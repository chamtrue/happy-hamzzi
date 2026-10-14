// 메뉴바 햄스터. 그림은 Resources/frames/*.png(art.py 산출물), 앱은 햄스터·소품·장면 3레이어를 나란히 그린다.
import AppKit
import EventKit
import IOKit.ps
import CoreLocation
import SwiftUI
import ServiceManagement

let N = 22
let CORE: Set<String> = ["idle", "working", "sprint", "focus", "done", "surprised", "faint", "sleep", "notify"]  // 22px 안에 들어가는 상태
let EVENT_PRIORITY: [String: Int] = ["faint": 8, "surprised": 7, "battery_low": 6, "meeting_soon": 5, "notify": 4, "cpu": 3, "charging": 3, "done": 2, "wake": 2,
                                     "pet": 1, "grumpy": 1, "sprint": 1, "pet_meeting": 1, "dizzy": 1, "stash": 1, "update": 2]
let EVENT_SECONDS: [String: Double] = ["faint": 6, "surprised": 4, "battery_low": 8, "meeting_soon": 8, "notify": 5, "cpu": 6, "charging": 6, "done": 5, "wake": 4,
                                       "pet": 4, "grumpy": 3, "sprint": 4, "pet_meeting": 4, "dizzy": 3, "stash": 2, "update": 6]
let AMBIENT_ORDER = ["birthday", "break", "water", "lunch", "leave", "night", "friday", "hot", "rain", "snow"]
// 감시 앱: 설정 키 → (Dock 이름 후보, 로고, 표시 이름)
let WATCH_APPS: [(key: String, names: [String], logo: String, label: String)] = [
    ("watchSlack", ["Slack"], "slack", "슬랙"), ("watchKakao", ["KakaoTalk", "카카오톡"], "kakao", "카톡"),
    ("watchOutlook", ["Microsoft Outlook", "Outlook"], "outlook", "아웃룩"), ("watchMail", ["Mail", "메일"], "generic", "메일")]
let REASONS: [String: String] = [
    "idle": "대기 중. 해바라기씨 먹는 중이에요", "working": "Claude가 일하는 중 (쳇바퀴)", "surprised": "Claude가 승인을 기다려요 (사이렌)",
    "faint": "Claude 작업이 실패했어요 (기절)", "done": "Claude 답변이 끝났어요 (체크)", "sleep": "3분 넘게 조용해서 자는 중 (zzz)",
    "meeting_soon": "회의가 5분 안에 시작해요 (알람시계)", "meeting": "회의 중이에요 (헤드폰)", "pet": "쓰다듬어 줘서 좋아해요 (하트)",
    "battery_low": "배터리 20% 이하! (빨간 배터리)", "charging": "충전 시작 (초록 배터리)", "cpu": "CPU 과부하! (불)",
    "lunch": "점심시간 (도시락)", "leave": "퇴근 시간 (가방)", "night": "늦었어요, 잘 시간 (잠옷 모자)", "friday": "금요일 오후! (파티 모자)",
    "break": "오래 일했어요, 좀 쉬어요 (커피)", "grumpy": "자는데 깨웠어요… (짜증)", "update": "새 버전이 있어요! 설정 → 시스템에서 설치 (선물 상자)", "typing": "같이 타자 치는 중 (봉고 햄스터)", "stash": "복사한 걸 볼주머니에 넣었어요", "focus": "집중 세션 중 (쳇바퀴)", "sprint": "응원받아서 전력질주! (쳇바퀴)",
    "pet_meeting": "회의 중이라 조용히 좋아해요 (하트)", "dizzy": "부활! 아직 어지러워요", "wake": "일어났어요, 기지개 (팔 번쩍)", "water": "물 한 잔 마셔요. 클릭하면 마신 걸로 기록 (물병)", "rain": "비 와요 (우산)", "snow": "눈 와요 (눈사람)", "hot": "30도 넘어요 (선풍기)", "birthday": "생일 축하해요! (케이크)"]
func setting(_ key: String, _ def: Int) -> Int { defaults.object(forKey: key) == nil ? def : defaults.integer(forKey: key) }
let IDLE_VARIANTS: [(String, Int)] = [("idle", 4), ("idle_groom", 1), ("idle_cheeks", 1), ("idle_roll", 1), ("idle_peek", 1)]  // 씨 먹기 50%, 나머지 12.5%씩
func isFamilyB(_ k: String) -> Bool { k.count == 2 && k.hasPrefix("S") }  // SB·SC = 디자인 B (키 "S" 레드아이 크림은 A)
func isFamilyC(_ k: String) -> Bool { k.count == 2 && k.hasPrefix("C") }  // CA~CF = 디자인 C (키 "C" 단독은 A)
/// 두 글자 키의 첫 글자가 묶음: S→B(햄찌), C(도톰), D(줄무늬), E(리본). 한 글자 키·모프는 A
func familyOf(_ k: String) -> String { guard k.count == 2, let f = k.first, "SCDE".contains(f) else { return "A" }; return f == "S" ? "B" : String(f) }
let FAMILY_NAMES = [("A", "클래식"), ("B", "햄찌"), ("C", "도톰"), ("D", "줄무늬"), ("E", "리본")]
let ACCESSORY_LABEL: [(String, String)] = [("", "없음"), ("halo", "후광 + 날개"), ("heart", "하트 안기"), ("tomato", "토마토 모자"), ("headphones", "헤드폰"), ("glasses", "빨간 안경"), ("bow", "리본")]
let SEASON_LABEL = ["xmas": "산타 모자", "halloween": "호박 모자", "seollal": "설빔 호건", "chuseok": "추석 호건", "summer": "튜브 타고 둥실"]
/// 오늘의 계절 코스튬. 12/1~26 산타, 10/25~31 호박, 7~8월 튜브, 설날·추석은 당일 -7일 ~ +3일 호건
func seasonToday(_ now: Date = Date()) -> String? {
    let g = Calendar.current, m = g.component(.month, from: now), d = g.component(.day, from: now)
    if m == 12, d <= 26 { return "xmas" }
    if m == 10, d >= 25 { return "halloween" }
    if m == 7 || m == 8 { return "summer" }
    let lunar = Calendar(identifier: .chinese)
    for off in -3...7 {  // now+off 가 명절이면 now 는 명절 -7 ~ +3 일 안
        guard let day = g.date(byAdding: .day, value: off, to: now) else { continue }
        let c = lunar.dateComponents([.month, .day, .isLeapMonth], from: day)
        if c.isLeapMonth == true { continue }
        if c.month == 1, c.day == 1 { return "seollal" }
        if c.month == 8, c.day == 15 { return "chuseok" }
    }
    return nil
}
func flag(_ key: String, _ def: Bool) -> Bool { defaults.object(forKey: key) == nil ? def : defaults.bool(forKey: key) }
/// 3x5 픽셀 숫자. 2배로 그려 22px 칸에 최대 3글자 ("24m", "59s")
let GLYPHS: [Character: [String]] = [
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"], "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "001", "001", "001"], "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"], "m": ["101", "111", "111", "101", "101"], "s": ["111", "100", "111", "001", "111"]]
func digitImage(_ text: String, size: Int = N) -> NSImage {
    let out = NSImage(size: NSSize(width: size, height: size), flipped: true) { _ in
        let glyphs = text.compactMap { GLYPHS[$0] }, w = glyphs.count * 8 - 2, x0 = (size - w) / 2, y0 = (size - 10) / 2
        for (shadow, color) in [(1, NSColor(white: 0.1, alpha: 0.9)), (0, NSColor.white)] {
            color.setFill()
            for (gi, g) in glyphs.enumerated() { for (y, row) in g.enumerated() { for (x, ch) in row.enumerated() where ch == "1" {
                NSRect(x: x0 + gi * 8 + x * 2 + shadow, y: y0 + y * 2 + shadow, width: 2, height: 2).fill()
            } } }
        }
        return true
    }
    out.isTemplate = false; return out
}
/// 레이어 이미지를 가로로 이어 붙인다. scale > 1 이면 픽셀 보간 없이 확대 (미리보기용)
func compose(_ imgs: [NSImage], scale: CGFloat = 1) -> NSImage {
    let w = CGFloat(imgs.count * N) * scale, h = CGFloat(N) * scale
    let out = NSImage(size: NSSize(width: w, height: h), flipped: false) { _ in
        NSGraphicsContext.current?.imageInterpolation = .none
        for (i, im) in imgs.enumerated() { im.draw(in: NSRect(x: CGFloat(i * N) * scale, y: 0, width: CGFloat(N) * scale, height: h)) }
        return true
    }
    out.isTemplate = false; return out
}
let defaults = UserDefaults.standard

// MARK: - 그림
final class Anim { let frames: [NSImage]; let ticks: [Int]; init(frames: [NSImage], ticks: [Int]) { self.frames = frames; self.ticks = ticks } }
/// 음영 변형 공식 — art.py VARIANTS 와 같아야 한다
func variantColor(_ c: (Int, Int, Int), _ v: Int) -> (Int, Int, Int) {
    func mix(_ o: (Int, Int, Int), _ t: Double) -> (Int, Int, Int) { (Int(Double(c.0) + Double(o.0 - c.0) * t), Int(Double(c.1) + Double(o.1 - c.1) * t), Int(Double(c.2) + Double(o.2 - c.2) * t)) }
    switch v {
    case 1: return mix((0, 0, 0), 0.14)
    case 2: return mix((255, 255, 255), 0.10)
    case 3: return mix((255, 255, 255), 0.05)
    case 4: return mix((120, 110, 100), 0.07)
    case 5: return mix((0, 0, 0), 0.30)
    case 6: return (Int(Double(c.0) + Double(255 - c.0) * 0.45), Int(Double(c.1) + Double(255 - c.1) * 0.45), Int(Double(c.2) + Double(255 - c.2) * 0.45))
    case 7: return mix((0, 0, 0), 0.16)
    case 8: return mix((255, 255, 255), 0.3)
    default: return c
    }
}
let ROLE_NAMES = ["cap", "belly", "eye", "nose", "out", "shine"]

/// 템플릿 시트: 8비트 인덱스 이미지 한 장 + 색 테이블(리터럴 또는 역할) + 상태별 오프셋
final class Sheet {
    let size: Int, width: Int, bytes: [UInt8], table: [[String: Any]], offset: [String: Int], ticks: [String: [Int]]
    init?(dir: URL) {
        guard let idx = (try? Data(contentsOf: dir.appendingPathComponent("index.json"))).flatMap({ try? JSONSerialization.jsonObject(with: $0) as? [String: Any] }),
              let rawTable = idx["table"] as? [Any], let offset = idx["offset"] as? [String: Int], let ticks = idx["ticks"] as? [String: [Int]], let size = idx["size"] as? Int,
              let rep = NSImageRep.imageReps(withContentsOf: dir.appendingPathComponent("sheet.png"))?.compactMap({ $0 as? NSBitmapImageRep }).first, let data = rep.bitmapData else { return nil }
        self.size = size; self.table = rawTable.map { $0 as? [String: Any] ?? [:] }; self.offset = offset; self.ticks = ticks; width = rep.pixelsWide  // 0번은 null(투명)
        let spp = rep.samplesPerPixel, row = rep.bytesPerRow; var out = [UInt8](repeating: 0, count: rep.pixelsWide * rep.pixelsHigh)
        for y in 0..<rep.pixelsHigh { for x in 0..<rep.pixelsWide { out[y * rep.pixelsWide + x] = data[y * row + x * spp] } }  // 첫 채널 = 인덱스
        bytes = out
    }
    /// 스킨 팔레트로 색 테이블을 RGBA 로 풀어 둔다
    func colors(pal: [String: [Int]]) -> [(UInt8, UInt8, UInt8, UInt8)] {
        table.map { e in
            if let rgba = e["rgba"] as? [Int] { return (UInt8(rgba[0]), UInt8(rgba[1]), UInt8(rgba[2]), UInt8(rgba[3])) }
            guard let r = e["role"] as? Int, let v = e["variant"] as? Int, r >= 1, r <= ROLE_NAMES.count, let base = pal[ROLE_NAMES[r - 1]], base.count >= 3 else { return (255, 0, 255, 255) }
            let c = variantColor((base[0], base[1], base[2]), v); return (UInt8(clamping: c.0), UInt8(clamping: c.1), UInt8(clamping: c.2), 255)
        }
    }
    func frame(_ n: Int, colors: [(UInt8, UInt8, UInt8, UInt8)]) -> NSImage {
        let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                                   colorSpaceName: .deviceRGB, bytesPerRow: size * 4, bitsPerPixel: 32)!
        let d = rep.bitmapData!
        for y in 0..<size { for x in 0..<size {
            let k = Int(bytes[y * width + n * size + x]), o = (y * size + x) * 4
            if k == 0 || k >= colors.count { d[o] = 0; d[o + 1] = 0; d[o + 2] = 0; d[o + 3] = 0; continue }
            let c = colors[k]; d[o] = c.0; d[o + 1] = c.1; d[o + 2] = c.2; d[o + 3] = c.3
        } }
        let im = NSImage(size: NSSize(width: size, height: size)); im.addRepresentation(rep); return im
    }
}

final class Art {
    let root = (Bundle.main.resourceURL ?? Bundle.main.bundleURL).appendingPathComponent("frames")
    let meta: [String: Any]
    lazy var meta32: [String: Any] = (try? Data(contentsOf: root.appendingPathComponent("n32/meta.json"))).flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Any] } ?? [:]
    var cache: [String: Anim] = [:], sheets: [String: Sheet?] = [:], colorCache: [String: [(UInt8, UInt8, UInt8, UInt8)]] = [:]
    init() {
        let data = try? Data(contentsOf: root.appendingPathComponent("meta.json"))
        meta = data.flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Any] } ?? [:]
        if meta.isEmpty { NSLog("frames/meta.json 을 읽지 못했다: \(root.path)") }
    }
    func m(_ pre: String) -> [String: Any] { pre.isEmpty ? meta : meta32 }
    var skins: [String: Any] { meta["skins"] as? [String: Any] ?? [:] }
    func image(_ name: String) -> NSImage {  // 누락 프레임은 빈 칸으로 그리고 로그만 남긴다
        if let im = NSImage(contentsOf: root.appendingPathComponent(name)) { return im }
        NSLog("프레임 없음: \(name)"); return NSImage(size: NSSize(width: N, height: N))
    }
    func load(_ path: String, _ ticks: [Int]) -> Anim {
        if let a = cache[path] { return a }
        let a = Anim(frames: (0..<ticks.count).map { image("\(path)-\($0).png") }, ticks: ticks); cache[path] = a; return a
    }
    /// 햄스터 프레임: 템플릿 시트에 스킨 팔레트를 입혀 만든다 (22: pre "", variant inline/plain · 32: pre "n32/")
    func hamsterFrames(_ skin: String, _ variant: String, _ state: String, pre: String) -> Anim? {
        let key = "\(pre)\(skin)/\(variant)/\(state)"
        if let a = cache[key] { return a }
        let skinsMeta = m(pre)["skins"] as? [String: Any] ?? [:]
        guard let sk = (skinsMeta[skin] ?? skinsMeta["A"]) as? [String: Any], let tpl = sk["template"] as? String else { return nil }
        let dir = pre.isEmpty ? "\(tpl)/\(variant)" : "n32/\(tpl)"
        if sheets[dir] == nil { sheets[dir] = Sheet(dir: root.appendingPathComponent(dir)) }
        guard let sheet = sheets[dir] ?? nil, let off = sheet.offset[state], let ticks = sheet.ticks[state] else { return nil }
        let ckey = "\(dir)|\(skin)"
        if colorCache[ckey] == nil { colorCache[ckey] = sheet.colors(pal: sk[pre.isEmpty ? "pal22" : "pal32"] as? [String: [Int]] ?? [:]) }
        let a = Anim(frames: (0..<ticks.count).map { sheet.frame(off + $0, colors: colorCache[ckey]!) }, ticks: ticks); cache[key] = a; return a
    }
    func hamster(_ skin: String, _ variant: String, _ state: String) -> Anim? { hamsterFrames(skin, variant, state, pre: "") }
    func hamster32(_ skin: String, _ state: String) -> Anim? { hamsterFrames(skin, "plain", state, pre: "n32/") }
    func prop(_ state: String, _ pre: String = "") -> Anim? { ((m(pre)["props"] as? [String: [Int]])?[state]).map { load("\(pre)props/\(state)", $0) } }
    func scene(_ state: String, _ pre: String = "") -> Anim? { ((m(pre)["scenes"] as? [String: [Int]])?[state]).map { load("\(pre)scene/\(state)", $0) } }
    func logo(_ app: String, _ pre: String = "") -> Anim {
        let name = (meta["logos"] as? [String] ?? []).contains(app) ? app : "generic"
        if let a = cache["\(pre)logo/\(name)"] { return a }
        let a = Anim(frames: [image("\(pre)logo/\(name).png")], ticks: [1]); cache["\(pre)logo/\(name)"] = a; return a
    }
    var costumeCache: [String: NSImage] = [:]
    func overlay(_ name: String, _ pre: String = "") -> NSImage? {
        if let c = costumeCache["\(pre)overlay/" + name] { return c }
        guard let c = NSImage(contentsOf: root.appendingPathComponent("\(pre)overlay/\(name).png")) else { return nil }
        costumeCache["\(pre)overlay/" + name] = c; return c
    }
    func costume(_ name: String, _ pre: String = "") -> NSImage? {
        if let c = costumeCache["\(pre)costume/" + name] { return c }
        guard let c = NSImage(contentsOf: root.appendingPathComponent("\(pre)costume/\(name).png")) else { return nil }
        costumeCache["\(pre)costume/" + name] = c; return c
    }
    var skinNames: [(String, String)] {
        skins.compactMap { k, v in ((v as? [String: Any])?["name"] as? String).map { (k, $0) } }.sorted { $0.0 < $1.0 }
    }
}
struct Player {
    var anim: Anim?; var frame = 0; var tick = 0; var looped = false  // looped: 직전 next() 에서 한 바퀴를 마쳤다
    mutating func set(_ a: Anim?) { if a !== anim { anim = a; frame = 0; tick = 0; looped = false } }
    mutating func next() -> NSImage? {
        guard let a = anim else { return nil }
        let img = a.frames[frame]; tick += 1; looped = false
        if tick >= a.ticks[frame] { tick = 0; frame += 1; if frame >= a.frames.count { frame = 0; looped = true } }
        return img
    }
}

// MARK: - 시스템 센서
enum Sensors {
    static func battery() -> (percent: Int, charging: Bool, onBattery: Bool)? {
        let info = IOPSCopyPowerSourcesInfo().takeRetainedValue()
        for ps in IOPSCopyPowerSourcesList(info).takeRetainedValue() as [CFTypeRef] {
            guard let d = IOPSGetPowerSourceDescription(info, ps).takeUnretainedValue() as? [String: Any] else { continue }
            let cap = d[kIOPSCurrentCapacityKey] as? Int ?? 100
            let charging = d[kIOPSIsChargingKey] as? Bool ?? false
            let onBattery = (d[kIOPSPowerSourceStateKey] as? String) == kIOPSBatteryPowerValue
            return (cap, charging, onBattery)
        }
        return nil
    }
    static var lastCPU: (used: UInt64, total: UInt64) = (0, 0)
    static func cpuPercent() -> Double {
        var count = natural_t(), info: processor_info_array_t? = nil, n = mach_msg_type_number_t()
        guard host_processor_info(mach_host_self(), PROCESSOR_CPU_LOAD_INFO, &count, &info, &n) == KERN_SUCCESS, let info else { return 0 }
        var used: UInt64 = 0, total: UInt64 = 0
        for i in 0..<Int(count) {
            let b = Int(CPU_STATE_MAX) * i
            let u = UInt64(info[b + Int(CPU_STATE_USER)]) + UInt64(info[b + Int(CPU_STATE_SYSTEM)]) + UInt64(info[b + Int(CPU_STATE_NICE)])
            used += u; total += u + UInt64(info[b + Int(CPU_STATE_IDLE)])
        }
        vm_deallocate(mach_task_self_, vm_address_t(bitPattern: info), vm_size_t(n) * vm_size_t(MemoryLayout<integer_t>.size))
        defer { lastCPU = (used, total) }
        let dt = total &- lastCPU.total; return dt == 0 ? 0 : Double(used &- lastCPU.used) / Double(dt) * 100
    }
    static func idleSeconds() -> Double {
        let svc = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("IOHIDSystem"))
        defer { IOObjectRelease(svc) }
        guard let v = IORegistryEntryCreateCFProperty(svc, "HIDIdleTime" as CFString, kCFAllocatorDefault, 0)?.takeRetainedValue() as? UInt64 else { return 0 }
        return Double(v) / 1e9
    }
    // Dock 배지: 이름 → 배지 문자열. 손쉬운 사용 권한 필요
    static func dockBadges() -> [String: String] {
        let src = """
        tell application "System Events" to tell process "Dock" to tell list 1
          set out to ""
          repeat with e in UI elements
            try
              set out to out & (name of e) & "|" & (value of attribute "AXStatusLabel" of e) & linefeed
            end try
          end repeat
          return out
        end tell
        """
        // ponytail: osascript 자식 프로세스. NSAppleScript는 메인 스레드 전용이라 5초마다 UI가 멈춘다
        let p = Process(); p.executableURL = URL(fileURLWithPath: "/usr/bin/osascript"); p.arguments = ["-e", src]
        let pipe = Pipe(); p.standardOutput = pipe; p.standardError = FileHandle.nullDevice
        guard (try? p.run()) != nil else { return [:] }
        DispatchQueue.global().asyncAfter(deadline: .now() + 5) { if p.isRunning { p.terminate() } }  // 자동화 팝업 등으로 멈추면 5초 뒤 정리
        let data = pipe.fileHandleForReading.readDataToEndOfFile(); p.waitUntilExit()
        guard let r = String(data: data, encoding: .utf8) else { return [:] }
        var out: [String: String] = [:]
        for line in r.split(separator: "\n") { let p = line.split(separator: "|", maxSplits: 1); if p.count == 2 { out[String(p[0])] = String(p[1]) } }
        return out
    }
}

// MARK: - 캘린더
final class CalendarWatch {
    let store = EKEventStore(); var events: [EKEvent] = []; var all: [EKEvent] = []; var granted = false
    var requested = false
    func requestAccess() {
        guard !requested else { return }; requested = true
        store.requestFullAccessToEvents { ok, _ in DispatchQueue.main.async { self.granted = ok; if ok { self.refresh() } } }  // 배열은 메인에서만 만진다
    }
    func refresh() {
        guard granted else { return }
        let p = store.predicateForEvents(withStart: Calendar.current.startOfDay(for: Date()), end: Date().addingTimeInterval(86400 * 14), calendars: nil)
        all = store.events(matching: p).filter { $0.status != .canceled }.sorted { $0.startDate < $1.startDate }
        events = all.filter { !$0.isAllDay && $0.availability != .free }
    }
    func inMeeting(_ now: Date) -> Bool { events.contains { $0.startDate <= now && now < $0.endDate } }
    func startingSoon(_ now: Date) -> EKEvent? { events.first { $0.startDate > now && $0.startDate.timeIntervalSince(now) <= 300 } }
}

// MARK: - 날씨 (위치 서비스 + Open-Meteo)
final class Weather: NSObject, CLLocationManagerDelegate {
    let lm = CLLocationManager(); var coord: CLLocationCoordinate2D?; var condition: String? = nil; var lastFetch = Date.distantPast
    var started = false
    override init() { super.init(); lm.delegate = self; lm.desiredAccuracy = kCLLocationAccuracyKilometer }
    func start() { guard !started else { return }; started = true; lm.requestWhenInUseAuthorization(); lm.startUpdatingLocation() }
    func locationManager(_ m: CLLocationManager, didUpdateLocations locs: [CLLocation]) { coord = locs.last?.coordinate; m.stopUpdatingLocation(); fetch() }
    func locationManager(_ m: CLLocationManager, didFailWithError e: Error) { NSLog("위치 실패: \(e.localizedDescription)") }
    func fetch() {
        guard let c = coord, Date().timeIntervalSince(lastFetch) > 1800 else { return }
        lastFetch = Date()
        let lat = (c.latitude * 100).rounded() / 100, lon = (c.longitude * 100).rounded() / 100  // 약 1km 로 뭉개서 보낸다
        guard let url = URL(string: "https://api.open-meteo.com/v1/forecast?latitude=\(lat)&longitude=\(lon)&current=temperature_2m,weather_code") else { return }
        URLSession.shared.dataTask(with: URLRequest(url: url, timeoutInterval: 15)) { [weak self] data, _, _ in
            guard let data, let j = try? JSONSerialization.jsonObject(with: data) as? [String: Any], let cur = j["current"] as? [String: Any],
                  let code = cur["weather_code"] as? Int, let temp = cur["temperature_2m"] as? Double else { return }
            let cond: String? = (71...77).contains(code) || (85...86).contains(code) ? "snow"
                : (51...67).contains(code) || (80...82).contains(code) || code >= 95 ? "rain"
                : temp >= 30 ? "hot" : nil
            DispatchQueue.main.async { self?.condition = cond }
        }.resume()
    }
}

// MARK: - Claude Code 훅 연결
enum ClaudeHooks {
    static let settings = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".claude/settings.json")
    static var claudeInstalled: Bool { FileManager.default.fileExists(atPath: settings.deletingLastPathComponent().path) }
    static let events: [(String, String?, String?)] = [  // (이벤트, matcher, 상태; nil 상태 = 파일 삭제)
        ("UserPromptSubmit", nil, "working"), ("PostToolUse", "*", "working"), ("Stop", nil, "done"), ("StopFailure", nil, "faint"),
        ("PostToolUseFailure", "*", "faint"), ("PermissionRequest", "*", "surprised"), ("SessionEnd", nil, nil)]
    static func command(_ state: String?) -> String {
        // session_id 는 stdin JSON 에서 뽑되 영숫자·-·_ 만 남기고(경로 탈출 방지) 경로는 따옴표로 감싼다
        let sid = "sid=$(grep -o '\"session_id\" *: *\"[^\"]*\"' | head -1 | sed 's/.*\"\\([^\"]*\\)\"$/\\1/' | tr -cd 'A-Za-z0-9_-' | cut -c1-64); mkdir -p ~/.hamster.d; chmod 700 ~/.hamster.d; "
        return sid + (state.map { "echo \($0) > \"$HOME/.hamster.d/${sid:-default}\"" } ?? "rm -f \"$HOME/.hamster.d/${sid:-default}\"")
    }
    static let hookMarker = ".hamster"
    enum HookError: LocalizedError {
        case unreadable, badHooks
        var errorDescription: String? { self == .unreadable ? "settings.json 을 읽을 수 없어요 (JSON 오류). 손으로 고친 뒤 다시 시도해 주세요" : "settings.json 의 hooks 가 예상한 형식이 아니에요" }
    }
    /// 파일이 없으면 빈 설정, 있는데 못 읽으면 에러 — 멀쩡한 설정을 날려 먹지 않기 위해
    static func load() throws -> [String: Any] {
        guard FileManager.default.fileExists(atPath: settings.path) else { return [:] }
        guard let data = try? Data(contentsOf: settings), let d = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { throw HookError.unreadable }
        if let h = d["hooks"], !(h is [String: Any]) { throw HookError.badHooks }
        return d
    }
    static func isHamster(_ entry: [String: Any]) -> Bool {
        ((entry["hooks"] as? [[String: Any]]) ?? []).contains { c in
            let cmd = c["command"] as? String ?? ""
            return cmd.contains(".hamster.d/${sid") || cmd.hasSuffix("> ~/.hamster") || cmd.contains("> ~/.hamster.d/")  // 우리가 만든 명령 형태만
        }
    }
    /// 연결된 이벤트 수 (7이면 완전 연결)
    static var connectedCount: Int {
        let hooks = ((try? load())?["hooks"] as? [String: Any]) ?? [:]
        return events.filter { e in ((hooks[e.0] as? [[String: Any]]) ?? []).contains(where: isHamster) }.count
    }
    static func save(_ d: [String: Any]) throws {
        let bak = settings.appendingPathExtension("bak-hamzzi")
        if FileManager.default.fileExists(atPath: settings.path) { try? FileManager.default.removeItem(at: bak); try FileManager.default.copyItem(at: settings, to: bak) }  // 매번 새 백업
        try FileManager.default.createDirectory(at: settings.deletingLastPathComponent(), withIntermediateDirectories: true)
        try JSONSerialization.data(withJSONObject: d, options: [.prettyPrinted, .withoutEscapingSlashes, .sortedKeys]).write(to: settings, options: .atomic)
    }
    static func connect() throws {
        var d = try load(); var hooks = d["hooks"] as? [String: Any] ?? [:]
        for (ev, matcher, state) in events {
            var list = hooks[ev] as? [[String: Any]] ?? []
            if list.contains(where: isHamster) { continue }
            var entry: [String: Any] = ["hooks": [["type": "command", "command": command(state)]]]
            if let matcher { entry["matcher"] = matcher }
            list.append(entry); hooks[ev] = list
        }
        d["hooks"] = hooks; try save(d)
    }
    static func disconnect() throws {
        var d = try load(); var hooks = d["hooks"] as? [String: Any] ?? [:]
        for (ev, _, _) in events { if let list = hooks[ev] as? [[String: Any]] { hooks[ev] = list.filter { !isHamster($0) } } }
        d["hooks"] = hooks; try save(d)
    }
}

// MARK: - 활동 기록 (날짜별 Claude 답변 완료 수, ~/.hamster.d/activity.json)
final class Activity {
    let file = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".hamster.d/activity.json")
    var counts: [String: Int] = [:]
    static let df: DateFormatter = { let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; return f }()
    init() { counts = (try? Data(contentsOf: file)).flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Int] } ?? [:] }
    func bump() {
        let k = Self.df.string(from: Date()); counts[k, default: 0] += 1
        let cutoff = Self.df.string(from: Date().addingTimeInterval(-120 * 86400)); counts = counts.filter { $0.key >= cutoff }
        try? FileManager.default.createDirectory(at: file.deletingLastPathComponent(), withIntermediateDirectories: true)
        try? JSONSerialization.data(withJSONObject: counts, options: [.sortedKeys]).write(to: file)
    }
    func count(_ d: Date) -> Int { counts[Self.df.string(from: d)] ?? 0 }
}

// MARK: - 업데이트 (GitHub Releases)
final class Updater: ObservableObject {
    static let repo = "chamtrue/happy-hamzzi"
    static let certSHA1 = "5804DEAA43655A2249C7272B52BDE60D212570D6"  // "Happy Hamzzi Dev" 서명 인증서. 바꾸면 기존 설치본이 새 버전을 거부하니 주의
    enum State: Equatable { case idle, checking, upToDate, available(String, URL, String), downloading(Double), installing, error(String) }
    @Published var state: State = .idle
    @Published var lastChecked: Date? = defaults.object(forKey: "updateLastChecked") as? Date
    var current: String { Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0" }
    var available: (String, URL)? { if case .available(let v, let u, _) = state { return (v, u) }; return nil }
    static func newer(_ a: String, than b: String) -> Bool {
        let pa = a.trimmingCharacters(in: CharacterSet(charactersIn: "v")).split(separator: ".").map { Int($0) ?? 0 }, pb = b.split(separator: ".").map { Int($0) ?? 0 }
        for i in 0..<max(pa.count, pb.count) { let x = i < pa.count ? pa[i] : 0, y = i < pb.count ? pb[i] : 0; if x != y { return x > y } }
        return false
    }
    /// API 는 비인증 시간당 60회 제한(사무실 공유 IP 에서 금방 막힘)이라, releases/latest 가 리다이렉트하는 태그 주소를 읽는다
    func check(manual: Bool = false, completion: ((Bool) -> Void)? = nil) {
        if case .downloading = state { return }
        state = .checking
        var req = URLRequest(url: URL(string: "https://github.com/\(Self.repo)/releases/latest")!, timeoutInterval: 15); req.httpMethod = "HEAD"
        URLSession.shared.dataTask(with: req) { _, resp, err in
            DispatchQueue.main.async {
                self.lastChecked = Date(); defaults.set(Date(), forKey: "updateLastChecked")
                guard let final = resp?.url, final.path.contains("/releases/tag/"), let tag = final.pathComponents.last,
                      tag.range(of: "^v?[0-9]+(\\.[0-9]+){0,3}$", options: .regularExpression) != nil else {  // 태그는 버전 형식만 허용
                    self.state = .error(err?.localizedDescription ?? "릴리스 페이지를 못 읽었어요 (\((resp as? HTTPURLResponse)?.statusCode ?? 0))"); completion?(false); return
                }
                let version = tag.trimmingCharacters(in: CharacterSet(charactersIn: "v"))
                let zip = URL(string: "https://github.com/\(Self.repo)/releases/download/\(tag)/HappyHamzzi-\(version).zip")!
                if Self.newer(tag, than: self.current) { self.state = .available(tag, zip, ""); completion?(true) }
                else { self.state = .upToDate; completion?(false) }
            }
        }.resume()
    }
    /// zip 을 받아 풀고 서명·번들 ID 를 확인한 뒤, 앱을 끄고 교체·재실행하는 스크립트를 띄운다
    func install() {
        guard let (version, url) = available else { return }
        guard Bundle.main.bundleIdentifier != nil, Bundle.main.bundleURL.pathExtension == "app" else { state = .error("앱 번들이 아닌 상태라 자동 설치를 할 수 없어요"); return }
        state = .downloading(0)
        let task = URLSession.shared.downloadTask(with: url) { tmp, resp, err in
            DispatchQueue.main.async {
                guard let tmp, (resp as? HTTPURLResponse)?.statusCode == 200 else { self.state = .error(err?.localizedDescription ?? "다운로드 실패 (HTTP \((resp as? HTTPURLResponse)?.statusCode ?? 0))"); return }
                self.state = .installing
                do {
                    let work = FileManager.default.temporaryDirectory.appendingPathComponent("hamzzi-update-\(version)")
                    try? FileManager.default.removeItem(at: work); try FileManager.default.createDirectory(at: work, withIntermediateDirectories: true)
                    let zip = work.appendingPathComponent("update.zip"); try FileManager.default.moveItem(at: tmp, to: zip)
                    let unzip = Process(); unzip.executableURL = URL(fileURLWithPath: "/usr/bin/ditto"); unzip.arguments = ["-x", "-k", zip.path, work.path]; try unzip.run(); unzip.waitUntilExit()
                    guard unzip.terminationStatus == 0 else { throw NSError(domain: "hamzzi", code: 3, userInfo: [NSLocalizedDescriptionKey: "zip 을 풀 수 없어요 (손상됐거나 불완전)"]) }
                    let newApp = work.appendingPathComponent("Happy Hamzzi.app")
                    guard FileManager.default.fileExists(atPath: newApp.path) else { throw NSError(domain: "hamzzi", code: 1, userInfo: [NSLocalizedDescriptionKey: "zip 안에 앱이 없어요"]) }
                    // 서명 검증: 제작자 인증서 지문(SHA-1)과 번들 ID 를 고정 요구사항으로 검사한다. 이름만 같은 다른 인증서는 통과 못 함
                    let req = "identifier \"\(Bundle.main.bundleIdentifier ?? "com.gipeum.happyhamzzi")\" and certificate leaf = H\"\(Self.certSHA1)\""
                    let cs = Process(); cs.executableURL = URL(fileURLWithPath: "/usr/bin/codesign"); cs.arguments = ["--verify", "--deep", "--strict", "-R=\(req)", newApp.path]
                    cs.standardError = FileHandle.nullDevice; cs.standardOutput = FileHandle.nullDevice; try cs.run(); cs.waitUntilExit()
                    guard cs.terminationStatus == 0 else { throw NSError(domain: "hamzzi", code: 2, userInfo: [NSLocalizedDescriptionKey: "서명 확인 실패: 제작자 인증서가 아니에요"]) }
                    // 교체 스크립트: 경로는 문자열에 끼워 넣지 않고 인자로 넘긴다
                    let script = """
                    while kill -0 "$1" 2>/dev/null; do sleep 0.3; done
                    if rm -rf "$3" && mv "$2" "$3"; then xattr -dr com.apple.quarantine "$3" 2>/dev/null; fi
                    open "$3"; rm -rf "$4"
                    """
                    let sh = Process(); sh.executableURL = URL(fileURLWithPath: "/bin/sh")
                    sh.arguments = ["-c", script, "hamzzi-update", String(ProcessInfo.processInfo.processIdentifier), newApp.path, Bundle.main.bundleURL.path, work.path]; try sh.run()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { NSApp.terminate(nil) }
                } catch { self.state = .error(error.localizedDescription) }
            }
        }
        task.resume()
        // 진행률
        Timer.scheduledTimer(withTimeInterval: 0.3, repeats: true) { [weak self] t in
            guard let self, case .downloading = self.state else { t.invalidate(); return }
            let p = task.progress.fractionCompleted; self.state = .downloading(p)
        }
    }
}

// MARK: - 볼주머니 (클립보드 최근 5개, 메모리에만 둔다)
final class Pouch {
    struct Item { let text: String; let at: Date }
    var items: [Item] = []; var lastChange = NSPasteboard.general.changeCount
    /// 새로 복사된 글이 있으면 담고 true
    func poll() -> Bool {
        let pb = NSPasteboard.general
        guard pb.changeCount != lastChange else { return false }
        lastChange = pb.changeCount
        let secret = ["org.nspasteboard.ConcealedType", "org.nspasteboard.TransientType", "com.agilebits.onepassword", "com.apple.passwordmanager"]
        if pb.types?.contains(where: { t in secret.contains { t.rawValue.hasPrefix($0) } }) == true { return false }  // 비밀번호 관리자 등이 숨김 표시한 건 담지 않는다
        guard let s = pb.string(forType: .string)?.trimmingCharacters(in: .whitespacesAndNewlines), !s.isEmpty, s.count < 20_000 else { return false }
        items.removeAll { $0.text == s }; items.insert(Item(text: s, at: Date()), at: 0); items = Array(items.prefix(5))
        return true
    }
    func copy(_ s: String) { let pb = NSPasteboard.general; pb.clearContents(); pb.setString(s, forType: .string); lastChange = pb.changeCount }
    func clear() { items = [] }
}

// MARK: - 일정 팝오버
struct AgendaView: View {
    let granted: Bool
    var focusRemaining: () -> Int? = { nil }
    var focusMinutes = 25
    var toggleFocus: () -> Void = {}
    var pouch: Pouch? = nil
    var activity: Activity? = nil
    @State var tab = "일정"
    @State var copied: String? = nil
    let byDay: [Date: [EKEvent]]      // 하루 단위로 미리 묶어 두고 본문에서는 조회만 한다
    let week: [Date]                  // 오늘부터 7일
    @State var month: Date
    static let cal = Calendar.current
    static var formatters: [String: DateFormatter] = [:]
    var cal: Calendar { Self.cal }
    init(events: [EKEvent], granted: Bool, focusRemaining: @escaping () -> Int? = { nil }, focusMinutes: Int = 25, toggleFocus: @escaping () -> Void = {}, pouch: Pouch? = nil, activity: Activity? = nil, initialTab: String? = nil) {
        self.granted = granted; self.focusRemaining = focusRemaining; self.focusMinutes = focusMinutes; self.toggleFocus = toggleFocus; self.pouch = pouch; self.activity = activity
        if let t = initialTab { _tab = State(initialValue: t) }
        let cal = Self.cal, today = cal.startOfDay(for: Date())
        byDay = Dictionary(grouping: events) { cal.startOfDay(for: $0.startDate) }
        week = (0..<7).compactMap { cal.date(byAdding: .day, value: $0, to: today) }
        _month = State(initialValue: cal.dateInterval(of: .month, for: Date())?.start ?? today)
    }
    var days: [Date?] {  // 월요일 시작 그리드
        let first = month, n = cal.range(of: .day, in: .month, for: first)?.count ?? 30
        let lead = (cal.component(.weekday, from: first) + 5) % 7
        return Array(repeating: nil, count: lead) + (0..<n).map { cal.date(byAdding: .day, value: $0, to: first) }
    }
    func fmt(_ d: Date, _ f: String) -> String {
        let df = Self.formatters[f] ?? { let df = DateFormatter(); df.locale = Locale(identifier: "ko_KR"); df.dateFormat = f; Self.formatters[f] = df; return df }()
        return df.string(from: d)
    }
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            TimelineView(.periodic(from: .now, by: 1)) { _ in
                HStack {
                    if let r = focusRemaining() {
                        Image(systemName: "timer").foregroundStyle(Color.accentColor)
                        Text("집중 중 · \(r / 60):\(String(format: "%02d", r % 60)) 남음").font(.callout.weight(.medium))
                        Spacer(); Button("중단") { toggleFocus() }
                    } else {
                        Image(systemName: "timer").foregroundStyle(.secondary)
                        Text("집중 세션 \(focusMinutes)분").font(.callout)
                        Spacer(); Button("시작") { toggleFocus() }.buttonStyle(.borderedProminent).controlSize(.small)
                    }
                }.padding(8).background(Color.primary.opacity(0.05)).clipShape(RoundedRectangle(cornerRadius: 8))
            }
            Picker("", selection: $tab) {
                Text("일정").tag("일정")
                if pouch != nil { Text("볼주머니").tag("볼주머니") }
                Text("활동").tag("활동")
            }.pickerStyle(.segmented).labelsHidden()
            if tab == "볼주머니", let pouch { pouchView(pouch) } else if tab == "활동" { activityView() } else {
            HStack {
                Text(fmt(month, "yyyy년 M월")).font(.title3.bold())
                Spacer()
                Button { month = cal.date(byAdding: .month, value: -1, to: month) ?? month } label: { Image(systemName: "chevron.left") }.accessibilityLabel("이전 달")
                Button { month = cal.dateInterval(of: .month, for: Date())?.start ?? month } label: { Text("오늘").font(.caption) }
                Button { month = cal.date(byAdding: .month, value: 1, to: month) ?? month } label: { Image(systemName: "chevron.right") }.accessibilityLabel("다음 달")
            }.buttonStyle(.borderless)
            let cols = Array(repeating: GridItem(.flexible(), spacing: 2), count: 7)
            LazyVGrid(columns: cols, spacing: 4) {
                ForEach(["월", "화", "수", "목", "금", "토", "일"], id: \.self) { Text($0).font(.caption2).foregroundStyle(.secondary) }
                ForEach(Array(days.enumerated()), id: \.offset) { _, d in
                    if let d {
                        let today = cal.isDateInToday(d)
                        VStack(spacing: 1) {
                            Text("\(cal.component(.day, from: d))").font(.callout.weight(today ? .bold : .regular))
                                .frame(width: 26, height: 26).background(today ? Color.accentColor : .clear).foregroundStyle(today ? .white : (cal.component(.weekday, from: d) == 1 ? .red : .primary)).clipShape(Circle())
                            Circle().fill(byDay[cal.startOfDay(for: d)] != nil ? Color.secondary : .clear).frame(width: 4, height: 4)
                        }.accessibilityElement(children: .combine).accessibilityLabel("\(cal.component(.day, from: d))일\(byDay[cal.startOfDay(for: d)] != nil ? ", 일정 있음" : "")")
                    } else { Text("") }
                }
            }
            Divider()
            if !granted { Text("캘린더 권한이 없어요. 시스템 설정 → 개인정보 보호 → 캘린더에서 Happy Hamzzi를 켜 주세요.").font(.caption).foregroundStyle(.secondary) }
            ScrollView {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(Array(week.enumerated()), id: \.offset) { i, day in
                        let evs = byDay[day] ?? []
                        HStack { Text(i == 0 ? "오늘" : i == 1 ? "내일" : fmt(day, "EEEE")).font(.caption.bold()).foregroundStyle(i == 0 ? Color.accentColor : .primary); Text(fmt(day, "M월 d일")).font(.caption).foregroundStyle(.secondary) }
                            .padding(.top, i == 0 ? 0 : 6)
                        if evs.isEmpty { Text("일정 없음").font(.caption).foregroundStyle(.secondary).padding(.leading, 4) }
                        ForEach(Array(evs.enumerated()), id: \.offset) { _, e in
                            HStack(alignment: .top, spacing: 8) {
                                VStack(alignment: .trailing, spacing: 0) {
                                    Text(e.isAllDay ? "종일" : fmt(e.startDate, "a h:mm")).font(.caption)
                                    if !e.isAllDay { Text(dur(e)).font(.caption2).foregroundStyle(.secondary) }
                                }.frame(width: 58, alignment: .trailing)
                                RoundedRectangle(cornerRadius: 2).fill(e.calendar.map { Color(cgColor: $0.cgColor) } ?? Color.secondary).frame(width: 3)
                                VStack(alignment: .leading, spacing: 1) {
                                    Text(e.title ?? "").font(.callout).lineLimit(1)
                                    if let l = e.location, !l.isEmpty { Text(l).font(.caption).foregroundStyle(.secondary).lineLimit(1) }
                                }
                                Spacer(minLength: 0)
                            }
                            .padding(6).background(e.startDate <= Date() && Date() < e.endDate ? Color.accentColor.opacity(0.12) : Color.primary.opacity(0.04)).clipShape(RoundedRectangle(cornerRadius: 6))
                        }
                    }
                }
            }
            }
        }.padding(14).frame(width: 340, height: 480, alignment: .top)  // 탭을 바꿔도 팝오버 크기가 안 바뀌므로 높이를 고정한다
    }
    @ViewBuilder func activityView() -> some View {
        let a = activity ?? Activity(), today = cal.startOfDay(for: Date())
        let lead = (cal.component(.weekday, from: today) + 5) % 7  // 월요일 시작
        let start = cal.date(byAdding: .day, value: -(28 + lead), to: today) ?? today  // 5주 격자의 첫 월요일
        let days = (0..<35).compactMap { cal.date(byAdding: .day, value: $0, to: start) }
        let maxC = max(1, days.map(a.count).max() ?? 1)
        let monday = cal.date(byAdding: .day, value: -lead, to: today) ?? today
        let week = days.filter { $0 >= monday && $0 <= today }  // 이번 주 월요일 ~ 오늘
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 16) {
                VStack(alignment: .leading) { Text("오늘").font(.caption).foregroundStyle(.secondary); Text("\(a.count(today))회").font(.title3.bold()) }
                VStack(alignment: .leading) { Text("이번 주").font(.caption).foregroundStyle(.secondary); Text("\(week.map(a.count).reduce(0, +))회").font(.title3.bold()) }
                VStack(alignment: .leading) { Text("5주").font(.caption).foregroundStyle(.secondary); Text("\(days.map(a.count).reduce(0, +))회").font(.title3.bold()) }
                Spacer()
            }
            Text("Claude 답변 완료 횟수").font(.caption).foregroundStyle(.secondary)
            LazyVGrid(columns: Array(repeating: GridItem(.fixed(38), spacing: 4), count: 7), spacing: 4) {
                ForEach(["월", "화", "수", "목", "금", "토", "일"], id: \.self) { Text($0).font(.caption2).foregroundStyle(.secondary) }
                ForEach(Array(days.enumerated()), id: \.offset) { _, d in
                    let n = a.count(d), future = d > today
                    RoundedRectangle(cornerRadius: 4)
                        .fill(future ? Color.clear : n == 0 ? Color.primary.opacity(0.06) : Color.green.opacity(0.25 + 0.75 * Double(n) / Double(maxC)))
                        .overlay(RoundedRectangle(cornerRadius: 4).stroke(cal.isDateInToday(d) ? Color.accentColor : Color.clear, lineWidth: 1.5))
                        .overlay(Text(n > 0 ? "\(n)" : "").font(.caption2).foregroundStyle(n > maxC / 2 ? .white : .primary))
                        .frame(width: 38, height: 26)
                        .help("\(fmt(d, "M/d (E)")) · \(n)회")
                }
            }
            Text("가장 많이 한 날 \(maxC)회 기준으로 진하기를 정해요. 세션별 상태 파일을 쓰는 Claude Code 훅이 연결돼 있어야 세어져요.").font(.caption2).foregroundStyle(.secondary)
            Spacer(minLength: 0)
        }.frame(minHeight: 200)
    }
    func ago(_ d: Date) -> String { let m = Int(Date().timeIntervalSince(d) / 60); return m < 1 ? "방금" : m < 60 ? "\(m)분 전" : "\(m / 60)시간 전" }
    @ViewBuilder func pouchView(_ pouch: Pouch) -> some View {
        TimelineView(.periodic(from: .now, by: 2)) { _ in
            VStack(alignment: .leading, spacing: 6) {
                HStack { Text("최근 복사한 것 \(pouch.items.count)개 · 클릭하면 다시 복사").font(.caption).foregroundStyle(.secondary); Spacer(); if !pouch.items.isEmpty { Button("비우기") { pouch.clear() }.controlSize(.small) } }
                if pouch.items.isEmpty { Text("아직 비어 있어요. 글을 복사하면 햄스터가 볼주머니에 넣어 둬요.").font(.caption).foregroundStyle(.secondary).padding(.vertical, 20) }
                ForEach(Array(pouch.items.enumerated()), id: \.offset) { i, it in
                    Button {
                        pouch.copy(it.text); copied = it.text
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { if copied == it.text { copied = nil } }
                    } label: {
                        HStack(alignment: .top, spacing: 8) {
                            Text("\(i + 1)").font(.caption2.monospacedDigit()).foregroundStyle(.secondary).frame(width: 12)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(it.text.replacingOccurrences(of: "\n", with: " ")).font(.callout).lineLimit(2).multilineTextAlignment(.leading)
                                Text(copied == it.text ? "복사됨 ✓" : "\(ago(it.at)) · \(it.text.count)자").font(.caption2).foregroundStyle(copied == it.text ? Color.accentColor : .secondary)
                            }
                            Spacer(minLength: 0)
                        }.padding(8).frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.primary.opacity(copied == it.text ? 0.1 : 0.04)).clipShape(RoundedRectangle(cornerRadius: 6))
                    }.buttonStyle(.plain)
                }
                Spacer(minLength: 0)
            }.frame(minHeight: 200)
        }
    }
    func dur(_ e: EKEvent) -> String { let m = Int(e.endDate.timeIntervalSince(e.startDate) / 60); return m % 60 == 0 ? "\(m / 60)h" : m < 60 ? "\(m)m" : "\(m / 60)h \(m % 60)m" }
}

// MARK: - 설정 창 (탭: 모습 · 하루 리듬 · 건강 · 알림 · 시스템)
struct PermissionStatus { let calendar: Bool; let location: Bool; let accessibility: Bool }
struct SettingsView: View {
    let art: Art; let preview: (String, String) -> NSImage; let status: () -> PermissionStatus; let updater: Updater; let request: (String) -> Void
    @State var tab: String
    init(initialTab: String? = nil, updater: Updater, art: Art, preview: @escaping (String, String) -> NSImage, status: @escaping () -> PermissionStatus, request: @escaping (String) -> Void = { _ in }) {
        self.art = art; self.preview = preview; self.status = status; self.updater = updater; self.request = request
        _tab = State(initialValue: initialTab ?? ProcessInfo.processInfo.environment["HAMSTER_TEST_SETTINGS"].flatMap { $0.count > 1 ? $0 : nil } ?? "모습")
    }
    var body: some View {
        TabView(selection: $tab) {
            AppearanceTab(art: art, preview: preview).tabItem { Label("모습", systemImage: "paintpalette") }.tag("모습")
            RhythmTab().tabItem { Label("하루 리듬", systemImage: "sun.horizon") }.tag("하루 리듬")
            HealthTab().tabItem { Label("건강", systemImage: "heart") }.tag("건강")
            NotifyTab(art: art).tabItem { Label("알림", systemImage: "bell") }.tag("알림")
            SystemTab(status: status, request: request, updater: updater).tabItem { Label("시스템", systemImage: "gearshape") }.tag("시스템")
        }.padding(.top, 6).frame(width: 520, height: 520)
    }
}
struct AppearanceTab: View {
    @AppStorage("skin") var skin = "SC"
    @AppStorage("layout") var layout = "A"
    @AppStorage("typingEnabled") var typing = false
    @AppStorage("accessory") var accessory = ""
    @State var family = familyOf(UserDefaults.standard.string(forKey: "skin") ?? "SC")
    let art: Art; let preview: (String, String) -> NSImage
    var familySkins: [(String, String)] { art.skinNames.filter { familyOf($0.0) == family } }
    var body: some View {
        Form {
            Section {
                Picker("디자인", selection: $family) { ForEach(FAMILY_NAMES, id: \.0) { f, n in Text("\(f) \(n)").tag(f) } }.pickerStyle(.segmented)
                Text(family == "B" ? "참고 그림 그대로의 얼굴을 유지해요. 표정은 바뀌지 않고 소품만 바뀌어요." : family == "C" ? "소품과 같은 화풍의 도톰한 햄찌. 상태마다 포즈가 바뀌어요. 노치 모드에서 가장 잘 보여요." : family == "D" || family == "E" ? "참고 그림을 픽셀 그대로 옮기고 색만 바꿨어요. 상태마다 눈·입 표정이 바뀌어요. (\(familySkins.count)종)" : "표정·음영이 바뀌는 기본 디자인. 색 24종 + 패턴 5종 모프 포함.").font(.caption).foregroundStyle(.secondary)
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 6), count: 6), spacing: 6) {
                    ForEach(familySkins, id: \.0) { k, name in
                        VStack(spacing: 4) {
                            Image(nsImage: art.hamster32(k, "idle")?.frames.first ?? art.hamster(k, "plain", "idle")?.frames.first ?? NSImage()).interpolation(.none).resizable().frame(width: 48, height: 48)  // 설정 타일은 32px 그림
                            Text(name).font(.caption2).foregroundStyle(skin == k ? .primary : .secondary).lineLimit(1)
                        }
                        .padding(4).frame(maxWidth: .infinity)
                        .background(RoundedRectangle(cornerRadius: 8).fill(skin == k ? Color.accentColor.opacity(0.15) : Color.clear))
                        .overlay(RoundedRectangle(cornerRadius: 8).stroke(skin == k ? Color.accentColor : Color.clear, lineWidth: 2))
                        .contentShape(Rectangle()).onTapGesture { skin = k }
                        .accessibilityAddTraits(skin == k ? [.isButton, .isSelected] : .isButton).accessibilityLabel("스킨 \(name)")
                    }
                }
            }
            Section {
                Picker("액세서리", selection: $accessory) { ForEach(ACCESSORY_LABEL, id: \.0) { Text($0.1).tag($0.0) } }
            } header: { Text("액세서리") } footer: { Text("항상 쓰고 있어요. 계절 코스튬보다 우선하고, 쳇바퀴·구르기·빼꼼 중엔 잠깐 벗어요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
            Section {
                Toggle("타자 반응 (봉고 햄스터)", isOn: $typing)
            } header: { Text("반응") } footer: { Text("키를 누를 때마다 귀가 쫑긋하고, 2초에 8타 넘게 치면 햄스터가 키보드를 꺼내 같이 쳐요. 어떤 키인지는 읽지 않고 눌린 횟수만 세요. 손쉬운 사용 권한이 필요해요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
            Section("레이아웃") {
                ForEach([("S", "22px 단독", "핵심 7개 상태만. 그 밖의 상태는 그 순간만 44px로 넓어져요"),
                         ("A", "44px 햄스터 + 소품", "추천. 소품이 햄스터와 같은 크기로 보여요"),
                         ("B", "66px 햄스터 + 소품 + 장면", "장면 칸까지. 노치 맥북에서는 자리가 모자랄 수 있어요"),
                         ("N", "노치 모드 (32px)", NotchTray.notchScreen == nil ? "노치 맥북 화면에서만 켜져요. 지금은 노치 화면이 없어 44px로 보여요" : "노치 아래 검은 트레이에 32px 햄스터. 프로토타입: 스킨은 클래식 2톤만")], id: \.0) { k, name, note in
                    HStack(spacing: 12) {
                        Image(nsImage: preview(skin, k)).interpolation(.none).padding(.horizontal, 6).padding(.vertical, 4)
                            .background(Color(white: 0.23)).clipShape(RoundedRectangle(cornerRadius: 6)).frame(width: 148, alignment: .leading)
                        VStack(alignment: .leading, spacing: 2) { Text(name); Text(note).font(.caption).foregroundStyle(.secondary) }
                        Spacer()
                        Image(systemName: layout == k ? "checkmark.circle.fill" : "circle").foregroundStyle(layout == k ? Color.accentColor : .secondary)
                    }.contentShape(Rectangle()).onTapGesture { layout = k }
                }
            }
        }.formStyle(.grouped)
    }
}
struct RhythmTab: View {
    @AppStorage("lunchHour") var lunchHour = 12
    @AppStorage("leaveHour") var leaveHour = 19
    @AppStorage("nightHour") var nightHour = 23
    @AppStorage("fridayParty") var fridayParty = true
    @AppStorage("seasonEnabled") var seasonEnabled = true
    @AppStorage("birthday") var birthday = ""
    var bMonth: Int { Int(birthday.split(separator: "/").first ?? "") ?? 1 }
    var bDay: Int { birthday.split(separator: "/").count == 2 ? Int(birthday.split(separator: "/")[1]) ?? 1 : 1 }
    func daysIn(_ m: Int) -> Int { [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1] }
    var body: some View {
        Form {
            Section("시간대") {
                Stepper(value: $lunchHour, in: 10...15) { LabeledContent("점심", value: "\(lunchHour)시 ~ \(lunchHour + 1)시 · 도시락") }
                Stepper(value: $leaveHour, in: 16...22) { LabeledContent("퇴근", value: "\(leaveHour)시 이후 · 가방") }
                Stepper(value: $nightHour, in: 21...24) { LabeledContent("잘 시간", value: "\(nightHour)시 이후 · 잠옷 모자") }
            }
            Section("특별한 날") {
                Toggle("금요일 오후 파티 모자 (15시 ~ 퇴근)", isOn: $fridayParty)
                Toggle("계절 코스튬 (12월 산타 · 핼러윈 호박 · 설과 추석 호건)", isOn: $seasonEnabled)
                Toggle("생일에 케이크 (종일)", isOn: Binding(get: { !birthday.isEmpty }, set: { birthday = $0 ? "\(bMonth)/\(bDay)" : "" }))
                if !birthday.isEmpty {
                    HStack {
                        Picker("월", selection: Binding(get: { bMonth }, set: { birthday = "\($0)/\(min(bDay, daysIn($0)))" })) { ForEach(1...12, id: \.self) { Text("\($0)월").tag($0) } }
                        Picker("일", selection: Binding(get: { bDay }, set: { birthday = "\(bMonth)/\($0)" })) { ForEach(1...daysIn(bMonth), id: \.self) { Text("\($0)일").tag($0) } }
                    }
                }
            }
        }.formStyle(.grouped)
    }
}
struct HealthTab: View {
    @AppStorage("breakEnabled") var breakEnabled = true
    @AppStorage("breakMinutes") var breakMinutes = 50
    @AppStorage("waterEnabled") var waterEnabled = true
    @AppStorage("waterMinutes") var waterMinutes = 90
    @AppStorage("focusMinutes") var focusMinutes = 25
    @AppStorage("focusQuiet") var focusQuiet = true
    var body: some View {
        Form {
            Section {
                Stepper(value: $focusMinutes, in: 15...90, step: 5) { LabeledContent("세션 길이", value: "\(focusMinutes)분") }
                Toggle("집중 중엔 슬랙·카톡 봉투 안 띄우기", isOn: $focusQuiet)
            } header: { Text("집중 세션") } footer: { Text("일정 팝오버나 우클릭 메뉴에서 시작해요. 쳇바퀴를 돌고 소품 칸에 남은 시간이 보이다가 끝나면 체크.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
            Section {
                Toggle("연속 사용 알림 (커피)", isOn: $breakEnabled)
                if breakEnabled { Stepper(value: $breakMinutes, in: 25...120, step: 5) { LabeledContent("쉬지 않고 쓴 지", value: "\(breakMinutes)분") } }
            } header: { Text("쉬기") } footer: { Text("5분 이상 자리를 비우면 카운트가 처음부터 시작해요. 10분 동안 커피를 들고 있어요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
            Section {
                Toggle("물 마시기 알림 (물병)", isOn: $waterEnabled)
                if waterEnabled { Stepper(value: $waterMinutes, in: 30...180, step: 15) { LabeledContent("간격", value: "\(waterMinutes)분") } }
            } header: { Text("물") } footer: { Text("물병을 든 동안 햄스터를 클릭하면 마신 것으로 기록하고 다음 간격을 다시 세요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
        }.formStyle(.grouped)
    }
}
struct NotifyTab: View {
    @AppStorage("watchSlack") var watchSlack = true
    @AppStorage("watchKakao") var watchKakao = true
    @AppStorage("watchOutlook") var watchOutlook = false
    @AppStorage("watchMail") var watchMail = false
    let art: Art
    func row(_ title: String, _ logo: String, _ on: Binding<Bool>) -> some View {
        Toggle(isOn: on) { HStack(spacing: 8) { Image(nsImage: art.logo(logo).frames[0]).interpolation(.none).resizable().frame(width: 22, height: 22); Text(title) } }
    }
    var body: some View {
        Form {
            Section {
                row("슬랙", "slack", $watchSlack); row("카카오톡", "kakao", $watchKakao); row("아웃룩", "outlook", $watchOutlook); row("메일", "generic", $watchMail)
            } header: { Text("Dock 배지가 바뀌면 봉투를 들어요") } footer: {
                Text(AXIsProcessTrusted() ? "손쉬운 사용 권한이 있어 배지를 읽고 있어요." : "손쉬운 사용 권한이 없어 배지를 못 읽어요. 시스템 탭에서 켜 주세요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading)
            }
        }.formStyle(.grouped)
    }
}
struct SystemTab: View {
    let status: () -> PermissionStatus
    var request: (String) -> Void = { _ in }
    @ObservedObject var updater: Updater
    @AppStorage("autoUpdateCheck") var autoCheck = true
    @State var login = SMAppService.mainApp.status == .enabled
    @AppStorage("clipboardEnabled") var clipboard = true
    @State var hookCount = ClaudeHooks.connectedCount
    @State var hookError: String? = nil
    @State var st = PermissionStatus(calendar: false, location: false, accessibility: false)
    func open(_ pane: String) { if let u = URL(string: "x-apple.systempreferences:com.apple.preference.security?\(pane)") { NSWorkspace.shared.open(u) } }
    func fmtDate(_ d: Date) -> String { let f = DateFormatter(); f.locale = Locale(identifier: "ko_KR"); f.dateFormat = "M/d a h:mm"; return f.string(from: d) }
    func perm(_ name: String, _ what: String, _ ok: Bool, _ pane: String) -> some View {
        HStack {
            Image(systemName: ok ? "checkmark.circle.fill" : "exclamationmark.circle").foregroundStyle(ok ? .green : .orange)
            VStack(alignment: .leading, spacing: 1) { Text(name); Text(what).font(.caption).foregroundStyle(.secondary) }
            Spacer()
            if !ok { Button("허용") { request(pane) } }
        }
    }
    var body: some View {
        Form {
            Section("실행") {
                Toggle("로그인 시 자동 실행", isOn: $login).onChange(of: login) { _, on in
                    do { if on { try SMAppService.mainApp.register() } else { try SMAppService.mainApp.unregister() } } catch { NSLog("로그인 항목 실패: \(error)") }
                    login = SMAppService.mainApp.status == .enabled
                }
            }
            Section("권한") {
                perm("캘린더", "회의 5분 전 · 회의 중 · 일정 팝오버", st.calendar, "calendar")
                perm("위치", "날씨 (비 · 눈 · 더위)", st.location, "location")
                perm("손쉬운 사용", "Dock 배지 읽기 (슬랙 · 카톡 · 아웃룩 알림)", st.accessibility, "accessibility")
            }
            Section {
                if !ClaudeHooks.claudeInstalled {
                    Text("이 맥에 Claude Code가 없어요 (~/.claude 없음). 설치 후 다시 열면 연결 버튼이 보여요.").font(.caption).foregroundStyle(.secondary)
                } else {
                    HStack {
                        Image(systemName: hookCount == ClaudeHooks.events.count ? "checkmark.circle.fill" : "exclamationmark.circle").foregroundStyle(hookCount == ClaudeHooks.events.count ? .green : .orange)
                        VStack(alignment: .leading, spacing: 1) {
                            Text(hookCount == ClaudeHooks.events.count ? "훅 연결됨" : hookCount == 0 ? "연결 안 됨" : "일부만 연결됨 (\(hookCount)/\(ClaudeHooks.events.count))")
                            Text("작업 중 쳇바퀴 · 완료 체크 · 승인 대기 사이렌 · 에러 기절 · 활동 잔디").font(.caption).foregroundStyle(.secondary)
                        }
                        Spacer()
                        if hookCount < ClaudeHooks.events.count { Button("연결") { do { try ClaudeHooks.connect() } catch { hookError = "\(error)" }; hookCount = ClaudeHooks.connectedCount } }
                        else { Button("해제") { do { try ClaudeHooks.disconnect() } catch { hookError = "\(error)" }; hookCount = ClaudeHooks.connectedCount } }
                    }
                    if let e = hookError { Text(e).font(.caption2).foregroundStyle(.red) }
                }
            } header: { Text("Claude Code") } footer: { Text("~/.claude/settings.json 의 hooks 에 7개 항목을 넣어요. 바꾸기 전 settings.json.bak-hamzzi 로 백업하고, 다른 훅은 건드리지 않아요. 연결 후 새로 여는 Claude 세션부터 반영돼요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
            Section {
                Toggle("볼주머니: 최근 복사한 글 5개 기억", isOn: $clipboard)
            } header: { Text("클립보드") } footer: { Text("메모리에만 두고 파일로 저장하지 않아요. 앱을 끄면 사라져요. 일정 팝오버의 볼주머니 탭에서 다시 복사할 수 있어요.").frame(maxWidth: .infinity, alignment: .leading).multilineTextAlignment(.leading) }
            Section {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("현재 \(updater.current)").font(.callout)
                        Group {
                            switch updater.state {
                            case .idle: Text(updater.lastChecked.map { "마지막 확인 \(fmtDate($0))" } ?? "아직 확인 안 함")
                            case .checking: Text("확인 중…")
                            case .upToDate: Text("최신 버전이에요")
                            case .available(let v, _, _): Text("새 버전 \(v) 있음").foregroundStyle(Color.accentColor)
                            case .downloading(let p): Text("내려받는 중 \(Int(p * 100))%")
                            case .installing: Text("설치 중… 앱이 잠시 꺼졌다 켜져요")
                            case .error(let e): Text("실패: \(e)").foregroundStyle(.red)
                            }
                        }.font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    if case .available = updater.state { Button("설치") { updater.install() }.buttonStyle(.borderedProminent) }
                    Button("지금 확인") { updater.check(manual: true) }.disabled({ if case .checking = updater.state { return true }; if case .downloading = updater.state { return true }; return false }())
                }
                Toggle("하루 한 번 자동 확인", isOn: $autoCheck)
            } header: { Text("업데이트") } footer: { Text("GitHub Releases(\(Updater.repo))에서 최신 버전을 확인해요. 설치는 zip을 받아 서명·번들 ID를 확인한 뒤 앱을 교체하고 다시 열어요. 새 버전이 있으면 햄스터가 선물 상자를 들고, 우클릭 메뉴에도 설치 항목이 떠요.") }
            Section("정보") {
                LabeledContent("버전", value: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "-")
                LabeledContent("상태 파일", value: "~/.hamster.d (Claude Code 훅)")
                LabeledContent("저작권", value: "© 2026 moon.gipeum")
            }
        }.formStyle(.grouped).onAppear { st = status() }
    }
}

// MARK: - 노치 트레이 (노치 아래 검은 영역에 사는 모드)
let TRAY_H: CGFloat = 34
final class NotchView: NSView {
    weak var pet: Pet?
    var image: NSImage? { didSet { needsDisplay = true } }
    var hovering = false
    override func updateTrackingAreas() {
        super.updateTrackingAreas(); trackingAreas.forEach(removeTrackingArea)
        addTrackingArea(NSTrackingArea(rect: bounds, options: [.mouseEnteredAndExited, .activeAlways, .inVisibleRect], owner: self, userInfo: nil))
    }
    override func mouseEntered(with e: NSEvent) { hovering = true; pet?.lastDrawn = [] }
    override func mouseExited(with e: NSEvent) { hovering = false; pet?.lastDrawn = [] }
    override func draw(_ dirty: NSRect) {
        let b = bounds, r: CGFloat = 12, p = NSBezierPath()
        p.move(to: NSPoint(x: b.minX, y: b.maxY)); p.line(to: NSPoint(x: b.maxX, y: b.maxY)); p.line(to: NSPoint(x: b.maxX, y: b.minY + r))
        p.appendArc(withCenter: NSPoint(x: b.maxX - r, y: b.minY + r), radius: r, startAngle: 0, endAngle: -90, clockwise: true)
        p.line(to: NSPoint(x: b.minX + r, y: b.minY))
        p.appendArc(withCenter: NSPoint(x: b.minX + r, y: b.minY + r), radius: r, startAngle: -90, endAngle: -180, clockwise: true)
        p.close(); NSColor.black.setFill(); p.fill()
        NSGraphicsContext.current?.imageInterpolation = .none
        if let im = image { let s = im.size; im.draw(in: NSRect(x: ((b.width - s.width) / 2).rounded(), y: ((TRAY_H - s.height) / 2).rounded(), width: s.width, height: s.height)) }  // 아래 TRAY_H 가운데
    }
    override func mouseDown(with e: NSEvent) { pet?.handleClick(agendaOnly: false, anchor: self) }
    override func rightMouseDown(with e: NSEvent) { pet?.showMenu(anchor: self) }
}
final class NotchTray {
    let panel: NSPanel, view = NotchView()
    init(pet: Pet) {
        panel = NSPanel(contentRect: NSRect(x: 0, y: 0, width: 200, height: 40), styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.isOpaque = false; panel.backgroundColor = .clear; panel.hasShadow = false; panel.level = .statusBar
        panel.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary]; panel.isReleasedWhenClosed = false
        view.pet = pet; panel.contentView = view
    }
    static var notchScreen: NSScreen? { NSScreen.screens.first { $0.safeAreaInsets.top > 0 } }
    /// 노치 바로 아래로 TRAY_H 내려온다. 폭은 노치 폭과 내용 폭 중 큰 쪽
    func place(contentWidth: CGFloat) -> Bool {
        guard let sc = Self.notchScreen, let l = sc.auxiliaryTopLeftArea, let r = sc.auxiliaryTopRightArea else { panel.orderOut(nil); return false }
        let inset = sc.safeAreaInsets.top, notchW = sc.frame.width - l.width - r.width
        let w = max(notchW, contentWidth + 24), h = TRAY_H + inset  // 노치 영역까지 위로 늘려 이음새를 없앤다
        let f = NSRect(x: (sc.frame.midX - w / 2).rounded(), y: sc.frame.maxY - h, width: w, height: h)
        if panel.frame != f { panel.setFrame(f, display: true) }
        if !panel.isVisible { panel.orderFrontRegardless() }
        return true
    }
}

// MARK: - 첫 실행 안내 (튜토리얼 3쪽 + 권한 설정 1쪽)
struct OnboardingView: View {
    let art: Art; let skin: String
    let status: () -> PermissionStatus
    let openSettings: () -> Void
    let close: () -> Void
    let request: (String) -> Void
    @State var page: Int
    @State var st = PermissionStatus(calendar: false, location: false, accessibility: false)
    @State var hooks = ClaudeHooks.connectedCount
    init(art: Art, skin: String, page: Int = 0, status: @escaping () -> PermissionStatus, openSettings: @escaping () -> Void, close: @escaping () -> Void, request: @escaping (String) -> Void = { _ in }) {
        self.art = art; self.skin = skin; self.status = status; self.openSettings = openSettings; self.close = close; self.request = request; _page = State(initialValue: page)
    }
    func pane(_ p: String) { if let u = URL(string: "x-apple.systempreferences:com.apple.preference.security?\(p)") { NSWorkspace.shared.open(u) } }
    func anim(_ a: Anim?, size: CGFloat) -> some View {  // 프레임을 실제 속도로 돌린다
        TimelineView(.periodic(from: .now, by: 0.12)) { ctx in
            let frames = a?.frames ?? [], ticks = a?.ticks ?? []
            let total = max(1, ticks.reduce(0, +)); var t = Int(ctx.date.timeIntervalSinceReferenceDate / 0.12) % total; var idx = 0
            for (i, n) in ticks.enumerated() { if t < n { idx = i; break }; t -= n }
            return Image(nsImage: frames.isEmpty ? NSImage() : frames[min(idx, frames.count - 1)]).interpolation(.none).resizable().frame(width: size, height: size)
        }
    }
    func cell(_ state: String, _ title: String, _ sub: String) -> some View {
        VStack(spacing: 4) {
            HStack(spacing: 2) { anim(art.hamster32(skin, state), size: 56); anim(art.prop(state, "n32/"), size: 56) }
                .padding(6).background(Color.black).clipShape(RoundedRectangle(cornerRadius: 8))
            Text(title).font(.caption.weight(.medium)); Text(sub).font(.caption2).foregroundStyle(.secondary).lineLimit(1)
        }.frame(maxWidth: .infinity)
    }
    func how(_ symbol: String, _ title: String, _ body: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: symbol).font(.title3).foregroundStyle(Color.accentColor).frame(width: 26)
            VStack(alignment: .leading, spacing: 2) { Text(title).font(.callout.weight(.medium)); Text(body).font(.caption).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true) }
        }
    }
    func row(_ n: Int, _ title: String, _ body: String, ok: Bool?, action: String? = nil, _ act: @escaping () -> Void = {}) -> some View {
        HStack(alignment: .top, spacing: 10) {
            ZStack { Circle().fill(ok == true ? Color.green : Color.accentColor.opacity(0.15)).frame(width: 22, height: 22); Text(ok == true ? "✓" : "\(n)").font(.caption.bold()).foregroundStyle(ok == true ? .white : Color.accentColor) }
            VStack(alignment: .leading, spacing: 2) { Text(title).font(.callout.weight(.medium)); Text(body).font(.caption).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true) }
            Spacer()
            if let action, ok != true { Button(action) { act() }.controlSize(.small) }
        }
    }
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Group {
                switch page {
                case 0:
                    VStack(spacing: 14) {
                        anim(art.hamster32(skin, "idle"), size: 128).padding(16).background(Color.black).clipShape(RoundedRectangle(cornerRadius: 16))
                        Text("안녕, 햄찌예요").font(.title2.bold())
                        VStack(alignment: .leading, spacing: 6) {
                            how("menubar.rectangle", "메뉴바(또는 노치 아래)에 살아요", "일하는 동안 늘 보이는 자리에서 작게 움직여요. 자리는 ⌘+드래그로 옮길 수 있어요.")
                            how("sparkles", "내 하루에 반응해요", "Claude Code 작업, 회의, 슬랙·카톡 알림, 점심·퇴근 시간, 날씨, 계절까지. 표정과 소품이 바뀌어요.")
                            how("paintpalette", "44종 중에 골라요", "클래식 34종(색·패턴 모프)과 햄찌 10종. 액세서리와 계절 코스튬도 있어요.")
                        }
                    }.frame(maxWidth: .infinity)
                case 1:
                    VStack(alignment: .leading, spacing: 10) {
                        Text("햄찌가 하는 것").font(.title2.bold())
                        Text("상태마다 햄스터 표정과 옆 소품이 달라져요. 마우스를 올리면 지금 왜 그런지 툴팁으로 알려줘요.").font(.caption).foregroundStyle(.secondary)
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 10) {
                            cell("working", "쳇바퀴", "Claude가 일하는 중"); cell("done", "체크", "답변 끝"); cell("surprised", "사이렌", "승인 기다리는 중"); cell("notify", "봉투", "슬랙·카톡 알림")
                            cell("meeting", "헤드폰", "회의 중"); cell("lunch", "도시락", "점심시간"); cell("break", "커피", "오래 일했어요"); cell("pet", "하트", "쓰다듬기")
                        }
                    }
                case 2:
                    VStack(alignment: .leading, spacing: 10) {
                        Text("조작법").font(.title2.bold())
                        how("cursorarrow.click", "좌클릭", "쓰다듬기 + 팝오버. 팝오버엔 달력과 7일 일정, 볼주머니(최근 복사한 글 5개), 활동 잔디, 집중 세션 시작 버튼이 있어요.")
                        how("cursorarrow.click.2", "우클릭", "지금 상태 설명, 다음 회의, 스킨·레이아웃·상태 테스트, 설정(⌘,).")
                        how("rectangle.split.3x1", "레이아웃", "메뉴바 22px 단독 · 44px 햄스터+소품 · 66px +장면 · 노치 모드(노치 아래 32px). 노치 맥북이면 노치 모드를 권해요.")
                        how("slider.horizontal.3", "설정", "모습(스킨·액세서리·타자 반응) · 하루 리듬(점심·퇴근·잘 시간·생일) · 건강(쉬기·물·집중) · 알림(감시 앱) · 시스템(권한·Claude 훅·업데이트).")
                        how("keyboard", "봉고 햄스터", "설정에서 켜면 키를 칠 때 귀가 쫑긋하고 빠르게 치면 같이 쳐요. 어떤 키인지는 읽지 않아요. 기본은 꺼짐.")
                    }
                default:
                    VStack(alignment: .leading, spacing: 10) {
                        Text("권한 설정").font(.title2.bold())
                        Text("필요한 것만, 원하는 순서로 켜면 돼요. 안 켜도 햄스터는 돌아가요. 나중에 설정 → 시스템에서도 할 수 있어요.").font(.caption).foregroundStyle(.secondary)
                        row(1, "캘린더", "회의 5분 전 알람시계, 회의 중 헤드폰, 좌클릭 일정 보기. 아웃룩 일정은 시스템 설정 → 인터넷 계정 → Exchange 추가(캘린더만 켜기)로 맥 캘린더에 들어와요.", ok: st.calendar, action: "허용") { request("calendar") }
                        row(2, "손쉬운 사용", "Dock 배지로 슬랙·카톡·아웃룩 알림을 알아채요. 타자 반응(봉고)도 이 권한을 써요. 키 내용은 읽지 않아요.", ok: st.accessibility, action: "허용") { request("accessibility") }
                        row(3, "위치", "현재 위치 날씨로 비·눈·더위 코스튬. 30분마다 한 번, 약 1km 로 뭉갠 좌표만 보내요.", ok: st.location, action: "허용") { request("location") }
                        row(4, "Claude Code 훅", ClaudeHooks.claudeInstalled ? "Claude가 일하면 쳇바퀴, 끝나면 체크, 승인 대기면 사이렌. ~/.claude/settings.json에 훅 7개를 넣어요(백업 후)." : "이 맥엔 Claude Code가 없어요. 나중에 설치하면 설정 → 시스템에서 연결할 수 있어요.",
                            ok: ClaudeHooks.claudeInstalled ? hooks == ClaudeHooks.events.count : nil, action: ClaudeHooks.claudeInstalled ? "연결" : nil) { try? ClaudeHooks.connect(); hooks = ClaudeHooks.connectedCount }
                    }
                }
            }.frame(maxWidth: .infinity, minHeight: 330, alignment: .top)
            Divider()
            HStack {
                HStack(spacing: 5) { ForEach(0..<4, id: \.self) { i in Circle().fill(i == page ? Color.accentColor : Color.secondary.opacity(0.3)).frame(width: 6, height: 6) } }
                Spacer()
                if page > 0 { Button("이전") { page -= 1 } }
                if page < 3 { Button("다음") { page += 1 }.buttonStyle(.borderedProminent) }
                else { Button("설정 열기") { openSettings() }; Button("시작하기") { close() }.buttonStyle(.borderedProminent) }
            }
        }.padding(18).frame(width: 560).onAppear { st = status() }
        .onReceive(NotificationCenter.default.publisher(for: NSApplication.didBecomeActiveNotification)) { _ in st = status(); hooks = ClaudeHooks.connectedCount }
    }
}

// MARK: - 본체
final class Pet: NSObject {
    let art = Art(), item = NSStatusBar.system.statusItem(withLength: 22), cal = CalendarWatch(), weather = Weather()
    var skin: String { get { defaults.string(forKey: "skin") ?? "SC" } set { defaults.set(newValue, forKey: "skin") } }  // 기본: 리본 햄찌
    var layout: String { get { defaults.string(forKey: "layout") ?? "A" } set { defaults.set(newValue, forKey: "layout") } }
    var watched: [(names: [String], logo: String, label: String)] {
        WATCH_APPS.filter { defaults.object(forKey: $0.key) == nil ? ["watchSlack", "watchKakao"].contains($0.key) : defaults.bool(forKey: $0.key) }.map { ($0.names, $0.logo, $0.label) }
    }
    var hamster = Player(), prop = Player(), scene = Player()
    var claude = "idle", claudeSince = Date(), lastSeen: [String: String] = [:]
    let stateDir = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".hamster.d").path
    var settingsWindow: NSWindow?, onboardingWindow: NSWindow?
    var ambient: String? = nil, inMeeting = false
    var event: (kind: String, app: String, since: Date)? = nil
    var queue: [(kind: String, app: String, at: Date)] = []
    var lastFired: [String: Date] = [:]
    var badges: [String: String] = [:], firedMeetings: Set<String> = [], lastBadgePoll = Date.distantPast, badgePolling = false
    var activeSince: Date? = nil, breakUntil: Date? = nil
    var testUntil: Date? = nil, testState: String? = nil
    let stateFile = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".hamster").path
    var idleSec = 0.0, ticks = 0, lastDrawn: [ObjectIdentifier] = [], lastReason = ""
    let popover = NSPopover()
    lazy var tray = NotchTray(pet: self)
    var cpuHot = false, wasCharging = false, lastBatteryWarn = Date.distantPast, lastCpuWarn = Date.distantPast
    var lastWater = Date(), wasAsleep = false
    var season: String? = nil, testSeasonUntil: Date? = nil, testSeason: String? = nil
    var focusUntil: Date? = nil, digitAnims: [String: Anim] = [:]
    var idleVariant: String? = nil
    // 타자 반응: 키 내용은 안 읽고 눌림 시각만 쌓는다
    var keyTimes: [Date] = [], earFlickUntil = Date.distantPast, earLeft = false, typeLeft = false, typingUntil: Date? = nil
    var dressed2: [String: NSImage] = [:]
    let pouch = Pouch(), log = Activity(), updater = Updater()
    var notifiedUpdate = ""
    var focusRemaining: Int? { focusUntil.map { max(0, Int($0.timeIntervalSinceNow.rounded(.up))) } }
    var dressed: [String: NSImage] = [:]  // 프레임 id + 코스튬 → 합성 캐시

    override init() {
        super.init()
        item.autosaveName = "hamster"
        if let b = item.button {
            b.target = self; b.action = #selector(clicked); b.sendAction(on: [.leftMouseUp, .rightMouseUp])
            b.setAccessibilityLabel("Happy Hamzzi"); b.setAccessibilityHelp("클릭: 쓰다듬기와 일정 보기. 우클릭: 메뉴")
        }
        Timer.scheduledTimer(withTimeInterval: 0.12, repeats: true) { [weak self] _ in self?.tick() }
        Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { [weak self] _ in self?.sense() }
        Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in self?.cal.refresh() }
        try? FileManager.default.createDirectory(atPath: stateDir, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
        try? FileManager.default.setAttributes([.posixPermissions: 0o700], ofItemAtPath: stateDir)
        _ = Sensors.cpuPercent(); sense()
        syncKeyMonitor()  // 타자 반응을 켰을 때만 전역 키 모니터를 둔다
        NotificationCenter.default.addObserver(forName: NSApplication.didChangeScreenParametersNotification, object: nil, queue: .main) { [weak self] _ in self?.lastDrawn = [] }  // 손쉬운 사용 권한이 있어야 들어온다
        if SMAppService.mainApp.status == .notRegistered { try? SMAppService.mainApp.register() }  // 첫 실행에 로그인 항목 등록. 설정에서 끌 수 있다
        if !defaults.bool(forKey: "onboarded") { DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in self?.showOnboarding() } }
        DispatchQueue.main.asyncAfter(deadline: .now() + 30) { [weak self] in self?.autoCheckUpdate() }
        Timer.scheduledTimer(withTimeInterval: 3600, repeats: true) { [weak self] _ in self?.autoCheckUpdate() }
        if defaults.bool(forKey: "onboarded") { cal.requestAccess(); weather.start() }  // 처음이면 튜토리얼의 버튼에서 요청한다
    }

    // --- 입력 ---
    func fire(_ kind: String, app: String = "") {
        if kind == "notify", focusUntil != nil, flag("focusQuiet", true) { return }  // 집중 중엔 봉투 안 띄움
        let key = kind + app
        if let t = lastFired[key], Date().timeIntervalSince(t) < 5 { return }
        lastFired[key] = Date()
        if let e = event, e.kind == kind, e.app == app { return }
        if let e = event, EVENT_PRIORITY[kind, default: 0] <= EVENT_PRIORITY[e.kind, default: 0] {
            if !queue.contains(where: { $0.kind == kind && $0.app == app }) { queue.append((kind, app, Date())) }
            return
        }
        event = (kind, app, Date())
    }
    // 세션별 파일(~/.hamster.d/<session>)을 합산한다. (구형 단일 파일 ~/.hamster 는 더 이상 읽지 않는다 — 시간 제한이 없어 쳇바퀴가 안 멈추는 버그의 원인이었다)
    func readHookFile() {
        var files: [String] = []
        if let names = try? FileManager.default.contentsOfDirectory(atPath: stateDir) { files += names.filter { !$0.hasPrefix(".") && $0 != "cmd" && $0 != "activity.json" }.map { stateDir + "/" + $0 } }
        var states: [String: String] = [:]
        for f in files {
            guard let attrs = try? FileManager.default.attributesOfItem(atPath: f), let m = attrs[.modificationDate] as? Date else { continue }
            let age = Date().timeIntervalSince(m)
            if age > 2 * 3600 { try? FileManager.default.removeItem(atPath: f); continue }  // 죽은 세션 파일 정리
            guard let s = try? String(contentsOfFile: f, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines) else { continue }
            if s == "surprised", age > 30 * 60 { continue }   // 세션이 죽어 남은 승인 대기는 30분 뒤 무시
            if s == "working", age > 20 * 60 { continue }     // 도구 호출마다 갱신되므로 20분 넘게 조용하면 죽은 세션으로 본다
            states[f] = s
            if s != lastSeen[f] {  // 바뀐 순간에만 이벤트
                if lastSeen[f] != nil, s == "done" || s == "faint" { fire(s); if s == "done" { log.bump() } }
                lastSeen[f] = s
            }
        }
        for f in lastSeen.keys where states[f] == nil { lastSeen[f] = nil }
        let agg = states.values.contains("surprised") ? "waiting" : states.values.contains("working") ? "working" : "idle"
        if agg != claude { claude = agg; claudeSince = Date() }
    }
    func sense() {
        let now = Date(), cal = Calendar.current, h = cal.component(.hour, from: now), m = cal.component(.minute, from: now)
        let minutes = h * 60 + m, wd = cal.component(.weekday, from: now)
        // 활동(연속 사용) → 쉬어
        let idle = Sensors.idleSeconds(); idleSec = idle
        season = flag("seasonEnabled", true) ? seasonToday(now) : nil
        syncKeyMonitor()
        if defaults.bool(forKey: "onboarded") { self.cal.requestAccess(); weather.start() }  // sense() 안의 cal 은 Calendar 라 self 로 구분
        let asleep = activity == "sleep"
        if wasAsleep, !asleep, idle < 30 { fire("wake") }  // 자다가 입력이 돌아오면 기지개
        wasAsleep = asleep
        if idle < 60 { if activeSince == nil { activeSince = now } } else if idle > 300 { activeSince = nil; breakUntil = nil }
        if flag("breakEnabled", true), let a = activeSince, now.timeIntervalSince(a) > Double(setting("breakMinutes", 50)) * 60, breakUntil == nil { breakUntil = now.addingTimeInterval(600); activeSince = now }
        if let b = breakUntil, now > b { breakUntil = nil }
        let bat = Sensors.battery()
        cpuHot = Sensors.cpuPercent() > 80
        if let bat, bat.onBattery, bat.percent <= 20, now.timeIntervalSince(lastBatteryWarn) > 600 { lastBatteryWarn = now; fire("battery_low") }
        if let bat, bat.charging, !wasCharging { fire("charging") }
        wasCharging = bat?.charging ?? false
        if cpuHot, now.timeIntervalSince(lastCpuWarn) > 300 { lastCpuWarn = now; fire("cpu") }
        weather.fetch()
        // 회의
        inMeeting = self.cal.inMeeting(now)
        if let e = self.cal.startingSoon(now) {
            let key = "\(e.eventIdentifier ?? "")|\(Int(e.startDate.timeIntervalSince1970))"  // 반복 회의는 회차마다
            if !firedMeetings.contains(key) { firedMeetings.insert(key); fire("meeting_soon") }
            firedMeetings = firedMeetings.filter { ($0.split(separator: "|").last).flatMap { Double($0) }.map { now.timeIntervalSince1970 - $0 < 86400 } ?? false }
        }
        // Dock 배지: 배터리면 15초, 전원이면 5초
        if !watched.isEmpty, AXIsProcessTrusted(), now.timeIntervalSince(lastBadgePoll) >= ((bat?.onBattery ?? false) ? 15 : 5) {  // 감시 앱·권한 없으면 osascript 안 띄움
            lastBadgePoll = now
            guard !badgePolling else { return }; badgePolling = true
            DispatchQueue.global().async { [self] in
                let b = Sensors.dockBadges()
                DispatchQueue.main.async {
                    self.badgePolling = false
                    for app in self.watched {
                        guard let name = app.names.first(where: { b[$0] != nil }), let v = b[name] else { continue }
                        if let old = self.badges[app.logo], old != v { self.fire("notify", app: app.logo) }
                        self.badges[app.logo] = v
                    }
                }
            }
        }
        // 분위기 후보
        var c: Set<String> = []
        if let w = weather.condition { c.insert(w) }
        if let b = defaults.string(forKey: "birthday")?.split(separator: "/").compactMap({ Int($0) }), b.count == 2, b[0] == cal.component(.month, from: now), b[1] == cal.component(.day, from: now) { c.insert("birthday") }
        if breakUntil != nil { c.insert("break") }
        if flag("waterEnabled", true), idle < 300, now.timeIntervalSince(lastWater) > Double(setting("waterMinutes", 90)) * 60 { c.insert("water") }
        let lunch = setting("lunchHour", 12), leave = setting("leaveHour", 19), night = setting("nightHour", 23)
        if (lunch * 60..<(lunch + 1) * 60).contains(minutes) { c.insert("lunch") }
        if (leave * 60..<night * 60).contains(minutes) { c.insert("leave") }
        if minutes >= night * 60 || minutes < 5 * 60 { c.insert("night") }
        if wd == 6, defaults.object(forKey: "fridayParty") == nil || defaults.bool(forKey: "fridayParty"), (15 * 60..<leave * 60).contains(minutes) { c.insert("friday") }
        ambient = AMBIENT_ORDER.first { c.contains($0) }
    }

    // --- 표시 상태 ---
    var activity: String {
        if claude == "waiting" { return "surprised" }
        if inMeeting { return "meeting" }
        if let f = focusUntil, Date() < f { return "focus" }
        if claude == "working" { return "working" }
        return Date().timeIntervalSince(claudeSince) > 180 && idleSec > 180 ? "sleep" : "idle"
    }
    /// 만료된 이벤트를 치우고 큐에서 다음 것을 꺼낸다. tick 에서만 부른다.
    func advance() {
        if let t = testUntil, Date() >= t { testState = nil; testUntil = nil }
        guard let e = event, Date().timeIntervalSince(e.since) >= EVENT_SECONDS[e.kind, default: 4] else { return }
        event = nil
        queue.removeAll { Date().timeIntervalSince($0.at) > 60 }
        if !queue.isEmpty { let q = queue.removeFirst(); event = (q.kind, q.app, Date()) }
    }
    /// 지금 보여 줄 상태. 부작용 없음 — 메뉴·툴팁에서도 안전하게 부른다.
    func displayed() -> (state: String, app: String) {
        if let s = testState { return (s, "slack") }
        if let e = event { return (e.kind, e.app) }
        let a = activity
        if a == "working" || a == "meeting" { return (a, "") }
        if let t = typingUntil, Date() < t, a == "idle" || a == "sleep" { return ("typing", "") }
        return (ambient ?? a, "")
    }
    func reason(_ state: String, _ app: String) -> String {
        var r = REASONS[state] ?? state
        if state == "focus", let m = focusRemaining { r = "집중 세션 중, \(m >= 60 ? "\(m / 60)분" : "\(m)초") 남음 (쳇바퀴)" }
        if state == "notify" { r = "\(WATCH_APPS.first { $0.logo == app }?.label ?? app) 알림이 도착했어요 (봉투)" }
        if let q = queue.first { r += "  · 대기 중: \(REASONS[q.kind]?.components(separatedBy: " (").first ?? q.kind)" }
        if let c = testSeason ?? season, let l = SEASON_LABEL[c] { r += "  · \(l)" }
        if let a = defaults.string(forKey: "accessory"), let l = ACCESSORY_LABEL.first(where: { $0.0 == a })?.1, !a.isEmpty { r += "  · \(l)" }
        return r
    }
    func tick() {
        ticks += 1
        if ticks % 4 == 0 { readHookFile() }  // 0.5초면 충분하다
        if ticks % 8 == 0, flag("clipboardEnabled", true), pouch.poll() { fire("stash") }  // 1초마다 클립보드 확인
        if ticks % 8 == 0 { runCommandFile() }
        advance()
        if let f = focusUntil, Date() >= f { focusUntil = nil; fire("done") }  // 집중 끝 → 체크
        let (state, app) = displayed()
        let notch = layout == "N" && NotchTray.notchScreen != nil
        let cell = notch ? 32 : N, pre = notch ? "n32/" : ""
        if !notch, tray.panel.isVisible { tray.panel.orderOut(nil) }
        if item.isVisible == notch { item.isVisible = !notch }
        let wide = notch || layout != "S" || !CORE.contains(state)
        let variant = (!notch && layout == "S" && CORE.contains(state)) ? "inline" : "plain"
        // 대기 동작은 한 바퀴 끝날 때마다 무작위로 바꾼다. 같은 동작 연속은 피한다(씨 먹기 제외)
        var hs = state
        if state == "idle" {
            if idleVariant == nil || hamster.looped {
                let pool = IDLE_VARIANTS.filter { $0.0 == "idle" || $0.0 != idleVariant }
                var r = Int.random(in: 0..<pool.reduce(0) { $0 + $1.1 }); var pick = "idle"
                for (k, w) in pool { if r < w { pick = k; break }; r -= w }
                idleVariant = pick
            }
            hs = idleVariant ?? "idle"
        } else { idleVariant = nil }
        hamster.set(notch ? art.hamster32(skin, hs) ?? art.hamster32(skin, "idle") : art.hamster(skin, variant, hs) ?? art.hamster(skin, variant, "idle"))
        var focusProp: Anim? = nil
        if state == "focus", let r = focusRemaining {
            let text = r >= 60 ? "\(r / 60)m" : "\(r)s", key = "\(cell)-\(text)"
            if digitAnims[key] == nil { digitAnims[key] = Anim(frames: [digitImage(text, size: cell)], ticks: [1]) }
            focusProp = digitAnims[key]
        }
        if let t = testSeasonUntil, Date() >= t { testSeason = nil; testSeasonUntil = nil }
        let accessory = defaults.string(forKey: "accessory").flatMap { $0.isEmpty ? nil : $0 }
        let costume = (testSeason ?? accessory ?? season).flatMap { ["working", "sprint", "focus"].contains(state) || ["idle_roll", "idle_peek"].contains(hs) ? nil : $0 }  // 옆모습·구르기·빼꼼엔 안 씀. 액세서리가 계절보다 우선
        let width = notch || layout == "B" ? 3 : (wide ? 2 : 1)  // 노치 모드는 항상 3칸
        if width >= 2 {
            prop.set(focusProp ?? (state == "notify" && width == 2 ? art.logo(app, pre) : (state == "idle" && costume != nil ? art.prop(costume!, pre) : nil) ?? art.prop(state, pre) ?? art.prop("idle", pre)))
        }
        if width == 3 { scene.set(state == "notify" ? art.logo(app, pre) : (state == "idle" && costume != nil ? art.scene(costume!, pre) : nil) ?? art.scene(state, pre) ?? art.scene("idle", pre)) }
        var h = hamster.next()
        // 코스튬·봉고·귀 쫑긋을 얹은 프레임은 캐시해서 identity 비교가 유지되게
        let front = !["working", "sprint", "focus"].contains(state) && !["idle_roll", "idle_peek"].contains(hs)
        let wheelView = ["working", "sprint", "focus"].contains(state)
        let flick = (front || wheelView) && Date() < earFlickUntil, typing = front && state == "typing"
        if let h0 = h, costume != nil || typing || flick {
            let key = "\(cell)-\(ObjectIdentifier(h0).hashValue)-\(costume ?? "")-\(typing ? (typeLeft ? "L" : "R") : "")-\(flick ? (earLeft ? "l" : "r") : "")"
            if let d = dressed[key] { h = d } else {
                let hat = costume.flatMap { art.costume($0, pre) }, kb = typing ? art.overlay(typeLeft ? "type_l" : "type_r", pre) : nil, left = earLeft
                let sc = CGFloat(cell) / CGFloat(N)
                let d = NSImage(size: h0.size, flipped: false) { r in
                    h0.draw(in: r)
                    if flick {  // 귀 영역을 1px 위로 복사 → 쫑긋. 정면은 양쪽 번갈아, 옆모습(쳇바퀴)은 보이는 귀 하나
                        let rect = wheelView ? NSRect(x: 12 * sc, y: CGFloat(cell) - 11 * sc, width: 4 * sc, height: 4 * sc)
                                             : NSRect(x: (left ? 3.0 : 14.0) * sc, y: CGFloat(cell) - 5 * sc, width: 5 * sc, height: 4 * sc)
                        h0.draw(in: rect.offsetBy(dx: 0, dy: 1), from: rect, operation: .sourceOver, fraction: 1)
                    }
                    hat?.draw(in: r); kb?.draw(in: r); return true
                }
                dressed[key] = d; h = d
            }
        }
        let imgs = [h, width >= 2 ? prop.next() : nil, width == 3 ? scene.next() : nil].compactMap { $0 }
        let ids = imgs.map(ObjectIdentifier.init)
        let r = reason(state, app)
        if r != lastReason { lastReason = r; item.button?.toolTip = r; item.button?.setAccessibilityValue(r); tray.view.toolTip = r }
        if notch { _ = tray.place(contentWidth: CGFloat(imgs.count * cell) + CGFloat(max(0, imgs.count - 1)) * 4) }
        if ids == lastDrawn { return }  // 프레임이 안 바뀌었으면 다시 그리지 않는다
        lastDrawn = ids
        let gap: CGFloat = notch ? 4 : 0, total = CGFloat(imgs.count * cell) + gap * CGFloat(max(0, imgs.count - 1))
        let out = NSImage(size: NSSize(width: total, height: CGFloat(cell)), flipped: false) { _ in
            NSGraphicsContext.current?.imageInterpolation = .none
            for (i, im) in imgs.enumerated() { im.draw(in: NSRect(x: CGFloat(i) * (CGFloat(cell) + gap), y: 0, width: CGFloat(cell), height: CGFloat(cell))) }
            return true
        }
        out.isTemplate = false
        if notch { tray.view.image = out } else {
            if item.length != total + 4 { item.length = total + 4 }
            item.button?.image = out
        }
    }

    // --- 클릭·메뉴 ---
    @objc func clicked() { handleClick(agendaOnly: false) }
    func handleClick(agendaOnly: Bool, anchor: NSView? = nil) {
        if !agendaOnly, anchor == nil, NSApp.currentEvent?.type == .rightMouseUp { showMenu(); return }
        if popover.isShown { popover.performClose(nil) } else if let b = anchor ?? (layout == "N" && tray.panel.isVisible ? tray.view : item.button) {
            cal.refresh()
            popover.contentViewController = NSHostingController(rootView: AgendaView(events: cal.all, granted: cal.granted,
                focusRemaining: { [weak self] in self?.focusRemaining }, focusMinutes: setting("focusMinutes", 25), toggleFocus: { [weak self] in self?.toggleFocus() },
                pouch: flag("clipboardEnabled", true) ? pouch : nil, activity: log, initialTab: testTab))
            testTab = nil
            popover.behavior = .transient; popover.animates = true
            popover.show(relativeTo: b.bounds, of: b, preferredEdge: .minY)
            NSApp.activate(ignoringOtherApps: true)
        }
        let state = displayed().state
        let today = Calendar.current.startOfDay(for: Date())
        let dayKey = defaults.object(forKey: "petDay") as? Date
        let count = (dayKey == today ? defaults.integer(forKey: "petCount") : 0) + 1
        defaults.set(today, forKey: "petDay"); defaults.set(count, forKey: "petCount"); defaults.set(Date(), forKey: "lastPet")
        // 상태별 반응
        switch state {
        case "water": lastWater = Date(); ambient = nil; fire("pet")      // 물병 든 채 클릭 = 마셨다
        case "sleep", "grumpy": fire("grumpy")                              // 자는데 깨움
        case "working", "sprint", "focus": event = nil; fire("sprint")              // 응원 → 전력질주
        case "meeting", "pet_meeting": fire("pet_meeting")                  // 회의 중엔 조용히
        case "faint": event = nil; queue.removeAll { $0.kind == "faint" }; fire("dizzy")  // 부활
        default: fire("pet")
        }
    }
    func item(_ title: String, _ symbol: String?, _ action: Selector?, key: String = "", enabled: Bool = true) -> NSMenuItem {
        let m = NSMenuItem(title: title, action: action, keyEquivalent: key); m.target = self; m.isEnabled = enabled
        if let symbol, let im = NSImage(systemSymbolName: symbol, accessibilityDescription: nil) { m.image = im }
        return m
    }
    func showMenu(anchor: NSView? = nil) {
        let menu = NSMenu(); menu.autoenablesItems = false
        let (st, app) = displayed()
        menu.addItem(item("지금: " + reason(st, app), "info.circle", nil, enabled: false))
        if let e = cal.events.first(where: { $0.startDate > Date() }) {
            let m = Int(e.startDate.timeIntervalSinceNow / 60), when = m < 60 ? "\(m)분 후" : m < 24 * 60 ? "\(m / 60)시간 \(m % 60)분 후" : "\(m / 1440)일 후"
            let df = DateFormatter(); df.locale = Locale(identifier: "ko_KR"); df.dateFormat = "M/d a h:mm"
            menu.addItem(item("다음 회의: \(df.string(from: e.startDate)) \(e.title ?? "") (\(when))", "calendar", nil, enabled: false))
        }
        if let (v, _) = updater.available { menu.addItem(item("업데이트 \(v) 설치…", "arrow.down.circle.fill", #selector(installUpdate))) }
        if ClaudeHooks.claudeInstalled, ClaudeHooks.connectedCount < ClaudeHooks.events.count {
            menu.addItem(item("Claude Code 훅이 연결되지 않았어요 → 설정에서 연결", "exclamationmark.triangle", #selector(openSystemSettings)))
        }
        menu.addItem(.separator())
        menu.addItem(item("일정 보기", "calendar.badge.clock", #selector(openAgenda)))
        if let r = focusRemaining { menu.addItem(item("집중 중단 (\(max(1, r / 60))분 남음)", "stop.circle", #selector(toggleFocus))) }
        else { menu.addItem(item("집중 \(setting("focusMinutes", 25))분 시작", "timer", #selector(toggleFocus))) }
        menu.addItem(item("쓰다듬기", "hand.raised", #selector(petNow)))
        menu.addItem(.separator())
        let skins = NSMenu(), famA = NSMenu(), famB = NSMenu(), famC = NSMenu(), famD = NSMenu(), famE = NSMenu(), morphs = NSMenu()
        for (k, name) in art.skinNames {
            let m = NSMenuItem(title: name, action: #selector(pickSkin(_:)), keyEquivalent: ""); m.target = self; m.state = k == skin ? .on : .off; m.representedObject = k
            if let im = art.hamster(k, "plain", "idle")?.frames.first { m.image = im }
            (["B": famB, "C": famC, "D": famD, "E": famE][familyOf(k)] ?? (k.count == 1 && k <= "E" ? famA : morphs)).addItem(m)
        }
        famA.addItem(.separator()); let mm = item("골든 햄스터 모프 (\(morphs.items.count)종)", "pawprint", nil); mm.submenu = morphs; famA.addItem(mm)
        let a = item("디자인 A — 클래식 (\(famA.items.count - 2 + morphs.items.count)종)", "a.circle", nil); a.submenu = famA; a.state = familyOf(skin) == "A" ? .on : .off; skins.addItem(a)
        let b = item("디자인 B — 햄찌 (\(famB.items.count)종)", "b.circle", nil); b.submenu = famB; b.state = isFamilyB(skin) ? .on : .off; skins.addItem(b)
        let c = item("디자인 C — 도톰 (\(famC.items.count)종)", "c.circle", nil); c.submenu = famC; c.state = isFamilyC(skin) ? .on : .off; skins.addItem(c)
        let d = item("디자인 D — 줄무늬 (\(famD.items.count)종)", "d.circle", nil); d.submenu = famD; d.state = familyOf(skin) == "D" ? .on : .off; skins.addItem(d)
        let e = item("디자인 E — 리본 (\(famE.items.count)종)", "e.circle", nil); e.submenu = famE; e.state = familyOf(skin) == "E" ? .on : .off; skins.addItem(e)
        let layouts = NSMenu(); for (k, name) in [("S", "22px 단독"), ("A", "44px 햄스터 + 소품"), ("B", "66px 햄스터 + 소품 + 장면"), ("N", "노치 모드 (32px)")] { let m = NSMenuItem(title: name, action: #selector(pickLayout(_:)), keyEquivalent: ""); m.target = self; m.state = k == layout ? .on : .off; m.representedObject = k; layouts.addItem(m) }
        let tests = NSMenu(); for s in (art.meta["props"] as? [String: Any] ?? [:]).keys.sorted() { let m = NSMenuItem(title: "\(REASONS[s]?.components(separatedBy: " (").first ?? s)  [\(s)]", action: #selector(testState(_:)), keyEquivalent: ""); m.target = self; m.representedObject = s; tests.addItem(m) }
        let seasons = NSMenu(); for (k, l) in SEASON_LABEL.sorted(by: { $0.key < $1.key }) { let m = NSMenuItem(title: l, action: #selector(testSeasonPick(_:)), keyEquivalent: ""); m.target = self; m.representedObject = k; seasons.addItem(m) }
        for (title, symbol, sub) in [("스킨", "paintpalette", skins), ("레이아웃", "rectangle.split.3x1", layouts), ("상태 테스트", "play.circle", tests), ("코스튬 테스트", "party.popper", seasons)] { let m = item(title, symbol, nil); m.submenu = sub; menu.addItem(m) }
        menu.addItem(.separator())
        menu.addItem(item("설정…", "gearshape", #selector(openSettings), key: ","))
        menu.addItem(item("시작 안내 다시 보기", "questionmark.circle", #selector(showOnboarding)))
        let count = (defaults.object(forKey: "petDay") as? Date) == Calendar.current.startOfDay(for: Date()) ? defaults.integer(forKey: "petCount") : 0
        menu.addItem(item("오늘 쓰다듬기 \(count)회", "heart", nil, enabled: false))
        menu.addItem(.separator())
        menu.addItem(item("Happy Hamzzi 종료", "power", #selector(NSApplication.terminate(_:)), key: "q"))
        if let anchor { menu.popUp(positioning: nil, at: NSPoint(x: 0, y: 0), in: anchor); return }
        item.menu = menu; item.button?.performClick(nil); item.menu = nil
    }
    @objc func pickSkin(_ m: NSMenuItem) { if let k = m.representedObject as? String { skin = k } }
    @objc func pickLayout(_ m: NSMenuItem) { if let k = m.representedObject as? String { layout = k } }
    func autoCheckUpdate() {
        guard flag("autoUpdateCheck", true) else { return }
        if let t = updater.lastChecked, Date().timeIntervalSince(t) < 86400 { return }  // 하루 한 번
        updater.check { [weak self] found in
            guard let self, found, let (v, _) = self.updater.available, self.notifiedUpdate != v else { return }
            self.notifiedUpdate = v; self.fire("update")  // 선물 상자
        }
    }
    @objc func installUpdate() { updater.install() }
    @objc func showOnboarding() { showOnboardingPage(0) }
    func showOnboardingPage(_ page: Int) {
        let view = OnboardingView(art: art, skin: skin, page: page, status: { [weak self] in PermissionStatus(calendar: self?.cal.granted ?? false, location: self?.weather.coord != nil, accessibility: AXIsProcessTrusted()) },
                                  openSettings: { [weak self] in self?.openSettings() },
                                  close: { [weak self] in defaults.set(true, forKey: "onboarded"); self?.onboardingWindow?.close() },
                                  request: { [weak self] what in self?.requestPermission(what) })
        let w = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 560, height: 460), styleMask: [.titled, .closable], backing: .buffered, defer: false)
        w.title = "Happy Hamzzi 시작하기"; w.contentViewController = NSHostingController(rootView: view); w.isReleasedWhenClosed = false; w.center()
        onboardingWindow = w; NSApp.activate(ignoringOtherApps: true); w.makeKeyAndOrderFront(nil)
        defaults.set(true, forKey: "onboarded")
    }
    /// 권한은 사용자가 버튼을 눌렀을 때만 요청한다 (튜토리얼·설정)
    func requestPermission(_ what: String) {
        switch what {
        case "calendar": cal.requestAccess(); if cal.requested, !cal.granted { NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Calendars")!) }
        case "location": weather.start()
        case "accessibility":
            if !AXIsProcessTrustedWithOptions([kAXTrustedCheckOptionPrompt.takeUnretainedValue(): true] as CFDictionary) {
                NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")!)
            }
        default: break
        }
    }
    @objc func openSystemSettings() { settingsTab = "시스템"; settingsWindow = nil; openSettings() }
    var settingsTab: String? = nil
    @objc func openSettings() {
        if settingsWindow == nil {
            let view = SettingsView(initialTab: settingsTab, updater: updater, art: art, preview: { [weak self] skin, layout in self?.previewImage(skin: skin, layout: layout) ?? NSImage() },
                                    status: { [weak self] in PermissionStatus(calendar: self?.cal.granted ?? false, location: self?.weather.coord != nil, accessibility: AXIsProcessTrusted()) },
                                    request: { [weak self] in self?.requestPermission($0) })
            let hc = NSHostingController(rootView: view)
            let w = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 520, height: 520), styleMask: [.titled, .closable], backing: .buffered, defer: false)
            w.title = "Happy Hamzzi 설정"; w.contentViewController = hc; w.setContentSize(NSSize(width: 520, height: 520)); w.isReleasedWhenClosed = false; w.center()
            settingsWindow = w
        }
        NSApp.activate(ignoringOtherApps: true); settingsWindow?.makeKeyAndOrderFront(nil)
    }
    func previewImage(skin: String, layout: String) -> NSImage {
        if layout == "N", let h = art.hamster32(skin, "idle")?.frames.first {
            let out = NSImage(size: NSSize(width: 64, height: 64), flipped: false) { r in NSColor.black.setFill(); r.fill(); NSGraphicsContext.current?.imageInterpolation = .none; h.draw(in: r); return true }
            return out
        }
        var imgs = [art.hamster(skin, layout == "S" ? "inline" : "plain", "idle")?.frames.first].compactMap { $0 }
        if layout != "S", let p = art.prop("idle")?.frames.first { imgs.append(p) }
        if layout == "B", let sc = art.scene("idle")?.frames.first { imgs.append(sc) }
        return compose(imgs, scale: 2)
    }
    @objc func toggleFocus() {
        if focusUntil != nil { focusUntil = nil } else { focusUntil = Date().addingTimeInterval(Double(setting("focusMinutes", 25)) * 60); event = nil }
    }
    var keyMonitor: Any? = nil
    func syncKeyMonitor() {
        let on = flag("typingEnabled", false)
        if on, keyMonitor == nil { keyMonitor = NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { [weak self] _ in self?.keystroke() } }
        if !on, let m = keyMonitor { NSEvent.removeMonitor(m); keyMonitor = nil }
    }
    func keystroke() {
        guard flag("typingEnabled", false) else { return }
        let now = Date()
        keyTimes.append(now); keyTimes.removeAll { now.timeIntervalSince($0) > 2 }
        earFlickUntil = now.addingTimeInterval(0.15); earLeft.toggle(); typeLeft.toggle()
        if keyTimes.count >= 8 { typingUntil = now.addingTimeInterval(2) }  // 2초에 8타 이상이면 같이 친다
    }
    /// ~/.hamster.d/cmd 에 "popover 볼주머니" / "settings 모습" / "state faint" / "season xmas" 를 쓰면 실행하고 지운다 (테스트·자동화용)
    func runCommandFile() {
        let path = stateDir + "/cmd"
        guard let raw = try? String(contentsOfFile: path, encoding: .utf8) else { return }
        try? FileManager.default.removeItem(atPath: path)
        let parts = raw.trimmingCharacters(in: .whitespacesAndNewlines).split(separator: " ", maxSplits: 1).map(String.init)
        guard let verb = parts.first else { return }
        let arg = parts.count > 1 ? parts[1] : ""
        switch verb {
        case "popover": testTab = arg.isEmpty ? nil : arg; if popover.isShown { popover.performClose(nil) }; handleClick(agendaOnly: true)
        case "settings": openSettings()
        case "onboarding": showOnboardingPage(Int(arg) ?? 0)
        case "close": popover.performClose(nil)
        case "checkupdate": updater.check(manual: true)
        case "installupdate": updater.install()
        case "state": testState = arg; testUntil = Date().addingTimeInterval(8)
        case "skin": if art.skins[arg] != nil { skin = arg; art.cache.removeAll() }  // 테스트: 앱 안에서 스킨 전환 (defaults 캐시 경쟁 회피)
        case "season": testSeason = arg; testSeasonUntil = Date().addingTimeInterval(10)
        default: break
        }
    }
    var testTab: String? = nil
    @objc func openAgenda() { if !popover.isShown { handleClick(agendaOnly: true) } }
    @objc func petNow() { fire("pet") }
    @objc func testSeasonPick(_ m: NSMenuItem) { testSeason = m.representedObject as? String; testSeasonUntil = Date().addingTimeInterval(10) }
    @objc func testState(_ m: NSMenuItem) { testState = m.representedObject as? String; testUntil = Date().addingTimeInterval(6) }
}

let app = NSApplication.shared
let testSettings = ProcessInfo.processInfo.environment["HAMSTER_TEST_SETTINGS"] != nil  // 설정 창 캡처용
if !testSettings, let id = Bundle.main.bundleIdentifier, NSRunningApplication.runningApplications(withBundleIdentifier: id).count > 1 { exit(0) }  // 이미 떠 있으면 조용히 종료
app.setActivationPolicy(.accessory)
let pet = Pet()
if testSettings { DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { pet.openSettings() } }
app.run()
