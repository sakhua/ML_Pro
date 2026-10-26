# Nhóm 05 – Bài kiểm tra 1 (Học máy, KHMT K22)

**Đề tài:** So sánh các thuật toán học máy truyền thống trong dự đoán tương tác thuốc dựa trên cấu trúc hóa học
**Giai đoạn 1:** Xác định bài toán, khảo sát và tiền xử lý dữ liệu

**Thành viên:** Sùng A Khua (DTC235160020), Hoàng Bảo Ngọc (DTC235160033)

## Cấu trúc thư mục

```
Nhom 05/
├── BaoCao_Nhom_05.pdf            # Báo cáo theo mẫu của bộ môn (biên dịch từ LaTeX/)
├── LaTeX/
│   ├── BaoCao_Nhom_05.tex        # Mã nguồn LaTeX (biên dịch bằng XeLaTeX)
│   └── images/                   # Hình do notebook tạo ra
├── data/
│   ├── raw/                      # Dữ liệu trích xuất từ DrugBank 5.1
│   │   ├── drugs.csv             # 17.430 thuốc
│   │   ├── ddi_pairs.csv.gz      # 1.428.193 cặp tương tác duy nhất
│   │   └── meta.txt              # Phiên bản, ngày xuất, thống kê
│   └── processed/                # Notebook tạo ra
│       ├── drugs_clean.csv       # 2.472 thuốc sau làm sạch + đặc trưng mô tả
│       ├── dataset_pairs.csv.gz  # 100.000 cặp (nhãn, tập train/test, nhóm thuốc mới)
│       ├── data_quality_issues.csv
│       └── eda_stats.json        # Toàn bộ số liệu dùng trong báo cáo
├── notebooks/
│   └── 01_EDA_TienXuLy.ipynb     # Khảo sát + tiền xử lý (đã chạy, có sẵn kết quả)
├── src/
│   └── extract_drugbank.py       # Trích xuất drugs.csv, ddi_pairs.csv.gz từ DrugBank XML
├── requirements.txt
└── PhanCong_NhatKy.md            # Bảng phân công + nhật ký công việc
```

## Cách chạy lại

```bash
pip install -r requirements.txt
# (Tùy chọn) trích xuất lại từ file gốc DrugBank:
python src/extract_drugbank.py "duong/dan/full database.xml" data/raw
# Mở notebooks/01_EDA_TienXuLy.ipynb và chọn Run All (~1–2 phút, CPU)
```

- Notebook dùng đường dẫn tương đối (`../data/raw`, `../data/processed`, `../LaTeX/images`), nên cần chạy từ trong thư mục `notebooks/`.
- Mọi bước ngẫu nhiên cố định `SEED = 42`, chạy lại sẽ ra đúng số liệu trong báo cáo.

## Dữ liệu

- Nguồn: DrugBank 5.1, file `full database.xml`, xuất ngày 02/01/2025 (https://go.drugbank.com/releases/latest, cần tài khoản học thuật).
- Dữ liệu được dùng theo giấy phép học thuật phi thương mại của DrugBank; thư mục `data/raw/` chỉ phục vụ chấm bài, không phân phối công khai.

## Biên dịch báo cáo

Overleaf: tải thư mục `LaTeX/` lên, chọn *Menu → Compiler → XeLaTeX*.
Trên máy: `latexmk -xelatex BaoCao_Nhom_05.tex` (chạy trong thư mục `LaTeX/`).
