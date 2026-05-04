import os
import sys
import requests
from huggingface_hub import list_repo_files, hf_hub_url

MODEL_NAME = "redlessone/PanDerm-base-w-PubMed-256"   # می‌توانی نام کامل مثل "org/مدل" بدهی
OUTPUT_DIR = "model_files"                 # پوشه‌ای که فایل‌های یکپارچه ذخیره می‌شوند
CHUNK_SIZE = 90 * 1024 * 1024              # ۹۰ مگابایت
HF_TOKEN = os.getenv("HF_TOKEN")           # برای مدل‌های خصوصی توکن را در Secrets بگذار

def download_file_in_chunks(url, dest_path, file_size):
    """فایل را در تکه‌های ۹۰MB دانلود کرده و در نهایت سرهم می‌کند."""
    os.makedirs(os.path.dirname(dest_path) if os.path.dirname(dest_path) else ".", exist_ok=True)

    part_files = []
    for start in range(0, file_size, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE - 1, file_size - 1)
        headers = {"Range": f"bytes={start}-{end}"}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"

        print(f"  دریافت بازهٔ {start}-{end} از {file_size} بایت ...")
        resp = requests.get(url, headers=headers, stream=True)
        resp.raise_for_status()

        chunk_path = f"{dest_path}.part{len(part_files):04d}"
        with open(chunk_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        part_files.append(chunk_path)

    # چسباندن تکه‌ها به هم
    print("  یکپارچه‌سازی تکه‌ها ...")
    with open(dest_path, "wb") as outfile:
        for part in part_files:
            with open(part, "rb") as infile:
                outfile.write(infile.read())
            os.remove(part)   # حذف تکهٔ موقت
    print(f"  ذخیره شد: {dest_path}")

def main():
    token = HF_TOKEN
    print(f"دریافت لیست فایل‌های مخزن {MODEL_NAME} ...")
    files = list_repo_files(MODEL_NAME, token=token)
    print(f"تعداد فایل‌ها: {len(files)}")

    for f in files:
        # پرش از فولدرها
        if f.endswith("/"):
            continue

        # گرفتن URL اصلی (بدون redirect نهایی با range ساپورت می‌کند)
        url = hf_hub_url(MODEL_NAME, f, revision="main")
        # یک HEAD بزنیم تا حجم فایل را بفهمیم
        head_resp = requests.head(url, headers={"Authorization": f"Bearer {token}"} if token else {})
        head_resp.raise_for_status()
        file_size = int(head_resp.headers.get("Content-Length", 0))
        dest_path = os.path.join(OUTPUT_DIR, f)

        print(f"\nفایل: {f} ({file_size} بایت)")
        if file_size > CHUNK_SIZE:
            print("  حجم بزرگتر از ۹۰MB است، دانلود تکه‌تکه ...")
            download_file_in_chunks(url, dest_path, file_size)
        else:
            # دانلود مستقیم
            print("  دانلود مستقیم ...")
            os.makedirs(os.path.dirname(dest_path) if os.path.dirname(dest_path) else ".", exist_ok=True)
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"} if token else {})
            resp.raise_for_status()
            with open(dest_path, "wb") as fout:
                fout.write(resp.content)
            print(f"  ذخیره شد: {dest_path}")

    print("\nهمه فایل‌ها با موفقیت دریافت و یکپارچه شدند.")

if __name__ == "__main__":
    main()
