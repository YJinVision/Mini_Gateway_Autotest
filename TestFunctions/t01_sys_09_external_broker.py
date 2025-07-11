#==============================================================================
# 程式功能: 測試middle對外部Broker訂閱/發佈功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Network Configuration分頁
# 05_00.點擊MQTT/Cloud ServerSetting Enable
# 06_00.輸入Broker資訊
# 07_00.等待Gateway重啟完成
# 08_00.訂閱external broker
# 09_00.發送訊息到external broker
# 10_00.確認Gateway回傳訊息
# 11_00.復原MQTT/Cloud ServerSetting設定
# 12_00.重做07_00
# 13_00.點擊MQTT/Cloud ServerSetting Disable
# 14_00.點擊Save
# 15_00.重做07_00
#==============================================================================
import os
import sys
import json
import time
import threading
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(os.path.dirname(curr_path))  #.\iHub_Autotest
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import MiniGateway.mqtt_lite as mq

class sys_09_external_broker(unittest.TestCase):
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

# 04_00.點擊Network Configuration分頁
    def test_04_00_click_network_config(self):
        """點擊Network Configuration分頁"""
        # 如果前面測試失敗，就略過此測試
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
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 05_00.點擊MQTT/Cloud ServerSetting Enable
    def test_05_00_click_cloud_server_enable(self):
        """點擊MQTT/Cloud ServerSetting Enable"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                enable_elem = '//*[@id="System_MQTT_Enable"]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, enable_elem)))
                enable_op = self.d.find_element(By.XPATH, enable_elem)
                enable_op.click()
                print(f"[CLICK] Enable")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Enable時發生錯誤", self._testMethodName,  err)
                tf.screen_cap(self)
                return False
        
        def check(info):
            try:
                enable_elem = '//*[@id="System_MQTT_Enable"]'
                enable_op = self.d.find_element(By.XPATH, enable_elem)
                if enable_op.is_selected():
                    print(f"[INFO] 已確認選擇Enable")
                    return True
                print(f"[FAIL] Enable未被選擇")
                return False
            except Exception as err:
                tf.catch_exc(f"", self._testMethodName,  err)
                tf.screen_cap(self)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 06_00.輸入Broker資訊
    def test_06_00_set_external_broker(self):
        """輸入Broker資訊"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.3)
                # 輸入External broker資訊
                server_ip_elem = '//*[@id="System_MQTT_Server_IP"]'
                server_ip = self.d.find_element(By.XPATH, server_ip_elem)
                server_ip.clear()
                server_ip.send_keys(tf.ex_test_broker["server_ip"])
                print(f"[SENDKEY] {tf.ex_test_broker["server_ip"]}")
                client_id_elem = '//*[@id="System_MQTT_Client_ID"]'
                client_id = self.d.find_element(By.XPATH, client_id_elem)
                client_id.clear()
                client_id.send_keys(tf.ex_test_broker["client_id"])
                print(f"[SENDKEY] {tf.ex_test_broker["client_id"]}")
                sub_topic_elem = '//*[@id="System_MQTT_Broker_Pub"]'
                sub_topic = self.d.find_element(By.XPATH, sub_topic_elem)
                sub_topic.clear()
                sub_topic.send_keys(tf.ex_test_broker["subscribe_topic"])
                print(f"[SENDKEY] {tf.ex_test_broker["subscribe_topic"]}")
                pub_topic_elem = '//*[@id="System_MQTT_Broker_Sub"]'
                pub_topic = self.d.find_element(By.XPATH, pub_topic_elem)
                pub_topic.clear()
                pub_topic.send_keys(tf.ex_test_broker["publish_topic"])
                print(f"[SENDKEY] {tf.ex_test_broker["publish_topic"]}")
                save_elem = '//*[@id="Network_Config"]/input[2]'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"輸入Broker資訊時發生錯誤", self._testMethodName,  err)
                tf.screen_cap(self)
                return False
        
        def check(info):
            try:
                WebDriverWait(self.d, 10).until(EC.alert_is_present())
                print(f"[INFO] 出現確認Alert")
                time.sleep(1)
                mq.msg_que = [] # 清空queue來確認訊息
                alert = self.d.switch_to.alert
                alert.accept()
                print(f"[CLICK] Alert確定")
                tf.output(f"[INFO] 已設定MQTT/Cloud Server, 等待Gateway重啟")
                return True
            except Exception as err:
                tf.catch_exc(f"沒有出現確認Alert", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_00.等待Gateway重啟完成
    def test_07_00_wait_gw_restart(self):
        """等待Gateway重啟完成"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                keyword = ["MIDDLE_TO_USER", "ROLETYPE_FN"]
                msg = tf.wait_mqtt_msg(keyword, 40, ack_busy=False)
                if msg == "timeout":
                    print(f"[FAIL] 超時, 沒有出現包含{keyword}的訊息")
                    return False
                print(msg)
                print(f"[INFO] Gateway已重啟完成")
                tf.output(f"[INFO] Gateway已重啟完成")
                return True
            except Exception as err:
                tf.catch_exc(f"等待Gateway重啟時發生錯誤", self._testMethodName,  err)
                return False
            
        def reset():
            try:
                save_elem = '//*[@id="Network_Config"]/input[2]'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
            except:
                pass

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 07_01.確認Gateway可接收命令
    def test_07_01_check_gw_stat(self):
        """確認Gateway可接收命令"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                tf.wait_mqtt_info_loading(5)
                time.sleep(1)
                mq.msg_que = []
                msg = '{"EVENT":"GET_WIFI_SETTING"}'
                result = mq.pub_msg(broker=tf.gw_ip, 
                                    topic="USER_TO_MIDDLE", 
                                    msg=msg)
                if result:
                    print(f"[INFO] 已發送訊息: {msg}")
                    tf.output(f"[INFO] 已發送訊息: {msg}")
                    return True
                print(f"[FAIL] 發送訊息失敗")
                tf.output(f"[FAIL] 發送訊息失敗")
                return False
            except Exception as err:
                tf.catch_exc(f"發送訊息時發生錯誤", self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                keyword = ['"ZwCmd": "WIFI_SETTING"']
                msg = tf.wait_mqtt_msg(keyword, 10, ack_busy=False)
                if msg == "timeout":
                    print(f"[FAIL] 超時, 沒有出現包含{keyword}的訊息")
                    return False
                print(msg)
                print(f"[INFO] 已確認回覆訊息")
                tf.output(f"[INFO] 已確認回覆訊息")
                tf.wait_mqtt_info_loading(5)
                return True
            except Exception as err:
                tf.catch_exc(f"確認Gateway回傳訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.訂閱external broker
    def test_08_00_subscribe_external_broker(self):
        """訂閱external broker"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.sub_loop(tf.ex_test_broker["server_ip"], 
                            tf.ex_test_broker["publish_topic"], 
                            daemon_flag=True)
                print(f"[INFO] 已訂閱external broker")
                return True
            except Exception as err:
                tf.catch_exc(f"訂閱external broker時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.發送訊息到external broker
    def test_09_00_publish_to_external_broker(self):
        """發送訊息到external broker"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                mq.msg_que = []
                msg = '{"EVENT":"GET_NODE_ID_LIST"}'
                result = mq.pub_msg(broker=tf.ex_test_broker["server_ip"], 
                                    topic=tf.ex_test_broker["subscribe_topic"], 
                                    msg=msg)
                if result:
                    print(f"[INFO] 已發送訊息: {msg}")
                    tf.output(f"[INFO] 已發送訊息: {msg}")
                    return True
                print(f"[FAIL] 發送訊息失敗")
                tf.output(f"[FAIL] 發送訊息失敗")
                return False
            except Exception as err:
                tf.catch_exc(f"發送訊息時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.確認Gateway回傳訊息
    def test_10_00_check_gw_report(self):
        """確認Gateway回傳訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                keyword = [tf.ex_test_broker["publish_topic"], 
                           "NodeIdList"]
                msg = tf.wait_mqtt_msg(keyword, 30, ack_busy=False)
                if msg == "timeout":
                    print(f"[FAIL] 超時, 沒有出現包含{keyword}的訊息")
                    return False
                print(msg)
                print(f"[INFO] 已確認回覆訊息")
                tf.output(f"[INFO] 已確認回覆訊息")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Gateway回傳訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_09_00_publish_to_external_broker()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.復原MQTT/Cloud ServerSetting設定
    def test_11_00_restore_setting(self):
        """復原MQTT/Cloud ServerSetting設定"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.3)
                # 輸入External broker資訊
                server_ip_elem = '//*[@id="System_MQTT_Server_IP"]'
                server_ip = self.d.find_element(By.XPATH, server_ip_elem)
                server_ip.clear()
                server_ip.send_keys(tf.ex_default_broker["server_ip"])
                print(f"[SENDKEY] {tf.ex_default_broker["server_ip"]}")
                client_id_elem = '//*[@id="System_MQTT_Client_ID"]'
                client_id = self.d.find_element(By.XPATH, client_id_elem)
                client_id.clear()
                client_id.send_keys(tf.ex_default_broker["client_id"])
                print(f"[SENDKEY] {tf.ex_default_broker["client_id"]}")
                sub_topic_elem = '//*[@id="System_MQTT_Broker_Pub"]'
                sub_topic = self.d.find_element(By.XPATH, sub_topic_elem)
                sub_topic.clear()
                sub_topic.send_keys(tf.ex_default_broker["subscribe_topic"])
                print(f"[SENDKEY] {tf.ex_default_broker["subscribe_topic"]}")
                pub_topic_elem = '//*[@id="System_MQTT_Broker_Sub"]'
                pub_topic = self.d.find_element(By.XPATH, pub_topic_elem)
                pub_topic.clear()
                pub_topic.send_keys(tf.ex_default_broker["publish_topic"])
                print(f"[SENDKEY] {tf.ex_default_broker["publish_topic"]}")
                save_elem = '//*[@id="Network_Config"]/input[2]'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"復原MQTT/Cloud ServerSetting設定時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                WebDriverWait(self.d, 10).until(EC.alert_is_present())
                print(f"[INFO] 出現確認Alert")
                time.sleep(1)
                mq.msg_que = [] # 清空queue來確認訊息
                alert = self.d.switch_to.alert
                alert.accept()
                print(f"[CLICK] Alert確定")
                tf.output(f"[INFO] 已設定MQTT/Cloud Server, 等待Gateway重啟")
                return True
            except Exception as err:
                tf.catch_exc(f"沒有出現確認Alert", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.重做07_00
    def test_12_00_redo_0700(self):
        """重做07_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_07_00_wait_gw_restart()
                print(f"[INFO] 已重做07_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做07_00時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.點擊MQTT/Cloud ServerSetting Disable
    def test_13_00_click_cloud_server_disable(self):
        """點擊MQTT/Cloud ServerSetting Disable"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                disable_elem = '//*[@id="System_MQTT_Disable"]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, disable_elem)))
                disable_op = self.d.find_element(By.XPATH, disable_elem)
                disable_op.click()
                print(f"[CLICK] Disable")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Disable時發生錯誤", self._testMethodName,  err)
                tf.screen_cap(self)
                return False
        
        def check(info):
            try:
                enable_elem = '//*[@id="System_MQTT_Disable"]'
                enable_op = self.d.find_element(By.XPATH, enable_elem)
                if enable_op.is_selected():
                    print(f"[INFO] 已確認選擇Disable")
                    return True
                print(f"[FAIL] Disable未被選擇")
                return False
            except Exception as err:
                tf.catch_exc(f"", self._testMethodName,  err)
                tf.screen_cap(self)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.點擊Save
    def test_14_00_click_save(self):
        """點擊Save"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(0.3)
                save_elem = '//*[@id="Network_Config"]/input[2]'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Save時發生錯誤", self._testMethodName,  err)
                tf.screen_cap(self)
                return False
        
        def check(info):
            try:
                WebDriverWait(self.d, 10).until(EC.alert_is_present())
                print(f"[INFO] 出現確認Alert")
                time.sleep(1)
                mq.msg_que = [] # 清空queue來確認訊息
                alert = self.d.switch_to.alert
                alert.accept()
                print(f"[CLICK] Alert確定")
                tf.output(f"[INFO] 已設定MQTT/Cloud Server, 等待Gateway重啟")
                return True
            except Exception as err:
                tf.catch_exc(f"沒有出現確認Alert", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.重做07_00
    def test_15_00_redo_0700(self):
        """重做07_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_07_00_wait_gw_restart()
                print(f"[INFO] 已重做07_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做07_00時發生錯誤", self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag


if __name__ == "__main__":
    tf.init_test(sys_09_external_broker)
