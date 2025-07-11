#==============================================================================
# 程式功能: 測試修改裝置名稱, 位置
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置
# 07_00.點擊atsiren
# 07_01.取得裝置Information
# 08_00.關閉彈窗
# 09_00.重做07_00
# 10_00.修改裝置位置
# 11_00.確認Location MQTT訊息
# 12_00.修改裝置名稱
# 13_00.確認Rename MQTT訊息
# 14_00.關閉彈窗並確認名稱及位置
# 15_00.重做07_00
# 16_00.復原設定
#==============================================================================
import os
import sys
import json
import time
import subprocess
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(os.path.dirname(curr_path))  #.\iHub_Autotest
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import MiniGateway.mqtt_lite as mq

class zw_04_device_info(unittest.TestCase):
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

# 07_00.點擊atsiren
    def test_07_00_click_atsiren(self):
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

# 07_01.取得裝置Information
    def test_07_01_get_dev_info(self):
        """取得裝置Information"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                info = {}
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                tb_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Modal_Body_Info"]/tbody'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, tb_elem)))
                info_tb = self.d.find_element(By.XPATH, tb_elem)
                tr = info_tb.find_elements(By.TAG_NAME, 'tr')
                print(f"[INFO] Information:")
                for i in tr:
                    td = i.find_elements(By.TAG_NAME, 'td')
                    info[td[0].text] = td[2].text
                    print(td[0].text, ":", td[2].text)
                return info
            except Exception as err:
                tf.catch_exc(f"取得裝置Information時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                if info["Vendor ID"] == "0x0000":
                    print(f"[FAIL] Vendor ID錯誤: {info["Vendor ID"]}")
                print(f"[INFO] 已確認資訊")
                return True
            except Exception as err:
                tf.catch_exc(f"確認資訊時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()
            self.test_07_00_click_atsiren()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.關閉彈窗
    def test_08_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                slide_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                        f'_Modal"]/div/div[2]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, slide_elem)))
                slide = self.d.find_element(By.XPATH, slide_elem)
                close_elem = 'zw-setting-modal-closeBtn'
                close_btn = slide.find_element(By.CLASS_NAME, close_elem)
                close_btn.click()
                print(f"[CLICK] Close")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                node_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_Modal_Name"]'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.XPATH, node_elem)))
                print(f"[INFO] 已關閉彈窗")
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

# 09_00.重做07_00
    def test_09_00_redo_0700(self):
        """重做07_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                self.test_07_00_click_atsiren()
                print(f"[INFO] 已重做07_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做07_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.修改裝置位置
    def test_10_00_change_location(self):
        """修改裝置位置"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global m_dev_room
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                dev_room_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_LocationSelector"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, dev_room_elem)))
                room_sele = self.d.find_element(By.XPATH, dev_room_elem)
                room_sele.click()
                # 前端做法: 下拉選單並非Selector, 而是點開元素後才展開<ul>及<li>
                # 故需點開元素後, 再從<ul>元素中取出所有<li>內容再進行互動 
                time.sleep(1)   # 等待下拉選單展開
                ul_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_LocationSelector"]/ul'
                room_ul = self.d.find_element(By.XPATH, ul_elem)
                rooms = room_ul.find_elements(By.TAG_NAME, 'li')
                print(f"[INFO] 全部的Location: ")
                for room in rooms:
                    print(f"/{room.text} ", end=" ")
                m_dev_room = rooms[len(rooms)-1].text
                rooms[len(rooms)-1].click() # 點選排序最底下的房間
                print(f"\n[CLICK] {m_dev_room}")
                return True
            except Exception as err:
                tf.catch_exc(f"時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(1)   # 等待下拉選單收合
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                dev_room_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_LocationSelector"]'
                dev_room_sele = self.d.find_element(By.XPATH, dev_room_elem)
                curr_gw_room = dev_room_sele.text
                if curr_gw_room == m_dev_room:
                    print(f"[INFO] 已確認顯示位置")
                    return True
                print(f"[FAIL] 顯示的位置錯誤: {curr_gw_room}\n")
                return False
            except Exception as err:
                tf.catch_exc(f"時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 11_00.確認Location MQTT訊息
    def test_11_00_check_location_mqtt_msg(self):
        """確認Rename MQTT訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "ZW_POSITION_REPORT"', 
                           f'"Position": "{m_dev_room}"', 
                           f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, ack_busy=False)
                if "timeout" in msg:
                    print(f"[FAIL] 已超時, 未出現Location訊息")
                    return False
                print(f"[INFO] 已確認訊息: {msg}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Location MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_10_00_change_location()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.修改裝置名稱
    def test_12_00_rename_device(self):
        """修改裝置名稱"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global m_siren
            try:
                mq.msg_que = []
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                edit_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_EditBtn"]'
                edit_btn = self.d.find_element(By.XPATH, edit_elem)
                edit_btn.click()
                print(f"[CLICK] Edit")
                time.sleep(0.5)
                m_siren = f"at_test"
                box_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_Modal_Rename"]'
                name_box = self.d.find_element(By.XPATH, box_elem)
                name_box.clear()
                name_box.send_keys(m_siren)
                print(f"[SENDKEY] {m_siren}")
                edit_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"修改裝置名稱時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.確認Rename MQTT訊息
    def test_13_00_check_rename_mqtt_msg(self):
        """確認Rename MQTT訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "NODE_RENAME"', 
                           f'"Name": "{m_siren}"', 
                           f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, ack_busy=False)
                if "timeout" in msg:
                    print(f"[FAIL] 已超時, 未出現Rename訊息")
                    return False
                print(f"[INFO] 已確認訊息: {msg}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Rename MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_12_00_rename_device()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.關閉彈窗並確認名稱及位置
    def test_14_00_close_pop_and_check_modify(self):
        """關閉彈窗並確認名稱及位置"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_08_00_close_pop()
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                name_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_name"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, name_elem)))
                curr_name = self.d.find_element(By.XPATH, name_elem).text
                room_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_position"]'
                curr_room = self.d.find_element(By.XPATH, room_elem).text
                if curr_name != m_siren:
                    print(f"[FAIL] 裝置名稱錯誤: {curr_name}")
                    return False
                if curr_room != m_dev_room:
                    print(f"[FAIL] 裝置位置錯誤: {curr_room}")
                    return False
                print(f"[INFO] 已確認名稱及位置")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗並確認名稱及位置時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_07_00_click_atsiren()

        success_flag = tf.execute(action, reset=reset)
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
                self.test_07_00_click_atsiren()
                print(f"[INFO] 已重做07_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做07_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.復原設定
    def test_16_00_restroe_setting(self):
        """復原設定"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                edit_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_EditBtn"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, edit_elem)))
                edit_btn = self.d.find_element(By.XPATH, edit_elem)      
                edit_btn.click()
                print(f"[CLICK] Edit")
                time.sleep(0.5)
                box_elem = f'//*[@id="Zw_Setting_{uuid}_{node}_Modal_Rename"]'
                name_box = self.d.find_element(By.XPATH, box_elem)
                name_box.clear()
                name_box.send_keys(at_dev_name[tf.siren])
                print(f"[SENDKEY] {at_dev_name[tf.siren]}")
                edit_btn.click()
                print(f"[CLICK] Save")
            except Exception as err:
                tf.catch_exc(f"復原名稱時發生錯誤", 
                             self._testMethodName,  err)
                
            try:
                time.sleep(0.5)
                dev_room_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_LocationSelector"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, dev_room_elem)))
                room_sele = self.d.find_element(By.XPATH, dev_room_elem)
                room_sele.click()
                time.sleep(1)   # 等待下拉選單展開
                ul_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_LocationSelector"]/ul'
                room_ul = self.d.find_element(By.XPATH, ul_elem)
                rooms = room_ul.find_elements(By.TAG_NAME, 'li')
                for room in rooms:
                    if room.text == at_dev_room[tf.siren]:
                        room.click() # 點選原來的房間
                        print(f"[CLICK] {at_dev_room[tf.siren]}")
                        return True
            except Exception as err:
                tf.catch_exc(f"復原位置時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                time.sleep(1)
                self.test_08_00_close_pop()
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                name_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_name"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, name_elem)))
                curr_name = self.d.find_element(By.XPATH, name_elem).text
                room_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_position"]'
                curr_room = self.d.find_element(By.XPATH, room_elem).text
                if curr_name != at_dev_name[tf.siren]:
                    print(f"[FAIL] 裝置名稱錯誤: {curr_name}")
                    return False
                if curr_room != at_dev_room[tf.siren]:
                    print(f"[FAIL]  裝置位置錯誤: {curr_room}")
                    return False
                print(f"[INFO] 已確認名稱及位置")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗並確認名稱及位置時發生錯誤", 
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
    tf.init_test(zw_04_device_info)

