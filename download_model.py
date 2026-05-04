import os
import shutil

MODEL_DIR = "model_files"        # فایل‌های دانلودشدهٔ اصلی
CHUNKS_DIR = "model_chunks"      # پوشه‌ای که قطعات در آن ذخیره می‌شوند
SPLIT_SIZE = 90 * 1024 * 1024    # ۹۰ مگابایت

def split_file(src_path, dest_dir, original_rel_path):
    """فایل بزرگ را به قطعات ۹۰MB تقسیم کرده و در مسیر مقصد ذخیره می‌کند."""
    os.makedirs(dest_dir, exist_ok=True)
    base_name = os.path.basename(original_rel_path)
    part_num = 0
    with open(src_path, "rb") as f:
        while True:
            chunk = f.read(SPLIT_SIZE)
            if not chunk:
                break
            part_name = f"{base_name}.part{part_num:04d}"
            part_path = os.path.join(dest_dir, part_name)
            with open(part_path, "wb") as p:
                p.write(chunk)
            part_num += 1
    print(f"  تقسیم شد به {part_num} قطعه: {base_name}")

def main():
    if not os.path.exists(MODEL_DIR):
        print("پوشهٔ model_files وجود ندارد. ابتدا دانلود کنید.")
        return

    # پاک‌سازی پوشهٔ chunks (اختیاری)
    if os.path.exists(CHUNKS_DIR):
        shutil.rmtree(CHUNKS_DIR)
    os.makedirs(CHUNKS_DIR, exist_ok=True)

    for root, dirs, files in os.walk(MODEL_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            relative_path = os.path.relpath(full_path, MODEL_DIR)
            target_dir = os.path.join(CHUNKS_DIR, os.path.dirname(relative_path))

            file_size = os.path.getsize(full_path)

            if file_size > SPLIT_SIZE:
                print(f"تقسیم فایل بزرگ: {relative_path} ({file_size} بایت)")
                split_file(full_path, target_dir, relative_path)
            else:
                # کپی مستقیم
                os.makedirs(target_dir, exist_ok=True)
                dest = os.path.join(target_dir, f)
                shutil.copy2(full_path, dest)
                print(f"کپی مستقیم: {relative_path}")

    print("\nتمام فایل‌ها آمادهٔ کامیت در پوشهٔ model_chunks/ هستند.")

if __name__ == "__main__":
    main()
