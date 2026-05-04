import os
import shutil

CHUNKS_DIR = "model_chunks"
OUTPUT_DIR = "model_files"

def assemble_parts(part_files, output_path):
    """قطعات پشت‌سرهم را به فایل اصلی می‌چسباند."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as out:
        for part in sorted(part_files):   # ترتیب اسمی .part0000, .part0001, ...
            with open(os.path.join(CHUNKS_DIR, part), "rb") as pf:
                out.write(pf.read())

def main():
    if not os.path.exists(CHUNKS_DIR):
        print("پوشهٔ model_chunks پیدا نشد. ابتدا مخزن را clone کنید.")
        return

    # پاک‌سازی خروجی قبلی (دلخواه)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # یافتن تمام فایل‌های قطعه‌قطعه (براساس .part0000)
    parts_dict = {}
    for root, dirs, files in os.walk(CHUNKS_DIR):
        for f in files:
            if ".part" in f:
                # استخراج نام اصلی و شمارهٔ قطعه
                base, part_ext = f.rsplit(".part", 1)
                parts_dict.setdefault(base, []).append(f)
            else:
                # فایل‌های کوچک → کپی مستقیم
                rel_dir = os.path.relpath(root, CHUNKS_DIR)
                dest_dir = os.path.join(OUTPUT_DIR, rel_dir)
                os.makedirs(dest_dir, exist_ok=True)
                src = os.path.join(root, f)
                shutil.copy2(src, os.path.join(dest_dir, f))
                print(f"کپی فایل کوچک: {f}")

    # یکپارچه‌سازی فایل‌های بزرگ
    for base_name, part_list in parts_dict.items():
        # مسیر خروجی: حفظ ساختار پوشه
        # چون base_name ممکن است شامل مسیر نسبی باشد، آن را استخراج می‌کنیم
        # ولی در CHUNKS_DIR ساختار یکسان است. بهتر است base_name شامل مسیر نسبی از CHUNKS_DIR باشد.
        # در split_file، original_rel_path را حفظ کردیم. اما در اینجا فایل‌ها مستقیماً در root هستند.
        # root نسبی از CHUNKS_DIR است. پس base_name باید مسیر کامل نسبی باشد.
        # اما ما در split_file فقط اسم بیس را برای قطعات نگه داشتیم (base_name = os.path.basename(original_rel_path))
        # بنابراین اطلاعات پوشه از دست رفته! باید اصلاح کنم.
