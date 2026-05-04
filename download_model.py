import os
import requests
from huggingface_hub import list_repo_files, hf_hub_url

MODEL_NAME = "redlessone/PanDerm-base-w-PubMed-256"   # نام کامل مدل
OUTPUT_DIR = "model_files"
CHUNK_SIZE = 90 * 1024 * 1024   # ۹۰ مگابایت

# ---------- مدیریت صحیح توکن ----------
raw_token = os.getenv("HF_TOKEN")
HF_TOKEN = None if raw_token in (None, "") else raw_token
# ---------------------------------------

def download_file_in_chunks(url, dest_path, file_size):
    """دانلود تکه‌تکه و یکپارچه‌سازی فایل‌های بزرگتر از CHUNK_SIZE"""
    os.makedirs(os.path.dirname(dest_path) if os.path.dirname(dest_path) else ".", exist_ok=True)
    part_files = []
    for start in range(0, file_size, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE - 1, file_size - 1)
        headers = {"Range": f"bytes={start}-{end}"}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        print(f"  دریافت بازهٔ {start}-{end} ...")
        resp = requests.get(url, headers=headers, stream=True)
        resp.raise_for_status()
        chunk_path = f"{dest_path}.part{len(part_files):04d}"
        with open(chunk_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        part_files.append(chunk_path)

    print("  یکپارچه‌سازی تکه‌ها ...")
    with open(dest_path, "wb") as outfile:
        for part in part_files:
            with open(part, "rb") as infile:
                outfile.write(infile.read())
            os.remove(part)
    print(f"  ذخیره شد: {dest_path}")

def main():
    print(f"دریافت لیست فایل‌های مخزن {MODEL_NAME} ...")
    # token=None برای مدل عمومی بدون توکن
    files = list_repo_files(MODEL_NAME, token=HF_TOKEN)
    print(f"تعداد فایل‌ها: {len(files)}")

    for f in files:
        if f.endswith("/"):   # پوشه‌ها را نادیده بگیر
            continue

        url = hf_hub_url(MODEL_NAME, f, revision="main")
        # دریافت حجم فایل با HEAD
        head_headers = {}
        if HF_TOKEN:
            head_headers["Authorization"] = f"Bearer {HF_TOKEN}"
        head_resp = requests.head(url, headers=head_headers)
        head_resp.raise_for_status()
        file_size = int(head_resp.headers.get("Content-Length", 0))
        dest_path = os.path.join(OUTPUT_DIR, f)

        print(f"\nفایل: {f} ({file_size} بایت)")
        if file_size > CHUNK_SIZE:
            print("  حجم > 90MB → دانلود تکه‌تکه")
            download_file_in_chunks(url, dest_path, file_size)
        else:
            print("  دانلود مستقیم ...")
            os.makedirs(os.path.dirname(dest_path) if os.path.dirname(dest_path) else ".", exist_ok=True)
            dl_headers = {}
            if HF_TOKEN:
                dl_headers["Authorization"] = f"Bearer {HF_TOKEN}"
            resp = requests.get(url, headers=dl_headers)
            resp.raise_for_status()
            with open(dest_path, "wb") as fout:
                fout.write(resp.content)
            print(f"  ذخیره شد: {dest_path}")

if __name__ == "__main__":
    main()
