#coding: gbk
import subprocess
import os
import sys
import re
from compiler.ast import flatten

reload(sys)
sys.setdefaultencoding('gbk')

class Adb(object):
    _path = None  #adb path
    _lastError = ''
    _params = ''

    def __init__(self, dits):
        self._path = dits['adb_path'] #dit = {'adb_path':'','input_para':''}
        self._lastError = ''
        self._params = dits['input_para']
        self.phoneInfoDict = {"2_sysversion":'', "3_sysapi":'', "4_cpu":'',
                              "1_product":'', "6_serialId":'', "7_imei":'',
                              "5_mac":'', "9_density":'', "a_memory":'',
                              "b_storage":'', "c_sdcard":'', "8_pix":'',
                              "d_sdcard":''}

    @staticmethod
    def _run(args):
        p = subprocess.Popen(flatten(args), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=False)
        ret = p.communicate()
        output = Adb._out2str(p.stdout.readlines())
        error = Adb._out2str(p.stderr.readlines())
        # return output if ret is 0 else error
        return Adb._out2str(ret)

    @staticmethod
    def _out2str(text_seq):
        return str.strip(" ".join(text_seq).replace("\r", "").replace("\n", "")).decode('utf-8')

    def connect(self, host):
        return self._run([self._path, "connect", host])

    def disconnect(self, host):
        return self._run([self._path, "disconnect", host])

    def shell(self, host, command):
        args = flatten([self._path, "-s", host, command.split(" ")])
        return self._run(args)

    def logcat(self, host):
        args = [self._path, "-s", host, "logcat"]
        return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=False)

    # -r: replace existing application
    # -t: allow test packages
    # -d: allow version code downgrade
    def install_apk(self, host, file_path):
        _state = self.get_state(host)
        self._lastError = ''
        if _state is "offline":
            self._lastError = "device offline"
            return False

        args = [self._path, "-s", host, "install", "-r", file_path]
        # args = [self._path, "-s", host, "install", "-rt", file_path]
        print(self._run(args))
        return True

    def uninstall_apk(self, host, packageName):
        _state = self.get_state(host)
        self._lastError = ''
        if _state is "offline":
            self._lastError = "device offline"
            return False

        args = [self._path, "-s", host, "uninstall", packageName]
        result=self._run(args)
        if result.find("Unknown package")!=-1:
            print(u'�豸��δ��װ��APK')
        return True

    def get_state(self, host):
        _state = self.shell(host, "get-state")
        if "unknown" in _state:
            return "offline"
        elif "device" in _state:
            return "online"
        else:
            return "offline"
        pass

    def restart(self):
        self._run([self._path, "kill-server"])
        return self._run([self._path, "start-server"])

    def screencap(self,host,outfile):
        _state = self.get_state(host)
        self._lastError = ''
        if _state is "offline":
            self._lastError = "device offline"
            return False

        args = [self._path, "-s", host, "shell","/system/bin/screencap", "-p", "/data/local/tmp/screenshot.png"]
        result = self._run(args)

        if result.find('Error') == -1:
            args = [self._path, "-s", host, "pull", "/data/local/tmp/screenshot.png", outfile]
            result = self._run(args)

            if os.path.exists(outfile):
               return True

            result = u'�����ֻ���ͼ������ʧ��'

        self._lastError = result
        return False


    def getDeviceList(self):
        device = self._run([self._path, "devices"])
        lists = None
        if device != 'List of devices attached':
            #��ȡdevice,list�б�
            lists = device.replace('List of devices attached','').replace('device','').replace('offline','').replace('unknown','').replace(' ','').strip().split('\t')
        if lists:
            pass
        else:
            lists = []
        return lists

    def kill(self):
        self._run([self._path, "kill-server"])

    def path_provided(self):
        return self._path is not None and not self._path == ""

    def getScreenCap(self):
        devicelist = self.getDeviceList()
        if len(devicelist) == 0:
            print(u'�豸�б�Ϊ�գ��������豸')
            return False

        host = devicelist[0]
        result = self.screencap(host, self._params)
        if not result:
            print(self._lastError)
            return False
        else:
            print(self._params)
            return True

    # ��ȡϵͳ�汾
    def getSysversion(self, host):
        args = [self._path, "-s", host, "shell", "getprop", "ro.build.version.release"]
        result = self._run(args)
        result = str(result).strip()

        try:
            pattern = r'^[1-9]+\.?\d*\.?\d*\.?\d*$'
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['2_sysversion'] = u"ϵͳ�汾��" + result
                # print result
        except Exception as e:
            self.phoneInfoDict['2_sysversion'] = ''

    # ��ȡϵͳAPI
    def getSysApi(self, host):
        args = [self._path, "-s", host, "shell", "getprop", "ro.build.version.sdk"]
        result = self._run(args)
        result = str(result).strip()

        try:
            pattern = r'^[1-9]+\.?\d*$'
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['3_sysapi'] = u"ϵͳAPI�汾��" + result
                # print result
        except Exception as  e:
            self.phoneInfoDict['3_sysapi'] = ''

    # ��ȡCPU����
    def getCpu(self, host):
        args = [self._path, "-s", host, "shell", "getprop", "ro.product.cpu.abi"]
        result = self._run(args)
        result = str(result).strip()

        try:
            if result != '' and result.find('not found') == -1:
                self.phoneInfoDict['4_cpu'] = u"ϵͳCPU���ͣ�" + result
                # print result
        except Exception as  e:
            self.phoneInfoDict['4_cpu'] = ''

    # ��ȡ��Ʒ��Ϣ  adb -d shell getprop ro.product.model
    def getProduct(self, host):
        args = [self._path, "-s", host,  "-d", "shell", "getprop", "ro.product.model"]
        result = self._run(args)
        result = str(result).strip()

        try:
            if result != '' and result.find('not found') == -1:
                self.phoneInfoDict['1_product'] = u"�ֻ����ͣ�" + result
                # print result
        except Exception as  e:
            self.phoneInfoDict['1_product'] = ''

    # ��ȡ���к�
    def getSerialId(self, host):
        args = [self._path, "-s", host,  "get-serialno"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'^\w+$'
        try:
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['6_serialId'] = u"���кţ�" + result
                # print result
                return
        except Exception as  e:
            self.phoneInfoDict['6_serialId'] = ''

        # �ڶ��ַ�����ȡ  adb shell getprop ro.serialno
        args = [self._path, "-s", host,  "shell", "getprop", "ro.serialno"]
        result = self._run(args)
        result = str(result).strip()
        try:
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['6_serialId'] = u"���кţ�" + result
                # print result
        except Exception as  e:
            self.phoneInfoDict['6_serialId'] = ''


    # ��ȡIMEI
    '''
    1��adb shell dumpsys iphonesubinfo
    2��adb shell getprop gsm.baseband.imei
    3��adb shell service call iphonesubinfo 1
    '''
    def getImei(self, host):
        args = [self._path, "-s", host,  "shell", "dumpsys", "iphonesubinfo"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'Device ID\s*=\s*(\d+)'
        try:
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['7_imei'] = u"IMEI��" + str(m.group(1))
                # print str(m.group(1))
                return
        except Exception as  e:
            self.phoneInfoDict['7_imei'] = ''

        # �ڶ���

        # �����ַ���
        args = [self._path, "-s", host,  "shell", "service", "call", "iphonesubinfo", "1"]
        result = self._run(args)
        result = str(result).strip()
        pattern = r'.+\'(.+)\'.+\'(.+)\'.+\'(.+)\''
        try:
            m = re.search(pattern, result)
            if m:
                imei = str(m.group(1) + m.group(2) + m.group(3))
                imei = imei.replace('.', '').strip()
                if imei != '':
                    self.phoneInfoDict['7_imei'] = u"IMEI��" + imei
                    # print imei
        except Exception as  e:
            self.phoneInfoDict['7_imei'] = ''

    # ��ȡMAC adb shell cat /sys/class/net/wlan0/address
    def getMac(self, host):
        args = [self._path, "-s", host,  "shell", "cat", "/sys/class/net/wlan0/address"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}'
        try:
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['5_mac'] = u"MAC��" + result
                # print result
                return
        except Exception as  e:
            self.phoneInfoDict['5_mac'] = ''

        args = [self._path, "-s", host,  "shell", "cat", "/sys/class/net/eth0/address"]
        result = self._run(args)
        result = str(result).strip()

        try:
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['5_mac'] = u"MAC��" + result
                # print result
                return
        except Exception as  e:
            self.phoneInfoDict['5_mac'] = ''

    # ��ȡ�����ܶ�
    def getDensity(self, host):
        args = [self._path, "-s", host,  "shell", "wm", "density"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'Physical density\s*:\s*(\d+)'
        try:
            m = re.search(pattern, result)
            if m:
                self.phoneInfoDict['9_density'] = u"�ֻ��ܶȣ�" + str(m.group(1))
                # print str(m.group(1))
        except Exception as  e:
            self.phoneInfoDict['9_density'] = ''

    # ��ȡ�ֱ��� 1152x1920
    def getPix(self, host):
        args = [self._path, "-s", host,  "shell", "dumpsys", "window", "|", "grep", "mUnrestrictedScreen"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'.+ (\d+)x(\d+)'
        try:
            m = re.search(pattern, result)
            if m:
                pix = str(m.group(1) + ' x ' + m.group(2))
                self.phoneInfoDict['8_pix'] = u"�ֱ��ʣ�" + pix
                # print pix
        except Exception as  e:
            self.phoneInfoDict['8_pix'] = ''

    # ��ȡ�ڴ����ռ��  adb shell cat /proc/meminfo
    def getMemory(self, host):
        args = [self._path, "-s", host,  "shell", "cat", "/proc/meminfo"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'MemTotal.+ (\d+).+MemFree.+ (\d+).+Buffers.+ (\d+).+Cached.+ (\d+).+SwapCached'
        try:
            m = re.search(pattern, result)
            if m:
                total = float(str(m.group(1)))
                # print total
                free = float(str(m.group(2))) + float(str(m.group(3))) + float(str(m.group(4)))
                # print free
                result = free /total
                availableMegs = int(result*100)
                total = int(total / 1024)
                free = int(free / 1024)
                self.phoneInfoDict['a_memory'] = u"�ڴ����ռ�ȣ�" + str(availableMegs) + '%' + '(' + str(free) + 'M/'+ str(total) + 'M)'
                # print str(availableMegs) + '%'
        except Exception as  e:
            self.phoneInfoDict['a_memory'] = ''

    # ��ȡ���̿���ռ��  adb shell df /data
    def getDataStorage(self, host):
        args = [self._path, "-s", host,  "shell", "df", "/data"]
        result = self._run(args)
        result = str(result).strip()

        if result.find('No such file or directory') == -1:
            pattern = r'/data.+ (\d+.*\d*[GM]).+ (\d+.*\d*[GMK]).+ (\d+.*\d*[GM]).+'
            try:
                m = re.search(pattern, result)
                if m:
                    total = m.group(1)
                    free = m.group(3)
                    units = 'G'
                    if total.find('G') != -1:
                        total = float(total.split('G')[0])
                    elif total.find('M') != -1:
                        units = 'M'
                        total = float(total.split('M')[0])
                    else:
                        return

                    if free.find('G') != -1:
                        free = float(free.split('G')[0])
                        if units == 'M':
                            free = free * 1024
                    elif free.find('M') != -1:
                        free = float(free.split('M')[0])
                        if units == 'G':
                            free = free / 1024
                    else:
                        return

                    availbeStore = free/total
                    availbeStore = int(availbeStore * 100)
                    self.phoneInfoDict['b_storage'] = u"dataĿ¼����ռ�ȣ�" + str(availbeStore) + '%'+ '(' + str(free) + units+ '/'+ str(total) + units+ ')'
                    # print str(availbeStore) + '%'
            except Exception as  e:
                self.phoneInfoDict['b_storage'] = ''

    # ��ȡ����SD��ʣ��ռ��
    def getSdcardInteral(self, host):
        args = [self._path, "-s", host,  "shell", "df", "/storage/sdcard0"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'/storage/sdcard.+ (\d+.*\d*[GM]).+ (\d+.*\d*[GMK]).+ (\d+.*\d*[GM]).+'
        if result.find('No such file or directory') == -1:
            try:
                m = re.search(pattern, result)
                if m:
                    total = m.group(1)
                    free = m.group(3)
                    units = 'G'
                    if total.find('G') != -1:
                        total = float(total.split('G')[0])
                    elif total.find('M') != -1:
                        units = 'M'
                        total = float(total.split('M')[0])
                    else:
                        return

                    if free.find('G') != -1:
                        free = float(free.split('G')[0])
                        if units == 'M':
                            free = free * 1024
                    elif free.find('M') != -1:
                        free = float(free.split('M')[0])
                        if units == 'G':
                            free = free / 1024
                    else:
                        return

                    availbeStore = free/total
                    availbeStore = int(availbeStore * 100)
                    self.phoneInfoDict['c_sdcard'] = u"�ڲ�SD��ʣ��ռ�ȣ�" + str(availbeStore) + '%'+ '(' + str(free) + units+ '/'+ str(total) + units+ ')'
                    # print str(availbeStore) + '%'
                    return
            except Exception as  e:
                self.phoneInfoDict['c_sdcard'] = ''


        #������
        args = [self._path, "-s", host,  "shell", "df", "/mnt/sdcard"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'/mnt/sdcard.+ (\d+.*\d*[GM]).+ (\d+.*\d*[GMK]).+ (\d+.*\d*[GM]).+'
        if result.find('No such file or directory') == -1:
            try:
                m = re.search(pattern, result)
                if m:
                    total = m.group(1)
                    free = m.group(3)
                    units = 'G'
                    if total.find('G') != -1:
                        total = float(total.split('G')[0])
                    elif total.find('M') != -1:
                        units = 'M'
                        total = float(total.split('M')[0])
                    else:
                        return

                    if free.find('G') != -1:
                        free = float(free.split('G')[0])
                        if units == 'M':
                            free = free * 1024
                    elif free.find('M') != -1:
                        free = float(free.split('M')[0])
                        if units == 'G':
                            free = free / 1024
                    else:
                        return

                    availbeStore = free/total
                    availbeStore = int(availbeStore * 100)
                    self.phoneInfoDict['c_sdcard'] = u"�ڲ�SD��ʣ��ռ�ȣ�" + str(availbeStore) + '%'+ '(' + str(free) + units+ '/'+ str(total) + units+ ')'
                    # print str(availbeStore) + '%'
                    return
            except Exception as  e:
                self.phoneInfoDict['c_sdcard'] = ''

    # ��ȡ����SD��ʣ��ռ��
    def getSdcardExternal(self, host):
        args = [self._path, "-s", host,  "shell", "df", "/storage/sdcard1"]
        result = self._run(args)
        result = str(result).strip()

        pattern = r'/storage/sdcard.+ (\d+.*\d*[GM]).+ (\d+.*\d*[GMK]).+ (\d+.*\d*[GM]).+'
        if result.find('No such file or directory') == -1:
            try:
                m = re.search(pattern, result)
                if m:
                    total = m.group(1)
                    free = m.group(3)
                    units = 'G'
                    if total.find('G') != -1:
                        total = float(total.split('G')[0])
                    elif total.find('M') != -1:
                        units = 'M'
                        total = float(total.split('M')[0])
                    else:
                        return

                    if free.find('G') != -1:
                        free = float(free.split('G')[0])
                        if units == 'M':
                            free = free * 1024
                    elif free.find('M') != -1:
                        free = float(free.split('M')[0])
                        if units == 'G':
                            free = free / 1024
                    else:
                        return

                    availbeStore = free/total
                    availbeStore = int(availbeStore * 100)
                    self.phoneInfoDict['c_sdcard'] = u"�ⲿSD��ʣ��ռ�ȣ�" + str(availbeStore) + '%'+ '(' + str(free) + units+ '/'+ str(total) + units+ ')'
                    # print str(availbeStore) + '%'
                    return
            except Exception as  e:
                self.phoneInfoDict['c_sdcard'] = ''

    def getPhoneInfo(self):
        devicelist = self.getDeviceList()
        if len(devicelist) == 0:
            print(u'�豸�б�Ϊ�գ��������豸')
            return False

        host = devicelist[0]

        _state = self.get_state(host)
        if _state is "offline":
            print("device offline")
            return False

        self.getSysversion(host)
        self.getSysApi(host)
        self.getCpu(host)
        self.getProduct(host)
        self.getSerialId(host)
        self.getImei(host)
        self.getMac(host)
        self.getDensity(host)
        self.getPix(host)
        self.getMemory(host)
        self.getDataStorage(host)
        self.getSdcardInteral(host)
        self.getSdcardExternal(host)

        for item in sorted(self.phoneInfoDict.keys()):
            if self.phoneInfoDict[item] != '':
                print(self.phoneInfoDict[item])

    def apkHandle(self, flag):
        devicelist = self.getDeviceList()
        if len(devicelist) == 0:
            print(u'�豸�б�Ϊ�գ��������豸')
            return False

        host = devicelist[0]
        if flag == 'install':
            result = self.install_apk(host, self._params)
            if not result:
                print(self._lastError)
                return False
        elif flag == 'uninstall':
            result = self.uninstall_apk(host, self._params)
            if not result:
                print(self._lastError)
                return False
        else:
            print(u'����Ĳ�������ȷ')
            return False

        return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(u"����Ĳ�������ȷ")
    else:
        dits = {'adb_path':'','input_para':''}
        dits['adb_path'] = unicode(sys.argv[1],"gbk")
        dits['input_para'] = unicode(sys.argv[2],"gbk")
        flag = unicode(sys.argv[3], "gbk")

        adb = Adb(dits)

        if flag == 'screenCap':
            adb.getScreenCap()
        elif flag == 'install':
            adb.apkHandle('install')
        elif flag == 'uninstall':
            adb.apkHandle('uninstall')
        elif flag == 'getinfo':
            adb.getPhoneInfo()
        else:
            print(u"����Ĳ�������ȷ")

# if __name__ == "__main__":
#     adb_path = 'adb'
#     input_para = 'E:\\��   ��\\SlidingDemo_aligns.png'
#     # input_para = 'net.ting.sliding'
#     dits = {'adb_path':'','input_para':''}
#     dits['adb_path'] = adb_path
#     dits['input_para'] = unicode(input_para,"gbk")#'I:\\dddd\\03-17-46-09.apk'
#     flag = 'screenCap'
#
#     print dits
#
#     adb = Adb(dits)
#     adb.getPhoneInfo()