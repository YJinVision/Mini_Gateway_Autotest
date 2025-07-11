#==============================================================================
# 程式功能: 測試wifi sta mode功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.預先處理連線資訊 
# 05_00.點擊Network Configuration分頁
# 06_00.點選Sta Mode
# 07_00.從輸入框取得目前的Wi-Fi SSIP及Password
# 08_00.點擊Scan按鈕
# 09_00.從清單選擇SSID
# 10_00.輸入密碼並儲存
# 11_00.確認Gateway已切換網路
# 12_00.PC Wi-Fi連接到Sta測試SSID
# 13_00.從LAN中尋找Gateway新IP
# 14_00.開啟Gateway新的網頁位置
# 15_00.重做01_00、02_00、05_00
# 16_00.恢復Wi-Fi SSID設定並儲存
# 17_00.確認Gateway已切換網路
# 18_00.PC Wi-Fi連接到原來的SSID
# 19_00.從LAN中尋找Gateway新IP
# 20_00.開啟Gateway網頁位置
#==============================================================================
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(os.path.dirname(curr_path))  #.\iHub_Autotest
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import mqtt_lite as mq

class sys_07_wifi_sta_mode(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.encode = 'utf-8'
        subprocess.run('chcp 437', shell=True)
        
        tf.output(f"\n[STATUS] {self.__name__} start.\n")
        # 設置ChromeDriver選項
        self.d = webdriver.Chrome(tf.set_chrome_options()) 
        
        tf.set_fail(self, False)

        # 因需控制Wi-Fi介面, 確認目前是否使用系統管理員執行
        cmd = "net.exe session 1>NUL 2>NUL && (echo y)||(echo n)"
        feedback = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  shell=True)
        if "n" in feedback.stdout:
            msg = "Set wifi interface need admin permision. Skip test."
            tf.output(msg)
            tf.flag_test_fail = True
            tf.fail_reason = msg

        try:
            self.d.set_page_load_timeout(15)
            self.d.get(tf.gw_url)
        except:
            print(f"[ERROR] 無法開啟網頁 {tf.gw_url}")
            tf.set_fail("無法開啟網頁", True)

    @classmethod
    def tearDownClass(self):
        time.sleep(1)
        mq.msg_que = []
        tf.output(f"\n[STATUS] {self.__name__} finished.\n")
        self.d.quit()

# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
    def test_01_00_sendkey_to_login(self):
        """輸入帳號密碼/勾選Remember me並點擊登入"""
        # 如果前步驟失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                # 等待元素出現
                acc_elem = '//*[@id="Login_Account"]'
                WebDriverWait(self.d, 20).until(
                    EC.presence_of_element_located((By.XPATH, acc_elem)))
                # 等待元素能互動
                time.sleep(0.5)
                # 輸入帳號密碼並點擊登入
                acc_elem = '//*[@id="Login_Account"]'
                user_acc = self.d.find_element(By.XPATH, acc_elem)
                user_acc.clear()
                user_acc.send_keys(tf.gw_debug_acc)
                print(f"[SENDKEY] {tf.gw_debug_acc}")
                pw_elem = '//*[@id="Login_Pwd"]'
                user_pw = self.d.find_element(By.XPATH, pw_elem)
                user_pw.clear()
                user_pw.send_keys(tf.gw_debug_pw)
                print(f"[SENDKEY] {tf.gw_debug_pw}")
                rmb_me = '//*[@id="Login_Remember"]'
                chk_rmb = self.d.find_element(By.XPATH, rmb_me)
                chk_rmb.click()
                print(f"[CLICK] Remember me")
                btn_elem = '//*[@id="Login_Page_Btn"]'
                login_btn = self.d.find_element(By.XPATH, btn_elem)
                login_btn.click()
                print(f"[CLICK] Login")
                return True
            except Exception as err:
                tf.catch_exc(f"登入失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                #沒有Alert就會拋exception
                WebDriverWait(self.d, 2).until(EC.alert_is_present())
                print(f"[FAIL] 出現警示")
                return False
            except Exception as err:
                tf.catch_exc(f"[INFO] 無出現警示", self._testMethodName,  err)
                try:
                    # 若Loader沒出現->拋錯
                    elem = 'Loader_Modal'
                    WebDriverWait(self.d, 8).until(
                        EC.presence_of_element_located((By.ID, elem)))
                    print("[INFO] Loader出現")
                except Exception as err:
                    tf.catch_exc(f"沒有出現Loader, 登入失敗", 
                                 self._testMethodName,  err)
                    return False
                return True

        def reset():
            try:
                # 當Alert出現, 點擊確認來關閉Alert
                alert = self.d.switch_to.alert
                alert.accept()
                print(f"[CLICK] Alert-Accept.")
            except Exception as err:
                # 若登入失敗, 也沒有出現Alert->重整頁面再試
                tf.catch_exc(f"Accept alert failed.", 
                             self._testMethodName,  err)
                self.d.refresh()
                
        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 02_00.等待頁面載入完成
    def test_02_00_wait_page_loading(self):
        """等待頁面載入完成"""
        # 如果前步驟失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                elem = 'Loader_Modal'
                WebDriverWait(self.d, 10).until(
                    EC.invisibility_of_element((By.ID, elem)))
                print(f"[INFO] Loader消失, 頁面載入完成")
                return True
            except Exception as err:
                tf.catch_exc(f"Loader超時未消失, 頁面載入失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                elem = 'System_Software_Ver'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, elem)))
                print(f"[INFO] 已定位元素: Software Version")
                return True
            except Exception as err:
                tf.catch_exc(f"無法定位元素, 載入失敗", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 03_00.從System頁面取得Gateway資訊
    def test_03_00_get_gateway_info(self):
        """從System頁面取得Gateway資訊"""
        # 如果前步驟失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global info
            info = {}
            try:
                hw_elem = 'System_Hardware_Ver'
                info["hw_ver"] = self.d.find_element(By.ID, hw_elem).text
                sw_elem = 'System_Software_Ver'
                info["sw_ver"] = self.d.find_element(By.ID, sw_elem).text
                vd_elem = 'System_Ver_Date'
                info["ver_date"] = self.d.find_element(By.ID, vd_elem).text
                mac_elem = '//*[@id="System_Current_Network_Info"]/tbody/tr[1]/td[2]'
                info["mac"] = self.d.find_element(By.XPATH, mac_elem).text
                tf.gw_mac = info["mac"]
                dhcp_elem = '//*[@id="System_Current_Network_Info"]/tbody/tr[2]/td[2]'
                info["dhcp"] = self.d.find_element(By.XPATH, dhcp_elem).text
                ip_elem = '//*[@id="System_Current_Network_Info"]/tbody/tr[3]/td[2]'
                info["ip"] = self.d.find_element(By.XPATH, ip_elem).text
                tf.gw_ip = info["ip"]
                mask_elem = '//*[@id="System_Current_Network_Info"]/tbody/tr[4]/td[2]'
                info["mask"] = self.d.find_element(By.XPATH, mask_elem).text
                print(f"[INFO] Page info: {info}")
                return info
            except Exception as err:
                tf.catch_exc(f"取得Gateway資訊時發生錯誤", self._testMethodName,  err)
                return info

        def check(info):
            try:
                # 檢查資訊
                if len(info["hw_ver"]) < 5:    # v1.0A
                    print("[FAIL] hw_ver error")
                    raise 
                if len(info["sw_ver"]) < 8:    # v01.24.0
                    print("[FAIL] sw_ver error")
                    raise 
                if len(info["ver_date"]) < 8:  # 20241204
                    print("[FAIL] ver_date error")
                    raise 
                if len(str(info["mac"]).split(":")) != 6:  # 9C:65:F9:4F:BC:E2
                    print("[FAIL] mac error")
                    raise 
                if len(str(info["ip"]).split(".")) != 4:    #192.168.109.1
                    print("[FAIL] ip error")
                    raise
                if len(str(info["mask"]).split(".")) != 4:    #255.255.255.0
                    print("[FAIL] mask error")
                    raise 
                print(f"[INFO] Page info checked.")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查Gateway資訊時發生錯誤", self._testMethodName,  err)
                return False

        def reset():
            # 若頁面資訊出錯->需重整頁面->等待頁面載入->再試
            self.d.refresh()
            self.test_02_00_wait_page_loading()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 04_00.預先處理連線資訊
    def test_04_00_preprocess_connection_info(self):
        """預先處理連線資訊"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global pc_wifi_interf, pc_wifi_ssid
            # 取得PC的Wi-Fi介面卡名稱及目前連接的SSID
            try:
                pc_wifi_ssid = ""   # 若PC用有線網路連接可不連Wi-Fi
                show_cmd = "netsh wlan show interface"
                result = subprocess.run(show_cmd, 
                                        capture_output=True, 
                                        encoding=self.encode)
                for line in result.stdout.split("\n"):
                    if "Name" in line or "名稱" in line:
                        pc_wifi_interf = line[line.rfind(":")+2:]  
                        # Wi-Fi介面卡名稱
                    if "SSID" in line and "BSSID" not in line:
                        pc_wifi_ssid = line[line.rfind(":")+2:]
                        # 目前連接的SSID
                print(f"[INFO] PC Wi-Fi介面名稱: {pc_wifi_interf}")
                print(f"[INFO] 目前PC連接的SSID: {pc_wifi_ssid}")
            except Exception as err:
                tf.catch_exc(f"取得PC Wi-Fi資訊時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 新增Wi-Fi SSID Profile到系統
            try:
                profile_path = os.path.join(".", "wifi_profiles")
                if not os.path.exists(profile_path):
                    os.mkdir(profile_path)
                if not tf.add_new_wifi(tf.wifi_sta_ssid, 
                                       tf.wifi_sta_pw, 
                                       profile_path):
                    return False
                print(f"[INFO] 已建立Wi-Fi設定檔: {tf.wifi_sta_ssid}")
            except Exception as err:
                tf.catch_exc(f"建立Wi-Fi設定檔時發生錯誤", self._testMethodName,  err)
                return False
            
            # 刪除已新增完成的.xml
            try:
                rd_cmd = f"rmdir /s /q {profile_path}"
                result = subprocess.run(rd_cmd, 
                                        capture_output=True, 
                                        # encoding=self.encode, 
                                        shell=True)
                print(f"[INFO] 清除已設定檔案")
                return True
            except Exception as err:
                tf.catch_exc(f"清除已設定檔案時發生錯誤", self._testMethodName,  err)
                return True # 刪除檔案失敗不影響測試
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 05_00.點擊Network Configuration分頁
    def test_05_00_click_network_config(self):
        """點擊Network Configuration分頁"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                net_conf_elem = 'sys-network-config-word'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, net_conf_elem)))
                net_conf_tab = self.d.find_element(By.CLASS_NAME, net_conf_elem)
                net_conf_tab.click()
                print(f"[CLICK] Netwrok Configuration") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Netwrok Configuration分頁時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                ap_mode_elem = 'System_WIFI_Disable'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, ap_mode_elem)))
                print(f"[INFO] 已顯示Netwrok Configuration分頁") 
                return True
            except Exception as err:
                tf.catch_exc(f"未顯示Netwrok Configuration分頁", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 06_00.點選Sta Mode
    def test_06_00_click_ap_mode_option(self):
        """點選Sta Mode"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                sta_mode_elem = 'System_WIFI_Enable'
                sta_mode_op = self.d.find_element(By.ID, sta_mode_elem)
                sta_mode_op.click()
                print(f"[CLICK] Sta Mode option") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Ap Mode option時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                sta_mode_elem = 'System_WIFI_Enable'
                sta_mode_op = self.d.find_element(By.ID, sta_mode_elem)
                if sta_mode_op.is_selected():
                    print(f"[INFO] 已選擇Sta Mode") 
                    return True
                else:
                    print(f"[FAIL] 未選擇Sta Mode")
                    return False
            except Exception as err:
                tf.catch_exc(f"確認選擇Sta Mode時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_00.從輸入框取得目前的Wi-Fi SSIP及Password
    def test_07_00_get_current_ssid_pw(self):
        """從輸入框取得目前的Wi-Fi SSIP及Password"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global ori_ssid, ori_pw
            try:
                ssid_elem = 'System_Router_SSID'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, ssid_elem)))
                ssid_box = self.d.find_element(By.ID, ssid_elem)
                ori_ssid = ssid_box.get_attribute("value")
                pw_elem = 'System_Router_SSID_Pwd'
                pw_box = self.d.find_element(By.ID, pw_elem)
                ori_pw = pw_box.get_attribute("value")
                print(f"[INFO] 目前的SSID/PW: {ori_ssid}/{ori_pw}") 
                return True
            except Exception as err:
                tf.catch_exc(f"取得目前的Wi-Fi SSIP及Password時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                if not ori_ssid or not ori_pw:
                    print(f"[FAIL] SSID或Password為空值")
                    return False
                print(f"[INFO] 已檢查SSID/Password")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查SSID/Password時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_click_network_config()
            

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.點擊Scan按鈕
    def test_08_00_click_scan_wifi(self):
        """點擊Scan按鈕"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                scan_elem = 'scan_wifi'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.ID, scan_elem)))
                scan_btn = self.d.find_element(By.ID, scan_elem)
                scan_btn.click()
                print(f"[CLICK] Scan Wifi") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Scan按鈕時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = 'zw-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 出現確認彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查確認彈窗時發生錯誤", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_click_network_config()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_01.關閉確認彈窗
    def test_08_01_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.5) # 等待前端元素動作完成，避免操作過快
                close_elem = 'zw-setting-confirm-modal-closeBtn'
                close_btn = self.d.find_element(By.CLASS_NAME, close_elem)
                close_btn.click()
                print(f"[CLICK] 關閉彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                # 如果彈窗的關閉按鈕未消失->失敗
                # time.sleep(0.5) # 等待動作完成
                close_elem = 'zw-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 2).until(
                    EC.invisibility_of_element((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 彈窗消失")
                return True
            except Exception as err:
                tf.catch_exc(f"彈窗未消失", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_02.重做08_00
    def test_08_02_redo_step_08_00(self):
        """重做08_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            self.test_08_00_click_scan_wifi()
            print(f"[INFO] 重做08_00完成")
            return True

        def check(info):
            try:
                time.sleep(0.3)
                close_elem = 'zw-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 出現彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"無出現彈窗", self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.從清單選擇SSID
    def test_09_00_select_wifi_ssid(self):
        """從清單選擇SSID"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                scan_elem = 'wifi-list-scan-btn'
                WebDriverWait(self.d, 35).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, scan_elem)))
                ssid_list_elem = 'wifi-list'
                ssid_list = self.d.find_element(By.CLASS_NAME, ssid_list_elem)
                ssid_items = ssid_list.find_elements(By.TAG_NAME, "li")
                target_ssid = [tf.wifi_sta_ssid + "\nWPA2 PSK (CCMP)", 
                               tf.wifi_sta_ssid + "\nmixed WPA/WPA2 PSK (CCMP)"]
                for item in ssid_items:
                    if item.text in target_ssid:
                        item.click()
                        print(f"[CLICK] SSID: {tf.wifi_sta_ssid}")
                        return True
                print(f"[FAIL] 清單內沒有找到{tf.wifi_sta_ssid}") 
                return False
            except Exception as err:
                tf.catch_exc(f"Scan Wifi並選擇時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.5)
                ssid_elem = 'System_Router_SSID'
                ssid_box = self.d.find_element(By.ID, ssid_elem)
                get_ssid = ssid_box.get_attribute("value")
                if get_ssid == tf.wifi_sta_ssid:
                    print(f"[INFO] 已確認輸入框內的SSID: {get_ssid}")
                    return True
                else:
                    print(f"[FAIL] 認輸入框內的SSID: {get_ssid}")
                    return False
            except Exception as err:
                tf.catch_exc(f"檢查選擇的SSID時發生錯誤", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_click_network_config()
            self.test_06_00_click_ap_mode_option()
            self.test_08_00_click_scan_wifi()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.輸入密碼並儲存
    def test_10_00_sendkey_wifi_pw_and_save(self):
        """輸入密碼並儲存"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                pw_elem = 'System_Router_SSID_Pwd'
                pw_box = self.d.find_element(By.ID, pw_elem)
                pw_box.clear()
                pw_box.send_keys(tf.wifi_sta_pw)
                print(f"[SENDKEY] {tf.wifi_sta_pw}")
                save_elem = 'system-net-config-save-btn'
                save_btn = self.d.find_element(By.CLASS_NAME, save_elem)
                save_btn.click()
                print(f"[CLICK] Save") 
                return True
            except Exception as err:
                tf.catch_exc(f"輸入密碼並儲存時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 出現確認彈窗") 
                tf.output(f"[INFO] 已設定Sta Mode: {tf.wifi_sta_ssid}")
                return True
            except Exception as err:
                tf.catch_exc(f"未出現確認彈窗, 設定失敗", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_click_network_config()
            self.test_08_00_click_scan_wifi()
            self.test_09_00_select_wifi_ssid()


        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.確認Gateway已切換網路
    def test_11_00_check_gw_change_wifi(self):
        """確認Gateway已切換網路"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                ping_cmd = f'ping {tf.gw_ip} -w 1 -n 2'
                start_time = datetime.now()
                timeout = timedelta(seconds=30)
                while datetime.now() <= start_time + timeout:
                    result = subprocess.run(ping_cmd, 
                                            capture_output=True)
                    if result.returncode == 1:
                        print(f"[INFO] Gateway已切換網路")
                        return True
                else:
                    print(f"[FAIL] 已超時, Gateway未切換網路")
                    return False
            except Exception as err:
                tf.catch_exc(f"確認Gateway已切換網路時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.PC Wi-Fi連接到Sta測試SSID
    def test_12_00_pc_connect_to_sta_test_ssid(self):
        """PC Wi-Fi連接到Sta測試SSID"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 步驟1: 重啟Wi-Fi介面卡(刷新背景Wi-Fi清單)
            try:
                chk_interf = 'netsh wlan show interface'
                disable_cmd = f'netsh interface set interface '\
                    f'name="{pc_wifi_interf}" admin=disable'
                enable_cmd = f'netsh interface set interface '\
                    f'name="{pc_wifi_interf}" admin=enable'
                start_time = datetime.now()
                timeout = timedelta(seconds=30)
                while datetime.now() <= start_time + timeout:
                    result = subprocess.run(chk_interf, 
                                            capture_output=True, 
                                            encoding=self.encode).stdout
                    if pc_wifi_interf not in result:
                        break
                    subprocess.run(disable_cmd, 
                                    capture_output=True, 
                                    encoding=self.encode)   # Disable interface
                    time.sleep(1)
                else:
                    print(f"[FAIL] 已超時, 無法關閉Wi-Fi介面")
                    tf.output(f"[FAIL] 已超時, 無法關閉Wi-Fi介面")
                    return False
                start_time = datetime.now()
                timeout = timedelta(seconds=30)
                while datetime.now() <= start_time + timeout:
                    result = subprocess.run(chk_interf, 
                                            capture_output=True, 
                                            encoding=self.encode).stdout
                    if pc_wifi_interf in result:
                        break
                    subprocess.run(enable_cmd, 
                                capture_output=True, 
                                    encoding=self.encode)    # Enable interface
                    time.sleep(1)
                else:
                    print(f"[FAIL] 已超時, 無法開啟Wi-Fi介面")
                    tf.output(f"[FAIL] 已超時, 無法開啟Wi-Fi介面")
                    return False
                print(f"[INFO] 已重啟Wi-Fi介面卡({datetime.now()})")
                tf.output(f"[INFO] 已重啟Wi-Fi介面卡({datetime.now()})")
            except Exception as err:
                tf.catch_exc(f"重啟Wi-Fi介面卡時發生錯誤", self._testMethodName,  err)
                return False

            # 步驟2: 等待Sta測試SSID出現在可連線的Wi-Fi清單
            try:
                start_time = datetime.now()
                timeout = timedelta(seconds=60)   #等待60秒內Ap Mode SSID出現
                scan_cmd = "netsh wlan show network mode=bssid"
                while datetime.now() <= start_time + timeout:
                    wifi_list = subprocess.run(scan_cmd, 
                                               capture_output=True, 
                                               encoding=self.encode)
                    if tf.wifi_sta_ssid in wifi_list.stdout:
                        print(f"[INFO] {tf.wifi_sta_ssid}已可連線"\
                              f"({datetime.now()})") 
                        tf.output(f"[INFO] {tf.wifi_sta_ssid}已可連線"\
                                  f"({datetime.now()})") 
                        break
                    else:
                        time.sleep(2)
                else:
                    print(f"[FAIL] 已超時, 未出現{tf.wifi_sta_ssid}"\
                          f"({datetime.now()})")
                    tf.output(f"[FAIL] 已超時, 未出現{tf.wifi_sta_ssid}"\
                              f"({datetime.now()})")
                    return False
            except Exception as err:
                tf.catch_exc(f"等待Sta Mode測試SSID可連線時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 步驟3: 嘗試連線到Sta Mode測試SSID
            try:
                join_cmd = f'''netsh wlan connect name={tf.wifi_sta_ssid} \
                ssid={tf.wifi_sta_ssid} interface="{pc_wifi_interf}"'''
                start_time = datetime.now()
                timeout = timedelta(seconds=30)
                while datetime.now() <= start_time + timeout:
                    join_ack = subprocess.run(join_cmd, 
                                              capture_output=True, 
                                              encoding=self.encode)
                    if join_ack.returncode == 0:
                        print(f"[INFO] 已連線到{tf.wifi_sta_ssid}"\
                              f"({datetime.now()})")
                        tf.output(f"[INFO] 已連線到{tf.wifi_sta_ssid}"\
                                  f"({datetime.now()})")
                        return True
                    time.sleep(1)
                else:
                     print(f"[FAIL] 已超時, 無法連接{tf.wifi_sta_ssid}"\
                           f"({datetime.now()})")
                     tf.output(f"[FAIL] 已超時, 無法連接{tf.wifi_sta_ssid}"\
                               f"({datetime.now()})")
            except Exception as err:
                tf.catch_exc(f"連線到Sta Mode測試SSID時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.從LAN中尋找Gateway新IP
    def test_13_00_find_gw_ip_in_new_lan(self):
        """從LAN中尋找Gateway新IP"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global gw_new_ip
            try:
                time.sleep(3)   # 等待Gateway連上新網路
                gw_new_ip = tf.udp_find_master_ip(tf.gw_mac)
                if gw_new_ip:
                    print(f"[INFO] 已找到Gateway IP: {gw_new_ip}") 
                    tf.output(f"[INFO] 已找到Gateway IP: {gw_new_ip}")
                    return True
                else:
                    print(f"[FAIL] 在{tf.wifi_sta_ssid}中找不到Gateway IP")
                    tf.output(f"[FAIL] 在{tf.wifi_sta_ssid}中找不到Gateway IP")
                    time.sleep(5)   # 等待後重試
                    return False
            except Exception as err:
                tf.catch_exc(f"從LAN中尋找Gateway新IP時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                # 確認ping Gateway新IP可回應
                ping_cmd = f'ping -w 1 -n 1 {gw_new_ip}'
                start_time = datetime.now()
                timeout = timedelta(seconds=60)
                while datetime.now() <= start_time + timeout:
                    ack = subprocess.run(ping_cmd, 
                                         capture_output=True)
                    if ack.returncode == 0:
                        print(f"[INFO] {gw_new_ip} acked"\
                              f"({datetime.now()}).")
                        tf.output(f"[INFO] {gw_new_ip} acked"\
                                  f"({datetime.now()}).")
                        return True
                else:
                    print(f"[FAIL] 已超時, {gw_new_ip}無回應"\
                          f"({datetime.now()})")
                    tf.output(f"[FAIL] 已超時, {gw_new_ip}無回應"\
                              f"({datetime.now()})")
                    return False

            except Exception as err:
                tf.catch_exc(f"確認ping {gw_new_ip}時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check, retry=20)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.開啟Gateway新的網頁位置
    def test_14_00_get_new_gw_url(self):
        """開啟Gateway新的網頁位置"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.d.get(f"https://{gw_new_ip}")
                print(f"[INFO] 開啟Gateway新的網頁位置") 
                return True
            except Exception as err:
                tf.catch_exc(f"開啟Gateway新的網頁位置時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                acc_elem = '//*[@id="Login_Account"]'
                WebDriverWait(self.d, 20).until(
                    EC.presence_of_element_located((By.XPATH, acc_elem)))
                print(f"[INFO] 已確認開啟Gateway新的網頁位置")
                return True
            except Exception as err:
                tf.catch_exc(f"確認開啟新網頁位置時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.重做01_00、02_00、05_00
    def test_15_00_redo_0100_0200_0500(self):
        """重做01_00、02_00、05_00"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_01_00_sendkey_to_login()
                self.test_02_00_wait_page_loading()
                self.test_05_00_click_network_config()
                print(f"[INFO] 已重做01_00、02_00、05_00") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做01_00、02_00、05_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                ssid_elem = 'System_Router_SSID'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, ssid_elem)))
                print(f"[INFO] 重做01_00、02_00、05_00完成")
                return True
            except Exception as err:
                tf.catch_exc(f"確認重做時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.恢復Wi-Fi SSID設定並儲存
    def test_16_00_restore_wifi_setting(self):
        """恢復Wi-Fi SSID設定並儲存"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                ssid_elem = 'System_Router_SSID'
                ssid_box = self.d.find_element(By.ID, ssid_elem)
                ssid_box.clear()
                ssid_box.send_keys(ori_ssid)
                print(f"[SENDKEY] {ori_ssid}")
                pw_elem = 'System_Router_SSID_Pwd'
                pw_box = self.d.find_element(By.ID, pw_elem)
                pw_box.clear()
                pw_box.send_keys(ori_pw)
                print(f"[SENDKEY] {ori_pw}") 
                save_elem = 'system-net-config-save-btn'
                save_btn = self.d.find_element(By.CLASS_NAME, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"恢復Wi-Fi SSID設定並儲存時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 出現確認彈窗") 
                tf.output(f"[INFO] 已設定原來的SSID: {ori_ssid}")
                return True
            except Exception as err:
                tf.catch_exc(f"未出現確認彈窗, 設定失敗", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_click_network_config()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 17_00.確認Gateway已切換網路
    def test_17_00_check_gw_change_wifi(self):
        """確認Gateway已切換網路"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                ping_cmd = f'ping {gw_new_ip} -w 1 -n 2'
                start_time = datetime.now()
                timeout = timedelta(seconds=30)
                while datetime.now() <= start_time + timeout:
                    result = subprocess.run(ping_cmd, 
                                            capture_output=True)
                    if result.returncode == 1:
                        print(f"[INFO] Gateway已切換網路")
                        return True
                else:
                    print(f"[FAIL] 已超時, Gateway未切換網路")
                    return False
            except Exception as err:
                tf.catch_exc(f"確認Gateway已切換網路時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 18_00.PC Wi-Fi連接到原來的SSID
    def test_18_00_pc_connect_to_original_ssid(self):
        """PC Wi-Fi連接到原來的SSID"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 嘗試連線到原來的SSID
            if pc_wifi_ssid:
                try:
                    join_cmd = f'netsh wlan connect name={pc_wifi_ssid} '\
                        f'ssid={pc_wifi_ssid} interface="{pc_wifi_interf}"'
                    start_time = datetime.now()
                    timeout = timedelta(seconds=30)
                    while datetime.now() <= start_time + timeout:
                        join_ack = subprocess.run(join_cmd, 
                                                capture_output=True, 
                                                encoding=self.encode)
                        if join_ack.returncode == 0:
                            print(f"[INFO] 已連線到{pc_wifi_ssid}"\
                                  f"({datetime.now()})")
                            tf.output(f"[INFO] 已連線到{pc_wifi_ssid}"\
                                      f"({datetime.now()})")
                            return True
                        time.sleep(1)
                    else:
                        print(f"[FAIL] 已超時, 無法連接{pc_wifi_ssid}"\
                              f"({datetime.now()})")
                        tf.output(f"[FAIL] 已超時, 無法連接{pc_wifi_ssid}"\
                                  f"({datetime.now()})")
                except Exception as err:
                    tf.catch_exc(f"連線到Sta Mode測試SSID時發生錯誤", 
                                 self._testMethodName,  err)
                    return False
            else:
                return True # 使用有線網路連接時無需再連Wi-Fi 
                        
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 19_00.從LAN中尋找Gateway新IP
    def test_19_00_find_gw_ip_in_lan(self):
        """從LAN中尋找Gateway新IP"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global gw_new_ip
            try:
                time.sleep(3)   # 等待Gateway連上新網路
                gw_new_ip = ""
                gw_new_ip = tf.udp_find_master_ip(tf.gw_mac)
                if gw_new_ip:
                    print(f"[INFO] 已找到Gateway IP: {gw_new_ip}") 
                    tf.output(f"[INFO] 已找到Gateway IP: {gw_new_ip}")
                    return True
                else:
                    print(f"[FAIL] 在{pc_wifi_ssid}中找不到Gateway IP")
                    tf.output(f"[FAIL] 在{pc_wifi_ssid}中找不到Gateway IP")
                    return False
            except Exception as err:
                tf.catch_exc(f"從LAN中尋找Gateway新IP時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                # 確認ping Gateway新IP可回應
                ping_cmd = f'ping -w 1 -n 1 {gw_new_ip}'
                start_time = datetime.now()
                timeout = timedelta(seconds=60)
                while datetime.now() <= start_time + timeout:
                    ack = subprocess.run(ping_cmd, 
                                         capture_output=True)
                    if ack.returncode == 0:
                        print(f"[INFO] {gw_new_ip} acked({datetime.now()}).")
                        tf.output(f"[INFO] {gw_new_ip} acked({datetime.now()}).")
                        return True
                else:
                    print(f"[FAIL] 已超時, {gw_new_ip}無回應({datetime.now()})")
                    tf.output(f"[FAIL] 已超時, {gw_new_ip}無回應({datetime.now()})")
                    return False

            except Exception as err:
                tf.catch_exc(f"確認ping {gw_new_ip}時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 20_00.開啟Gateway網頁位置
    def test_20_00_get_new_gw_url(self):
        """開啟Gateway網頁位置"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.d.get(f"https://{gw_new_ip}")
                print(f"[INFO] 開啟Gateway新的網頁位置") 
                return True
            except Exception as err:
                tf.catch_exc(f"開啟Gateway新的網頁位置時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                acc_elem = '//*[@id="Login_Account"]'
                WebDriverWait(self.d, 20).until(
                    EC.presence_of_element_located((By.XPATH, acc_elem)))
                print(f"[INFO] 已確認開啟Gateway新的網頁位置")
                return True
            except Exception as err:
                tf.catch_exc(f"確認開啟新網頁位置時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag


if __name__ == "__main__":
    tf.init_test(sys_07_wifi_sta_mode)
