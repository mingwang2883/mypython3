#!/usr/bin/env python
# -*-coding:utf-8 -*-
import math
import serial
import argparse
import numpy as np
import time
def getArgs():
    parser = argparse.ArgumentParser(description='manual to serial camera configuration')
    parser.add_argument('--COM', type=int, default=5)
    args = parser.parse_args()
    return args


class serialCamera(object):
    def __init__(self,comserial):
        self.port = serial.Serial(comserial, baudrate=38400,bytesize=serial.EIGHTBITS, timeout=2)

    def __del__(self):
        self.port.close()

    def reset(self,no):
        #复位
        cmd = [0x56, no, 0x26, 0x00]
        # cmd = [0x56, 0x01, 0x31, 0x05, 0x04, 0x01, 0x00, 0x06, 0x02]
        strsrc = "76 %02x 26 00 " % no
        self.port.write(cmd)

        response = self.port.read(4)

        res = ''.join(['%02x ' % b for b in response]) #注意：多附加了个空格
        if (res == strsrc):
            return True
        else:
            return False
    def modifyNo(self,no1,no2 = 0):
        #修改序号之后，以旧序号复位，才是新序号使用
        cmd = [0x56, no1, 0x31, 0x05, 0x04, 0x01, 0x00, 0x06, no2]
        strsrc= "76 %02x 31 00 00 " % no1
        print(cmd)
        print(strsrc)
        self.port.write(cmd)
        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # 注意：多附加了个空格
        if (res == strsrc):
             return self.reset(no1)
        else:
             return False

    def setZipRate(self,no, XX=0x36):
        # 设置图像压缩率，XX=00~FF,默认36
        cmd = [0x56, no, 0x31, 0x05, 0x01, 0x01, 0x12, 0x04, XX]
        # cmd = [0x56, 0x01, 0x31, 0x05, 0x04, 0x01, 0x00, 0x06, 0x02]
        strsrc = "76 %02x 31 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)

        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # 注意：多附加了个空格
        if (res == strsrc):
            return True
        else:
            return False

    def flushBuffer(self,no):
        # 设置图像压缩率，XX=00~FF,默认36
        cmd = [0x56, no, 0x36, 0x01, 0x03]
        strsrc = "76 %02x 36 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)

        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # 注意：多附加了个空格
        if (res == strsrc):
            return True
        else:
            return False

    def setResolution(self, no, res = 0x00):
        # 设置图像分辨率，res = 0x00 640x480，11 320x240， 22 160x120
        cmd = [0x56, no, 0x31, 0x05, 0x04, 0x01, 0x00, 0x19, res]
        strsrc = "76 %02x 31 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)

        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # 注意：多附加了个空格
        if (res == strsrc):
            return True
        else:
            return False
    def clear_buf(self,no):
        cmd = [0x56, no, 0x36, 0x01, 0x02]
        self.port.write(cmd)

    def shotPhoto(self,no):
        #拍照
        cmd = [0x56, no, 0x36, 0x01, 0x00]
        strsrc = "76 %02x 36 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)

        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # 注意：多附加了个空格
        if (res == strsrc):
            return True
        else:
            return False
    def getPhotoLen(self,no):
        # 拍照
        cmd = [0x56, no, 0x34, 0x01, 0x00]
        strsrc = "76 %02x 36 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)

        response = self.port.read(9)
        # res = ''.join(['%02x ' % b for b in response])  # 注意：多附加了个空格

        # str1= '%x'%response[7]
        # str2 = '%x' % response[8]
        # str ='0x'+str1+str2
        return response[7:9]


    def getPhoto(self, no, photolen, filename):
        byteLen = int.from_bytes(photolen, byteorder='big', signed=False)
        #print(byteLen)
        i=0
        j = 0
        minval = byteLen
        cmd = [0x56, no, 0x32, 0x0c, 0x00, 0x0a, 0x00, 0x00, (i & 0xff00) >> 8, (i & 0x00ff), 0x00, 0x00,
                (minval & 0xff00) >> 8, (minval & 0x00ff), 0x00, 0xff]
        # t1=time.time()
        self.port.write(cmd)
        time.sleep(1) #这个时间与分辨率有关，建议640:15s，320:5s, 120:3s
        j_count = math.ceil(byteLen/6144)
        while j < j_count:
            re = self.port.read(6144)
            if j == 0:
                wf=open(filename,"wb")
                wf.write(re[5:])
                wf.close()
            elif j == j_count - 1:
                wf=open(filename,"ab+")
                wf.write(re[:-5])
                wf.close()
            else :
                wf=open(filename,"ab+")
                wf.write(re)
                wf.close()
            j += 1
            #res1 = ''.join(['%02x ' % b for b in re[0:5]])  # 注意：多附加了个空格 正确的是：76 01 32 00 00
            #res2 = ''.join(['%02x ' % b for b in re[-5:]])  # 注意：多附加了个空格 正确的是：76 01 32 00 00
            #print(res1,res2,len(re))
        print('OK')
        return 0






if __name__ == '__main__':
    # args = getArgs ()
    # print(args.COM)
    comserial = "/dev/ttyUSB0"
    sc = serialCamera(comserial)
    sc.clear_buf(2)
    # sc.port.flushInput()
    # sc.port.flushOutput()
    # sc.port.close()
    #ret =sc.reset(2)
    #print(ret)
    # ret=sc.modifyNo(0,1)
    # print(ret)
    #ret = sc.setResolution(2)
    #ret = sc.reset(2)
    # ret = sc.setZipRate(1)
    ret = sc.shotPhoto(2)
    photoLen = sc.getPhotoLen(2)
    #print(photoLen)
    #sc.port.set_buffer_size(60000, 60000)#一定要设置缓冲区，与图像大小有关
    sc.getPhoto(2,photoLen,'1.jpg')
    #sc.flushBuffer(2)

