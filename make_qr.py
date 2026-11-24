"""works.json の全作品ぶんのQRコード画像(qr-1.png, qr-2.png ...)を作り、
それぞれ読み取りテストまで行う。

使い方:
    pip install opencv-python-headless
    python make_qr.py https://ユーザー名.github.io/リポジトリ名/
"""
import json
import sys
import cv2

base = (sys.argv[1] if len(sys.argv) > 1 else input("公開ページのURL: ")).strip()
if not base.startswith("https://"):
    sys.exit("URL は https:// で始めてください(カメラ利用にHTTPSが必須です)")
if not base.endswith("/"):
    base += "/"

with open("works.json", encoding="utf-8") as f:
    works = json.load(f)["works"]

params = cv2.QRCodeEncoder_Params()
params.correction_level = cv2.QRCodeEncoder_CORRECT_LEVEL_Q  # 誤り訂正 Q(約25%)
encoder = cv2.QRCodeEncoder_create(params)
detector = cv2.QRCodeDetector()
cell, quiet, label_h = 16, 4, 64  # 1セル16px / 余白4セル / 番号表示の高さ

all_ok = True
for w in works:
    url = f"{base}?w={w['id']}"
    qr = encoder.encode(url)
    core = cv2.resize(qr, None, fx=cell, fy=cell, interpolation=cv2.INTER_NEAREST)
    q = quiet * cell
    img = cv2.copyMakeBorder(core, q, q + label_h, q, q, cv2.BORDER_CONSTANT, value=255)
    text = f"No. {w['id']}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3)
    cv2.putText(img, text, ((img.shape[1] - tw) // 2, img.shape[0] - q // 2 - 8 + th // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, 0, 3, cv2.LINE_AA)
    out = f"qr-{w['id']}.png"
    cv2.imwrite(out, img)

    results = []
    for scale in (1.0, 0.5, 0.25):  # 縮小しても読めるか
        small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        decoded, _, _ = detector.detectAndDecode(small)
        results.append(decoded == url)
    ok = all(results)
    all_ok = all_ok and ok
    print(f"{out}: {'OK' if ok else 'NG'}  {url}")

sys.exit(0 if all_ok else 1)
