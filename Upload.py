import requests
import json
import sqlite3

def data_upload(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    t_cursor = conn.cursor()
    d_cursor = conn.cursor()
    #d_info = d_cursor.execute('select * from Device_data where device_id="01" Order by id Desc limit 1;')
    #t_info = t_cursor.execute('PRAGMA table_info(Device_data);')
    d_info = d_cursor.execute('select * from Device_config where device_id="01" limit 1;')
    t_info = t_cursor.execute('PRAGMA table_info(Device_config);') 

    data_info = []
    for info in d_info:
        for i in range(len(info)):
            data_info.append(info[i])
    #print(data_info)
    #data_info = data_info[1:]

    table_info = []
    for info in t_info:
        table_info.append(info[1])
    #table_info = table_info[1:]
    print(table_info)

    all_info = {}
    for i in range(len(table_info)):
        all_info[table_info[i]] = data_info[i]

    print(all_info)
    d_cursor.close()
    t_cursor.close()
    conn.commit()
    conn.close()

    #req = requests.post('http://127.0.0.1:5005', json = all_info)
    req = requests.post('http://192.168.1.241:5000/Device_config', json = all_info)
    #print(req.json())

data_upload('Order_data.db')