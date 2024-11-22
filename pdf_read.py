import pdfplumber
import pandas as pd
import re

pdf_path = 'some.pdf'
# 目標表格標題清單，用於從PDF中提取所需的表格
titles = ('Current Day Executed Trades','Journals and Cash Sweeps')

# 用字典儲存提取的DataFrame，以表格標題作為鍵
results = {}


# 逐頁讀取pdf
with pdfplumber.open(pdf_path) as pdf:
    # 先取得所有表格
    # 方便後面辨別資料是否跨頁
    all_tables = []
    for page in range(len(pdf.pages)):
        print("搜尋第",page+1,"頁")
        page_tables = pdf.pages[page].crop((10,10,612,780)).extract_tables()
        
        all_tables.extend(page_tables) 


# 處裡取得的所有表格  
# 用正則辨別table是標題還是跨頁的表格
for table_index in range(len(all_tables)):
    if not re.fullmatch(r"[A-Za-z ]+",all_tables[table_index][0][0]):
        #將跨頁資料併入前面的table
        all_tables[table_index-1].extend(all_tables[table_index])

# 建立(標題:表格)的對應字典
title_table_map = {table[0][0]: table for table in all_tables}
# 依標題名稱讀取需求表格
for title in titles:
    table = title_table_map.get(title)
    if table:
        if title == 'Current Day Executed Trades':
            table.pop(1)
        # 取得表格的行名
        col_names = table[1]
        # 取得內容數據
        data = table[2:]
    else:
        raise Exception(f"找不到表格:{title}")

    # 處理換行符
    col_names = [col_name.replace('\n',' ') for col_name in col_names]
    data = [[element.replace('\n', ' ') for element in record] for record in data]

    results[title] = pd.DataFrame(data, columns=col_names)

print(results['Current Day Executed Trades'])