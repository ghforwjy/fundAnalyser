"""
创建fund_dividend表
"""
import sqlite3

conn = sqlite3.connect('../fund.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS fund_dividend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    imp_anndate DATE,
    base_date DATE,
    div_proc VARCHAR(20),
    record_date DATE,
    ex_date DATE,
    pay_date DATE,
    earpay_date DATE,
    net_ex_date DATE,
    div_cash DECIMAL(10,6),
    base_unit DECIMAL(12,2),
    ear_distr DECIMAL(15,2),
    ear_amount DECIMAL(15,2),
    account_date DATE,
    base_year VARCHAR(10),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, ex_date),
    FOREIGN KEY (fund_code) REFERENCES fund_info(fund_code) ON DELETE CASCADE
)
''')

# 创建索引
cursor.execute('CREATE INDEX IF NOT EXISTS idx_div_fund_code ON fund_dividend(fund_code)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_div_ann_date ON fund_dividend(ann_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_div_ex_date ON fund_dividend(ex_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_div_pay_date ON fund_dividend(pay_date)')

conn.commit()
print('fund_dividend表创建成功')

# 验证
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fund_dividend'")
result = cursor.fetchone()
print(f'表存在: {result is not None}')
conn.close()
