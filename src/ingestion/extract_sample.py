import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

def extract_sample(
    input_path: str = "data/bronze/2019-Oct.csv",
    output_path: str = "data/bronze/sample_100k.csv",
    num_rows: int = 100_000
):
    if not os.path.exists(input_path):
        print(f"[LỖI] Không tìm thấy file dữ liệu gốc: {input_path}")
        sys.exit(1)

    print(f"[*] Bắt đầu trích xuất {num_rows:,} dòng từ: {input_path}")
    start_time = time.time()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    lines_written = 0
    with open(input_path, "r", encoding="utf-8", errors="ignore") as fin, \
         open(output_path, "w", encoding="utf-8", newline="") as fout:
        
        # Đọc và ghi dòng tiêu đề (Header)
        header = fin.readline()
        fout.write(header)

        # Ghi num_rows dòng dữ liệu tiếp theo
        for i in range(num_rows):
            line = fin.readline()
            if not line:
                break
            fout.write(line)
            lines_written += 1

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

    print(f"[THÀNH CÔNG] Đã tạo file mẫu thành công!")
    print(f" - Đường dẫn file mẫu: {output_path}")
    print(f" - Số dòng dữ liệu (chưa tính header): {lines_written:,} dòng")
    print(f" - Kích thước file mẫu: {file_size_mb:.2f} MB")
    print(f" - Thời gian thực thi: {elapsed:.2f} giây")

if __name__ == "__main__":
    extract_sample()
