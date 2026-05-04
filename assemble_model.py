import os
import shutil

CHUNKS_DIR = "model_chunks"
OUTPUT_DIR = "model_files"

def main():
    if not os.path.exists(CHUNKS_DIR):
        print("پوشهٔ model_chunks پیدا نشد. ابتدا ریپو را clone کنید.")
        return

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # مرحله ۱: کپی فایل‌های کوچک (بدون .part)
    for root, dirs, files in os.walk(CHUNKS_DIR):
        for f in files:
            if ".part" not in f:
                rel_dir = os.path.relpath(root, CHUNKS_DIR)
                dest_dir = os.path.join(OUTPUT_DIR, rel_dir)
                os.makedirs(dest_dir, exist_ok=True)
                src = os.path.join(root, f)
                shutil.copy2(src, os.path.join(dest_dir, f))
                print(f"کپی مستقیم: {os.path.join(rel_dir, f)}")

    # مرحله ۲: یکپارچه‌سازی فایل‌های تکه‌شده
    for root, dirs, files in os.walk(CHUNKS_DIR):
        part_groups = {}
        for f in files:
            if ".part" in f:
                # base نام فایل بدون شماره قطعه است
                base = f.rsplit(".part", 1)[0]
                part_groups.setdefault(base, []).append(f)

        for base, parts in part_groups.items():
            rel_dir = os.path.relpath(root, CHUNKS_DIR)
            output_path = os.path.join(OUTPUT_DIR, rel_dir, base)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # مرتب‌سازی بر اساس عدد داخل .partNNNN
            parts_sorted = sorted(parts, key=lambda x: int(x.rsplit(".part", 1)[1]))

            print(f"یکپارچه‌سازی: {os.path.join(rel_dir, base)} ({len(parts_sorted)} قطعه)")
            with open(output_path, "wb") as out:
                for part in parts_sorted:
                    part_path = os.path.join(root, part)
                    with open(part_path, "rb") as pf:
                        out.write(pf.read())

    print("\n✅ مدل کامل در پوشهٔ model_files بازسازی شد.")

if __name__ == "__main__":
    main()
