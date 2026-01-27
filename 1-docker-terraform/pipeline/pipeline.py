import sys
import pandas as pd # Chúng ta sẽ cài cái này sau

# In ra các tham số đầu vào (arguments)
print("arguments", sys.argv)

# Lấy tham số thứ nhất làm "ngày" (tham số thứ 0 là tên file script)
day = sys.argv[1] 
print(f"Job finished successfully for day = {day}")

# Tạo dữ liệu giả lập
df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
print(df.head())

# Lưu ra file parquet (format tối ưu cho Big Data)
output_file = f"output_day_{day}.parquet"
df.to_parquet(output_file)
print(f"File saved to {output_file}")