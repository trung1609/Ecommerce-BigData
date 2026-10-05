# Phân tích hành vi khách hàng và dự đoán khả năng mua hàng

Dự án môn **Phân tích và Tích hợp Dữ liệu lớn** trên dữ liệu thương mại điện tử, dành cho nhóm **3 người trong 2 tuần**.

**Trạng thái hiện tại: đã chuẩn bị Pipeline 1 – Raw Data. Pipeline 2–6 mới là kế hoạch, chưa có mã triển khai.** README này hướng dẫn thực hiện bước 1 và mô tả đường đi cho các bước tiếp theo. Chỉ chuyển sang Pipeline 2 khi người dùng xác nhận.

## 1. Mục tiêu dự án

Dự án hướng tới hai kết quả:

- Phân tích hành vi: khách hàng tương tác với sản phẩm như thế nào, nhóm sản phẩm nào được quan tâm và hành vi thay đổi theo thời gian ra sao.
- Dự đoán mua hàng: xây dựng mô hình ước lượng khả năng mua dựa trên thông tin có sẵn trước thời điểm cần dự đoán.

Dataset đã chọn: **REES46 Multi-category Behavior Events**, file **`2019-Oct.csv`**. File hiện có dung lượng **5.668.612.855 byte**, khoảng **5,67 GB**.

Nguồn tải cụ thể, giấy phép và thời điểm tải chưa được ghi nhận; nhóm cần bổ sung từ nơi đã tải file. Chưa thống kê số dòng hoặc đánh giá chất lượng dữ liệu.

## 2. Hiểu luồng làm việc

Một pipeline là một giai đoạn có đầu vào, công việc xử lý và đầu ra rõ ràng. Dự án gồm 6 giai đoạn:

```text
1. Raw Data       Giữ nguyên CSV gốc
        ↓
2. Ingestion      Đọc CSV vào hệ thống xử lý
        ↓
3. ETL/ELT        Làm sạch, chuẩn hóa và tạo dữ liệu cần dùng
        ↓
4. Storage        Lưu dữ liệu đã xử lý để tái sử dụng
        ↓
5. Machine Learning   Huấn luyện và đánh giá dự đoán mua hàng
        ↓
6. Visualization  Hiển thị phân tích và kết quả mô hình
```

Dashboard sẽ sử dụng cả bảng phân tích từ bước 4 và kết quả mô hình từ bước 5. Việc ghi dữ liệu có thể diễn ra ngay trong quá trình xử lý; bước 4 làm rõ cách tổ chức và sử dụng lại các đầu ra đó.

| Thuật ngữ | Cách hiểu trong dự án |
| --- | --- |
| CSV | File văn bản dạng bảng, là định dạng đầu vào đã chọn |
| Spark / PySpark | Công cụ xử lý dữ liệu; PySpark là giao diện Python của Spark |
| DataFrame | Bảng dữ liệu có cột, được chương trình dùng để xử lý |
| ETL | Đọc dữ liệu → biến đổi → lưu kết quả |
| ELT | Đọc dữ liệu → lưu vào nơi xử lý → biến đổi |
| Parquet | Định dạng lưu theo cột, dự kiến dùng cho dữ liệu đã xử lý |
| Đặc trưng | Thông tin đầu vào của mô hình, ví dụ số lần tương tác trước thời điểm dự đoán |
| Nhãn | Kết quả cần dự đoán, ví dụ có mua trong khoảng thời gian đã quy định hay không |
| SHA-256 | Mã kiểm tra nội dung file, dùng để phát hiện sự thay đổi |

Giai đoạn đầu dự kiến chạy trên máy cá nhân. Nhóm chưa cần cụm máy, Kafka, Airflow hoặc Kubernetes. PostgreSQL chỉ là lựa chọn bổ sung nếu thực sự cần.

## 3. Cấu trúc thư mục

```text
ecommerce-bigdata/
├── data/
│   ├── bronze/
│   │   ├── .gitkeep
│   │   └── 2019-Oct.csv
│   ├── silver/
│   │   └── .gitkeep
│   └── gold/
│       └── .gitkeep
├── src/
│   ├── ingestion/
│   ├── etl/
│   ├── storage/
│   ├── analytics/
│   └── ml/
├── dashboard/
├── models/
├── notebooks/
├── config/
├── docs/
│   ├── project_structure.md
│   ├── raw_data.md
│   └── raw_data_manifest.json
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

Các thư mục chức năng trong `src/`, cùng `src/` và các thư mục `dashboard/`, `models/`, `notebooks/`, `config/`, `tests/` có `README.md` mô tả vai trò; cây trên lược bỏ các file này cho dễ nhìn.

| Vị trí | Chức năng |
| --- | --- |
| `data/bronze/` | Giữ CSV gốc; không sửa hoặc ghi đè |
| `data/silver/` | Dữ liệu đã làm sạch ở các bước sau |
| `data/gold/` | Bảng tổng hợp và đặc trưng phục vụ phân tích, ML, dashboard |
| `src/ingestion/` | Mã tiếp nhận và đọc dữ liệu của Pipeline 2 |
| `src/etl/` | Mã làm sạch, chuẩn hóa và biến đổi của Pipeline 3 |
| `src/storage/` | Mã quản lý đọc/ghi dữ liệu của Pipeline 4 |
| `src/analytics/` | Mã tính các chỉ số phân tích hành vi |
| `src/ml/` | Mã tạo tập học, huấn luyện và đánh giá của Pipeline 5 |
| `dashboard/` | Ứng dụng Streamlit của Pipeline 6 |
| `models/` | Mô hình được lưu sau khi huấn luyện |
| `notebooks/` | Notebook khám phá và thử nghiệm |
| `config/` | Cấu hình đường dẫn, tham số; không lưu mật khẩu |
| `docs/` | Thiết kế, hồ sơ dữ liệu và tài liệu dự án |
| `tests/` | Kiểm thử khi có mã xử lý |
| `requirements.txt` | Danh sách thư viện Python; hiện chỉ có chú thích |
| `.gitignore` | Quy tắc bỏ qua CSV, dữ liệu sinh ra, môi trường và file cục bộ |
| `.gitkeep` | File rỗng giúp lưu thư mục trống trong Git |
| `README.md` | Hướng dẫn tổng quan và thứ tự thực hiện |

Chi tiết từng file: [docs/project_structure.md](docs/project_structure.md).

## 4. Pipeline 1 – Raw Data: thực hiện ngay

**Mục tiêu:** có một file gốc ở đúng vị trí, thông tin nhận diện file và quy tắc bảo vệ dữ liệu. Bước này chưa đọc dữ liệu vào Spark hoặc làm sạch dữ liệu.

### Bước 1. Mở thư mục dự án

Mở PowerShell và chạy:

```powershell
cd 'E:\Trung\Code\Python\Phân tích dữ liệu lớn\ecommerce-bigdata'
```

### Bước 2. Kiểm tra vị trí CSV

Đường dẫn tương đối bắt buộc:

```text
data/bronze/2019-Oct.csv
```

Trên máy hiện tại:

```text
E:\Trung\Code\Python\Phân tích dữ liệu lớn\ecommerce-bigdata\data\bronze\2019-Oct.csv
```

```powershell
Test-Path -LiteralPath '.\data\bronze\2019-Oct.csv'
Get-Item -LiteralPath '.\data\bronze\2019-Oct.csv' | Select-Object Name, Length
```

Kết quả mong đợi: `True`, tên `2019-Oct.csv` và `Length` bằng `5668612855`. Nếu file không tồn tại hoặc kích thước khác, kiểm tra lại file trước khi tiếp tục.

### Bước 3. Đối chiếu tính toàn vẹn

Hồ sơ file nằm ở [docs/raw_data_manifest.json](docs/raw_data_manifest.json). File này ghi dung lượng, SHA-256, tên bộ dữ liệu và những thông tin nguồn còn thiếu.

Chạy đoạn sau để so sánh hash hiện tại với hồ sơ:

```powershell
$manifest = Get-Content -Raw -Encoding UTF8 '.\docs\raw_data_manifest.json' | ConvertFrom-Json
$actualHash = (Get-FileHash -LiteralPath '.\data\bronze\2019-Oct.csv' -Algorithm SHA256).Hash
$actualHash -eq $manifest.sha256
```

Kết quả mong đợi là `True`. Tính hash đọc toàn bộ file nên có thể mất vài phút, nhưng không sửa nội dung. Nếu kết quả là `False`, xác minh lại file; không đổi mã trong manifest chỉ để phép so sánh khớp.

Khi chuẩn bị Pipeline 1, bản sao đã được xác nhận khớp SHA-256 với file nguồn lúc đó. Thông tin đường dẫn nguồn trong manifest là lịch sử chuẩn bị; không yêu cầu file ở thư mục cha phải luôn tồn tại. Hash xác nhận nội dung khớp bản đã ghi nhận, không xác nhận nguồn tải có đáng tin hay không.

### Bước 4. Nhận diện các cột

Dòng tiêu đề đã quan sát được gồm 9 cột:

```text
event_time,event_type,product_id,category_id,category_code,brand,price,user_id,user_session
```

Ý nghĩa dự kiến: thời điểm sự kiện, loại sự kiện, mã sản phẩm, mã danh mục, mã phân loại danh mục, thương hiệu, giá, mã người dùng và mã phiên truy cập. Nhóm sẽ đối chiếu tài liệu nguồn và kiểm tra dữ liệu thực tế ở bước sau.

Hiện chưa kết luận về kiểu dữ liệu, múi giờ, đơn vị tiền, số dòng, giá trị thiếu hoặc trùng lặp. Không cần mở toàn bộ CSV bằng Excel để làm bước 1.

### Bước 5. Giữ nguyên dữ liệu gốc

- Không xóa dòng, sửa giá trị, điền dữ liệu thiếu hoặc đổi định dạng trong `data/bronze/`.
- Khi xử lý ở bước sau, lưu kết quả vào `silver/` hoặc `gold/`.
- Giữ bản sao dự phòng ở nơi an toàn; Git không sao lưu CSV đã bị bỏ qua.
- Bổ sung URL tải, giấy phép và ngày tải thực tế vào manifest khi nhóm có thông tin. Không phỏng đoán các mục đang là `null`.

### Bước 6. Kiểm tra Git bỏ qua CSV

`.gitignore` có quy tắc sau, áp dụng cho mọi thư mục con và cả phần mở rộng viết hoa:

```gitignore
*.[cC][sS][vV]
```

Nếu dự án đã là Git repository, kiểm tra bằng:

```powershell
git check-ignore -v -- data/bronze/2019-Oct.csv
git ls-files -- '*.csv' '*.CSV'
```

Lệnh đầu cần hiển thị quy tắc bỏ qua từ `.gitignore`; có thể là quy tắc bỏ qua toàn bộ `data/`. Lệnh thứ hai cần không có kết quả. `.gitignore` không tự gỡ những file Git đã theo dõi.

Nếu lệnh thứ hai liệt kê CSV, gỡ đúng đường dẫn đó khỏi Git index, ví dụ:

```powershell
git rm --cached -- data/bronze/2019-Oct.csv
```

`--cached` chỉ gỡ khỏi danh sách Git theo dõi, không xóa file dữ liệu trên ổ đĩa. Chỉ dùng lệnh này khi file đang được Git theo dõi. Nếu CSV đã có trong commit cũ, thao tác này không xóa CSV khỏi lịch sử cũ.

### Bước 7. Kết thúc Pipeline 1

Kiểm tra các điều kiện:

- CSV tồn tại đúng vị trí và có dung lượng khớp hồ sơ.
- SHA-256 khớp manifest.
- CSV không nằm trong danh sách Git theo dõi.
- Nhóm hiểu quy tắc không sửa dữ liệu gốc.
- Các thông tin nguồn chưa biết được ghi rõ, không tự suy đoán.

**Dừng tại đây và chờ xác nhận trước khi triển khai Pipeline 2. Chưa cần cài Spark, Java hoặc thư viện trong bước này.**

Thiết kế chi tiết: [docs/raw_data.md](docs/raw_data.md).

## 5. Pipeline 2–6: kế hoạch cho các bước sau

Phần này mô tả công việc dự kiến để cả nhóm hiểu quy trình. Chưa có script hoặc lệnh chạy cho các bước này.

### Pipeline 2 – Ingestion

**Đầu vào:** `data/bronze/2019-Oct.csv`.

1. Kiểm tra cấu hình máy và thống nhất phiên bản Python, Java, PySpark tương thích.
2. Tạo môi trường Python riêng, bổ sung thư viện cần thiết vào `requirements.txt`.
3. Xây dựng chương trình trong `src/ingestion/` để đọc CSV bằng Spark theo schema đã xác định.
4. Kiểm tra tên cột, khả năng đọc dữ liệu và ghi nhận các vấn đề đọc file.

**Đầu ra dự kiến:** DataFrame đầu vào và kết quả kiểm tra đọc dữ liệu. Đạt yêu cầu khi chương trình chạy lại được và đọc đúng cấu trúc; chưa tự sửa dữ liệu gốc.

### Pipeline 3 – ETL/ELT Processing

**Đầu vào:** dữ liệu đọc được từ Pipeline 2.

1. Thống kê giá trị thiếu, lỗi kiểu dữ liệu, bản ghi trùng và các giá trị bất thường.
2. Thống nhất quy tắc xử lý theo từng cột, ghi rõ lý do giữ hoặc loại bản ghi.
3. Chuẩn hóa thời gian, kiểu số và các cột cần dùng trong `src/etl/`.
4. Tạo các bảng tổng hợp hành vi trong `src/analytics/`; định nghĩa rõ mỗi dòng đại diện cho sự kiện, phiên hay người dùng.
5. Đối chiếu số bản ghi trước/sau và lưu báo cáo xử lý.

**Đầu ra dự kiến:** dữ liệu sạch và bảng tổng hợp sẵn sàng lưu. Không mặc định xóa mọi dòng thiếu hoặc mọi sự kiện giống nhau trước khi hiểu ý nghĩa của chúng.

### Pipeline 4 – Storage

**Đầu vào:** dữ liệu đã xử lý ở Pipeline 3.

1. Lưu dữ liệu sạch dưới dạng Parquet trong `data/silver/`.
2. Lưu bảng tổng hợp và các bảng đặc trưng phù hợp trong `data/gold/`.
3. Quy định tên đầu ra, schema và cách chạy lại mà không ghi đè dữ liệu gốc.
4. Đọc lại đầu ra để đối chiếu schema, số bản ghi và một số kết quả tổng hợp.

**Đầu ra dự kiến:** dữ liệu có thể tái sử dụng cho ML và dashboard. `src/storage/` chứa logic đọc/ghi chung nếu cần. PostgreSQL chưa bắt buộc.

### Pipeline 5 – Machine Learning

**Đầu vào:** bảng đặc trưng và dữ liệu cần thiết từ tầng đã xử lý.

1. Chốt bài toán: dự đoán cho người dùng hay phiên truy cập, tại thời điểm nào, trong khoảng thời gian tương lai nào.
2. Xác định nhãn mua hàng và cửa sổ quan sát. Chỉ lấy đặc trưng đã có tại thời điểm dự đoán; không đưa hành vi mua cần dự đoán vào đầu vào.
3. Chia tập huấn luyện, kiểm định và kiểm tra theo thời gian phù hợp, tránh sử dụng thông tin tương lai.
4. Tạo mốc so sánh đơn giản, sau đó huấn luyện một mô hình phù hợp bằng Spark MLlib.
5. Đánh giá khả năng phát hiện mua hàng và số dự đoán sai; xem precision, recall, F1 và PR-AUC phù hợp với bài toán, không chỉ accuracy.
6. Lưu mô hình vào `models/`, ghi tham số và kết quả đánh giá vào tài liệu.

**Đầu ra dự kiến:** mô hình đã đánh giá, kết quả dự đoán và báo cáo giới hạn. Cách tạo nhãn và mô hình cụ thể chưa được chốt ở Pipeline 1.

### Pipeline 6 – Visualization

**Đầu vào:** bảng tổng hợp ở `gold/` và kết quả đánh giá/dự đoán từ Pipeline 5.

1. Xây dựng ứng dụng Streamlit trong `dashboard/`.
2. Hiển thị tổng quan dữ liệu và các chỉ số hành vi đã định nghĩa rõ.
3. Thêm biểu đồ theo thời gian, sản phẩm hoặc danh mục tùy dữ liệu đã kiểm tra.
4. Hiển thị kết quả mô hình và giải thích ngắn gọn cách đọc các chỉ số.
5. Đối chiếu số liệu dashboard với bảng nguồn và chuẩn bị kịch bản demo.

**Đầu ra dự kiến:** dashboard chạy được và hướng dẫn sử dụng. Ưu tiên đọc bảng tổng hợp đã lưu để tránh xử lý lại toàn bộ CSV mỗi lần mở giao diện.