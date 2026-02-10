import pandas as pd
from sqlalchemy import create_engine

# 1. URL của file Zones (File CSV nhỏ chứa tên các Quận/Huyện)
url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

# 2. Kết nối Database (Lưu ý: Chạy từ máy host nên dùng localhost)
engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')

# 3. Đọc và nạp vào DB
print(f"Downloading and loading zones data from {url}...")
df = pd.read_csv(url)

# Ghi vào bảng tên là "zones"
df.to_sql(name='zones', con=engine, if_exists='replace')

print("Success! Table 'zones' created.")
print(f"Loaded {len(df)} rows.")