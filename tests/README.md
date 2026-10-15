# tests

Chạy kiểm thử feature engineering bằng Spark local:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_feature_engineering.py' -v
```

Test xác nhận nhãn theo phiên, cutoff trước purchase, phiên chỉ có purchase và giờ UTC.
