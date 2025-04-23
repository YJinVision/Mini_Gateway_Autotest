#==============================================================================
# 程式功能: 測試裝置控制、更新時間、小鈴鐺訊息
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置
# 07_00.點擊atSiren name
# 08_00.確認Toggle狀態
# 09_00.點擊Toggle switch
# 10_00.確認鈴鐺訊息
# 11_00.確認Switch MQTT訊息
# 12_00.檢查更新時間
# 13_00.復原toggle狀態
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
import mqtt_lite as mq

class zw_05_device_control(unittest.TestCase):
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

# 07_00.點擊atsiren name
    def test_07_00_click_atsiren_name(self):
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

# 10_00.確認鈴鐺訊息
    def test_10_00_check_alert_msg(self):
        """確認鈴鐺Alert訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                if toggle_stat:
                    check_str = "switch off"
                else:
                    check_str = "switch on"
                notify_msg_elem = 'Main_Header_CmdNofity'
                notify_msg = self.d.find_element(By.ID, notify_msg_elem)
                target_elem = f'.//*[contains(text(), "{check_str}")]'
                target = notify_msg.find_element(By.XPATH, target_elem)
                print(f"[INFO] 已確認訊息: {target.text.split("\n")[1]}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認鈴鐺Alert訊息時發生錯誤", 
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

# 11_00.確認Switch MQTT訊息
    def test_11_00_check_switch_on_mqtt_msg(self):
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
                
                msg = tf.wait_mqtt_msg(keyword, 20)
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

# 12_00.檢查更新時間
    def test_12_00_check_update_time(self):
        """檢查更新時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                update_elem = f'Zw_Setting_{uuid}_{node}_LastTime'
                update = self.d.find_element(By.ID, update_elem)
                update_str = update.text.split("\n")[1]
                print(f"[INFO] 已確認更新時間:{update.text}")
                return update_str
            except Exception as err:
                tf.catch_exc(f"檢查更新時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                # info: Mon Feb 03 2025 10:11:54 
                update_time = datetime.strptime(info, "%a %b %d %Y %H:%M:%S")
                allow_range = timedelta(seconds=10)
                # 若點擊時間與Update時間誤差大於10秒 -> FAIL
                if abs(update_time - click_time) > allow_range:
                    print(f"[FAIL] 更新時間誤差過大:")
                    print(f"[FAIL] 點擊時間:{click_time}, Update:{update_time}")
                    return False
                print(f"[INFO] 已確認更新時間")
                return True
            except Exception as err:
                tf.catch_exc(f"確認更新時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_09_00_click_toggle_switch()
            self.test_11_00_check_switch_on_mqtt_msg()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.復原toggle狀態
    def test_13_00_restore_toggle(self):
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
        
        success_flag = tf.execute(action)
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
    tf.init_test(zw_05_device_control)

