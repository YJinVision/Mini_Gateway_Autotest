#==============================================================================
# 程式功能: 測試裝置Firmware upgrade功能
# 需要裝置: Remotec ZXT-800 
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置
# 07_00.點擊atZxt800 name
# 08_00.點擊Firmware Upgrade
# 09_00.關閉彈窗
# 10_00.重做08_00
# 11_00.點擊Get
# 12_00.取得Firmware檔案路徑
# 13_00.選擇Firmware
# 14_00.點擊Upgrade
# 15_00.確認MQTT訊息
# 16_00.確認更新訊息
# 17_00.確認顯示結果
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

class zw_09_device_fw_upgrade(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        tf.output(f"\n[STATUS] {self.__name__} start.\n")
        # 設置ChromeDriver選項
        self.d = webdriver.Chrome(tf.set_chrome_options()) 

        tf.set_fail(self, False)
        try:
            self.d.get(tf.gw_url)
        except:
            print("[ERROR] 無法開啟網頁")
            tf.set_fail("setUpClass", True)

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
                dev_need = [tf.remot]
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

# 07_00.點擊atZxt800 name
    def test_07_00_click_atZxt800_name(self):
        """點擊atZxt800"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.remot], at_dev_id[tf.remot]
                atZxt800_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_name"]'
                atZxt800 = self.d.find_element(By.XPATH, atZxt800_elem)
                atZxt800.click()
                print(f"[CLICK] {at_dev_name[tf.remot]}")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊atZxt800時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.remot], at_dev_id[tf.remot]
                node_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_Modal_Name"]'
                WebDriverWait(self.d, 5).until(
                    EC.visibility_of_element_located((By.XPATH, node_elem)))
                print(f"[INFO] 已確認彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()
            self.test_05_00_wait_content_loading()
            self.test_06_00_check_device_need()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.點擊Firmware Upgrade
    def test_08_00_click_fw_upgrade(self):
        """點擊Firmware Upgrade"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                uuid, node = at_dev_uuid[tf.remot], at_dev_id[tf.remot]
                up_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Modal"]/div/div[2]/div[2]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, up_elem)))
                up_btn = self.d.find_element(By.XPATH, up_elem)
                #頁面縮放100%情況下此btn可能會超出可互動範圍，需滾動到元素位置
                self.d.execute_script("arguments[0].scrollIntoView();", up_btn)
                up_btn.click()
                print(f"[CLICK] 點擊Firmware Upgrade")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Firmware Upgrade時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                get_elem = '//*[@id="Zw_Setting_UpgradeFW_Modal"]'\
                    '/div/div[2]/input'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, get_elem)))
                print(f"[INFO] 彈窗出現")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗出現時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.關閉彈窗
    def test_09_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                head_elem = 'zw-setting-confirm-modal-header'
                header = self.d.find_element(By.CLASS_NAME, head_elem)
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
                head_elem = 'zw-setting-confirm-modal-header'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.CLASS_NAME, head_elem)))
                print(f"[INFO] 已關閉彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"確認關閉彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.重做08_00
    def test_10_00_redo_0800(self):
        """重做08_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                mq.msg_que = []
                self.test_08_00_click_fw_upgrade()
                print(f"[INFO] 已重做08_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做08_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            # 開啟Upgrade介面時, 會持續收到"ZwCmd": "AllowedUpdateState"
            try:
                uuid, node = at_dev_uuid[tf.remot], at_dev_id[tf.remot]
                keyword = ['"ZwCmd": "AllowedUpdateState"', 
                           '"AllowedUpdateState": 1',
                           f'"NodeID": {node}']
                msg = tf.wait_mqtt_msg(keyword, 10)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到AllowedUpdateState訊息")
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
                tf.catch_exc(f"確認訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_09_00_close_pop()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.點擊Get
    def test_11_00_click_get(self):
        """點擊Get"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                get_elem = '//*[@id="Zw_Setting_UpgradeFW_Modal"]/div/div[2]/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, get_elem)))
                get_btn = self.d.find_element(By.XPATH, get_elem)
                get_btn.click()
                print(f"[CLICK] Get")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Get時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                uuid, node = at_dev_uuid[tf.remot], at_dev_id[tf.remot]
                keyword = ["USER_TO_MIDDLE", '"EVENT":"ZW_BEGIN_OTA"', 
                           f'"NODE_ID":{node}']
                msg = tf.wait_mqtt_msg(keyword, 10)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未發出ZW_BEGIN_OTA訊息")
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
                tf.catch_exc(f"確認訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
            

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.取得Firmware檔案路徑
    def test_12_00_get_fw_path(self):
        """取得Firmware檔案路徑"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global fw_path, fw_file
            try:
                fw_path = os.path.join(main_path, "MiniGateway\\DeviceFirmware")
                if not os.path.exists(fw_path):
                    print(f"[FAIL] 找不到DeviceFirmware資料夾")
                    return False
                fw_file = tf.remot_fw
                print(f"[INFO] 取得檔案: {fw_file}")
                fw_path = os.path.join(fw_path, fw_file)
                return True
            except Exception as err:
                tf.catch_exc(f"取得檔案時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.選擇Firmware
    def test_13_00_select_file(self):
        """選擇Firmware"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                if not os.path.exists(fw_path):
                    print(f"[FAIL] 找不到檔案:{fw_path}")
                    return False
                # .../input[4]元素(隱藏的輸入棒)才能接收send_keys()
                browse_elem = '//*[@id="Zw_Setting_UpgradeFW_Modal_FwFile"]'\
                    '/form/input[4]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, browse_elem)))
                browse = self.d.find_element(By.XPATH, browse_elem)
                browse.send_keys(fw_path)
                print(f"[SENDKEY] 選擇檔案路徑:{fw_path}")
                return True
            except Exception as err:
                tf.catch_exc(f"選擇檔案時發生錯誤", self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                upfile_elem = '//*[@id="Zw_Setting_UpgradeFW_Modal_FwFile"]'\
                    '/form/input[5]' 
                upfile = self.d.find_element(By.XPATH, upfile_elem)
                upfile_text = upfile.get_property("value")
                if upfile_text == fw_file:
                    print(f"[INFO] 確認選擇檔案:{upfile_text}")
                    return True
                else:
                    print(f"[FAIL] 選擇檔案錯誤: {upfile_text}")
                    return False
            except Exception as err:
                tf.catch_exc(f"確認選擇檔案時發生錯誤", self._testMethodName,  err)
                return False
            
        def reset():
            self.test_12_00_get_fw_path()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.點擊Upgrade
    def test_14_00_click_upgrade(self):
        """點擊Upgrade"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                upload_elem = '//*[@id="Zw_Setting_UpgradeFW_Modal_FwFile"]'\
                    '/form/input[7]'
                upload_btn = self.d.find_element(By.XPATH, upload_elem)
                upload_btn.click()
                print(f"[CLICK] Upgrade")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Upload時發生錯誤", self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                pop_elem = '//*[@id="Zw_UpgradeFW_Modal_FooterContent"]/input'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, pop_elem)))
                print(f"[INFO] 已確認開始更新")
                return True
            except Exception as err:
                tf.catch_exc(f"確認開始更新時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check, retry=1)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.確認MQTT訊息
    def test_15_00_check_mqtt_msg(self):
        """確認MQTT訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.remot], at_dev_id[tf.remot]
                keyword = ['"ZwCmd": "ZIP_REQUEST"', 
                           f'"FROM_MS_UUID": "{uuid}"']
                msg = tf.wait_mqtt_msg(keyword, 30)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到ZIP_REQUEST訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認ZIP_REQUEST訊息")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_14_00_click_upgrade()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.確認更新訊息
    def test_16_00_check_result_msg(self):
        """確認更新訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            start_wait = datetime.now()
            wait_time = timedelta(minutes=120)       #等待MQTT訊息
            while datetime.now() <= start_wait + wait_time:
                try:
                    if '"ZipStatus": "OperationDone"' in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        print(f"[INFO] 更新成功")
                        return True
                    elif '"ZipStatus": "OperationFailed"' in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        print(f"[FAIL] 更新失敗")
                        return False
                    elif 'busy' in mq.msg_que[0]:
                        time.sleep(10)
                        del mq.msg_que[0]
                        return False
                    else:
                        del mq.msg_que[0]
                except:
                    time.sleep(1)
            else:
                print(f"[FAIL] 超時, 未收到OperationDone訊息")
                return False
            
        def reset():
            self.test_14_00_click_upload()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 17_00.確認顯示結果
    def test_17_check_display_result(self):
        """確認顯示結果"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                result_elem = '//*[@id="Zw_UpgradeFW_Modal_FooterContent"]/span'
                WebDriverWait(self.d, 60).until(
                    EC.presence_of_element_located((By.XPATH, result_elem)))
                result = self.d.find_element(By.XPATH, result_elem)
                if "upgrade successfully" in result.text:
                    print(f"[INFO] 已確認更新成功")
                    return True
                else:
                    print(f"[FAIL] 未顯示更新成功")
                    return False
            except Exception as err:
                tf.catch_exc(f"確認顯示結果時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, retry=1)
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
    tf.init_test(zw_09_device_fw_upgrade)

