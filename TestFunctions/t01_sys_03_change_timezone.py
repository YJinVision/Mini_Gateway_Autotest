#==============================================================================
# 程式功能: 測試修改時區、修改NTP Server功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊並檢查
# 04_00.點擊Change Timezone
# 05_00.關閉對話彈窗
# 06_00.重做04_00
# 07_00.輸入NTP Server: time.google.com並修改
# 08_00.檢查確認彈窗訊息
# 08_01.關閉確認彈窗
# 09_00.重整頁面並重做02_00及04_00
# 10_00.檢查NPT Server輸入框內的值
# 11_00.取得全部的時區選項
# 12_00.從選項中隨機選擇一個並修改
# 13_00.重整頁面並重做02_00及04_00
# 14_00.確認頁面顯示的時間是否正確套用時區
# 15_00.修改回原NTP Server並設定Timezone為(GMT +08:00) Asia/Taipei 
# 16_00.重做08_00及08_01
#==============================================================================
import os
import sys
import time
import random
from datetime import datetime, timedelta
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
import MiniGateway.mqtt_lite as mq

class sys_03_change_timezone(unittest.TestCase):
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

# 04_00.點擊Change Timezone
    def test_04_00_click_change_tz(self):
        """點擊Change Timezone"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                chg_tz_elem = 'system-gateway-info-changeTZ-icon'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, chg_tz_elem)))
                chg_tz_btn = self.d.find_element(By.CLASS_NAME, chg_tz_elem)
                chg_tz_btn.click()
                print(f"[CLICK] 點擊Change Timezone") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Change Timezone時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = 'System_ChangeTZ_Modal_CloseBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.ID, close_elem)))
                print(f"[INFO] 彈窗出現") 
                return True
            except Exception as err:
                tf.catch_exc(f"彈窗未出現", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 05_00.關閉對話彈窗
    def test_05_00_close_dialog_pop(self):
        """關閉對話彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.3) # 等待元素載入完成
                close_elem = 'System_ChangeTZ_Modal_CloseBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.ID, close_elem)))
                close_btn = self.d.find_element(By.ID, close_elem)
                close_btn.click()
                print(f"[CLICK] 關閉對話彈窗")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉對話彈窗時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.3) # 等待元素完成動作
                close_elem = 'System_ChangeTZ_Modal_CloseBtn'
                WebDriverWait(self.d, 2).until(
                    EC.invisibility_of_element((By.ID, close_elem)))
                print(f"[INFO] 對話彈窗已消失")
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未消失", self._testMethodName,  err)
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
            self.test_04_00_click_change_tz()
            print(f"[INFO] 重做04_00完成")
            return True

        def check(info):
            try:
                time.sleep(0.3)
                close_elem = 'System_ChangeTZ_Modal_CloseBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.ID, close_elem)))
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

# 07_00.輸入NTP Server並修改
    def test_07_00_set_ntp_server(self):
        """輸入NTP Server"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global ori_ntp
            try:
                # 取得目前的NTP Server供測試完成後復原
                # 如果取得失敗就復原為空值使用預設值(openwrt.pool.ntp.org)
                ori_ntp = ""    
                time.sleep(0.5) # 等待元素載入完成
                ntp_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, ntp_elem)))
                get_ntp_js = "return $('#System_ChangeTZ_Modal_BodyContent\
                  > input:nth-child(4)').val();"
                ori_ntp = self.d.execute_script(get_ntp_js)
                print(f"[INFO] 目前的NTP: '{ori_ntp}'") 
            except Exception as err: 
                tf.catch_exc(f"取得目前的NTP失敗, 測試結束後將以空值復原", 
                             self._testMethodName,  err)

            try:
                # 設定NTP
                ntp_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, ntp_elem)))
                ntp_box = self.d.find_element(By.XPATH, ntp_elem)
                ntp_box.clear()
                ntp_box.send_keys(tf.gw_ntp)
                print(f"[SENDKEY] NTP Server: {tf.gw_ntp}")
                chg_elem = 'zw-add-modal-next-btn'
                chg_btn = self.d.find_element(By.CLASS_NAME, chg_elem)
                chg_btn.click()
                print(f"[CLICK] Change")
                return True
            except Exception as err:
                tf.catch_exc(f"設定NTP Server時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.3) # 等待元素完成動作
                chg_elem = 'zw-add-modal-next-btn'
                WebDriverWait(self.d, 2).until(
                    EC.invisibility_of_element((By.ID, chg_elem)))
                print(f"[INFO] 對話彈窗消失")
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未消失", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.檢查確認彈窗訊息
    def test_08_00_check_confirm_msg(self):
        """檢查確認彈窗訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.5) # 等待元素動作完成
                msg_elem = '//*[@id="System_Gateway_Notify_Modal"]/div/div[2]/span'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, msg_elem)))
                msg = self.d.find_element(By.XPATH, msg_elem).text
                print(f"[INFO] 已取得訊息")
                return msg
            except Exception as err:
                tf.catch_exc(f"取得訊息時發生錯誤", self._testMethodName,  err)
                return False
            
        def check(msg):
            if "successfully" in msg:
                print(f"[INFO] 訊息內容: {msg}")
                print(f"[INFO] 設定完成") 
                return True
            else:
                print(f"[INFO] 訊息內容: {msg}")
                print(f"[FAIL] 設定失敗")
                tf.screen_cap(self)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_01.關閉確認彈窗
    def test_08_01_close_confirm_pop(self):
        """關閉確認彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                close_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, close_elem)))
                close_btn = self.d.find_element(By.CLASS_NAME, close_elem)
                close_btn.click()
                print(f"[CLICK] 關閉確認彈窗") 
                return True
            except Exception as err: 
                tf.catch_exc(f"關閉確認彈窗時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 2).until(
                    EC.invisibility_of_element((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 確認彈窗消失") 
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗未消失", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.重整頁面並重做02_00及04_00
    def test_09_00_reflash_redo_0200_0400(self):
        """重整頁面並重做02_00及04_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.d.refresh()
                print(f"[INFO] 重整頁面")
                self.test_02_00_wait_page_loading()
                self.test_04_00_click_change_tz()
                print(f"[INFO] 重做02_00及04_00") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00及04_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.3) # 等待元素載入完成
                close_elem = 'system-gateway-info-changeTZ-icon'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 已開啟Change timezone對話彈窗") 
                return True
            except Exception as err:
                tf.catch_exc(f"未開啟Change timezone對話彈窗", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.檢查NPT Server輸入框內的值
    def test_10_00_check_setted_ntp(self):
        """檢查NPT Server輸入框內的值"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                ntp_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, ntp_elem)))
                get_ntp_js = "return $('#System_ChangeTZ_Modal_BodyContent\
                  > input:nth-child(4)').val();"
                curr_ntp = self.d.execute_script(get_ntp_js)
                print(f"[INFO] 取得NTP") 
                return curr_ntp
            except Exception as err:
                tf.catch_exc(f"取得NTP時發生錯誤", self._testMethodName,  err)
                return False

        def check(curr_ntp):
            try:
                if curr_ntp == tf.gw_ntp:
                    print(f"[INFO] NTP: {curr_ntp}") 
                    print(f"[INFO] NTP設定完成")
                    return True
                else:
                    print(f"[INFO] NTP: {curr_ntp}") 
                    print(f"[FAIL] NTP設定失敗")
                    tf.screen_cap(self)
                    return False
            except Exception as err:
                tf.catch_exc(f"檢查NTP時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.取得全部的時區選項
    def test_11_00_get_all_tz_item(self):
        """取得全部的時區選項"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global tz_all, tz_taipei
            try:
                time.sleep(0.3) # 等待元素載入
                tz_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/select'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, tz_elem)))
                tz_select = Select(self.d.find_element(By.XPATH, tz_elem))
                tz_all = []
                for item in tz_select.options:
                    tz_all.append(item.text)
                    if "Taipei" in item.text:
                        tz_taipei = item.text
                print(f"[INFO] 已取得全部時區") 
                return len(tz_all)
            except Exception as err:
                tf.catch_exc(f"取得時區時發生錯誤", self._testMethodName,  err)
                return False

        def check(tz):
            try:
                if tz >= 0:
                    print(f"[INFO] 已取得{tz}個時區選項") 
                    return True
                else:
                    print(f"[FAIL] 已取得0個時區選項, 取得失敗")
                    return False
            except Exception as err:
                tf.catch_exc(f"確認取得時區時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.從選項中隨機選擇一個並修改
    def test_12_00_select_tz_random(self):
        """從選項中隨機選擇一個並修改"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global tz_rand_index
            try:
                # 從所有timezone選項中隨機選擇一項並修改
                tz_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/select'
                tz_select = Select(self.d.find_element(By.XPATH, tz_elem))
                tz_rand_index = random.randint(0, len(tz_all))
                tz_select.select_by_index(tz_rand_index)
                print(f"[INFO] 選擇第{tz_rand_index}項: {tz_all[tz_rand_index]}") 
                time.sleep(0.5) # 供人眼確認選擇項目
                chg_elem = 'zw-add-modal-next-btn'
                chg_btn = self.d.find_element(By.CLASS_NAME, chg_elem)
                chg_btn.click()
                print(f"[CLICK] Change")
                return True
            except Exception as err:
                tf.catch_exc(f"選擇Timezone時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.3) # 等待元素完成動作
                chg_elem = 'zw-add-modal-next-btn'
                WebDriverWait(self.d, 2).until(
                    EC.invisibility_of_element((By.ID, chg_elem)))
                print(f"[INFO] 對話彈窗消失")
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未消失", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.重整頁面並重做02_00及04_00
    def test_13_00_reflash_redo_0200_0400(self):
        """重整頁面並重做02_00及04_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.d.refresh()
                print(f"[INFO] 重整頁面")
                self.test_02_00_wait_page_loading()
                self.test_04_00_click_change_tz()
                print(f"[INFO] 重做02_00及04_00完成") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00及04_00失敗", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.3) # 等待元素載入完成
                close_elem = 'system-gateway-info-changeTZ-icon'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, close_elem)))
                print(f"[INFO] 已開啟Change timezone對話彈窗") 
                return True
            except Exception as err:
                tf.catch_exc(f"未開啟Change timezone對話彈窗", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.確認頁面顯示的時間是否正確套用時區
    def test_14_00_check_time_on_page(self):
        """確認頁面顯示的時間是否正確套用時區"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                # 將所選時區轉成timedelta格式 e.g., (GMT -10:00) HST
                print(f"[INFO] 所選時區: {tz_all[tz_rand_index]}")
                selected_tz = timedelta(
                    hours=int(tz_all[tz_rand_index][6:8]), 
                    minutes=int(tz_all[tz_rand_index][9:11]))
                
                # 取得目前+00:00的倫敦時間
                pc_tz = int(time.strftime("%z"))    # e.g., -0930 -> -930
                tz_hours, tz_min = divmod(abs(pc_tz), 100)
                pc_tz_delta = timedelta(
                    hours=tz_hours,     # 9
                    minutes=tz_min)     # 30
                if pc_tz < 0:  # 如為負時區
                    pc_tz_delta = -pc_tz_delta
                london_time = datetime.now() - pc_tz_delta
                london_time_str = london_time.strftime("%Y-%m-%d_%H:%M")
                print(f"[INFO] 目前倫敦時間: {london_time_str}")

                # 換算所選時區的真實時間
                if tz_all[tz_rand_index][5] == "+":
                    real_time = london_time + selected_tz
                else:
                    real_time = london_time - selected_tz
                real_time = real_time.strftime("%Y-%m-%d_%H:%M")
                print(f"[INFO] 所選時區的真實時間: {real_time}")

                time.sleep(0.5) # 等待元素載入
                # 取得頁面顯示的日期、時間字串
                date_elem = '//*[@id="System_ChangeTZ_Modal_FooterContent"]/span[2]'
                time_elem = '//*[@id="System_ChangeTZ_Modal_FooterContent"]/span[3]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_elem)))
                date_shown = self.d.find_element(
                    By.XPATH, date_elem).text.split(",")[0] # 2024-12-27, Fri
                time_shown = self.d.find_element(
                    By.XPATH, time_elem).text.split(" : ")  # 14 : 09 : 48
                
                # 將面頁時間統一格式:%Y-%m-%d_%H:%M
                shown_time = datetime.strptime(
                    f"{date_shown}_{time_shown[0]}:{time_shown[1]}",
                    "%Y-%m-%d_%H:%M").strftime("%Y-%m-%d_%H:%M")
                print(f"[INFO] 頁面顯示時間: {shown_time}")

                return shown_time, real_time
            except Exception as err:
                tf.catch_exc(f"取得頁面時間時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(time_info):
            shown_time = time_info[0]
            real_time = time_info[1]
            try:
                # 比對頁面顯示的時間與換算的真實時間
                if shown_time == real_time:
                    print(f"[INFO] 顯示時間正確")
                    return True
                else:
                    print(f"[FAIL] 顯示時間錯誤")
                    return False
            except Exception as err:
                tf.catch_exc(f"比對時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.修改回原NTP Server並設定Timezone為(GMT +08:00) Asia/Taipei
    def test_15_00_restore_setting(self):
        """修改回原NTP Server並設定Timezone為(GMT +08:00) Asia/Taipei"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                # 選擇時區(GMT +08:00) Asia/Taipei
                tz_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/select'
                tz_select = Select(self.d.find_element(By.XPATH, tz_elem))
                tz_select.select_by_visible_text(tz_taipei)
                print(f"[INFO] 選擇時區: {tz_taipei}") 
                time.sleep(0.5) # 供人眼確認選擇項目
                # 復原NTP Server
                ntp_elem = '//*[@id="System_ChangeTZ_Modal_BodyContent"]/input[2]'
                ntp_box = self.d.find_element(By.XPATH, ntp_elem)
                ntp_box.clear()
                ntp_box.send_keys(ori_ntp)
                print(f"[INFO] 復原NTP Server: {ori_ntp}")
                # 點擊Change
                time.sleep(2)   # 供人眼確認
                chg_elem = 'zw-add-modal-next-btn'
                chg_btn = self.d.find_element(By.CLASS_NAME, chg_elem)
                chg_btn.click()
                print(f"[CLICK] Change")
                return True
            except Exception as err:
                tf.catch_exc(f"復原設定時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.3) # 等待元素完成動作
                chg_elem = 'zw-add-modal-next-btn'
                WebDriverWait(self.d, 2).until(
                    EC.invisibility_of_element((By.ID, chg_elem)))
                print(f"[INFO] 對話彈窗消失")
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未消失", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.重做08_00及08_01
    def test_16_00_reflash_redo_0800_0801(self):
        """重整頁面並重做08_00及08_01"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_08_00_check_confirm_msg()
                self.test_08_01_close_confirm_pop()
                print(f"[INFO] 重做08_00及08_01完成") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做08_00及08_01時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

if __name__ == "__main__":
    tf.init_test(sys_03_change_timezone)
