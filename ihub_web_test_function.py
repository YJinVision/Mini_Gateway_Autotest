import os
import re
import sys
import json
import time
import socket
import subprocess
import configparser
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from BeautifulReport import BeautifulReport
import unittest
from MiniGateway import mqtt_lite as mq

# 設定測試相關資訊
def get_info() -> None:
    # 讀取ini檔
    curr_path = os.path.dirname(os.path.abspath(__file__))
    ini_file = os.path.join(curr_path, "config.ini")
    config = configparser.ConfigParser()
    config.read(ini_file, encoding="utf-8")
# account, password
    global gw_debug_acc, gw_debug_pw
    gw_debug_acc = config.get("gw_login", "gw_debug_acc", fallback="")
    gw_debug_pw = config.get("gw_login", "gw_debug_pw", fallback="")
   
# Gateway infomation
    global gw_mac, gw_ip, gw_ip_ap_mode, gw_url, gw_url_ap_mode
    gw_mac = ""
    gw_ip = config.get("gw_info", "gw_ip", fallback="")
    gw_ip_ap_mode = config.get(
        "gw_info", "gw_ip_ap_mode", fallback="")
    gw_url = f"https://{gw_ip}"
    gw_url_ap_mode = f"https://{gw_ip_ap_mode}"

    global gw_ntp
    gw_ntp = "time.google.com"

    global gw_dev_pw
    gw_dev_pw = config.get("gw_info", "gw_dev_pw", fallback="")

    global gw_udp_port
    gw_udp_port = int(config.get("gw_info", "gw_udp_port", fallback=""))
   
# Wifi setting
    global wifi_default_ssid, wifi_default_pw, wifi_ap_ssid, wifi_ap_pw
    wifi_default_ssid = config.get(
        "wifi_setting", "wifi_default_ssid", fallback="")
    wifi_default_pw = config.get(
        "wifi_setting", "wifi_default_pw", fallback="")
    wifi_ap_ssid = config.get(
        "wifi_setting", "wifi_ap_ssid", fallback="")
    wifi_ap_pw = config.get(
        "wifi_setting", "wifi_ap_pw", fallback="")

    global wifi_sta_ssid, wifi_sta_pw
    wifi_sta_ssid = config.get(
        "wifi_setting", "wifi_sta_ssid", fallback="")
    wifi_sta_pw = config.get(
        "wifi_setting", "wifi_sta_pw", fallback="")
    
# Device infomation
    global plug, siren, remot
    plug = config.get("device", "plug", fallback="atPlug")
    siren = config.get("device", "siren", fallback="atSiren")
    remot = config.get("device", "remot", fallback="atZxt800")


    global remot_fw
    remot_fw = config.get(
        "device", "remot_fw", fallback="ZXT-800_Zw_KR_Fw_V0.46.gbl")


    global dev_dsk
    dev_dsk = {"dev1":"58175-50706-30859-50064-32758-54539-18094-14575", 
               "dev2":"15528-41457-04221-11499-42638-33505-38309-49669",
               "dev3":"40376-56468-60569-27576-19028-40641-61955-63444"
               }

# MQTT infomation
    global ex_test_broker, ex_default_broker
    ex_test_broker = {}
    ex_test_broker["server_ip"] = config.get(
        "3rd_broker", "server_ip", fallback="broker.emqx.io")
    ex_test_broker["client_id"] = config.get(
        "3rd_broker", "client_id", fallback="VisionGateway")
    ex_test_broker["subscribe_topic"]= config.get(
        "3rd_broker", "subscribe_topic", fallback="Vision_B2V")
    ex_test_broker["publish_topic"] = config.get(
        "3rd_broker", "publish_topic", fallback="Vision_V2B")
    ex_test_broker["user_name"] = config.get(
        "3rd_broker", "user_name", fallback="vision_gw")
    ex_test_broker["user_pw"] = config.get(
        "3rd_broker", "user_pw", fallback="vision3rd")

    ex_default_broker = {"server_ip": "127.0.0.1", 
                         "client_id": "test", 
                         "subscribe_topic": "Broker_to_VisionGW",
                         "publish_topic": "VisionGW_to_Broker",
                         "user_name": "vision_gw", 
                         "user_pw":"vision3rd"
                         }

# 輸出訊息到console
def output(*args, **kwargs):
    """輸出訊息到console"""
    ori_std = sys.stdout    # 保存原始 stdout
    sys.stdout = sys.__stdout__ # 恢復到控制台輸出
    print(*args, **kwargs)
    sys.stdout = ori_std    # 恢復 BeautifulReport 的輸出攔截

# 輸入Gateway IP並確認可用
def input_gw_ip() -> str:
    """輸入Gateway IP並確認可用"""
    while True:
        get_gw_ip = input("Gateway IP: ")
        if mq.pub_msg(get_gw_ip, "test/topic", "test_message"):
            return get_gw_ip
        else:
            print(f"Please check gateway({get_gw_ip}) ready.")

# 測試步驟出現例外時的處理
def catch_exc(description, func_name, err) -> None:
    """
    紀錄例外內容。

    Args:
        discription: str, 要顯示在console中的描述內容
        func_name: str, 調用catch_exc的函數名稱
        err: str, 錯誤內容
    """
    print(f"[ERROR] {description}")
    try:
        curr_time = datetime.now()
        # 將class name做為檔案名稱
        log_file = os.path.join(report_path, "err.log")
        log = []
        log.append(f"#"*80 + "\n")
        log.append(f"[{curr_time}] test method: [{func_name}]\n")
        log.append(f"{err}\n")
        # 紀錄調用的時間、調用的類方法、錯誤訊息
        with open(log_file, "+a") as f:
            for i in log:
                f.write(i)
    except Exception as err:
        print(f"[ERROR] 紀錄Exception時發生錯誤:\n{err}")

# 截取畫面並儲存到報告路徑
def screen_cap(driver) -> None:
    try: 
        sc_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        pic_name = os.path.join(report_path, 
                                f"{driver._testMethodName}_{sc_time}.png")
        driver.d.get_screenshot_as_file(pic_name)
        print(f"[SCREEN] {pic_name}")
    except Exception as err:
        print(F"[ERROR] 截取畫面時發生錯誤:\n{err}")

# 設定測試檔案及報告(單個.py檔)
def set_test(pattern):
    # 載入要測試的單一class
    test_suite = unittest.TestLoader().loadTestsFromTestCase(pattern)
    return test_suite

# 設定測試檔案及報告(多個.py檔)
def set_test_pattern():
    def extract_test_topics(suite):
        topics = set()
        
        def traverse_suite(suite):
            for test in suite:
                if isinstance(test, unittest.TestSuite):
                    traverse_suite(test)
                else:
                    # e.g., 
                    # "t01_sys_01_login_logout.sys_01_login_logout.test_01_00_sendkey_to_login"
                    test_id = test.id()  
                    parts = test_id.split(".")
                    if len(parts) > 1:
                        topics.add(parts[0])  # 取得 "t01_sys_XX_XXXX"
        
        traverse_suite(suite)
        return sorted(topics)  # 排序後回傳

    # 設定檔案路徑
    curr_path = os.path.dirname(os.path.abspath(__file__))
    test_func_path = os.path.join(curr_path, "TestFunctions")
    # 載入要測試的多個class case: 
    # Loader將自動查找名稱為t開頭.py結尾的檔案並從中載入unittest.TestCase的class 
    test_suite = unittest.defaultTestLoader.discover(test_func_path, "t*.py")
    test_topics = extract_test_topics(test_suite)
    return test_suite, test_topics

# 設定報告檔案及路徑
def set_report() -> tuple[str, str]:
    global report_path
    # 設定報告儲存路徑
    curr_path = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(curr_path, "TestReport")
    if not os.path.exists(report_path):
        os.mkdir(report_path)
    # 設定報告名稱
    test_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_name = f"gw_test_report_{test_time}"
    return report_path, report_name

# 透過UDP向Master Gateway要求目前Master的IP
def udp_find_master_ip(gw_mac: str) -> str:
    """
    使用UDP向Master Gateway要求IP位置。

    Args:
        gw_mac: 目標 Gateway 的 MAC 位址。

    Returns:
        找到的 Master Gateway IP 或 False。
    """
    pc_ip_list = get_pc_ip()
    if not pc_ip_list:
        return False
    for pc_ip in pc_ip_list:
        subnet = pc_ip.rsplit(".", 1)[0]  
        # 設定UDP通訊的地址和埠號
        # print(f"[INFO] Find in subnet: {subnet}.255")
        multicast_group = (f"{subnet}.255", 50109)
        local_port = 50109

        try:
        # 建立Socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_socket.settimeout(0.5)  # 設置接收超時時間，避免無限阻塞

            # 綁定本地埠號，監聽來自其他終端的回應
            udp_socket.bind(('', local_port))

            # 發送訊息
            message = '{"MsgType":"MasterInfoReq","MasterMac":"%s"}' % (gw_mac)
            udp_socket.sendto(bytes(message, "utf-8"), multicast_group)
            # print(f"Sent message: {message}")

            # 開始監聽回應
            start_time = time.time()
            while time.time() - start_time < 3:  # 設置總等待時間3秒
                try:
                    data, address = udp_socket.recvfrom(1024)  # 最大緩衝區大小為1024 bytes
                    if '"MasterInfoRpt"' in data.decode():
                        rpt = json.loads(data.decode())
                        wlan_mac = str(rpt["WlanMac"]).replace("-", ":").upper()
                        if wlan_mac == gw_mac.replace("-", ":").upper():
                            # print(f"{data.decode()}")
                            return address[0]
                except socket.timeout:
                    pass    # 如果超時，繼續下一次嘗試
                except Exception as err:
                    print(f"[ERROR] 解析UDP訊息時發生錯誤:{err}")
        except Exception as err:
            print(err)
        finally:
            udp_socket.close()
    return False
            
# 使用arp方法尋找LAN中的Gateway IP
def arp_find_gateway_ip(gw_mac: str) -> str:
    """
    找到指定 MAC 位址的 Gateway IP。
    
    Args:
        gw_mac: 目標 Gateway 的 MAC 位址。
    
    Returns:
        找到的 Gateway IP 或 False。
    """
    gw_mac = gw_mac.replace(":", "-").lower()
     # 從所有網路介面卡取LAN IP並逐一搜尋
    pc_ip_list = get_pc_ip()
    if not pc_ip_list:
        return False 
    for pc_ip in pc_ip_list:
        subnet = pc_ip.rsplit(".", 1)[0] + "."
        pc_ip_last = int(pc_ip.rsplit(".", 1)[1])
        h_test_ip, l_test_ip = pc_ip_last + 1, pc_ip_last - 1
        step = 5  # 每次 ping 幾個 IP
        flip = 1  # 控制上下交替 ping
        
        while h_test_ip <= 254 or l_test_ip >= 1:
            ip_range = []
            
            if flip == 1 and h_test_ip <= 254:
                ip_range = range(h_test_ip, min(h_test_ip + step, 255))
                h_test_ip += step
                flip = 0 if l_test_ip >= 1 else 1
            elif flip == 0 and l_test_ip >= 1:
                ip_range = range(l_test_ip, max(l_test_ip - step, 0), -1)
                l_test_ip -= step
                flip = 1 if h_test_ip <= 254 else 0
            
            # Ping 範圍內的所有 IP
            for ip_last in ip_range:
                ip = f"{subnet}{ip_last}"
                ping_cmd = ["ping", "-w", "2", "-n", "1", ip]
                subprocess.Popen(ping_cmd, 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            
            # 查詢 ARP 表，檢查目標 MAC 是否存在
            arp_result = subprocess.run("arp -a", 
                                        shell=True, 
                                        capture_output=True, 
                                        text=True).stdout
            if gw_mac in arp_result:
                # 從 ARP 表中提取對應的 IP
                for line in arp_result.splitlines():
                    if gw_mac in line:
                        gw_ip = line.split()[0]
                        return gw_ip
        
    return False

# 從ipconfig取得目前的PC LAN IP
def get_pc_ip() -> list[str]:
    """
    取得目前電腦全部網路介面的LAN IP(IPv4)位置。

    Returns:
        list[str]
    """
    try:
        # 確認目前的編碼頁
        chcp_result = subprocess.run(["chcp"], 
                                     shell=True, 
                                     capture_output=True, 
                                     text=True
                                     )
        current_chcp = re.search(r"使用中的字碼頁: (\d+)", chcp_result.stdout)
        encoding = "big5"  # 預設編碼
        if current_chcp:
            code_page = current_chcp.group(1)
            if code_page == "437":  # 英文
                encoding = "cp437"
            elif code_page == "950":  # 繁體中文
                encoding = "cp950"

        # 執行 ipconfig 指令
        result = subprocess.run(["ipconfig"], 
                                capture_output=True, 
                                text=True, 
                                encoding=encoding)
        output = result.stdout

        # 正規表達式，匹配指定介面的 IP 位址
        # pattern = rf"{re.escape("Wi-Fi")}.*?IPv4(?: 位址| Address).*?:\s*([\d\.]+)"
        adapters = re.findall(r"IPv4(?: 位址| Address).*?:\s*([\d\.]+)", 
                              output, 
                              re.DOTALL)
        # match = re.search(adapters, output, re.DOTALL)
        if adapters:
            return adapters  # 回傳找到的 IP 位址 list
        else:
            return False
    except Exception as e:
        print(f"[ERROR] 取得目前IP時發生錯誤: {e}")
        return False

# 等得MQTT訊息傳送完畢
def wait_mqtt_info_loading(timeout=3) -> None:
    """
        等得MQTT訊息傳送完畢。
        訊息在(timeout)秒內無更動視為載入完成。
    """
    msg = f"[INFO] Wait MQTT info loading ..."
    print(msg)
    curr_msg = "MQTT msg"
    prev_msg = ""
    start_time = datetime.now()
    while prev_msg != curr_msg:
        prev_msg = curr_msg
        time.sleep(timeout)
        try:
            curr_msg = mq.msg_que[0]
            mq.msg_que = []
        except:
            pass
    end_time = datetime.now()
    msg = f"[INFO] Finished. Spend time: {end_time - start_time}"
    print(msg)

# 設置Chrome Opthion
def set_chrome_options() -> Options:
    # 設定Chrome視窗選項
    options = Options()
    # 無痕模式 #最大化視窗 #視窗解析度 #忽略SSL錯誤 #不顯示DevTools訊息
    options.add_argument("--incognito") 
    options.add_argument("--start-maximized")
    # 整體視窗的比例, 非zoom in/out, 未設定時約=1.4
    options.add_argument('--force-device-scale-factor=1.2')
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options

# 每個測試步驟的執行動作、確認、重做方法
def execute(action, check=None, reset=None, retry=3) -> bool:
    """
    每個測試步驟的執行動作、確認、重做方法。

    Args:
        action: 測試動作函數
        check: 確認動作結果函數
        reset: 當action或check回傳false時, 重試前要復歸的動作
        retry:  執行動作的次數(retry=0不會執行並回傳false)
    """
    success_flag = False
    for r in range(retry):
        try:
            result = action()
            if result:
                if check is None or check(result):
                    success_flag = True
                    break
            if reset:
                reset()
            time.sleep(1)
            print(f"[RETRY] {r + 1}")
        except Exception as err:
            catch_exc("執行動作execute發生錯誤", "execute", err)
    return success_flag

# 設定測試旗標
def set_fail(name, flag) -> None:
    """
    設定測試旗標。
    
    Args:
        driver: WebDriver
        flag:   bool
    """
    global flag_test_fail, fail_reason
    if flag:
        flag_test_fail = True
        fail_reason = f"Fail step: {name}"
    else:
        flag_test_fail = False
        fail_reason = ""

# 新增Wi-Fi到系統
def add_new_wifi(SSID, password, path="."):
    """
    Args:
        SSID (str): Wi-Fi 名稱。
        password (str): Wi-Fi 密碼。
        path (str): 存放 XML 檔案的路徑，預設為當前目錄。

    Returns:
        bool: 是否成功新增設定檔。
    """
    profile_template = f"""<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{SSID}</name>
    <SSIDConfig>
        <SSID>
            <name>{SSID}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    subprocess.run('chcp 437', shell=True)
    encode = 'utf-8'
    file_path = os.path.join(path, f"{SSID}.xml")
    # 寫入SSID.xml檔
    try:
        with open(file_path, 'w', encoding=encode) as profile:
            profile.write(profile_template)
    except OSError as err:
        print(f"[ERROR] 無法建立檔案 {file_path}: {err}")
        return False

    # 將設定檔新增到PC系統
    try:
        add_cmd = f'netsh wlan add profile filename="{file_path}'
        result = subprocess.run(add_cmd, 
                                capture_output=True, 
                                encoding=encode)
        if result.returncode != 0:  # return 0 when success
            print(f"[ERROR] 無法新增{SSID}設定檔")
            return False
    except Exception as err:
        print(f"[ERROR] netsh wlan新增設定檔時發生錯誤: {err}")
        return False

    # 驗證設定檔中是否已新增SSID
    try:
        show_cmd = 'netsh wlan show profiles'
        result = subprocess.run(show_cmd, 
                                capture_output=True, 
                                encoding=encode)
        if SSID in result.stdout:
            print(f"[INFO] 成功建立設定檔: {SSID}")
            return True
        else:
            print(f"[ERROR] 未在系統中找到 Wi-Fi 設定檔: {SSID}")
            return False
    except Exception as err:
        print(f"[ERROR] netsh wlan驗證設定檔時發生錯誤: {err}")
        return False

# 初始化並開始測試
def init_test(class_name):
    # 設定測試資訊
    get_info()
    test_suite = set_test(class_name)
    report_path, report_name = set_report()
    # 開始MQTT線程
    mq.sub_loop(broker=gw_ip, 
                topic=["MIDDLE_TO_USER", "USER_TO_MIDDLE"], 
                daemon_flag=True)
    # 測試開始
    result = BeautifulReport(test_suite)
    result.report(description="mini_gateway_test", 
                  filename=report_name, 
                  log_path=report_path)
    # 測試完成後自動開啟報告
    subprocess.run(f"start {report_path}\\{report_name}.html", 
                   capture_output=True, 
                   shell=True)
    
# 時間內等待出現目標訊息
def wait_mqtt_msg(keyword: list, timeout=30, ack_busy=True) -> str:
    """
    時間內等待出現特定關鍵字。

    Args:
        keyword: list, 要出現在同一則訊息的關鍵字串列
        timeout: int, 等待總時間
        ack_busy: bool, msg出現"Z-Wave is busy"時
            True: 立刻return "busy"
            False: 忽略"Z-Wave is busy", 繼續等待keyword
    Return:
        msg完全符合keyword: str, return訊息
        msg出現"Z-Wave is busy": str, return "busy"
        msg超時未符合keyword: str, return "timeout"
    """
    start_time = datetime.now()
    wait_time = timedelta(seconds=timeout)
    while datetime.now() <= start_time + wait_time:
        try:
            if all(word in mq.msg_que[0] for word in keyword):
                msg = mq.msg_que.pop(0)
                return msg
            elif ack_busy and "Z-Wave is busy" in mq.msg_que[0]:
                return "busy"
            else:
                del mq.msg_que[0]
        except:
            time.sleep(0.1)
    else:
        return "timeout"

# 取得PC目前的LAN IP位址
def get_pc_ip() -> list[str]:
    """
    取得目前電腦全部網路介面的LAN IP(IPv4)位置。

    Returns:
        list[str]
    """
    try:
        # 確認目前的編碼頁
        chcp_result = subprocess.run(["chcp"], 
                                     shell=True, 
                                     capture_output=True, 
                                     text=True
                                     )
        current_chcp = re.search(r"使用中的字碼頁: (\d+)", chcp_result.stdout)
        encoding = "big5"  # 預設編碼
        if current_chcp:
            code_page = current_chcp.group(1)
            if code_page == "437":  # 英文
                encoding = "cp437"
            elif code_page == "950":  # 繁體中文
                encoding = "cp950"

        # 執行 ipconfig 指令
        result = subprocess.run(["ipconfig"], 
                                capture_output=True, 
                                text=True, 
                                encoding=encoding)
        output = result.stdout

        # 正規表達式，匹配指定介面的 IP 位址
        # pattern = rf"{re.escape("Wi-Fi")}.*?IPv4(?: 位址| Address).*?:\s*([\d\.]+)"
        adapters = re.findall(r"IPv4(?: 位址| Address).*?:\s*([\d\.]+)", 
                              output, 
                              re.DOTALL)
        # match = re.search(adapters, output, re.DOTALL)
        if adapters:
            return adapters  # 回傳找到的 IP 位址 list
        else:
            return False
    except Exception as e:
        print(f"[ERROR] 取得目前IP時發生錯誤: {e}")
        return False





