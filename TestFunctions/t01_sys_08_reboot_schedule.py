#==============================================================================
# 程式功能: 測試Rebood schedule功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Network Configuration分頁
# 05_00.點擊Weekly選項
# 06_00.取得目前時間+2分鐘並設定
# 07_00.等待Gateway重啟訊息
# 08_00.確認UDP訊息
# 09_00.重做02_00、04_00
# 10.00.點擊Daily選項
# 11_00.取得目前時間+2分鐘並設定
# 12_00.重做07_00
# 13_00.重做08_00、09_00
# 14_00.點擊Disable選項
# 15_00.點擊儲存
# 16_00.確認Gateway未重啟
#==============================================================================
import os
import sys
import json
import time
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
import mqtt_lite as mq
import udp_tester as udp

class sys_08_reboot_schedule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        tf.output(f"\n[STATUS] {self.__name__} start.\n")
        # 設置ChromeDriver選項
        self.d = webdriver.Chrome(tf.set_chrome_options()) 
        # 開始監聽UDP
        udp.start_listen(tf.gw_udp_port)
        
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

# 04_00.點擊Network Configuration分頁
    def test_04_00_click_network_config(self):
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
                tf.catch_exc("點擊Netwrok Configuration分頁時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                ap_mode_elem = 'System_WIFI_Disable'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, ap_mode_elem)))
                print(f"[INFO] 已顯示Netwrok Configuration分頁") 
                return True
            except Exception as err:
                tf.catch_exc("未顯示Netwrok Configuration分頁", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 05_00.點擊Weekly選項
    def test_05_00_click_weekly_option(self):
        """點擊Weekly選項"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                week_elem = 'weekly_timer'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, week_elem)))
                week_op = self.d.find_element(By.ID, week_elem)
                week_op.click()
                print(f"[CLICK] Weekly option") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Weekly選項時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                week_elem = 'weekly_timer'
                week_op = self.d.find_element(By.ID, week_elem)
                if week_op.is_selected():
                    print(f"[INFO] 已選取Weekly")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認Weekly選取時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 06_00.取得目前時間+2分鐘並設定
    def test_06_00_set_week_and_time(self):
        """取得目前時間+2分鐘並設定"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 取得目前的星期、時、分 +2分鐘
            # datetime:     Mon:0, Tue:1, Wed:2, Thu:3, Fri:4, Sat:5, Sun:6
            # Web value:    Mon:1, Tue:2, Wed:3, Thu:4, Fri:5, Sat:6, Sun:0
            day_name = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            curr_time = datetime.now()
            set_time = curr_time + timedelta(minutes=2) # +2分鐘
            set_min = set_time.minute
            set_hour = set_time.hour
            set_day = (set_time.weekday() + 1) % 7  # Web數值差異處理, 加1後取%計算
            print(f"[INFO] 目前時間: {curr_time}")
            print(f"[INFO] 設定時間: {day_name[set_day]}, {set_hour}:{set_min}")
            tf.output(f"[INFO] 設定時間: {day_name[set_day]}, {set_hour}:{set_min}")

            # 設定時間並儲存
            try:
                day_elem = 'day_select'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, day_elem)))
                day_select = Select(self.d.find_element(By.ID, day_elem))
                day_select.select_by_index(set_day)
                hour_elem = 'hour_select'
                hour_select = Select(self.d.find_element(By.ID, hour_elem))
                hour_select.select_by_index(set_hour)
                min_elem = 'min_select'
                min_select = Select(self.d.find_element(By.ID, min_elem))
                min_select.select_by_index(set_min)
                print(f"[INFO] 已設定星期時間")
                save_elem = '//*[@id="Network_Config"]/div/input'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return (set_day, set_hour, set_min)
            except Exception as err:
                tf.catch_exc(f"設定星期時間時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                WebDriverWait(self.d, 3).until(EC.alert_is_present())
                time.sleep(1)
                alert = self.d.switch_to.alert
                mq.msg_que = [] # 清除queue來確認新訊息
                alert.accept()
                print(f"[INFO] 出現設定成功Alert視窗")
            except Exception as err:
                tf.catch_exc(f"沒有出現設定成功Alert視窗", self._testMethodName,  err)
                return False

            (set_day, set_hour, set_minute) = info
            start_time = datetime.now()
            timeout = timedelta(seconds=30)
            while datetime.now() <= start_time + timeout:
                try:
                    # 檢查Gateway回覆的Reboot schedule內容
                    if "AUTO_REBOOT_SETTINGS" in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        msg = json.loads(mq.msg_que[0])
                        content = msg["Payload"]["Content"]
                        reboot_type = int(content["RebootType"])
                        day_of_week = int(content["DayOfWeek"])
                        hour = int(content["Hour"])
                        minute = int(content["Minute"])
                        if reboot_type != 2:
                            print(f"[FAIL] RebootType 錯誤")
                            return False
                        if day_of_week != set_day:
                            print(f"[FAIL] DayOfWeek錯誤")
                            return False
                        if hour != set_hour:
                            print(f"[FAIL] Hour錯誤")
                            return False
                        if minute != set_minute:
                            print(f"[FAIL] Minute錯誤")
                            return False
                        print(f"[INFO] 已確認Reboot設定, 等待自動重啟")
                        tf.output(f"[INFO] 已確認Reboot設定, 等待自動重啟")
                        del mq.msg_que[0]
                        return True
                    elif "busy" in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        print(f"[INFO] Gateway忙錄中, 10秒後重試")
                        tf.output(f"[INFO] Gateway忙錄中, 10秒後重試")
                        time.sleep(10)
                        del mq.msg_que[0]
                        return False
                    else:
                        del mq.msg_que[0]
                except:
                    pass    # 忽略mq.msg_que[0]未給值的狀態
            else:
                print(f"[FAIL] 沒有收到AUTO_REBOOT_SETTINGS訊息")
                tf.output(f"[FAIL] 沒有收到AUTO_REBOOT_SETTINGS訊息")
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_00.等待Gateway重啟訊息
    def test_07_00_wait_gw_reboot(self):
        """開始監聽UDP並等待Gateway重啟訊息"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 清空queue訊息以利確認結果
            mq.msg_que = []
            udp.udp_que = []
            # 監聽MQTT訊息等待Gateway重啟
            middle_up = False
            middle_ready = False
            start_time = datetime.now()
            timeout = timedelta(seconds=180)
            while datetime.now() <= start_time + timeout:
                try:
                    if "Middle start up" in mq.msg_que[0]:
                        middle_up = True
                        print(f"[INFO] Gateway已重啟, 等待重啟完成({datetime.now()})")
                        tf.output(f"[INFO] Gateway已重啟, 等待重啟完成({datetime.now()})")
                        del mq.msg_que[0]
                        break
                    else:
                        del mq.msg_que[0]
                except:
                    time.sleep(1)    # 忽略mq.msg_que[0]未給值的狀態
            else:
                print(f"[FAIL] 超時({datetime.now()}), 未收到重啟訊息")
                tf.output(f"[FAIL] 超時({datetime.now()}), 未收到重啟訊息")
                return False
            
            start_time = datetime.now()
            timeout = timedelta(seconds=60)
            while datetime.now() <= start_time + timeout:
                try:
                    if "ROLETYPE_FN" in mq.msg_que[0]:
                        middle_ready = True
                        print(f"[INFO] Gateway重啟完成({datetime.now()})")
                        tf.output(f"[INFO] Gateway重啟完成({datetime.now()})")
                        del mq.msg_que[0]
                        break
                    else:
                        del mq.msg_que[0]
                except:
                    time.sleep(1)    # 忽略mq.msg_que[0]未給值的狀態
            else:
                print(f"[FAIL] 超時({datetime.now()}), 未收到重啟完成訊息")
                tf.output(f"[FAIL] 超時({datetime.now()}), 未收到重啟完成訊息")
                return False

            if middle_up and middle_ready:  # 待Middle重啟並準備完成
                return True

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_04_00_click_network_config()
            self.test_05_00_click_weekly_option()
            self.test_06_00_set_week_and_time()
            
        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.確認UDP訊息
    def test_08_00_check_udp_message(self):
        """確認UDP訊息"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                target = {"MasterInfoRpt", tf.gw_mac}
                # tf.output(udp.udp_que)
                # input()
                for msg in udp.udp_que:
                    # tf.output(msg)
                    # input()
                    if all((t in msg) for t in target):
                        print(msg)
                        print(f"[INFO] 已確認UDP訊息")
                        tf.output(f"[INFO] 已確認UDP訊息")
                        return True
                print(f"[FAIL] 沒有收到Gateway UDP訊息") 
                tf.output(f"[FAIL] 沒有收到Gateway UDP訊息")
                return False
            except Exception as err:
                tf.catch_exc(f"確認UDP訊息時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.重做02_00、04_00
    def test_09_00_redo_0200_0400(self):
        """重做02_00、04_00"""
        # 如果Weelky reboot測試失敗, 仍繼續做Daily reboot測試
        if tf.flag_test_fail:
            # self.skipTest(tf.fail_reason)
            tf.flag_test_fail = False
            tf.fail_reason = ""
        def action():
            try:
                self.d.refresh()
                self.test_02_00_wait_page_loading()
                self.test_04_00_click_network_config()
                print(f"[INFO] 已重做02_00、04_00") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00、04_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                daily_elem = 'daily_timer'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, daily_elem)))
                print(f"[INFO] 重做02_00、04_00完成")
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00、04_00失敗", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10.00.點擊Daily選項
    def test_10_00_click_daily_option(self):
        """點擊Daily選項"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                daily_elem = 'daily_timer'
                daily_op = self.d.find_element(By.ID, daily_elem)
                daily_op.click()
                print(f"[INFO] 已點擊Daily選項") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Daily選項時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                daily_elem = 'daily_timer'
                daily_op = self.d.find_element(By.ID, daily_elem)
                if daily_op.is_selected():
                    print(f"[INFO] 已確認點擊Daily選項")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認點擊Daily選項時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.取得目前時間+2分鐘並設定
    def test_11_00_set_time(self):
        """取得目前時間+2分鐘並設定"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 取得目前的星期、時、分 +2分鐘
            curr_time = datetime.now()
            set_time = curr_time + timedelta(minutes=2) # +2分鐘
            set_min = set_time.minute
            set_hour = set_time.hour
            print(f"[INFO] 目前時間: {curr_time}")
            print(f"[INFO] 設定時間: {set_hour}:{set_min}")
            tf.output(f"[INFO] 設定時間: {set_hour}:{set_min}")

            # 設定時間並儲存
            try:
                hour_elem = 'hour_select'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, hour_elem)))
                hour_select = Select(self.d.find_element(By.ID, hour_elem))
                hour_select.select_by_index(set_hour)
                min_elem = 'min_select'
                min_select = Select(self.d.find_element(By.ID, min_elem))
                min_select.select_by_index(set_min)
                print(f"[INFO] 已設定時間")
                save_elem = '//*[@id="Network_Config"]/div/input'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return (set_hour, set_min)
            except Exception as err:
                tf.catch_exc(f"設定時間時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                WebDriverWait(self.d, 3).until(EC.alert_is_present())
                time.sleep(1)
                alert = self.d.switch_to.alert
                mq.msg_que = [] # 清除queue來確認新訊息
                alert.accept()
                print(f"[INFO] 出現設定成功Alert視窗")
            except Exception as err:
                tf.catch_exc(f"沒有出現設定成功Alert視窗", self._testMethodName,  err)
                return False

            (set_hour, set_minute) = info
            start_time = datetime.now()
            timeout = timedelta(seconds=30)
            while datetime.now() <= start_time + timeout:
                try:
                    # 檢查Gateway回覆的Reboot schedule內容
                    if "AUTO_REBOOT_SETTINGS" in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        msg = json.loads(mq.msg_que[0])
                        content = msg["Payload"]["Content"]
                        reboot_type = int(content["RebootType"])
                        day_of_week = int(content["DayOfWeek"])
                        hour = int(content["Hour"])
                        minute = int(content["Minute"])
                        if reboot_type != 1:
                            print(f"[FAIL] RebootType 錯誤")
                            return False
                        if day_of_week != 0:
                            print(f"[FAIL] DayOfWeek 錯誤")
                            return False
                        if hour != set_hour:
                            print(f"[FAIL] Hour錯誤")
                            return False
                        if minute != set_minute:
                            print(f"[FAIL] Minute錯誤")
                            return False
                        print(f"[INFO] 已確認Reboot設定, 等待自動重啟")
                        tf.output(f"[INFO] 已確認Reboot設定, 等待自動重啟")
                        del mq.msg_que[0]
                        return True
                    elif "Zwave is busy" in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        print(f"[INFO] Gateway忙錄中, 10秒後重試")
                        tf.output(f"[INFO] Gateway忙錄中, 10秒後重試")
                        time.sleep(10)
                        del mq.msg_que[0]
                        return False
                    else:
                        del mq.msg_que[0]
                except:
                    pass    # 忽略mq.msg_que[0]未給值的狀態
            else:
                print(f"[FAIL] 沒有收到AUTO_REBOOT_SETTINGS訊息")
                tf.output(f"[FAIL] 沒有收到AUTO_REBOOT_SETTINGS訊息")
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.重做07_00
    def test_12_00_redo_0700(self):
        """重做07_00"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_07_00_wait_gw_reboot()
                print(f"[INFO] 已重做07_00") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做07_00時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.重做02_00、04_00
    def test_13_00_redo_0200_0400(self):
        """重做02_00、04_00"""
        # 如果Weelky reboot測試失敗, 仍繼續做Daily reboot測試
        if tf.flag_test_fail:
            # self.skipTest(tf.fail_reason)
            tf.flag_test_fail = False
            tf.fail_reason = ""
        def action():
            try:
                self.d.refresh()
                self.test_02_00_wait_page_loading()
                self.test_04_00_click_network_config()
                print(f"[INFO] 已重做02_00、04_00") 
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00、04_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                daily_elem = 'daily_timer'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, daily_elem)))
                print(f"[INFO] 重做02_00、04_00完成")
                return True
            except Exception as err:
                tf.catch_exc(f"重做02_00、04_00失敗", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.點擊Disable選項
    def test_14_00_click_disable_option(self):
        """點擊Disable選項"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                disable_elem = 'disabled_timer'
                disable_op = self.d.find_element(By.ID, disable_elem)
                disable_op.click()
                print(f"[CLICK] Disable option") 
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Disable選項時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                disable_elem = 'disabled_timer'
                disable_op = self.d.find_element(By.ID, disable_elem)
                if disable_op.is_selected():
                    print(f"[INFO] 已選取Disable")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認Disable選取時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.點擊儲存
    def test_15_00_click_save(self):
        """點擊儲存"""
        # 如果前面測試失敗, 就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
           # 點擊儲存
            try:
                print(f"[INFO] 設定時間: Disable")
                tf.output(f"[INFO] 設定時間: Disable")
                save_elem = '//*[@id="Network_Config"]/div/input'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊儲存時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                WebDriverWait(self.d, 3).until(EC.alert_is_present())
                time.sleep(1)
                alert = self.d.switch_to.alert
                mq.msg_que = [] # 清除queue來確認新訊息
                alert.accept()
                print(f"[INFO] 出現設定成功Alert視窗")
            except Exception as err:
                tf.catch_exc(f"沒有出現設定成功Alert視窗", self._testMethodName,  err)
                return False

            start_time = datetime.now()
            timeout = timedelta(seconds=30)
            while datetime.now() <= start_time + timeout:
                try:
                    # 檢查Gateway回覆的Reboot schedule內容
                    if "AUTO_REBOOT_SETTINGS" in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        msg = json.loads(mq.msg_que[0])
                        content = msg["Payload"]["Content"]
                        reboot_type = int(content["RebootType"])
                        day_of_week = int(content["DayOfWeek"])
                        hour = int(content["Hour"])
                        minute = int(content["Minute"])
                        if reboot_type != 0:
                            print(f"[FAIL] RebootType 錯誤")
                            return False
                        if day_of_week != 0:
                            print(f"[FAIL] DayOfWeek錯誤")
                            return False
                        if hour != 0:
                            print(f"[FAIL] Hour錯誤")
                            return False
                        if minute != 0:
                            print(f"[FAIL] Minute錯誤")
                            return False
                        print(f"[INFO] 已確認Reboot設定")
                        tf.output(f"[INFO] 已確認Reboot設定")
                        del mq.msg_que[0]
                        return True
                    elif "busy" in mq.msg_que[0]:
                        print(mq.msg_que[0])
                        print(f"\n[INFO] Gateway忙錄中, 10秒後重試")
                        tf.output(f"\n[INFO] Gateway忙錄中, 10秒後重試")
                        time.sleep(10)
                        del mq.msg_que[0]
                        return False
                    else:
                        del mq.msg_que[0]
                    return True
                except:
                    pass    # 忽略mq.msg_que[0]未給值的狀態
            else:
                print(f"[FAIL] 沒有收到AUTO_REBOOT_SETTINGS訊息")
                tf.output(f"[FAIL] 沒有收到AUTO_REBOOT_SETTINGS訊息")
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.測試Master回覆UDP功能
    def test_16_00_test_master_udp_rpt_mac(self):
        """測試Master回覆UDP功能"""
        # 如果前面測試失敗, 仍繼續測試
        if tf.flag_test_fail:
            # self.skipTest(tf.fail_reason)
            tf.flag_test_fail = False
            tf.fail_reason = ""
        def action():
            try:
                udp.udp_que = []
                msg = '{"MsgType":"MasterInfoReq","MasterMac":"%s"}'% tf.gw_mac
                result = udp.send_message(tf.gw_ip, 50109, msg)
                if result:
                    print(f"{msg}")
                    print(f"[INFO] 已送出UDP要求") 
                    tf.output(f"[INFO] 已送出UDP要求")
                    return True
                else:
                    print(f"[FAIL] 發送UDP失敗")
                    return False
            except Exception as err:
                tf.catch_exc(f"發送UDP要求時發生錯誤", self._testMethodName,  err)
                return False

        def check(info):
            try:
                time.sleep(3)   # 等待Master回應UDP
                target = {"MasterInfoRpt", tf.gw_mac}
                que = udp.udp_que
                for msg in que:
                    if all((t in msg) for t in target):
                        print(msg)
                        print(f"[INFO] 已確認UDP訊息")
                        tf.output(f"[INFO] 已確認UDP訊息")
                        return True
                print(f"[FAIL] 沒有收到Gateway UDP訊息") 
                return False
            except Exception as err: 
                tf.catch_exc(f"確認UDP訊息時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標, 並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag


if __name__ == "__main__":
    tf.init_test(sys_08_reboot_schedule)
