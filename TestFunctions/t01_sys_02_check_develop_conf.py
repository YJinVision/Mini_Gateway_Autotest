#==============================================================================
# 程式功能: 測試develop configuration(RF設定)功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊並檢查
# 04_00.點擊10次齒輪icon，並確認輸入密碼彈窗
# 05_00.關閉彈窗
# 06_00.重做04_00
# 07_00.輸入密碼
# 08_00.點擊Configuration分頁 
# 09_00.取得目前的Z-Wave頻率
#==============================================================================
import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(os.path.dirname(curr_path))  #.\iHub_Autotest
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import mqtt_lite as mq


class sys_02_check_develop_conf(unittest.TestCase):
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
                tf.catch_exc(f"無法定位元素，載入失敗", self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, check, reset)
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
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 04_00.點擊10次齒輪icon，並確認輸入密碼彈窗
    def test_04_00_click_gear_icon_10_times(self):
        """點擊10次齒輪icon，並確認輸入密碼彈窗"""
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
                print("[CLICK] Gear icon 10 times.")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊齒輪icon時發生錯誤", self._testMethodName,  err)
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

# 05_00.關閉彈窗
    def test_05_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.5) # 等待前端元素動作完成，避免操作過快
                close_elem = 'sys-setting-confirm-modal-closeBtn'
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
                close_elem = 'sys-setting-confirm-modal-closeBtn'
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

# 06_00.重做04_00
    def test_06_00_redo_step_04_00(self):
        """重做04_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            self.test_04_00_click_gear_icon_10_times()
            print(f"[INFO] 重做04_00完成")
            return True

        def check(info):
            try:
                time.sleep(0.3)
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
                pw_box_elem = '//*[@id="System_Gateway_AzCheck_Modal"]/div/div[2]/input[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, pw_box_elem)))
                pw_box = self.d.find_element(By.XPATH, pw_box_elem)
                pw_box.send_keys(tf.gw_dev_pw)
                print(f"[SENDKEY] 輸入密碼: {tf.gw_dev_pw}")
                send_elem = '//*[@id="System_Gateway_AzCheck_Modal"]/div/div[2]/input[2]'
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
                tab_elem = '//*[@id="System_Azure_tab"]/span'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, tab_elem)))
                print(f"[INFO] Configuration分頁出現")
                return True
            except Exception as err:
                tf.catch_exc(f"Configuration分頁未出現", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_04_00_click_gear_icon_10_times()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.點擊Configuration分頁 
    def test_08_00_click_conf_tab(self):
        """點擊Configuration分頁 """
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.3) # 等待彈窗消失
                tab_elem = '//*[@id="System_Azure_tab"]/span'
                conf_tab = self.d.find_element(By.XPATH, tab_elem)
                conf_tab.click()
                print(f"[CLICK] 點擊Configuration分頁")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Configuration分頁時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                rf_elem = '//*[@id="System_Region"]/select'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, rf_elem)))
                print(f"[INFO] RF Region出現")
                return True
            except Exception as err:
                tf.catch_exc(f"RF Region未出現", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.取得目前的Z-Wave頻率
    def test_09_00_get_zwave_rf_region(self):
        """取得目前的Z-Wave頻率"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                rf_elem = '//*[@id="System_Region"]/select'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, rf_elem)))
                rf_sele = Select(self.d.find_element(By.XPATH, rf_elem))
                curr_rf = rf_sele.first_selected_option.text
                print(f"[INFO] 取得RF Region: {curr_rf}")
                return curr_rf
            except Exception as err:
                tf.catch_exc(f"取得RF Region失敗", self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

if __name__ == "__main__":
    tf.init_test(sys_02_check_develop_conf)
