#!/usr/bin/env python3
"""Vertex AI Gemini 호출기 (ADC 사용, 키 파일 없음).
  python3 tools/gemini.py --prompt "..." [--image a.png ...] [--model gemini-3-pro-image|gemini-2.5-flash] [--out dir] [--n 1]
텍스트 응답은 stdout, 이미지 응답은 --out 폴더에 PNG 저장."""
import argparse, base64, json, os, subprocess, sys, mimetypes, tempfile
PROJECT = os.environ.get("VERTEX_PROJECT_ID", "pubg-publishing-div-846696")
ap = argparse.ArgumentParser()
ap.add_argument("--prompt", required=True); ap.add_argument("--image", action="append", default=[])
ap.add_argument("--model", default="gemini-3-pro-image"); ap.add_argument("--out", default="."); ap.add_argument("--n", type=int, default=1)
ap.add_argument("--text-only", action="store_true")
a = ap.parse_args()
tok = subprocess.check_output(["gcloud", "auth", "application-default", "print-access-token"], text=True).strip()
parts = [{"text": a.prompt}]
for p in a.image:
    parts.append({"inlineData": {"mimeType": mimetypes.guess_type(p)[0] or "image/png", "data": base64.b64encode(open(p, "rb").read()).decode()}})
body = {"contents": [{"role": "user", "parts": parts}]}
if not a.text_only and "image" in a.model: body["generationConfig"] = {"responseModalities": ["TEXT", "IMAGE"]}
url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{a.model}:generateContent"
os.makedirs(a.out, exist_ok=True)
for k in range(a.n):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf: json.dump(body, tf); bf = tf.name
    # python.org 파이썬은 CA 번들이 없어 urllib 가 SSL 검증에 실패한다 → curl 로 보낸다
    r = subprocess.run(["curl", "-s", "-w", "\n%{http_code}", "-H", f"Authorization: Bearer {tok}", "-H", "Content-Type: application/json", "--data-binary", f"@{bf}", url], capture_output=True, text=True); os.unlink(bf)
    out, _, code = r.stdout.rpartition("\n")
    if code != "200": sys.exit(f"HTTP {code}: {out[:300]}")
    d = json.loads(out)
    i = 0
    for part in d["candidates"][0]["content"]["parts"]:
        if "text" in part: print(part["text"])
        if "inlineData" in part:
            f = os.path.join(a.out, f"gen{k}_{i}.png"); open(f, "wb").write(base64.b64decode(part["inlineData"]["data"])); print("saved", f); i += 1
    u = d.get("usageMetadata", {}); print(f"tokens in={u.get('promptTokenCount')} out={u.get('candidatesTokenCount')}", file=sys.stderr)
