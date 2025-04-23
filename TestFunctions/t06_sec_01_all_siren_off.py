#==============================================================================
# 程式功能: 測試安防 All siren off
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置siren
# 07_00.點擊Security
# 08_00.重做02_00、05_00, 等待內容載入完成
# 09_00.發送訊息開啟Siren
# 10_00.點擊All siren off
# 11_00.關閉彈窗
#==============================================================================
import os
import sys
import time
import unittest
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(os.path.dirname(curr_path))  #.\iHub_Autotest
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import mqtt_lite as mq

class sec_01_all_siren_off(unittest.TestCase):
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
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()

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

# 06_00.檢查必要裝置siren
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

# 07_00.點擊Security
    def test_07_00_click_security(self):
        """點擊Security"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                sec_elem = '//*[@id="Main_menu_security"]'
                WebDriverWait(self.d, 10).until(
                    EC.element_to_be_clickable((By.XPATH, sec_elem)))
                sec = self.d.find_element(By.XPATH, sec_elem)
                sec.click()
                print(f"[CLICK] Security")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Security時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.重做02_00、05_00, 等待內容載入完成
    def test_08_00_redo_0200_0500(self):
        """重做02_00、05_00, 等待內容載入完成"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_02_00_wait_page_loading()
                self.test_05_00_wait_content_loading()
                print(f"[INFO] 已重做02_00、05_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00、05_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.發送訊息開啟Siren
    def test_09_00_turn_siren_off(self):
        """發送訊息開啟Siren"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 直接Publish訊息來關閉, 若原本狀態為OFF
            # 則不會收到回復, 故只要Publish成功即可 
            try:
                mq.msg_que = []
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                siren_on = '{"EVENT":"ZW_SWITCH_BINARY_SET", "NODE_ID":%s, "ENDPOINT_ID":0, "SWITCH":"ON", "TO_MS_UUID":"%s"}'%(node, uuid)
                result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", siren_on)
                if not result:
                    print(f"[FAIL] 開啟Siren失敗")
                    return False
                print(f"[INFO] 已送出訊息: {siren_on}")
                return True
            except Exception as err:
                tf.catch_exc(f"開啟Siren時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                node = at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "On"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 30)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到SWITCH_BINARY_REPORT訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認訊息")
                    tf.output(f"[INFO] 裝置已觸發")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.點擊All siren off
    def test_10_00_click_all_siren_off(self):
        """點擊All siren off"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(2)
                off_elem = '//*[@id="Security_All_List_Page"]/div[2]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, off_elem)))
                off_btn = self.d.find_element(By.XPATH, off_elem)
                off_btn.click()
                print(f"[CLICK] All Siren off")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊All siren off時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                node = at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "Off"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 30)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到SWITCH_BINARY_REPORT訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認訊息")
                    tf.output(f"[INFO] 裝置已觸發")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.關閉彈窗
    def test_11_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                cls_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, cls_elem)))
                cls_btn = self.d.find_element(By.CLASS_NAME, cls_elem)
                cls_btn.click()
                print(f"[CLICK] Close")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                cls_elem = '//*[@id="Security_Notify_Modal"]/div/div[1]/svg'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.XPATH, cls_elem)))
                print(f"[INFO] 彈窗消失")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗消失時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# # _00.Template
    # def _(self):
    #     """Temp"""
    #     # 如果前面測試失敗，就略過此測試
    #     if tf.flag_test_fail:
    #         self.skipTest(tf.fail_reason)
    #     def action():
    #         try:
    #             print(f"[INFO] ")
    #             return True
    #         except Exception as err:
    #             tf.catch_exc(f"時發生錯誤", 
    #                          self._testMethodName,  err)
    #             return False
        
    #     def check(info):
    #         try:
    #             print(f"[INFO] ")
    #             return True
    #         except Exception as err:
    #             tf.catch_exc(f"時發生錯誤", 
    #                          self._testMethodName,  err)
    #             return False
            
    #     def reset():
    #         ""

    #     success_flag = tf.execute(action, check, reset)
    #     # 測試失敗時設定旗標，並跳過後面的步驟
    #     if not success_flag: 
    #         tf.set_fail(self._testMethodName, True)
    #     assert success_flag

if __name__ == "__main__":
    tf.init_test(sec_01_all_siren_off)

