import pandas as pd
import mysql.connector


def db_to_xlsx(dbconfig, sqlstr):
    connect = mysql.connector.connect(**dbconfig)
    df = pd.read_sql(sqlstr, con = connect)
    print(df.head())
    df.to_excel('./17result.xlsx')
    connect.close()

dbconfig = {
    'host': '0.0.0.0',
    'user': 'root',
    'password': '!QAZ2wsx3edc',
    'database': 'EMG_zhuowei',
    'charset': 'utf8'
}

sqlstr="SELECT * FROM `eng_real` WHERE gw_mac='201827001010017' AND m_time>='2018-08-22 00:00:00.000000' AND m_time <='2018-08-23 00:00:00.000000' order by m_time ASC"
db_to_xlsx(dbconfig, sqlstr)
