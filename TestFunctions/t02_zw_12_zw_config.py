#==============================================================================
# 程式功能: 測試Set Poll Time
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.點擊10次zwave icon
# 07_00.輸入密碼
# 08_00.點擊Zwave_Configuratin分頁
# 09_00.取得目前的Poll Time
# 10_00.設定Poll Time
# 11_00.檢查設定的Poll Time
# 12_00.復原Poll Time
#==============================================================================
import os
import sys
import time
import json
import unittest
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(os.path.dirname(curr_path))  #.\iHub_Autotest
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import MiniGateway.mqtt_lite as mq

class zw_12_zw_config(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        tf.output(f"\n[STATUS] {self.__name__} start.\n")
        # 設置ChromeDriver選項
        self.d = webdriver.Chrome(tf.set_chrome_options()) 

        tf.set_fail(self, False)
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
        # 如果前步驟失敗，就略過此測試
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
                # 當Alert出現，點擊確認來關閉Alert
                alert = self.d.switch_to.alert
                alert.accept()
                print(f"[CLICK] Alert-Accept.")
            except Exception as err:
                # 若登入失敗，也沒有出現Alert->重整頁面再試
                tf.catch_exc(f"Accept alert failed.", 
                             self._testMethodName,  err)
                self.d.refresh()
                
        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 02_00.等待頁面載入完成
    def test_02_00_wait_page_loading(self):
        """等待頁面載入完成"""
        # 如果前步驟失敗，就略過此測試
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
                tf.catch_exc(f"Loader超時未消失, 頁面載入失敗", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 03_00.從System頁面取得Gateway資訊
    def test_03_00_get_gateway_info(self):
        """從System頁面取得Gateway資訊"""
        # 如果前步驟失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
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
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 04_00.點擊Z-Wave
    def test_04_00_click_zw_icon(self):
        """點擊Z-Wave"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                zw_elem = '//*[@id="Main_menu_zwave"]'
                WebDriverWait(self.d, 10).until(
                    EC.element_to_be_clickable((By.XPATH, zw_elem)))
                zw = self.d.find_element(By.XPATH, zw_elem)
                zw.click()
                print(f"[CLICK] Z-Wave")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Z-Wave時發生錯誤", self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(0.5)
                loader_elem = 'Loader_Modal'
                WebDriverWait(self.d, 5).until(
                    EC.visibility_of_element_located((By.ID, loader_elem)))
                print(f"[INFO] Loader出現")
                WebDriverWait(self.d, 15).until(
                    EC.invisibility_of_element((By.ID, loader_elem)))
                print(f"[INFO] Loader消失")
                return True
            except Exception as err:
                tf.catch_exc(f"確認頁面時發生錯誤", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 05_00.等待內容載入完成
    def test_05_00_wait_content_loading(self):
        """等待內容載入完成"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                tf.output(f"[INFO] MQTT訊息接收中...")
                tf.wait_mqtt_info_loading()
                print(f"[INFO] 載入完成")
                tf.output(f"[INFO] 接收完成")
                return True
            except Exception as err:
                tf.catch_exc(f"等待內容載入完成時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, retry=1)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 06_00.點擊10次zwave icon
    def test_06_00_click_zwave_icon_10_times(self):
        """點擊10次zwave icon"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                gear_elem = '//*[@id="Main_Header_Menu_Icon"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, gear_elem)))
                gear_icon = self.d.find_element(By.XPATH , gear_elem)
                for i in range(10):
                    gear_icon.click()
                print("[CLICK] zwave icon 10 times.")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊zwave icon時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = 'sys-setting-confirm-modal-closeBtn'
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

# 07_00.輸入密碼
    def test_07_00_input_password(self):
        """輸入密碼"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                pw_box_elem = '//*[@id="Zw_Setting_IMACheck_Modal"]/div/div[2]/input[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, pw_box_elem)))
                pw_box = self.d.find_element(By.XPATH, pw_box_elem)
                pw_box.send_keys(tf.gw_dev_pw)
                print(f"[SENDKEY] 輸入密碼: {tf.gw_dev_pw}")
                send_elem = '//*[@id="Zw_Setting_IMACheck_Modal"]/div/div[2]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, pw_box_elem)))
                send_btn = self.d.find_element(By.XPATH, send_elem)
                send_btn.click()
                print(f"[CLICK] 點擊Send")
                return True
            except Exception as err:
                tf.catch_exc(f"輸入密碼時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                tab_elem = '//*[@id="Zwave_Configuration"]/span'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, tab_elem)))
                print(f"[INFO] Zwave_Configuration分頁出現")
                return True
            except Exception as err:
                tf.catch_exc(f"Zwave_Configuration分頁未出現", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_04_00_click_zw_icon()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.點擊Zwave_Configuratin分頁
    def test_08_00_click_zw_config_tab(self):
        """點擊Zwave_Configuratin分頁"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                mq.msg_que = []
                zw_conf_elem = 'zw-config-word'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, zw_conf_elem)))
                zw_conf_tab = self.d.find_element(By.CLASS_NAME, zw_conf_elem)
                zw_conf_tab.click()
                print(f"[CLICK] Zwave_Configuratin")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Zwave_Configuratin分頁時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                poll_elem = 'poll_time'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, poll_elem)))
                print(f"[INFO] 已確認Zwave_Configuratin頁面")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Zwave_Configuratin頁面時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.取得目前的Poll Time
    def test_09_00_get_poll_time(self):
        """取得目前的Poll Time"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global poll_time
            try:
                poll_elem = 'poll_time'
                poll = self.d.find_element(By.CLASS_NAME, poll_elem)
                poll_time = int(poll.get_attribute("value"))
                print(f"[INFO] 目前的Poll Time: {poll_time}")
                return True
            except Exception as err:
                tf.catch_exc(f"取得目前的Poll Time時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.設定Poll Time
    def test_10_00_set_poll_time(self):
        """設定Poll Time"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定目前的Poll Time +1
            try:
                mq.msg_que = []
                poll_elem = 'poll_time'
                poll = self.d.find_element(By.CLASS_NAME, poll_elem)
                poll.clear()
                poll.send_keys(f"{poll_time + 1}")
                print(f"[SENDKEY] {poll_time + 1}")
                time.sleep(1)
                update_elem = '//*[@id="Zwave_Config"]/div[8]/div'
                update_btn = self.d.find_element(By.XPATH, update_elem)
                update_btn.click()
                print(f"[CLICK] update")
                return True
            except Exception as err:
                tf.catch_exc(f"設定Poll Time時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_SET_DEV_POLL_TIME"', 
                           F'"ZWAVE_POLL_TIME":{poll_time + 1}']
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_SET_DEV_POLL_TIME訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認訊息")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.檢查設定的Poll Time
    def test_11_00_check_poll_time(self):
        """檢查設定的Poll Time"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 按下update設定poll time後不會自動回報ZW_GET_DEV_POLL_TIME
            # 需再點擊Zwave_Configuratin分頁才會回到目前的poll time
            try:
                self.test_08_00_click_zw_config_tab()
                print(f"[INFO] 已點擊Zwave_Configuratin分頁")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查設定的Poll Time時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                keyword = ['"ZwCmd": "ZW_GET_DEV_POLL_TIME"', 
                           f'"DevPollTime": {poll_time + 1}']
                msg = tf.wait_mqtt_msg(keyword, 10)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_GET_DEV_POLL_TIME訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認訊息")
                    time.sleep(0.5)
                    poll_elem = 'poll_time'
                    poll = self.d.find_element(By.CLASS_NAME, poll_elem)
                    if int(poll.get_attribute("value")) != poll_time + 1:
                        print(f"[FAIL] 輸入框內的Poll Time數值錯誤")
                        return False
                    print(f"[INFO] 已確認輸入框內的Poll Time數值")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.復原Poll Time
    def test_12_00_set_poll_time(self):
        """復原Poll Time"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                poll_elem = 'poll_time'
                poll = self.d.find_element(By.CLASS_NAME, poll_elem)
                poll.clear()
                poll.send_keys(f"{poll_time}")
                print(f"[SENDKEY] {poll_time}")
                time.sleep(1)
                update_elem = '//*[@id="Zwave_Config"]/div[8]/div'
                update_btn = self.d.find_element(By.XPATH, update_elem)
                update_btn.click()
                print(f"[CLICK] update")
                return True
            except Exception as err:
                tf.catch_exc(f"復原Poll Time時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_SET_DEV_POLL_TIME"', 
                           F'"ZWAVE_POLL_TIME":{poll_time}']
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_SET_DEV_POLL_TIME訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認訊息")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# # Template
#     def test_(self):
#         """Temp"""
#         # 如果前面測試失敗，就略過此測試
#         if tf.flag_test_fail:
#             self.skipTest(tf.fail_reason)
#         def action():
#             try:
#                 print(f"[INFO] ")
#                 return True
#             except Exception as err:
#                 tf.catch_exc(f"時發生錯誤", 
#                              self._testMethodName,  err)
#                 return False
        
#         def check(info):
#             try:
#                 print(f"[INFO] ")
#                 return True
#             except Exception as err:
#                 tf.catch_exc(f"時發生錯誤", 
#                              self._testMethodName,  err)
#                 return False
            
#         def reset():
#             ""

#         success_flag = tf.execute(action, check, reset)
#         # 測試失敗時設定旗標，並跳過後面的步驟
#         if not success_flag: 
#             tf.set_fail(self._testMethodName, True)
#         assert success_flag

if __name__ == "__main__":
    tf.init_test(zw_12_zw_config)

