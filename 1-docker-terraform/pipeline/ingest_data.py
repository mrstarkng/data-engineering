import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine
import click

@click.command()
@click.option('--user', required=True, help='User name for postgres')
@click.option('--password', required=True, help='Password for postgres')
@click.option('--host', required=True, help='Host for postgres')
@click.option('--port', required=True, help='Port for postgres')
@click.option('--db', required=True, help='Database name for postgres')
@click.option('--table_name', required=True, help='Name of the table where we will write the results to')
@click.option('--url', required=True, help='URL of the csv file')
def main(user, password, host, port, db, table_name, url):
    
    # 1. Cấu hình kết nối (Lưu ý: dùng postgresql+psycopg như bài trước đã fix)
    connection_string = f'postgresql+psycopg://{user}:{password}@{host}:{port}/{db}'
    engine = create_engine(connection_string)

    # 2. Download file về máy (để tránh lỗi mạng khi đang chạy loop)
    csv_name = 'output.csv.gz'
    
    # Sử dụng lệnh curl của hệ thống để tải file (nhanh hơn python requests)
    # Nếu bạn dùng Windows (PowerShell), có thể cần thay bằng lệnh khác hoặc thư viện requests
    print(f"Downloading {url} ...")
    os.system(f"curl -L {url} -o {csv_name}") 
    print("Download finished.")

    # 3. Chuẩn bị Schema
    dtype_dict = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64"
    }

    parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

    # 4. Đọc file theo chunks
    df_iter = pd.read_csv(
        csv_name, 
        dtype=dtype_dict, 
        parse_dates=parse_dates,
        iterator=True, 
        chunksize=100000
    )

    # 5. Xử lý chunk đầu tiên (Tạo bảng)
    df = next(df_iter)
    
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')
    print("Inserted first chunk.")

    # 6. Vòng lặp các chunk còn lại
    try:
        while True: 
            t_start = time()
            
            df = next(df_iter)

            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print(f'Inserted another chunk, took {t_end - t_start:.3f} second')
            
    except StopIteration:
        print("Finished ingesting data into the postgres database")

if __name__ == '__main__':
    main()