#==============================================================================
# 程式功能: 測試Run scene功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置siren, plug
# 07_00.點擊Scene
# 08_00.重做02_00、05_00
# 08_01.檢查已存在的Scene
# 08_02.重做05_00, 等待內容載入完成
# 09_00.新增測試用的Scene
# 09_01.重做05_00, 等待內容載入完成
# 10_00.點擊Scene name
# 11_00.點擊Run Scene
# 12_00.取得顯示時間
# 13_00.點擊日期輸入框
# 14_00.設定日期
# 15_00.點擊時間輸入框
# 16_00.設定時間
# 17_00.檢查週期按鈕
# 18_00.設定週期
# 19_00.點擊Save
# 20_00.確認MQTT設定結果
# 21_00.確認MQTT觸發訊息
# 22_00.復原裝置動作
# 23_00.關閉彈窗
# 24_00.重做08_01, 刪除測試用的Scene
#==============================================================================
import os
import sys
import time
import json
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
import MiniGateway.mqtt_lite as mq

class sce_03_run_scene_schdule(unittest.TestCase):
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

# 06_00.檢查必要裝置
    def test_06_00_check_device_need(self):
        """檢查必要裝置"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global at_dev_name, at_dev_id, at_dev_uuid, at_dev_room
            try:
                dev_need = [tf.siren, tf.plug]
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

# 07_00.點擊Scene
    def test_07_00_click_scene(self):
        """點擊Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                sce_elem = '//*[@id="Main_menu_scenes"]'
                WebDriverWait(self.d, 10).until(
                    EC.element_to_be_clickable((By.XPATH, sce_elem)))
                sce = self.d.find_element(By.XPATH, sce_elem)
                sce.click()
                print(f"[CLICK] Scene")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Scene時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                elem = 'Loader_Modal'
                WebDriverWait(self.d, 10).until(
                    EC.presence_of_element_located((By.ID, elem)))
                print(f"[INFO] Loader 出現")
                WebDriverWait(self.d, 15).until(
                    EC.invisibility_of_element((By.ID, elem)))
                print(f"[INFO] Loader 消失")
                return True
            except Exception as err:
                tf.catch_exc(f"Loader動作超時", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_00.解析MQTT訊息並備份即將刪除的Scene
    def test_08_00_parse_msg_and_backup(self):
        """解析MQTT訊息並備份即將刪除的Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global restore_msg
            restore_msg = []
            pnode, snode = int(at_dev_id[tf.plug]), int(at_dev_id[tf.siren])
            p_tri = {"NODE_ID": pnode, "SCENE_EVENT": 110, "EP_ID": 0}
            s_tri = {"NODE_ID": snode, "SCENE_EVENT": 110, "EP_ID": 0}
            triggers = [p_tri, s_tri]
            scene_id = []
            node_id = []

            # 避免因頁面載入過久而略過訊息parser
            last_time = datetime.now()
            timeout = timedelta(seconds=10)
            while datetime.now() - last_time <= timeout:
                if mq.msg_que:
                    break
                time.sleep(0.1)
            else:
                print(f"[FAIL] 超時, 未收到MQTT訊息")
                return False

            curr_msg = "MQTT msg"
            prev_msg = ""
            last_time = datetime.now()
            timeout = timedelta(seconds=3)
            while datetime.now() - last_time <= timeout:
                # 若mq.msg_que為空值時避免解析mq.msg_que[0]造成Exception
                if not mq.msg_que:
                    time.sleep(0.1)
                    continue
                # 符合的訊息才解析內容
                try:
                    if '"ZwCmd": "SCENE_INFO_GET"' in mq.msg_que[0]:
                        msg = json.loads(mq.msg_que[0])
                        scene_info = msg["Payload"]["Content"]["SCENE_INFO"]
                        for idx, tri in enumerate(triggers):
                            if tri.items() <= scene_info.items():
                                pub_msg = {}
                                # 將收到的訊息重組成復原Scene的cmd
                                pub_msg["EVENT"] = "SCENE_INFO_SET"
                                pub_msg.update(scene_info)
                                restore_msg.append(str(pub_msg))
                                # 取出SCENE_ID用來parse GET_SCHEDULING_EVENT_INFO
                                scene_id.append(scene_info["PROPRIETARY_MAPPING"])
                                node_id.append(scene_info["NODE_ID"])

                    elif '"ZwCmd": "GET_SCHEDULING_EVENT_INFO"' in mq.msg_que[0]:
                        msg = json.loads(mq.msg_que[0])
                        content = msg["Payload"]["Content"]
                        for idx, sid in enumerate(scene_id):
                            if sid == content["SCENE_ID"]:
                                pub_msg = {}
                                # 將收到的訊息重組成復原Scene的cmd
                                pub_msg["EVENT"] = "SET_SCHEDULING_EVENT_INFO"
                                pub_msg.update(content)
                                restore_msg.append(pub_msg)

                    elif '"ZwCmd": "GET_SCHEDULING_ACTIVE_TIME"' in mq.msg_que[0]:
                        msg = json.loads(mq.msg_que[0])
                        content = msg["Payload"]["Content"]
                        for idx, nid in enumerate(node_id):
                            if nid == content["NODE_ID"]:
                                pub_msg = {}
                                # 將收到的訊息重組成復原Scene的cmd
                                pub_msg["EVENT"] = "SET_SCHEDULING_DEV_ACTIVE_TIME"
                                pub_msg.update(content)
                                restore_msg.append(pub_msg)
                except Exception as err:
                    tf.catch_exc(f"解析訊息時發生錯誤", 
                                self._testMethodName,  err)
                    return False
                        
                # 更新最後一筆訊息內容並設定收到的時間
                # 從收到最後一筆訊息後超過timeout視為訊息傳送完畢
                if prev_msg != curr_msg:
                    prev_msg = curr_msg
                    curr_msg = mq.msg_que[0]
                    last_time = datetime.now()

                # 非目標訊息或已處理完成的訊息刪除後再進行下一筆訊息    
                del mq.msg_que[0]

            print(f"[INFO] 備份的Scene:\n")
            for i in restore_msg:
                print(i)

            return True
        
        def reset():
            self.d.refresh()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 08_01.檢查已存在的Scene
    def test_08_01_check_scene(self):
        """檢查已存在的Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # Workaround: fw v01.25.0(含)以前的版本
            # 新增Trigger相同的scene後會覆蓋原有的scene
            # 但之後的版本可能會阻擋, 而無法新增
            # 故需先檢查並刪除才能再新增Scene來做測試 
            try:
                puuid, pnode = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                suuid, snode = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 後面測試步驟會將
                # 原本的plug on -> siren on
                # 修改為siren on -> plug on
                # 故若已存在這兩條scene就需先刪除 
                scenes = [f'{pnode}_110_0_0_{puuid}', f'{snode}_110_0_0_{suuid}']
                scene_names = []
                for scene_value in scenes:
                    scene_tb_elem = 'Scene_All_Secen_Rule_Tb'
                    WebDriverWait(self.d, 5).until(
                        EC.presence_of_element_located((By.ID, scene_tb_elem)))
                    scene_tb = self.d.find_element(By.ID, scene_tb_elem)
                    tr = scene_tb.find_elements(By.TAG_NAME, 'tr')
                    tar_scene = ""
                    for i in tr:
                        if i.get_attribute("data-value") == scene_value:
                            tar_scene = i
                            break
                    if tar_scene:
                        print(f"[INFO] 目標Scene ({scene_value})已存在, 即將刪除")
                        scene_name_elem = 'node-Tb-NameID-text'
                        scene_name = tar_scene.find_element(
                            By.CLASS_NAME, scene_name_elem).text
                        del_class = 'scene-list-delete-btn-bk'
                        del_btn = tar_scene.find_element(By.CLASS_NAME, del_class)
                        del_btn.click()
                        print(f"[CLICK] Delete")
                        del_ok_elem = '//*[@id="Scene_Notify_Modal"]'\
                            '/div/div[2]/input'
                        time.sleep(1)
                        WebDriverWait(self.d, 5).until(
                            EC.element_to_be_clickable((By.XPATH, del_ok_elem)))
                        del_ok = self.d.find_element(By.XPATH, del_ok_elem)
                        del_ok.click()
                        print(f"[CLICK] OK")
                        scene_names.append(scene_name)
                    else:
                        print(f"[INFO] 目標Scene不存在")
                        scene_names.append("scene not exist")
                return scene_names
            except Exception as err:
                tf.catch_exc(f"檢查Scene時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(1)
                flag = True
                for scene_name in info:
                    if scene_name == "scene not exist":
                        print(f"[INFO] 已檢查Scene: {scene_name}")
                    else:
                        elem = f'//*[contains(text(), "{scene_name}")]'
                        WebDriverWait(self.d, 5).until(
                            EC.invisibility_of_element((By.XPATH, elem)))
                        print(f"[INFO] Scene已刪除")
                        # 若有執行刪除Scene的動作, 則重整頁面後再檢查一次
                return flag
            except Exception as err:
                tf.catch_exc(f"確認Scene時發生錯誤", 
                             self._testMethodName,  err)
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

# 08_02.重做05_00, 等待內容載入完成
    def test_08_02_redo_0500(self):
        """重做05_00, 等待內容載入完成"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_05_00_wait_content_loading()
                print(f"[INFO] 已重做05_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做05_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 09_00.新增測試用的Scene
    def test_09_00_add_scene_for_test(self):
        """新增測試用的Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global scene_name
            scene_name = "PlugOn-SirenOn"
            try:
                puuid, pnode = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                suuid, snode = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                pub_msg = '''{"EVENT":"SCENE_INFO_SET","NODE_ID":%s, "SCENE_ID": 0, "SCENE_ICON":"3","SCENE_NAME":"%s" , "SCENE_EVENT": 110, "CMD_INFO":[{ "PROTO_TYPE":0, "TGT_NODE":%s, "TGT_EP":0, "EXEC_ACT":7, "MS_UUID":"%s"}], "MS_UUID":"%s", "ENABLE":1, "EP_ID":0, "APP_ENABLED":1}''' % (pnode, scene_name, snode, suuid, puuid)
                result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", pub_msg)
                print(f"[INFO] 已傳送訊息:\n{pub_msg}")
                return result
            except Exception as err:
                tf.catch_exc(f"新增測試用的Scene時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            global scene_id
            try:
                time.sleep(2)
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                scene_value = f'{node}_110_0_0_{uuid}'
                scene_tb_elem = 'Scene_All_Secen_Rule_Tb'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.ID, scene_tb_elem)))
                scene_tb = self.d.find_element(By.ID, scene_tb_elem)
                tr = scene_tb.find_elements(By.TAG_NAME, 'tr')
                for i in tr:
                    if i.get_attribute("data-value") == scene_value:
                        print(f"[INFO] 已新增測試用的Scene")
                        # 取得Scene Id
                        class_elem = 'scene-list-header-bk'
                        td = i.find_element(By.CLASS_NAME, class_elem)
                        onclick = td.get_attribute("onclick").split(";")
                        for j in onclick:
                            if "Scene_Schedule_UpdateDateTimePickerInfo" in j:
                                scene_id = j[j.rfind("(")+1:j.rfind(")")]
                                print(f"[INFO] Scene Id: {scene_id}")
                                return True
                        print(f"[FAIL] 取得Scene id失敗")
                        return False
                print(f"[FAIL] 新增Scene失敗")
                return False
            except Exception as err:
                tf.catch_exc(f"確認新增測試用的Scene時發生錯誤", 
                             self._testMethodName,  err)
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

# 09_01.重做05_00, 等待內容載入完成
    def test_09_01_redo_0500(self):
        """重做05_00, 等待內容載入完成"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_05_00_wait_content_loading()
                print(f"[INFO] 已重做05_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做05_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_00.點擊Scene name
    def test_10_00_click_scene_name(self):
        """點擊Scene name"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                elem = f'//*[contains(text(), "{scene_name}")]'
                tar_scene = self.d.find_element(By.XPATH, elem)
                tar_scene.click()
                print(f"[CLICK] Scene")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Scene時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                edit_elem = '//*[@id="Scene_Setting_Modal"]'\
                    '/div/div[2]/div[1]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, edit_elem)))
                print(f"[INFO] 彈窗出現")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗出現時發生錯誤", 
                             self._testMethodName,  err)
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

# 11_00.點擊Run Scene
    def test_11_00_click_run_scene(self):
        """點擊Run Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                # <svg>圖示無法互動
                # 能夠click的<div>元素尺吋660x0, 無法直接使用click()
                run_scene_elem = '//*[@id="Run_Scene_Setting_Btn"]'
                run_scene = self.d.find_element(By.XPATH, run_scene_elem)
                self.d.execute_script("arguments[0].click();", run_scene)
                print(f"[CLICK] Run Scene")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Run Scene時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                sch_title_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[1]/span'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, sch_title_elem)))
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

# 12_00.取得顯示時間
    def test_12_00_get_curr_time(self):
        """取得顯示時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global set_time
            try:
                time.sleep(1)
                clock_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, clock_elem)))
                clock = self.d.find_element(By.XPATH, clock_elem)
                date_ = clock.find_element(By.CLASS_NAME, 'date').text
                time_ = clock.find_element(By.CLASS_NAME, 'time').text
                curr_time = datetime.strptime(f"{date_} {time_}", 
                                              "%Y-%m-%d, %a %H : %M : %S")
                print(f"[INFO] 目前時間: {curr_time}")
                if curr_time.second >= 50:
                    set_time = curr_time + timedelta(minutes=2)
                else:
                    set_time = curr_time + timedelta(minutes=1)
                print(f"[INFO] 設定時間: {set_time}")
                return True
            except Exception as err:
                tf.catch_exc(f"取得顯示時間時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()
            self.test_10_00_click_scene()
            self.test_11_00_click_run_scene()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.點擊日期輸入框
    def test_13_00_click_date_input(self):
        """點擊日期輸入框"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                input_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[2]/div[1]/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, input_elem)))
                date_input = self.d.find_element(By.XPATH, input_elem)
                date_input.click()
                print(f"[CLICK] Date")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊日期輸入框時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                date_pick_elem = 'datepicker-calendar-container'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, date_pick_elem)))
                print(f"[INFO] Calendar出現")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Calendar出現時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.設定日期
    def test_14_00_set_date(self):
        """設定日期"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定年
            flag_y = flag_m = flag_d = False
            try:
                time.sleep(0.5)
                # 取得Calander title的動態id
                caland_elem = '//*[starts-with(@id, "datepicker-title-")]'
                caland_title = self.d.find_element(By.XPATH, caland_elem)
                # 由ID組成year xpath路徑
                caland_id = caland_title.get_attribute("id")
                year_elem = f'//*[@id="{caland_id}"]/div/div[2]/input'
                year_btn = self.d.find_element(By.XPATH, year_elem)
                # 要先點擊year input產生drop down之後data-target元素才能互動
                year_btn.click() 
                # 取得year data-target的id
                year_data_id = year_btn.get_attribute("data-target")   
                # 用id找到years元素
                y_ul = self.d.find_element(By.ID, year_data_id)    
                y_li = y_ul.find_elements(By.TAG_NAME, 'li')
                for i in y_li:
                    year = i.find_element(By.TAG_NAME, 'span')
                    if year.text == str(set_time.year):
                        i.click()
                        print(f"設定年: {year.text}")
                        flag_y = True
                        break
                if not flag_y:
                    print(f"[FAIL] 設定失敗: 年")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定年時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 設定月
            try:
                time.sleep(0.5)
                month_elem = f'//*[@id="{caland_id}"]/div/div[1]/input'
                month_btn = self.d.find_element(By.XPATH, month_elem)
                month_btn.click()
                month_data_id = month_btn.get_attribute("data-target")
                monthUl = self.d.find_element(By.ID, month_data_id)
                m_li = monthUl.find_elements(By.TAG_NAME, 'li')
                for i in m_li:
                    month = i.find_element(By.TAG_NAME, 'span')
                    if month.text == set_time.strftime("%B"):
                        i.click()
                        print(f"設定月: {month.text}")
                        flag_m = True
                        break
                if not flag_m:
                    print(f"[FAIL] 設定失敗: 月")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定月時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 設定日
            try:
                time.sleep(0.5)
                # caland_elem = '//*[contains(@class, "datepicker-table-wrapper")]'
                # caland_table = self.d.find_element(By.XPATH, caland_elem)
                caland_elem = 'datepicker-table-wrapper'
                caland_table = self.d.find_element(By.CLASS_NAME, caland_elem)
                td = caland_table.find_elements(By.TAG_NAME, 'td')
                for d in td:
                    if d.text == str(set_time.day):
                        # d.click()後, 前端會自動收合元素
                        # 故需先將text另存後才能在後面的print使用
                        # 否則會出現stale element not found in the current frame問題 
                        day = d.text
                        d.click()
                        print(f"設定日: {day}")
                        flag_d = True
                        break
                if not flag_d:
                    print(f"[FAIL] 設定失敗: 日")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定日時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 點擊 ok
            try:
                time.sleep(0.5)
                footer_elem = '//*[contains(@class, "datepicker-footer")]'
                caland_footer = self.d.find_element(By.XPATH, footer_elem)
                btns = caland_footer.find_elements(By.TAG_NAME, "button")
                for ok in btns:
                    if ok.text in ("OK", "Ok", "ok"):
                        ok.click()
                        print(f"[CLICK] OK")
                        return True
            except Exception as err:
                tf.catch_exc(f"點擊ok時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                time.sleep(1)
                date_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[2]/div[1]/input'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, date_elem)))
                date_box = self.d.find_element(By.XPATH, date_elem)
                seted_d = date_box.get_property("value")
                chk_d = f"{set_time.strftime("%b")} "\
                    f"{set_time.strftime("%d")}, {set_time.year}"
                if seted_d != chk_d:
                    print(f"[FAIL] 設定的日期錯誤")
                    return False
                print(f"[INFO] 已確認設定日期: {seted_d}")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查設定日期時發生錯誤", 
                             self._testMethodName,  err)
                tf.output("exc")
                input()
                return False
            
        def reset():
            self.test_13_00_click_date_input()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.點擊時間輸入框
    def test_15_00_click_time_input(self):
        """點擊日期輸入框"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[2]/div[2]/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, time_elem)))
                time_box = self.d.find_element(By.XPATH, time_elem)
                time_box.click()
                print(f"[CLICK] Date")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊日期輸入框時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time_pick_elem = 'datepicker-calendar-container'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, time_pick_elem)))
                print(f"[INFO] Time-picker出現")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Time-picker出現時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.設定時間
    def test_16_00_set_time(self):
        """設定時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定 AM/PM
            try:
                time.sleep(0.5)
                pick_elem = '//*[contains(@class, "modal timepicker-modal open")]'
                time_pick = self.d.find_element(By.XPATH, pick_elem)
                picker_id = time_pick.get_attribute("id")
                am_elem = f'//*[@id="{picker_id}"]'\
                    '/div/div[1]/div/div[2]/div/div[1]'
                pm_elem = f'//*[@id="{picker_id}"]'\
                    '/div/div[1]/div/div[2]/div/div[2]'

                if set_time.strftime("%p") == "AM":
                    self.d.find_element(By.XPATH, am_elem).click()
                    print(f"[CLICK] AM")
                elif set_time.strftime("%p") == "PM":
                    self.d.find_element(By.XPATH, pm_elem).click()
                    print(f"[CLICK] PM")
                else:
                    print(f"[FAIL] 點擊AM/PM失敗")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定AM/PM時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 設定 Hour
            flag_h = False
            try:
                time.sleep(1)
                hour_elem = f'//*[@id="{picker_id}"]'\
                    '/div/div[2]/div[1]/div[2]'
                hour_picker = self.d.find_element(By.XPATH, hour_elem)
                div = hour_picker.find_elements(By.TAG_NAME, 'div')
                for hour in div:
                    # .lstrip("0"): 去除leader 0
                    if hour.text == set_time.strftime("%I").lstrip("0"):
                        h = hour.text
                        hour.click()
                        print(f"[CLICK] Hour: {h}")
                        flag_h = True
                if not flag_h:
                    print(f"[FAIL] 設定失敗: Hour")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Hour時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 設定 Minute
            # UI介面為類比時鐘, 先將focus移動到中心, 再點選分鐘的x, y座標
            # 座標來源元素:<circle class="timepicker-canvas-bg" 
            # r="20" cx="0" cy="-105"></circle>
            try:
                time.sleep(1)
                canvas_elem = 'timepicker-canvas'
                canvas = time_pick.find_element(By.CLASS_NAME, canvas_elem)
                center_elem = 'timepicker-canvas-bearing'
                center = canvas.find_element(By.CLASS_NAME, center_elem)
                action = ActionChains(self.d)
                # 移動到時鐘的中心元素
                action.move_to_element(center)
                # 取得類比時鐘裡此分鐘的x, y座標
                position = self.get_minute_position(str(set_time.minute))
                # 移動到此座標後點click()
                action.move_by_offset(position[0], position[1])
                action.click()
                action.perform()
                print(f"[CLICK] Minute: {set_time.minute}")
            except Exception as err:
                tf.catch_exc(f"設定Minute時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 點擊 OK
            try:
                time.sleep(0.5)
                footer_elem = f'//*[@id="{picker_id}"]/div/div[2]/div[2]'
                # footer_elem = '//*[contains(@class, "timepicker-footer")]'
                footer = self.d.find_element(By.XPATH, footer_elem)
                btns = footer.find_elements(By.TAG_NAME, "button")
                for ok in btns:
                    if ok.text in ("OK", "Ok", "ok"):
                        ok.click()
                        print(f"[CLICK] OK")
                        return True
            except Exception as err:
                tf.catch_exc(f"點擊OK時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def check(info):
            try:
                time.sleep(1)
                time_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[2]/div[2]/input'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_elem)))
                time_box = self.d.find_element(By.XPATH, time_elem)
                seted_t = time_box.get_property("value")
                chk_t = f"{set_time.strftime("%I")}:{set_time.strftime("%M")} "\
                    f"{set_time.strftime("%p")}"
                if seted_t != chk_t:
                    print(f"[FAIL] 設定的日期錯誤")
                    return False
                print(f"[INFO] 已確認設定日期: {seted_t}")
                return True
            except Exception as err:
                tf.catch_exc(f"時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_15_00_click_time_input()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 17_00.檢查週期按鈕
    def test_17_00_check_repeat_toggle(self):
        """檢查週期按鈕"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # Every Day active後檢查其他toggle狀態是否也為active
            try:
                container_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[3]'
                container = self.d.find_element(By.XPATH, container_elem)
                every_elem = './div[1]/div'
                every = container.find_element(By.XPATH, every_elem)
                # 若EveryDay已開啟則先點擊關閉
                if "active" in every.get_attribute("class"):
                    every.click()
                    time.sleep(0.5)
                # Every Day active
                every.click()
                print(f"[CLICK] Every Day")
                # 檢查其他toggle的狀態
                toggles = container.find_elements(By.CLASS_NAME, 'day-btn')
                for toggle in toggles:
                    toggle_stat = toggle.find_element(By.TAG_NAME, 'div')
                    if "active" in toggle_stat.get_attribute("class"):
                        pass
                    else:
                        miss_day = toggle.find_element(By.TAG_NAME, 'span').text
                        print(f"[FAIL] Every Day active時, {miss_day} 沒有active")
                        return False
                print(f"[INFO] 已確認Toggles status")
                time.sleep(0.5)

               # Every Day active後檢查其他toggle狀態是否也為active
                every.click()
                print(f"[CLICK] Every Day")
                time.sleep(0.5)
                for toggle in toggles:
                    toggle_stat = toggle.find_element(By.TAG_NAME, 'div')
                    if "active" in toggle_stat.get_attribute("class"):
                        miss_day = toggle.find_element(By.TAG_NAME, 'span').text
                        print(f"[FAIL] Every Day off時, {miss_day} 沒有off")
                        return False
                        break
            except Exception as err:
                tf.catch_exc(f"檢查Every Day toggle時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 檢查各別toggle
            # 各別點擊後, 除了點擊項目之外的toggle是否受影響
            try:
                flag = True
                for toggle in toggles:
                    # 略過every day
                    toggle_name = toggle.find_element(By.TAG_NAME, 'span').text
                    if toggle_name == "Every Day":    
                        continue
                    # 檢查點擊後自身是否active
                    toggle_stat = toggle.find_element(By.TAG_NAME, 'div')
                    toggle_stat.click()
                    print(f"[CLICK] {toggle_name}")
                    time.sleep(0.1)
                    if "active" in toggle_stat.get_attribute("class"):
                        pass
                    else:
                        print(f"[FAIL] {toggle_name} 點擊後沒有active")
                        flag = False
                    # 檢查其他toggle是否受影響
                    for toggle1 in toggles:
                        if toggle1 == toggle:   # 略過目前點擊的toggle
                            continue
                        toggle_stat1 = toggle1.find_element(By.TAG_NAME, 'div')
                        toggle_name1 = toggle1.find_element(By.TAG_NAME, 'span').text
                        if "active" in toggle_stat1.get_attribute("class"):
                            print(f"[FAIL] {toggle_name}active後"\
                                  f"{toggle_name1}也受影響而active")
                            flag = False
                    # 檢查點擊後自身是否off
                    toggle_stat.click()
                    print(f"[CLICK] {toggle_name}")
                    time.sleep(0.1)
                    if "active" in toggle_stat.get_attribute("class"):
                        print(f"[FAIL] {toggle_name} 點擊後沒有off")
                        flag = False

                if flag:
                    print(f"[INFO] 已確認toggles")
                    return True
                else:
                    print(f"[FAIL] toggles部分功能錯誤")
                    return False
            except Exception as err:
                tf.catch_exc(f"檢查toggles時發生錯誤", 
                             self._testMethodName,  err)
                return False        

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 18_00.設定週期
    def test_18_00_set_repeat(self):
        """設定週期"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 點選目前星期
            global repeat_day
            try:
                container_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[3]'
                container = self.d.find_element(By.XPATH, container_elem)
                days = container.find_elements(By.CLASS_NAME, 'day-btn')
                for day in days:
                    day_name = day.find_element(By.TAG_NAME, 'span').text
                    day_btn = day.find_element(By.TAG_NAME, 'div')
                    if day_name == set_time.strftime("%a"):
                        repeat_day = day_name
                        day_btn.click()
                        print(f"[CLICK] {day_name}")
                        return True
            except Exception as err:
                tf.catch_exc(f"設定週期時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                container_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[2]/div[3]'
                container = self.d.find_element(By.XPATH, container_elem)
                days = container.find_elements(By.CLASS_NAME, 'day-btn')
                for day in days:
                    day_name = day.find_element(By.TAG_NAME, 'span').text
                    day_btn = day.find_element(By.TAG_NAME, 'div')
                    if day_name == repeat_day:
                        if "active" in day_btn.get_attribute("class"):
                            print(f"[INFO] 已確認設定週期")
                            return True
                print(f"[FAIL] 設定週期失敗")
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

# 19_00.點擊Save
    def test_19_00_click_save(self):
        """點擊Save"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                mq.msg_que = []
                save_elem = '//*[@id="Scene_Scheduling_Modal"]/div/div[3]/input'
                save_btn = self.d.find_element(By.XPATH, save_elem)
                save_btn.click()
                print(f"[CLICK] Save")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Save時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(0.5)
                finish_elem = '//*[@id="Scene_Setting_Modal"]/div/div[3]/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, finish_elem)))
                print(f"[INFO] 已儲存")
                return True
            except Exception as err:
                tf.catch_exc(f"確認儲存時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 20_00.確認MQTT設定結果
    def test_20_00_check_setting_msg(self):
        """確認MQTT設定結果"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                rep_val = {"Sun":1, "Mon":2, "Tue":4, "Wed":8, 
                              "Thu":16, "Fri":32, "Sat":64}
                chk = [set_time.year, set_time.month, set_time.day, 
                       set_time.hour, set_time.minute, 
                       rep_val[set_time.strftime("%a")]]
                keyword = ['"ZwCmd": "GET_SCHEDULING_EVENT_INFO"', 
                           f'"SCENE_ID": {scene_id}']
                msg = tf.wait_mqtt_msg(keyword, 15)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到GET_SCHEDULING_EVENT_INFO訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    content = json.loads(msg)["Payload"]["Content"]
                    date_info = content["DATE_INFO"]
                    if date_info == chk:
                        print(f"[INFO] 已確認訊息")
                        tf.output(f"[INFO] 已設定, 等待Schedul觸發裝置")
                        return True
                    else:
                        print(f"[FAIL] 重覆週期錯誤: {chk}")
                        return False
            except Exception as err:
                tf.catch_exc(f"確認GET_SCHEDULING_EVENT_INFO訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def reset():
            self.test_11_00_click_run_scene()
            self.test_19_00_click_save()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 21_00.確認MQTT觸發訊息
    def test_21_00_check_trigger_msg(self):
        """確認MQTT觸發訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                node = at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "On"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 150)
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
                tf.catch_exc(f"確認SWITCH_BINARY_REPORT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def reset():
            self.test_11_00_click_run_scene()
            self.test_12_00_get_curr_time()
            self.test_13_00_click_date_input()
            self.test_14_00_set_date()
            self.test_15_00_click_time_input()
            self.test_16_00_set_time()
            self.test_18_00_set_repeat()
            self.test_19_00_click_save()
            self.test_20_00_check_setting_msg()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 22_00.復原裝置動作
    def test_22_00_restore_action(self):
        """復原裝置動作"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(2)
                mq.msg_que = []
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                pub_msg = '{"EVENT":"ZW_SWITCH_BINARY_SET", "NODE_ID":%s, "ENDPOINT_ID":0, "SWITCH":"OFF", "TO_MS_UUID":"%s"}' %(node, uuid)
                result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", pub_msg)
                print(f"[INFO] 已傳送訊息:\n{pub_msg}")
                return result
            except Exception as err:
                tf.catch_exc(f"復原裝置動作時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                node = at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "Off"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 15)
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
                    return True
            except Exception as err:
                tf.catch_exc(f"確認SWITCH_BINARY_REPORT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        # if not success_flag: 
        #     tf.set_fail(self._testMethodName, True)
        assert success_flag

# 23_00.關閉彈窗
    def test_23_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 點擊 Finish
            try:
                cls_elem = '//*[@id="Scene_Setting_Modal"]/div/div[1]/div[3]'
                cls_btn = self.d.find_element(By.XPATH, cls_elem)
                cls_btn.click()
                print(f"[CLICK] Close")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                cls_elem = '//*[@id="Scene_Setting_Modal"]/div/div[1]/div[3]'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.XPATH, cls_elem)))
                print(f"[INFO] 彈窗消失")
                return True
            except Exception as err:
                tf.catch_exc(f"檢查彈窗消失時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            ""

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 24_00.重做08_01, 刪除測試用的Scene
    def test_24_00_redo_08_01(self):
        """重做08_01, 刪除測試用的Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_08_01_check_scene()
                print(f"[INFO] 已重做08_01")
                return True
            except Exception as err:
                tf.catch_exc(f"重做08_01時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# # 25_00.復原備份的Scene
#     def test_25_00_restore_scene(self):
#         """復原備份的Scene"""
#         # 如果前面測試失敗，就略過此測試
#         if tf.flag_test_fail:
#             self.skipTest(tf.fail_reason)
#         def action():
#             tf.output(f"[INOF] 正在復原測試前已刪除的Scene")
#             total = len(restore_msg)
#             while restore_msg:
#                 pub_msg = restore_msg[0]
#                 try:
#                     mq.msg_que = []
#                     result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", str(pub_msg))
#                     if result:
#                         kw = ["busy"]
#                         ack = tf.wait_mqtt_msg(kw, 2)
#                         if "timeout" in ack:
#                             tf.output()
#                             restore_msg.pop(0)
#                             # tf.output(f"[INFO]\t{int(total-len(restore_msg))/total*100} %")
#                             tf.wait_mqtt_info_loading()
#                             continue
#                         elif "busy" in ack:
#                             print(f"[FAIL] Gateway忙錄中, 10秒後重試")
#                             tf.output(f"[FAIL] Gateway忙錄中, 10秒後重試")
#                             time.sleep(10)
#                             continue
#                     else:
#                         print(f"[FAIL] 送出訊息失敗, 3秒後重試")
#                         tf.output(f"[FAIL] 送出訊息失敗, 3秒後重試")
#                         time.sleep(3)
#                 except Exception as err:
#                     tf.catch_exc(f"送出訊息時發生錯誤", 
#                                 self._testMethodName,  err)
#                     return False

#                 if not restore_msg:
#                     return True
#             else:
#                 print(f"[INFO] 完成")
#                 return True

#         success_flag = tf.execute(action)
#         # 測試失敗時設定旗標，並跳過後面的步驟
#         if not success_flag: 
#             tf.set_fail(self._testMethodName, True)
#         assert success_flag

# # _00.Template
#     def _(self):
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

    def get_minute_position(self, minute: str):
        """
        回傳類比時鐘裡minute分鐘的元素x, y座標
        """
        x = f"m{minute}x"
        y = f"m{minute}y"
        minute_position = {
            "m0x":           0,     "m0y":        -105, 
            "m1x": 10.97548864,     "m1y": -104.424799, 
            "m2x": 21.83072754,     "m2y":-102.7054981, 
            "m3x": 32.44678441,     "m3y":-99.86093421, 
            "m4x": 42.70734752,     "m4y":-95.92227305, 
            "m5x":        52.5,     "m5y": -90.9326674, 
            "m6x": 61.71745149,     "m6y":-84.94678441, 
            "m7x": 70.25871367,     "m7y":-78.03020668, 
            "m8x": 78.03020668,     "m8y":-70.25871367, 
            "m9x": 84.94678441,     "m9y":-61.71745149, 
            "m10x":  90.9326674,    "m10y":       -52.5, 
            "m11x": 95.92227305,    "m11y":-42.70734752, 
            "m12x": 99.86093421,    "m12y":-32.44678441, 
            "m13x": 102.7054981,    "m13y":-21.83072754, 
            "m14x":  104.424799,    "m14y":-10.97548864, 
            "m15x":         105,    "m15y":           0, 
            "m16x":  104.424799,    "m16y": 10.97548864, 
            "m17x": 102.7054981,    "m17y": 21.83072754, 
            "m18x": 99.86093421,    "m18y": 32.44678441, 
            "m19x": 95.92227305,    "m19y": 42.70734752, 
            "m20x":  90.9326674,    "m20y":        52.5, 
            "m21x": 84.94678441,    "m21y": 61.71745149, 
            "m22x": 78.03020668,    "m22y": 70.25871367,
            "m23x": 70.25871367,    "m23y": 78.03020668,
            "m24x": 61.71745149,    "m24y": 84.94678441,
            "m25x":        52.5,    "m25y":  90.9326674,
            "m26x": 42.70734752,    "m26y": 95.92227305,
            "m27x": 32.44678441,    "m27y": 99.86093421,
            "m28x": 21.83072754,    "m28y": 102.7054981,
            "m29x": 10.97548864,    "m29y":  104.424799,
            "m30x":           0,    "m30y":         105,
            "m31x":-10.97548864,    "m31y":  104.424799,
            "m32x":-21.83072754,    "m32y": 102.7054981,
            "m33x":-32.44678441,    "m33y": 99.86093421,
            "m34x":-42.70734752,    "m34y": 95.92227305,
            "m35x":       -52.5,    "m35y":  90.9326674,
            "m36x":-61.71745149,    "m36y": 84.94678441,
            "m37x":-70.25871367,    "m37y": 78.03020668,
            "m38x":-78.03020668,    "m38y": 70.25871367,
            "m39x":-84.94678441,    "m39y": 61.71745149,
            "m40x": -90.9326674,    "m40y":        52.5,
            "m41x":-95.92227305,    "m41y": 42.70734752,
            "m42x":-99.86093421,    "m42y": 32.44678441,
            "m43x":-102.7054981,    "m43y": 21.83072754,
            "m44x": -104.424799,    "m44y": 10.97548864,
            "m45x":        -105,    "m45y":           0,
            "m46x": -104.424799,    "m46y":-10.97548864,
            "m47x":-102.7054981,    "m47y":-21.83072754,
            "m48x":-99.86093421,    "m48y":-32.44678441,
            "m49x":-95.92227305,    "m49y":-42.70734752,
            "m50x": -90.9326674,    "m50y":       -52.5,
            "m51x":-84.94678441,    "m51y":-61.71745149,
            "m52x":-78.03020668,    "m52y":-70.25871367,
            "m53x":-70.25871367,    "m53y":-78.03020668,
            "m54x":-61.71745149,    "m54y":-84.94678441,
            "m55x":       -52.5,    "m55y": -90.9326674,
            "m56x":-42.70734752,    "m56y":-95.92227305,
            "m57x":-32.44678441,    "m57y":-99.86093421,
            "m58x":-21.83072754,    "m58y":-102.7054981,
            "m59x":-10.97548864,    "m59y": -104.424799
        }
        return minute_position[x], minute_position[y]



if __name__ == "__main__":
    tf.init_test(sce_03_run_scene_schdule)

