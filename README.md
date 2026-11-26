# Nhóm 19 – Dự án Học máy (KHMT K22)

**Đề tài:** So sánh các thuật toán học máy truyền thống trong dự đoán tương tác thuốc dựa trên cấu trúc hóa học
**Nội dung:** Bài kiểm tra 1 (khảo sát, tiền xử lý), Bài kiểm tra 2 (huấn luyện, đánh giá), Bài kiểm tra 3 (tối ưu, cải tiến)

**Thành viên:** Sùng A Khua (DTC235160020), Hoàng Bảo Ngọc (DTC235160033)

## Cấu trúc thư mục

```
Nhom 19/
├── BaoCao_Nhom_19.pdf            # Báo cáo theo mẫu của bộ môn (biên dịch từ LaTeX/)
├── LaTeX/
│   ├── BaoCao_Nhom_19.tex        # Mã nguồn LaTeX (biên dịch bằng XeLaTeX)
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
├── notebooks/                    # Đã chạy, có sẵn kết quả; chạy theo thứ tự 01 → 02 → 03
│   ├── 01_EDA_TienXuLy.ipynb     # BKT1: khảo sát + tiền xử lý
│   ├── 02_HuanLuyen_DanhGia.ipynb# BKT2: mô hình cơ sở, LR, RF, XGBoost, SVM; 5-fold; tập kiểm tra; phân tích lỗi
│   └── 03_ToiUu_CaiTien.ipynb    # BKT3: hạn chế, cải tiến đặc trưng, Random Search, Voting, thuốc mới
├── results/                      # Số liệu do notebook 02, 03 tạo ra (json, csv)
├── src/
│   ├── extract_drugbank.py       # Trích xuất drugs.csv, ddi_pairs.csv.gz từ DrugBank XML
│   └── ddi_features.py           # Tạo vân tay Morgan/MACCS và các cách biểu diễn cặp thuốc
├── requirements.txt
├── .gitignore                    # Bỏ qua file build LaTeX, cache, __pycache__
└── PhanCong_NhatKy.md            # Bảng phân công + nhật ký công việc
```

## Cách chạy lại

```bash
pip install -r requirements.txt
# (Tùy chọn) trích xuất lại từ file gốc DrugBank:
python src/extract_drugbank.py "duong/dan/full database.xml" data/raw
# Mở lần lượt trong thư mục notebooks/ và chọn Run All:
#   01_EDA_TienXuLy.ipynb      (~2 phút)
#   02_HuanLuyen_DanhGia.ipynb (~45 phút lần đầu, CPU 2 nhân)
#   03_ToiUu_CaiTien.ipynb     (~2,5–3 giờ lần đầu, CPU 2 nhân; cần chạy 02 trước)
```

- Notebook dùng đường dẫn tương đối (`../data/raw`, `../data/processed`, `../LaTeX/images`), nên cần chạy từ trong thư mục `notebooks/`.
- Mọi bước ngẫu nhiên cố định `SEED = 42`, chạy lại sẽ ra đúng số liệu trong báo cáo.
- Các bước tốn thời gian của notebook 02, 03 được lưu trong `results/cache/`; khi có sẵn thư mục này, chạy lại mỗi notebook chỉ mất vài phút. Xóa `results/cache/` để tính lại toàn bộ từ đầu.
- Notebook 03 cần khoảng 5,5 GB RAM ở bước nặng nhất (Random Forest trên 80.000 mẫu).
- Thư mục `results/cache/` không được đưa lên kho vì sinh lại được; vì vậy lần chạy đầu sau khi tải kho về sẽ mất trọn thời gian nêu trên.

## Dữ liệu

- Nguồn: DrugBank 5.1, file `full database.xml`, xuất ngày 02/01/2025 (https://go.drugbank.com/releases/latest, cần tài khoản học thuật).
- Dữ liệu được dùng theo giấy phép học thuật phi thương mại của DrugBank; thư mục `data/raw/` chỉ phục vụ chấm bài, không phân phối công khai.

## Biên dịch báo cáo

Overleaf: tải thư mục `LaTeX/` lên, chọn *Menu → Compiler → XeLaTeX*.
Trên máy: `latexmk -xelatex BaoCao_Nhom_19.tex` (chạy trong thư mục `LaTeX/`).
