#==============================================================================
# 程式功能: 測試裝置History
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置
# 07_00.點擊關閉鈴鐺Alert
# 07_01.點擊atsiren name
# 08_00.確認Toggle狀態
# 09_00.點擊Toggle switch
# 10_00.確認Switch MQTT訊息
# 11_00.復原toggle狀態
# 12_00.點擊Event History
# 13_00.等待歷史資料載入
# 14_00.關閉彈窗
# 15_00.重做12_00、13_00
# 16_00.檢查最後一筆資料
# 17_00.點擊選擇Type
# 18_00.點擊下拉選單中的最後項目
# 19_00.點擊選擇時間
# 20_00.點選Today並檢查MQTT "USER_TO_MIDDLE"
# 21_00.點選Yesterday並檢查MQTT "USER_TO_MIDDLE"
# 22_00.點選Two days ago並檢查MQTT "USER_TO_MIDDLE"
# 23_00.點選Three days ago並檢查MQTT "USER_TO_MIDDLE"
# 24_00.選擇時間區間並檢查MQTT "USER_TO_MIDDLE"
#==============================================================================
import os
import sys
import time
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

class zw_06_device_history(unittest.TestCase):
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
    def test_04_00_click_zw(self):
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

# 06_00.檢查必要裝置
    def test_06_00_check_device_need(self):
        """檢查必要裝置"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global at_dev_name, at_dev_id, at_dev_uuid, at_dev_room
            try:
                dev_need = [tf.siren]
                at_dev_name, at_dev_room, at_dev_id, at_dev_uuid = {}, {}, {}, {}
                for dev in dev_need:
                    elem = f'//*[contains(text(), "{dev}")]'
                    WebDriverWait(self.d, 10).until(
                        EC.presence_of_element_located((By.XPATH, elem)))
                    device = self.d.find_element(By.XPATH, elem)
                    at_dev_name[dev] = device.text
                    at_dev_id[dev] = device.get_property("id").split("_")[4]
                    at_dev_uuid[dev] = device.get_property("id").split("_")[3]
                    room_elem = f'//*[@id="All_dev_tb_{at_dev_uuid[dev]}'\
                        f'_{at_dev_id[dev]}_position"]'
                    at_dev_room[dev] = self.d.find_element(By.XPATH, room_elem).text
                    print(f"[INFO] 已確認裝置: ")
                    print(f"Name:{at_dev_name[dev]}", end="/ ")
                    print(f"NodeId:{at_dev_id[dev]}", end="/ ")
                    print(f"uuid:{at_dev_uuid[dev]}", end="/ ")
                    print(f"Room:{at_dev_room[dev]}")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查必要裝置時發生錯誤", 
                             self._testMethodName,  err)
                return False       

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_00.點擊關閉鈴鐺Alert
    def test_07_00_click_alert_bell(self):
        """點擊關閉鈴鐺Alert"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                bell_elem = f'//*[@id="Alert_Toggle_Tag"]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, bell_elem)))
                bell = self.d.find_element(By.XPATH, bell_elem)
                bell.click()
                print(f"[CLICK] Bell")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊關閉鈴鐺Alert時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(0.5)
                bell_elem = f'//*[@id="Alert_Toggle_Tag"]'
                bell = self.d.find_element(By.XPATH, bell_elem)
                if "enable" in bell.get_attribute("class"):
                    print(f"[FAIL] 關閉鈴鐺Alert失敗")
                    return False
                print(f"[INFO] 已關閉鈴鐺Alert")
                return True
            except Exception as err:
                tf.catch_exc(f"確認關閉鈴鐺Alert時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_01.點擊atsiren name
    def test_07_01_click_atsiren_name(self):
        """點擊atsiren"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                atsiren_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_name"]'
                atsiren = self.d.find_element(By.XPATH, atsiren_elem)
                atsiren.click()
                print(f"[CLICK] {at_dev_name[tf.siren]}")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊atsiren時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                node_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_Modal_Name"]'
                WebDriverWait(self.d, 5).until(
                    EC.visibility_of_element_located((By.XPATH, node_elem)))
                print(f"[INFO] 已確認彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.確認Toggle狀態
    def test_08_00_check_toggle_stat(self):
        """確認Toggle狀態"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                global toggle_stat
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, status_elem)))
                status = self.d.find_element(By.XPATH, status_elem)
                # 從toggle的class判斷目前開關狀態(它不能click): 
                # on: class="toggle-btn active"
                # off: class="toggle-btn"
                toggle_elem = './/*[starts-with(@class, "toggle-btn")]'
                toggle = status.find_element(By.XPATH, toggle_elem)
                if "active" in toggle.get_attribute("class"):
                    toggle_stat = True
                    print(f"[INFO] 目前siren為On")
                else:
                    toggle_stat = False
                    print(f"[INFO] 目前siren為Off")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Toggle狀態時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.點擊Toggle switch
    def test_09_00_click_toggle_switch(self):
        """點擊Toggle switch"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global click_time
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                status = self.d.find_element(By.XPATH, status_elem)
                mq.msg_que = []
                # # 從區塊中找到toggle裡的小圓球(它才能被click)
                circle_elem = 'inner-circle'
                circle = status.find_element(By.CLASS_NAME, circle_elem)
                circle.click()
                click_time = datetime.now()
                print(f"[CLICK] Toggle switch")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Toggle switch時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.確認Switch MQTT訊息
    def test_10_00_check_switch_on_mqtt_msg(self):
        """確認Switch MQTT訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 若當前siren為Off, 則click後應收到"TgtSts": "On"
                if toggle_stat:
                    stat = '"TgtSts": "Off"'
                else:
                    stat = '"TgtSts": "On"'
                
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           f'"NodeID": "{node}"', stat]
                
                msg = tf.wait_mqtt_msg(keyword, 10)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到Switch On/Off訊息")
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
                tf.catch_exc(f"確認Switch MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_08_00_check_toggle_stat()
            self.test_09_00_click_toggle_switch()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.復原toggle狀態
    def test_11_00_restore_toggle(self):
        """復原toggle狀態"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, status_elem)))
                status = self.d.find_element(By.XPATH, status_elem)
                # 從toggle的class判斷目前開關狀態(它不能click): 
                # on: class="toggle-btn active"
                # off: class="toggle-btn"
                toggle_elem = './/*[starts-with(@class, "toggle-btn")]'
                toggle = status.find_element(By.XPATH, toggle_elem)
                if "active" in toggle.get_attribute("class"):
                    if toggle_stat == False:
                        self.test_09_00_click_toggle_switch()
                        print(f"[INFO] 已復原toggle狀態")
                        return True
                else:
                    if toggle_stat == True:
                        self.test_09_00_click_toggle_switch()
                        print(f"[INFO] 已復原toggle狀態")
                        return True
            except Exception as err:
                tf.catch_exc(f"復原toggle狀態時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 若當前siren為Off, 則click後應收到"TgtSts": "On"

                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           f'"NodeID": "{node}"']
                
                msg = tf.wait_mqtt_msg(keyword, 10)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到Switch On/Off訊息")
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
                tf.catch_exc(f"確認Switch MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.點擊Event History
    def test_12_00_click_event_history(self):
        """點擊Event History"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                history_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_Modal"]/div/div[2]/div[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, history_elem)))
                history_btn = self.d.find_element(By.XPATH, history_elem)
                history_btn.click()
                print(f"[CLICK] Event History")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Event History時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                cls_elem = f'zw-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, cls_elem)))
                print(f"[INFO] 確認彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.等待歷史資料載入
    def test_13_00_wait_history_loading(self):
        """等待歷史資料載入"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                print(f"[INFO] 歷史資料載入中...")
                tf.output(f"[INFO] 歷史資料載入中...")
                tf.wait_mqtt_info_loading(1)
                print(f"[INFO] 載入完成")
                tf.output(f"[INFO] 載入完成")
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

# 14_00.關閉彈窗
    def test_14_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                header_elem = 'zw-setting-history-modal-header'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, header_elem)))
                header = self.d.find_element(By.CLASS_NAME, header_elem)
                cls_elem = 'zw-setting-confirm-modal-closeBtn'
                cls_btn = header.find_element(By.CLASS_NAME, cls_elem)
                cls_btn.click()
                print(f"[CLICK] Close")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                cls_elem = '//*[@id="Zw_Setting_History_Modal"]/div/div[1]/svg'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.XPATH, cls_elem)))
                print(f"[INFO] 已關閉彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.重做12_00、13_00
    def test_15_00_redo_1200_1300(self):
        """重做12_00, 13_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_12_00_click_event_history()
                self.test_13_00_wait_history_loading()
                print(f"[INFO] 已重做12_00、13_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做12_00、13_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.檢查最後一筆資料
    def test_16_00_check_last_log(self):
        """檢查最後一筆資料"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                tb_elem = f'//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[3]/table/tbody'
                tb = self.d.find_element(By.XPATH, tb_elem)
                tr = tb.find_elements(By.TAG_NAME, "tr")
                td = tr[0].find_elements(By.TAG_NAME, "td")
                td_type = td[1].text
                if "Switch Binary" not in td_type:
                    print(f"[FAIL] 資料型態錯誤:{td_type}")
                    return False
                td_time = td[0].text
                log_time = datetime.strptime(td_time, "%Y-%m-%dT%H:%M:%S")
                allow_range = timedelta(seconds=10)
                if abs(log_time - click_time) > allow_range:
                    print(f"[FAIL] 資料時間錯誤:{log_time}")
                    return False
                print(f"[INFO] 已確認歷史記錄:")
                print(f"點擊時間:{click_time}")
                print(f"紀錄時間:{log_time}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認歷史記錄時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_14_00_close_pop()
            self.test_12_00_click_event_history()
            self.test_13_00_wait_history_loading()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 17_00.點擊選擇Type
    def test_17_00_click_select_type(self):
        """點擊選擇Type"""
        # 如果前面測試失敗，仍繼續測試
        if tf.flag_test_fail:
            tf.flag_test_fail = False
            tf.fail_reason = ""

        def action():
            try:
                sel_type_elem = '//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[2]/table/tbody/tr/td[2]/div'
                sel_type = self.d.find_element(By.XPATH, sel_type_elem)
                sel_type.click()
                print(f"[CLICK] Select Type")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊選擇Type時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                sel_type_elem = '//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[2]/table/tbody/tr/td[2]/div'
                sel_type = self.d.find_element(By.XPATH, sel_type_elem)
                if "active" not in sel_type.get_attribute("class"):
                    print(f"[FAIL] 下拉選單未展開")
                    return False
                print(f"[INFO] 下拉選單已展開")
                return True
            except Exception as err:
                tf.catch_exc(f"確認下拉選單時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 18_00.點擊下拉選單中的最後項目
    def test_18_00_click_last_item(self):
        """點擊下拉選單中的最後項目"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.5)
                ul_elem = '//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[2]/table/tbody/tr/td[2]/div/ul'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, ul_elem)))
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, "li")
                item_name = li[len(li)-1].text
                li[len(li)-1].click()
                print(f"[CLICK] {item_name}")
                return item_name
            except Exception as err:
                tf.catch_exc(f"時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        # 檢查是否正確過濾Type
        def check(info):
            try:
                time.sleep(1)
                item_name = info
                tb_elem = f'//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[3]/table/tbody'
                tb = self.d.find_element(By.XPATH, tb_elem)
                tr = tb.find_elements(By.TAG_NAME, "tr")
                for i in tr:
                    if "display: none;" in i.get_attribute("style"):
                        continue
                    td = i.find_elements(By.TAG_NAME, "td")
                    if td[1].text != item_name:
                        print(f"[FAIL] Type錯誤, 出現非{item_name}的項目")
                        return False
                print(f"[INFO] 已檢查Type")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查Type時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_17_00_click_select_type()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 19_00.點擊選擇時間
    def test_19_00_click_select_time(self):
        """點擊選擇時間"""
        # 如果前面測試失敗，仍繼續測試
        if tf.flag_test_fail:
            tf.flag_test_fail = False
            tf.fail_reason = ""
        def action():
            try:
                sel_time_elem = '//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[2]/table/tbody/tr/td[1]/div'
                sel_time = self.d.find_element(By.XPATH, sel_time_elem)
                sel_time.click()
                print(f"[CLICK] Select time")
                time.sleep(0.5)
                return True
            except Exception as err:
                tf.catch_exc(f"點擊選擇時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                sel_time_elem = '//*[@id="Zw_Setting_History_Modal"]'\
                    f'/div/div[2]/table/tbody/tr/td[1]/div'
                sel_time = self.d.find_element(By.XPATH, sel_time_elem)
                if "active" not in sel_time.get_attribute("class"):
                    print(f"[FAIL] 下拉選單未展開")
                    return False
                print(f"[INFO] 下拉選單已展開")
                return True
            except Exception as err:
                tf.catch_exc(f"確認下拉選單時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 20_00.點選Today並檢查MQTT "USER_TO_MIDDLE"
    def test_20_00_click_today(self):
        """點選Today"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                today_elem = '//*[@id="Zw_History_DropDownDate"]/a[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, today_elem)))
                today = self.d.find_element(By.XPATH, today_elem)
                today.click()
                print(f"[CLICK] Today")
                tf.output(f"[INFO] 查詢資料: Today")
                return True
            except Exception as err:
                tf.catch_exc(f"點選Today時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                # Today: 查詢時間為前日16:00:00-今日16:00:00
                st = datetime.now() - timedelta(days=1)
                ed = datetime.now()
                date_st = f'"DateStart":"{st.year}-{st.month:02d}-{st.day:02d} 16:00:00"'
                date_ed = f'"DateEnd":"{ed.year}-{ed.month:02d}-{ed.day:02d} 16:00:00"'
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_HISTORY_GETOFDATE"', 
                           date_st, date_ed]
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_HISTORY_GETOFDATE訊息")
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
            
        def reset():
            self.test_19_00_click_select_time()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 21_00.點選Yesterday並檢查MQTT "USER_TO_MIDDLE"
    def test_21_00_click_yesterday(self):
        """點選Yesterday"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_13_00_wait_history_loading()
                self.test_19_00_click_select_time()
                mq.msg_que = []
                yesterday_elem = '//*[@id="Zw_History_DropDownDate"]/a[2]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, yesterday_elem)))
                yesterday = self.d.find_element(By.XPATH, yesterday_elem)
                yesterday.click()
                print(f"[CLICK] Yesterday")
                tf.output(f"[INFO] 查詢資料: Yesterday")
                return True
            except Exception as err:
                tf.catch_exc(f"點選Yesterday時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                # Yesterday: 查詢時間為兩日前16:00:00-前日16:00:00
                st = datetime.now() - timedelta(days=2)
                ed = datetime.now() - timedelta(days=1)
                date_st = f'"DateStart":"{st.year}-{st.month:02d}-{st.day:02d} 16:00:00"'
                date_ed = f'"DateEnd":"{ed.year}-{ed.month:02d}-{ed.day:02d} 16:00:00"'
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_HISTORY_GETOFDATE"', 
                           date_st, date_ed]
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_HISTORY_GETOFDATE訊息")
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
            
        def reset():
            self.test_19_00_click_select_time()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 22_00.點選Two days ago並檢查MQTT "USER_TO_MIDDLE"
    def test_22_00_click_two_days_ago(self):
        """點選Two days ago"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_13_00_wait_history_loading()
                self.test_19_00_click_select_time()
                mq.msg_que = []
                two_days_elem = '//*[@id="Zw_History_DropDownDate"]/a[3]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, two_days_elem)))
                two_days = self.d.find_element(By.XPATH, two_days_elem)
                two_days.click()
                print(f"[CLICK] Two days ago")
                tf.output(f"[INFO] 查詢資料: Two days ago")
                return True
            except Exception as err:
                tf.catch_exc(f"點選Two days ago時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                # Two days ago: 查詢時間為三日前16:00:00-兩日前16:00:00
                st = datetime.now() - timedelta(days=3)
                ed = datetime.now() - timedelta(days=2)
                date_st = f'"DateStart":"{st.year}-{st.month:02d}-{st.day:02d} 16:00:00"'
                date_ed = f'"DateEnd":"{ed.year}-{ed.month:02d}-{ed.day:02d} 16:00:00"'
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_HISTORY_GETOFDATE"', 
                           date_st, date_ed]
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_HISTORY_GETOFDATE訊息")
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
            
        def reset():
            self.test_19_00_click_select_time()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 23_00.點選Three days ago並檢查MQTT "USER_TO_MIDDLE"
    def test_23_00_click_three_days_ago(self):
        """點選Three days ago"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_13_00_wait_history_loading()
                self.test_19_00_click_select_time()
                mq.msg_que = []
                three_days_elem = '//*[@id="Zw_History_DropDownDate"]/a[4]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, three_days_elem)))
                three_days = self.d.find_element(By.XPATH, three_days_elem)
                three_days.click()
                print(f"[CLICK] Three days ago")
                tf.output(f"[INFO] 查詢資料: Three days ago")
                return True
            except Exception as err:
                tf.catch_exc(f"點選Three days ago時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                # Three days ago: 查詢時間為四日前16:00:00-三日前16:00:00
                st = datetime.now() - timedelta(days=4)
                ed = datetime.now() - timedelta(days=3)
                date_st = f'"DateStart":"{st.year}-{st.month:02d}-{st.day:02d} 16:00:00"'
                date_ed = f'"DateEnd":"{ed.year}-{ed.month:02d}-{ed.day:02d} 16:00:00"'
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_HISTORY_GETOFDATE"', 
                           date_st, date_ed]
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_HISTORY_GETOFDATE訊息")
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
            
        def reset():
            self.test_19_00_click_select_time()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 24_00.選擇時間區間並檢查MQTT "USER_TO_MIDDLE"
    def test_24_00_select_range(self):
        """選擇時間區間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # From: 選擇Date Picker table中的第4列第2行的日期
            # To: 選擇Date Picker table中的第4列第6行的日期
            try:
                self.test_13_00_wait_history_loading()
                self.test_19_00_click_select_time()
                mq.msg_que = []
                st_day_elem = '//*[@id="Zw_History_Datepicker_From"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, st_day_elem)))
                st_day = self.d.find_element(By.XPATH, st_day_elem)
                st_day.click()
                print(f"[CLICK] Date From")
                time.sleep(0.5) # 等待date picker展開
                st_date_elem = '//*[@id="ui-datepicker-div"]/table/tbody/tr[4]/td[2]/a'
                st_date = self.d.find_element(By.XPATH, st_date_elem)
                st_num = st_date.text
                st_date.click()
                print(f"[CLICK] {st_num}")
                ed_day_elem = '//*[@id="Zw_History_Datepicker_To"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, ed_day_elem)))
                ed_day = self.d.find_element(By.XPATH, ed_day_elem)
                ed_day.click()
                print(f"[CLICK] Date To")
                time.sleep(0.5) # 等待date picker展開
                ed_date_elem = '//*[@id="ui-datepicker-div"]/table/tbody/tr[4]/td[6]/a'
                ed_date = self.d.find_element(By.XPATH, ed_date_elem)
                ed_num = ed_date.text
                ed_date.click()
                print(f"[CLICK] {ed_num}")
                go_elem = '//*[@id="Zw_History_DropDownDate"]/table/tbody/tr[3]/td/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, go_elem)))
                go_btn = self.d.find_element(By.XPATH, go_elem)
                go_btn.click()
                print(f"[CLICK] Go")
                tf.output(f"[INFO] 查詢資料: Date from {st_num} to {ed_num}")
                return st_num, ed_num
            except Exception as err:
                tf.catch_exc(f"選擇時間區間時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                # 時間區間為Date From的前一日到Date To
                t = datetime.now()
                date_st = f'"DateStart":"{t.year}-{t.month:02d}-{int(info[0])-1} 16:00:00"'
                date_ed = f'"DateEnd":"{t.year}-{t.month:02d}-{info[1]} 16:00:00"'
                keyword = ["USER_TO_MIDDLE", 
                           '"EVENT":"ZW_HISTORY_GETOFDATE"', 
                           date_st, date_ed]
                msg = tf.wait_mqtt_msg(keyword, 5)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZW_HISTORY_GETOFDATE訊息")
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
            
        def reset():
            self.test_19_00_click_select_time()

        success_flag = tf.execute(action, check, reset)
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
    tf.init_test(zw_06_device_history)

