import requests
import json
import serial
import binascii
import time
import sqlite3
from CRC16 import *


class order:
    def __init__(self,dev_id):
        self.PT_info = 0
        self.CT_info = 0
        self.device_id = ''
        self.db_path = 'Order_data.db'
        self.gw_id = '001'
        self.Device_config = []
        self.Device_data = []
        port = '0'
        relay_address =['000','010','013','0d4','014','02f','04b','100','112','130','14e','16c','18a','1a8','1c6','1d8']
        relay_count = ['06','01','01','05','1b','0c','03','12','1e','1e','1e','1e','1e','1e','09','08']
	try:
	    for i in range(len(relay_count)):
		data_order = dev_id + '040' + relay_address[i] + '00' + relay_count[i]
		self.handle_order(port,data_order)
	    if g_flag:
		self.handle_Device_config(self.db_path)
		config_flag()

	    self.insert_Device_data(self.db_path)
        except:
            pass

    def handle_order(self,port,data):
        ser = serial.Serial(
            port = '/dev/ttyUSB' + port,
            baudrate = 9600,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 1
            )

        send_data = self.make_group(data)
        creat_data = crc16()
        set_data = creat_data.createarray(send_data)
        send_data = data + '%02x'%set_data[-2] + '%02x'%set_data[-1]

        ser.write(bytes.fromhex(send_data))
        time.sleep(1/10)
        num = ser.inWaiting()
        if num:
            recv_data = str(binascii.b2a_hex(ser.read(num)))[2:-1] #十六进制显示方法2
            #print(recv_data)
            argv = self.make_group(recv_data)
            result = creat_data.calcrc(argv)
            if result == 0:
                self.handle_order_function(recv_data,send_data)
                #print(int.from_bytes(bytes().fromhex(recv_data[6:10]),'big')/10.0)
                #print(int.from_bytes(bytes().fromhex(recv_data[10:14]),'big')/10.0)
                #print(int.from_bytes(bytes().fromhex(recv_data[14:18]),'big')/10.0)
        ser.close()

    def handle_order_function(self,data,send_data):
        count = int.from_bytes(bytes().fromhex(data[4:6]),'big')
        #print(count)
        if send_data[2:4] == '04' and send_data[5:8] == '000':
            self.handle_status_data(count,data)
        elif send_data[2:4] == '04' and send_data[5:8] == '010':
            self.handle_clear_data(data)
        elif send_data[2:4] == '04' and send_data[5:8] == '013':
            self.handle_state_data(data)
        elif send_data[2:4] == '04' and send_data[5:8] == '0d4':
            self.handle_relay_data(count,data)
        elif send_data[2:4] == '04' and send_data[5:8] == '014':
            self.handle_recv_data(count,data)
        elif send_data[2:4] == '04' and send_data[5:8] == '02f':
            self.handle_eng_data(count,data)
        elif send_data[2:4] == '04' and send_data[5:8] == '04b':
            self.handle_vector_data(data)
        elif send_data[2:4] == '04' and send_data[5:8] == '100':
            self.handle_thd_data(count,data)
        elif send_data[2:4] == '04' and (send_data[5:8] in ['112','130','14e','16c','18a','1a8']):
            self.handle_thdv_data(count,data)
        elif send_data[2:4] == '04' and send_data[5:8] == '1c6':
            self.handle_cf_data(count,data)
        elif send_data[2:4] == '04' and send_data[5:8] == '1d8':
            self.handle_VI_data(count,data)

    #0-5
    def handle_status_data(self,count,data):
        for i in range(6,6+count*2,4):
            if i == 6:
                self.Device_config.append(str(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')).zfill(4))
            elif (i >= 10 and i < 14) or (i >= 22 and i < 26):
                self.Device_config.append(int.from_bytes(bytes().fromhex(data[i:i+2]),'big'))
                self.Device_config.append(int.from_bytes(bytes().fromhex(data[i+2:i+4]),'big'))
            else:
                self.Device_config.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big'))
        self.PT_info = int.from_bytes(bytes().fromhex(data[14:18]),'big')
        self.CT_info = int.from_bytes(bytes().fromhex(data[18:22]),'big')
        self.device_id = '%02x'%int.from_bytes(bytes().fromhex(data[0:2]),'big')
        #print(self.Device_config)

    #16
    def handle_clear_data(self,data):
        self.Device_config.append(str(int.from_bytes(bytes().fromhex(data[6:10]),'big')))
        #print(self.Device_config)

    #19
    def handle_state_data(self,data):
        self.Device_config.append('{:08b}'.format(int.from_bytes(bytes().fromhex(data[6:8]),'big')))
        self.Device_config.append('{:08b}'.format(int.from_bytes(bytes().fromhex(data[8:10]),'big')))
        #print(self.Device_config)

    #212-216
    def handle_relay_data(self,count,data):
        for i in range(6,6+count*2,4):
            self.Device_config.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/1.0)
        print(self.Device_config)

    #20-46
    def handle_recv_data(self,count,data):
        for i in range(6,6+count*2,4):
            if i < 30:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')*self.PT_info/10.0)
            elif i >= 30 and i < 42:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')*self.CT_info/1000.0)
            elif i >= 42 and i < 46:
                pass
                #self.Device_data.append('{:12b}'.format(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')))
            elif i >= 46 and i < 94:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')*self.PT_info*self.CT_info/10.0)
            elif i >= 94 and i < 110:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/1000.0)
            elif i >= 110 and i < 114:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/100.0)
        #self.data_upload(db_path)
        #print(self.Device_data)

    #47-58
    def handle_eng_data(self,count,data):
        for i in range(6,6+count*2,12):
            self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big') * 65536 + int.from_bytes(bytes().fromhex(data[i+4:i+8]),'big') + int.from_bytes(bytes().fromhex(data[i+8:i+12]),'big')/1000)
        #print(self.Device_data)

    #75-77
    def handle_vector_data(self,data):
        self.Device_data.append(int.from_bytes(bytes().fromhex(data[6:10]),'big')*self.CT_info/1000.0)
        self.Device_data.append(int.from_bytes(bytes().fromhex(data[10:14]),'big')*self.PT_info/10.0)
        self.Device_data.append(int.from_bytes(bytes().fromhex(data[14:18]),'big'))
        #print(self.Device_data)

    #256-273
    def handle_thd_data(self,count,data):
        for i in range(6,6+count*2,4):
            self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/100.0)
        #print(self.Device_data)

    #274-453
    def handle_thdv_data(self,count,data):
        recv_data = []
        for i in range(6,6+count*2,4):
            recv_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/100.0)
        #print(recv_data)
        str_data = str(recv_data)
        self.Device_data.append(str_data)
    
    #454-462
    def handle_cf_data(self,count,data):
        for i in range(6,6+count*2,4):
            if i < 18:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/1000.0)
            else:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')/100.0)
        #print(self.Device_data)

    #472-479
    def handle_VI_data(self,count,data):
        for i in range(6,6+count*2,4):
            if i >= 22 and i < 34:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')*self.CT_info/1000.0)
            else:
                self.Device_data.append(int.from_bytes(bytes().fromhex(data[i:i+4]),'big')*self.PT_info/10.0)
        print(self.Device_data)

    def handle_Device_config(self,db_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        all_dev_info = cursor.execute('select device_id from Device_config;')
        all_dev_id = ()
        for info in all_dev_info:
            all_dev_id = all_dev_id + info
        if self.device_id in all_dev_id:
            self.update_Device_config(self.db_path,self.device_id)
        else:
            self.insert_Device_config(self.db_path)
        #self.data_upload(db_path)
        cursor.close()
        conn.close()

    def update_Device_config(self,db_path,device_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        field_cursor = conn.cursor()
        field_name = field_cursor.execute('PRAGMA table_info(Device_config);')
        field_info = []
        for info in field_name:
            field_info.append(info[1])
        for i in range(len(self.Device_config)):
            if type(self.Device_config[i]) == int:
                update_sql = 'update Device_config set {} = {} where device_id = {};'.format(field_info[i],self.Device_config[i],device_id)
            else:
                update_sql = 'update Device_config set {} = "{}" where device_id = {};'.format(field_info[i],self.Device_config[i],device_id)
            cursor.execute(update_sql)
        cursor.close()
        field_cursor.close()
        conn.commit()
        conn.close()

    def insert_Device_config(self,db_path):
        self.Device_config = [self.gw_id,self.device_id] + self.Device_config
        data = tuple(self.Device_config)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Device_config VALUES {}'.format(data))
        cursor.close()
        conn.commit()
        conn.close()

    def insert_Device_data(self,db_path):
        now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        self.Device_data = [self.gw_id,self.device_id,now_time] + self.Device_data
        data = tuple(self.Device_data)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        field_cursor = conn.cursor()
        field_name = field_cursor.execute('PRAGMA table_info(Device_data);')
        field_info = []
        for info in field_name:
            field_info.append(info[1])
        field_info = tuple(field_info)
        values_info = field_info[1:]
        cursor.execute('INSERT INTO Device_data {} VALUES {}'.format(values_info,data))
        cursor.close()
        field_cursor.close()
        conn.commit()
        conn.close()

    def make_group(self,data):
        send_data = []
        for i in range(0,len(data),2):
            send_data.append(int.from_bytes(bytes().fromhex(data[i]+data[i+1]),'big'))
        return send_data

global g_flag
g_flag = True
        
def config_flag():
    global g_flag
    g_flag = False

if __name__ == "__main__":
    while True:
        order('01')
        order('02')
