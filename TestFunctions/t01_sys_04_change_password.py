#==============================================================================
# 程式功能: 測試修改登入的使用者密碼
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊並檢查
# 04_00.點擊Change Password
# 05_00.確認對話視窗並關閉對話視窗
# 06_00.重做04_00
# 07_00.輸入密碼並點擊顯示密碼按鈕
# 08_00.點擊修改並確認顯示訊息 
# 09_00.等待是否自動登出
# 10_00.使用新密碼登入
# 11_00.重做02_00及04_00
# 12_00.復原密碼
# 13_00.重做08_00
# 14_00.使用原密碼登入 
#==============================================================================
import os
import sys
import time
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


class sys_04_change_password(unittest.TestCase):
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

# 04_00.點擊Change Password
    def test_04_00_click_change_pw(self):
        """點擊Change Password"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                chg_pw_elem = '//*[@id="Gateway_Info"]/div[3]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, chg_pw_elem)))
                chg_pw_btn = self.d.find_element(By.XPATH, chg_pw_elem)
                chg_pw_btn.click()
                print(f"[CLICK] Change Password") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Change Password失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = '//*[@id="System_ChangePwd_Modal_CloseBtn"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, close_elem)))
                print(f"[INFO] 對話彈窗出現") 
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未出現", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 05_00.確認對話視窗並關閉對話視窗
    def test_05_00_check_pop_than_close(self):
        """確認對話視窗並關閉對話視窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                close_elem = '//*[@id="System_ChangePwd_Modal_CloseBtn"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, close_elem)))
                close_btn = self.d.find_element(By.XPATH, close_elem)
                close_btn.click()
                print(f"[CLICK] 關閉對話彈窗") 
                return True
            except Exception as err: 
                tf.catch_exc(f"關閉對話彈窗失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(0.5) # 等待元素動作完成
                close_elem = '//*[@id="System_ChangePwd_Modal_CloseBtn"]'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.XPATH, close_elem)))
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

# 06_00.重做04_00
    def test_06_00_redo_04_00(self):
        """重做04_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_04_00_click_change_pw()
                print(f"[INFO] 重做04_00完成") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做04_00失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = '//*[@id="System_ChangePwd_Modal_CloseBtn"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, close_elem)))
                print(f"[INFO] 對話彈窗出現") 
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未出現", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_00.輸入密碼並點擊顯示密碼按鈕
    def test_07_00_change_pw_and_check_msg(self):
        """輸入密碼並點擊顯示密碼按鈕"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                gw_debug_new_pw = tf.gw_debug_pw + "0"
                time.sleep(0.5) # 等待元素載入完成
                old_pw_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, old_pw_elem)))
                old_pw_box = self.d.find_element(By.XPATH, old_pw_elem)
                old_pw_box.clear()
                old_pw_box.send_keys(tf.gw_debug_pw)
                print(f"[SENDKEY] 輸入舊密碼")
                new_pw_elem1 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[2]'
                new_pw_box1 = self.d.find_element(By.XPATH, new_pw_elem1)
                new_pw_box1.clear()
                new_pw_box1.send_keys(gw_debug_new_pw)
                print(f"[SENDKEY] 輸入新密碼")
                new_pw_elem2 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[3]'
                new_pw_box2 = self.d.find_element(By.XPATH, new_pw_elem2)
                new_pw_box2.clear()
                new_pw_box2.send_keys(gw_debug_new_pw)
                print(f"[SENDKEY] 再次輸入新密碼")
                show_old_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/*[name()="svg"][1]'
                show_old_btn = self.d.find_element(By.XPATH, show_old_elem)
                show_old_btn.click()
                print(f"[CLICK] 點擊顯示舊密碼")
                show_pw1_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/*[name()="svg"][2]'
                show_pw1_btn = self.d.find_element(By.XPATH, show_pw1_elem)
                show_pw1_btn.click()
                print(f"[CLICK] 點擊顯示新密碼")
                show_pw2_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/*[name()="svg"][3]'
                show_pw2_btn = self.d.find_element(By.XPATH, show_pw2_elem)
                show_pw2_btn.click()
                print(f"[CLICK] 點擊顯示確認新密碼")
                return True
            except Exception as err:
                tf.catch_exc(f"修改密碼失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                old_pw_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[1]'
                old_pw = self.d.find_element(By.XPATH, old_pw_elem).get_property("type")
                new_pw_elem1 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[2]'
                new_pw1 = self.d.find_element(By.XPATH, new_pw_elem1).get_property("type")
                new_pw_elem2 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[3]'
                new_pw2 = self.d.find_element(By.XPATH, new_pw_elem2).get_property("type")
                if "password" in [old_pw, new_pw1, new_pw2]:
                    print(f"[FAIL] 無顯示輸入內容")
                    return False
                else:
                    print(f"[INFO] 正確顯示輸入內容")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認顯示內容失敗", self._testMethodName,  err)
                return False

        def reset():
            # 關閉對話彈窗再重試
            self.test_05_00_check_pop_than_close()
            time.sleep(0.5)
            self.test_04_00_click_change_pw()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.點擊修改並確認顯示訊息 
    def test_08_00_click_change_than_check_msg(self):
        """點擊修改並確認顯示訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(2)   #供人眼確認
                chg_elem = '//*[@id="System_ChangePwd_Modal_FooterContent"]/input'
                chg_btn = self.d.find_element(By.XPATH, chg_elem)
                chg_btn.click()
                print(f"[CLICK] Change") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Change失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                footer_elem = '//*[@id="System_ChangePwd_Modal_FooterContent"]/span'
                st_time = datetime.now()
                wt_time = timedelta(seconds=10)
                # 等待10秒內footer內容出現"successfully"
                while datetime.now() <= st_time + wt_time:
                    footer = self.d.find_element(By.XPATH, footer_elem).text
                    if "successfully" in footer:
                        print(f"[INFO] 輸出訊息: {footer}") 
                        print(f"[INFO] 密碼修改成功")
                        return True
                    time.sleep(0.2)
                print(f"[FAIL] 未出現成功訊息，密碼修改失敗")
                return False                    
            except Exception as err:
                tf.catch_exc(f"確認訊息時發生錯誤", self._testMethodName,  err)
                return False

        def reset():
            # 關閉對話彈窗再重試
            self.test_05_00_check_pop_than_close()
            time.sleep(0.5)
            self.test_04_00_click_change_pw()
            time.sleep(0.5)
            self.test_07_00_change_pw_and_check_msg()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.等待是否自動登出
    def test_09_00_check_auto_logout(self):
        """等待是否自動登出"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                # 等待元素出現
                acc_elem = '//*[@id="Login_Account"]'
                WebDriverWait(self.d, 20).until(
                    EC.presence_of_element_located((By.XPATH, acc_elem)))
                print(f"[INFO] 已自動登出") 
                return True
            except Exception as err:
                tf.catch_exc(f"未自動登出", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.使用新密碼登入
    def test_10_00_login_with_new_pw(self):
        """使用新密碼登入"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                gw_debug_new_pw = tf.gw_debug_pw + "0"
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
                user_pw.send_keys(gw_debug_new_pw)
                print(f"[SENDKEY] {gw_debug_new_pw}")
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
                # 當Alert出現時selenium無法截圖，故取消截圖
                # screen_cap(self, self._testMethodName)
                return False
            except Exception as err:
                tf.catch_exc(f"無出現警示", self._testMethodName,  err)
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
                tf.catch_exc(f"點擊Alert確定時發生錯誤", self._testMethodName,  err)
                self.d.refresh()
                
        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.重做02_00及04_00
    def test_11_00_redo_02_00_04_00(self):
        """重做02_00及04_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_02_00_wait_page_loading()
                self.test_04_00_click_change_pw()
                print(f"[INFO] 重做02_00及04_00完成") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00及04_00失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                close_elem = '//*[@id="System_ChangePwd_Modal_CloseBtn"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, close_elem)))
                print(f"[INFO] 對話彈窗出現") 
                return True
            except Exception as err:
                tf.catch_exc(f"對話彈窗未出現", self._testMethodName,  err)
                return False
                
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag
  
# 12_00.復原密碼
    def test_12_00_restore_pw(self):
        """輸入密碼並點擊顯示密碼按鈕"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                gw_debug_new_pw = tf.gw_debug_pw + "0"
                time.sleep(0.5) # 等待元素載入完成
                old_pw_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, old_pw_elem)))
                old_pw_box = self.d.find_element(By.XPATH, old_pw_elem)
                old_pw_box.clear()
                old_pw_box.send_keys(gw_debug_new_pw)
                print(f"[SENDKEY] 輸入舊密碼")
                new_pw_elem1 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[2]'
                new_pw_box1 = self.d.find_element(By.XPATH, new_pw_elem1)
                new_pw_box1.clear()
                new_pw_box1.send_keys(tf.gw_debug_pw)
                print(f"[SENDKEY] 輸入新密碼")
                new_pw_elem2 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[3]'
                new_pw_box2 = self.d.find_element(By.XPATH, new_pw_elem2)
                new_pw_box2.clear()
                new_pw_box2.send_keys(tf.gw_debug_pw)
                print(f"[SENDKEY] 再次輸入新密碼")
                show_old_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/*[name()="svg"][1]'
                show_old_btn = self.d.find_element(By.XPATH, show_old_elem)
                show_old_btn.click()
                print(f"[CLICK] 點擊顯示舊密碼")
                show_pw1_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/*[name()="svg"][2]'
                show_pw1_btn = self.d.find_element(By.XPATH, show_pw1_elem)
                show_pw1_btn.click()
                print(f"[CLICK] 點擊顯示新密碼")
                show_pw2_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/*[name()="svg"][3]'
                show_pw2_btn = self.d.find_element(By.XPATH, show_pw2_elem)
                show_pw2_btn.click()
                print(f"[CLICK] 點擊顯示確認新密碼")
                return True
            except Exception as err: 
                tf.catch_exc(f"修改密碼失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                old_pw_elem = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[1]'
                old_pw = self.d.find_element(By.XPATH, old_pw_elem).get_property("type")
                new_pw_elem1 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[2]'
                new_pw1 = self.d.find_element(By.XPATH, new_pw_elem1).get_property("type")
                new_pw_elem2 = '//*[@id="System_ChangePwd_Modal_BodyContent"]/input[3]'
                new_pw2 = self.d.find_element(By.XPATH, new_pw_elem2).get_property("type")
                if "password" in [old_pw, new_pw1, new_pw2]:
                    print(f"[FAIL] 無顯示輸入內容")
                    return False
                else:
                    print(f"[INFO] 正確顯示輸入內容")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認顯示內容失敗", self._testMethodName,  err)
                return False

        def reset():
            # 關閉對話彈窗再重試
            self.test_05_00_check_pop_than_close()
            time.sleep(0.5)
            self.test_04_00_click_change_pw()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.重做08_00
    def test_13_00_redo_08_00(self):
        """重做08_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_08_00_click_change_than_check_msg()
                print(f"[INFO] 重做08_00完成") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做08_00失敗", self._testMethodName,  err)
                return False

        def check(info):
            try:
                self.test_09_00_check_auto_logout()
                print(f"[INFO] 重做09_00完成") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做09_00失敗", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.使用原密碼登入 
    def test_14_00_login_with_old_pw(self):
        """使用原密碼登入 """
        # 如果前面測試失敗，就略過此測試
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
                # 當Alert出現時selenium無法截圖，故取消截圖
                # screen_cap(self, self._testMethodName)
                return False
            except Exception as err:
                tf.catch_exc(f"無出現警示", self._testMethodName,  err)
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
                tf.catch_exc(f"點擊Alert確定時發生錯誤", self._testMethodName,  err)
                self.d.refresh()
                
        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

if __name__ == "__main__":
    tf.init_test(sys_04_change_password)
