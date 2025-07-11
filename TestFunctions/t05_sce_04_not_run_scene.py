#==============================================================================
# 程式功能: 測試Not run scene功能
# 測試步驟: 
# 01_00.輸入帳號密碼/勾選Remember me並點擊登入
# 02_00.等待頁面載入完成
# 03_00.從System頁面取得Gateway資訊
# 04_00.點擊Z-Wave
# 05_00.等待內容載入完成
# 06_00.檢查必要裝置siren, plug
# 07_00.點擊Scene
# 08_00.重做02_00、05_00, 等待內容載入完成
# 08_01.檢查已存在的Scene
# 08_02.重做05_00, 等待內容載入完成
# 09_00.新增測試用的Scene
# 09_01.重做05_00, 等待內容載入完成
# 10_00.點擊Scene name
# 10_01.點擊Run Scene
# 10_02.取得顯示時間
# 10_03.關閉彈窗
# 11_00.點擊Not Run Scene
# 12_00.點擊Set Enable取消勾選
# 13_00.點擊Save
# 14_00.關閉彈窗
# 15_00.發送訊息關閉Plug
# 16_00.發送訊息關閉Siren
# 17_00.發送訊息開啟Plug
# 18_00.等待訊息確認Siren未觸發
# 19_00.重做11_00, 點擊Not Run Scene
# 19_01.點擊Set Enable勾選
# 20_00.點擊開始時間輸入框
# 21_00.設定開始時間
# 22_00.點擊結束時間輸入框
# 23_00.設定結束時間
# 24_00.重做13_00, 14_00, 點擊Save, 關閉彈窗
# 25_00.重做1500-1700, 發送訊息
# 26_00.等待訊息確認Siren未觸發
# 27_00.重做15_00, 發送訊息關閉Plug
# 28_00.重做11_00, 點擊Not Run Scene
# 29_00.重做22_00, 點擊開始時間輸入框
# 30_00.設定結束時間, 00:00-11:59
# 31_00.重做08_01, 刪除測試用的Scene
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
import MiniGateway.mqtt_lite as mq

class sce_04_not_run_scene(unittest.TestCase):
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

# 06_00.檢查必要裝置siren, plug
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
                        print(f"[INOF] Scene已刪除")
                        # 若有執行刪除Scene的動作, 則重整頁面後再檢查一次
                        flag = False
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

# 10_01.點擊Run Scene
    def test_10_01_click_run_scene(self):
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

# 10_02.取得顯示時間
    def test_10_02_get_curr_time(self):
        """取得顯示時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            global curr_time
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
                return True
            except Exception as err:
                tf.catch_exc(f"取得顯示時間時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()
            self.test_10_00_click_scene_name()
            self.test_10_01_click_run_scene()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 10_03.關閉彈窗
    def test_10_03_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                cls_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[1]/div'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, cls_elem)))
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
                cls_elem = '//*[@id="Scene_Scheduling_Modal"]'\
                    '/div/div[1]/div'
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

# 11_00.點擊Not Run Scene
    def test_11_00_click_not_run_scene(self):
        """點擊Run Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                # <svg>圖示無法互動
                # 能夠click的<div>元素尺吋660x0, 無法直接使用click()
                run_scene_elem = '//*[@id="Not_Run_Scene_Setting_Btn"]'
                run_scene = self.d.find_element(By.XPATH, run_scene_elem)
                self.d.execute_script("arguments[0].click();", run_scene)
                print(f"[CLICK] Not Run Scene")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Run Scene時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                
                sch_title_elem = '//*[@id="Scene_Scheduling_Not_Trigger_Modal"]'\
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

# 12_00.點擊Set Enable取消勾選
    def test_12_00_click_set_enable(self):
        """點擊Set Enable取消勾選"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                set_elem = '//*[@id="Scene_Scheduling_Not_Trigger_Modal"]'\
                    '/div/div[2]/div[1]/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, set_elem)))
                set_btn = self.d.find_element(By.XPATH, set_elem)
                set_btn.click()
                print(f"[CLICK] Set Enable")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Set Enable時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(0.5)
                set_elem = '//*[@id="Scene_Scheduling_Not_Trigger_Modal"]'\
                    '/div/div[2]/div[1]/input'
                set_btn = self.d.find_element(By.XPATH, set_elem)
                if set_btn.is_selected():
                    print(f"[FAIL] Set Enable未取消勾選")
                    return False
                print(f"[INFO] 已確認Set Enable取消勾選")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Set Enable時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.點擊Save
    def test_13_00_click_save(self):
        """點擊Save"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                save_elem = '//*[@id="Scene_Scheduling_Not_Trigger_Modal"]'\
                    '/div/div[3]/input'
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
                cls_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, cls_elem)))
                print(f"[INFO] 彈窗出現")
                return True
            except Exception as err:
                tf.catch_exc(f"確認彈窗時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            try:
                zoom_in = "document.body.style.zoom='0.9'"
                self.d.execute_script(zoom_in)
            except:
                pass

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.關閉彈窗
    def test_14_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
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
                cls_elem = 'sys-setting-confirm-modal-closeBtn'
                WebDriverWait(self.d, 5).until(
                    EC.invisibility_of_element((By.CLASS_NAME, cls_elem)))
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

# 15_00.發送訊息關閉Plug
    def test_15_00_turn_plug_off(self):
        """關閉Plug"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 直接Publish訊息來關閉, 若原本狀態為OFF
            # 則不會收到回復, 故只要Publish成功即可 
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                plug_off = '{"EVENT":"ZW_SWITCH_BINARY_SET", "NODE_ID":%s, "ENDPOINT_ID":0, "SWITCH":"OFF", "TO_MS_UUID":"%s"}'%(node, uuid)
                result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", plug_off)
                if not result:
                    print(f"[FAIL] 關閉Plug失敗")
                    return False
                print(f"[INFO] 已送出訊息: {plug_off}")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉Plug時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.發送訊息關閉Siren
    def test_16_00_turn_siren_off(self):
        """關閉Siren"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 直接Publish訊息來關閉, 若原本狀態為OFF
            # 則不會收到回復, 故只要Publish成功即可 
            try:
                time.sleep(1)   # 避免太快速publish
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                siren_off = '{"EVENT":"ZW_SWITCH_BINARY_SET", "NODE_ID":%s, "ENDPOINT_ID":0, "SWITCH":"OFF", "TO_MS_UUID":"%s"}'%(node, uuid)
                result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", siren_off)
                if not result:
                    print(f"[FAIL] 關閉Siren失敗")
                    return False
                print(f"[INFO] 已送出訊息: {siren_off}")
                return True
            except Exception as err:
                tf.catch_exc(f"關閉Siren時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 17_00.發送訊息開啟Plug
    def test_17_00_turn_plug_on(self):
        """開啟Plug"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)   # 避免太快速publish
                mq.msg_que = []
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                plug_on = '{"EVENT":"ZW_SWITCH_BINARY_SET", "NODE_ID":%s, "ENDPOINT_ID":0, "SWITCH":"ON", "TO_MS_UUID":"%s"}'%(node, uuid)
                result = mq.pub_msg(tf.gw_ip, "USER_TO_MIDDLE", plug_on)
                if not result:
                    print(f"[FAIL] 開啟Plug失敗")
                    return False
                print(f"[INFO] 已送出訊息: {plug_on}")
                return True
            except Exception as err:
                tf.catch_exc(f"開啟Plug時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def check(info):
            try:
                node = at_dev_id[tf.plug]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "On"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 15)
                if "timeout" in msg:
                    print(f"[INFO] 超時, 未收到Plug On訊息")
                    return False
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[INFO] 已確認Plug On")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認Plug On訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 18_00.等待訊息確認Siren未觸發
    def test_18_00_check_siren_not_on(self):
        """確認Siren未觸發"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                node = at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "On"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 30)
                if "timeout" in msg:
                    print(f"[INFO] 超時, 未收到Siren On訊息")
                    print(f"[INFO] Siren未被Scene觸發")
                    return True
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[FAIL] Siren被觸發")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認SWITCH_BINARY_REPORT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
        def reset():
            self.test_15_00_turn_plug_off()
            self.test_17_00_turn_plug_on()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 19_00.重做11_00, 點擊Not Run Scene
    def test_19_00_redo_1100(self):
        """重做11_00, 點擊Not Run Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_11_00_click_not_run_scene()
                print(f"[INFO] 已重做11_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做11_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 19_01.點擊Set Enable勾選
    def test_19_01_click_set_enable(self):
        """點擊Set Enable勾選"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                set_elem = '//*[@id="Scene_Scheduling_Not_Trigger_Modal"]'\
                    '/div/div[2]/div[1]/input'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, set_elem)))
                set_btn = self.d.find_element(By.XPATH, set_elem)
                set_btn.click()
                print(f"[CLICK] Set Enable")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Set Enable時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(0.5)
                set_elem = '//*[@id="Scene_Scheduling_Not_Trigger_Modal"]'\
                    '/div/div[2]/div[1]/input'
                set_btn = self.d.find_element(By.XPATH, set_elem)
                if set_btn.is_selected():
                    print(f"[INFO] 已確認Set Enable勾選")
                    return True
                print(f"[FAIL] Set Enable未勾選")
                return False
            except Exception as err:
                tf.catch_exc(f"確認Set Enable時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 20_00.點擊開始時間輸入框
    def test_20_00_click_start_time_box(self):
        """點擊開始時間輸入框"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                st_box_elem = '//*[@id="time1"]'
                WebDriverWait(self.d, 10).until(
                    EC.element_to_be_clickable((By.XPATH, st_box_elem)))
                st_box = self.d.find_element(By.XPATH, st_box_elem)
                st_box.click()
                print(f"[CLICK] 開始時間")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊開始時間輸入框時發生錯誤", 
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

# 21_00.設定開始時間
    def test_21_00_set_start_time(self):
        """設定開始時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定 AM/PM
            try:
                set_time = curr_time + timedelta(hours=-3)
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
                set_time = curr_time + timedelta(hours=-3)
                time.sleep(1)
                time_elem = '//*[@id="time1"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_elem)))
                time_box = self.d.find_element(By.XPATH, time_elem)
                seted_t = time_box.get_property("value")
                chk_t = f"{set_time.strftime("%I")}:{set_time.strftime("%M")} "\
                    f"{set_time.strftime("%p")}"
                if seted_t != chk_t:
                    print(f"[FAIL] 設定的時間錯誤: {seted_t}")
                    return False
                print(f"[INFO] 已確認設定時間: {seted_t}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認設定時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_20_00_click_start_time_box()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 22_00.點擊結束時間輸入框
    def test_22_00_click_end_time_box(self):
        """點擊結束時間輸入框"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                st_box_elem = '//*[@id="time2"]'
                WebDriverWait(self.d, 10).until(
                    EC.element_to_be_clickable((By.XPATH, st_box_elem)))
                st_box = self.d.find_element(By.XPATH, st_box_elem)
                st_box.click()
                print(f"[CLICK] 結束時間")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊結束時間輸入框時發生錯誤", 
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

# 23_00.設定結束時間
    def test_23_00_set_end_time(self):
        """設定結束時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定 AM/PM
            try:
                set_time = curr_time + timedelta(hours=-2)
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
                set_time = curr_time + timedelta(hours=-2)
                time.sleep(1)
                time_elem = '//*[@id="time2"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_elem)))
                time_box = self.d.find_element(By.XPATH, time_elem)
                seted_t = time_box.get_property("value")
                chk_t = f"{set_time.strftime("%I")}:{set_time.strftime("%M")} "\
                    f"{set_time.strftime("%p")}"
                if seted_t != chk_t:
                    print(f"[FAIL] 設定的時間錯誤: {seted_t}")
                    return False
                print(f"[INFO] 已確認設定時間: {seted_t}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認設定時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_22_00_click_end_time_box()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 24_00.重做13_00, 14_00, 點擊Save, 關閉彈窗
    def test_24_00_redo_1300_1400(self):
        """重做13_00, 14_00, 點擊Save, 關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_13_00_click_save()
                self.test_14_00_close_pop()
                print(f"[INFO] 已重做13_00, 14_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做13_00, 14_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 25_00.重做1500-1700, 發送訊息
    def test_25_00_redo_1500_to_1800(self):
        """重做1500-1700, 確認Scene未觸發"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_15_00_turn_plug_off()
                self.test_16_00_turn_siren_off()
                self.test_17_00_turn_plug_on()
                print(f"[INFO] 已重做1500-1700")
                return True
            except Exception as err:
                tf.catch_exc(f"重做1500-1700時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 26_00.等待訊息確認Siren未觸發
    def test_26_00_check_siren_not_on(self):
        """確認Siren未觸發"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                node = at_dev_id[tf.siren]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           'CurrSts": "On"', f'"NodeID": "{node}"']
                msg = tf.wait_mqtt_msg(keyword, 30)
                if "timeout" in msg:
                    print(f"[INFO] 超時, 未收到Siren On訊息")
                    print(f"[INFO] Siren未被Scene觸發")
                    return True
                elif "busy" in msg:
                    print(f"[FAIL] Gateway忙錄中, 10秒後重試")
                    time.sleep(10)
                    return False
                else:
                    print(msg)
                    print(f"[FAIL] Siren被觸發")
                    return True
            except Exception as err:
                tf.catch_exc(f"確認SWITCH_BINARY_REPORT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False
        def reset():
            self.test_15_00_turn_plug_off()
            self.test_17_00_turn_plug_on()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 27_00.重做15_00, 發送訊息關閉Plug
    def test_27_00_redo_1500(self):
        """重做15_00, 發送訊息關閉Plug"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_15_00_turn_plug_off()
                print(f"[INFO] 已重做15_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做15_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 28_00.重做11_00, 點擊Not Run Scene
    def test_28_00_redo_1100(self):
        """重做11_00, 點擊Not Run Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_11_00_click_not_run_scene()
                print(f"[INFO] 已重做11_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做11_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag
# Work around:
# Redmine #1458: Scene刪除再重建後，Not Run Scene時間區間仍保留舊資料
# 29_00.重做22_00, 點擊開始時間輸入框
    def test_29_00_redo_2200(self):
        """重做22_00, 點擊開始時間輸入框"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_22_00_click_end_time_box()
                print(f"[INFO] 已重做22_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做22_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 29_01.設定開始時間: 12:00 AM
    def test_29_01_restore_start_time(self):
        """設定開始時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定 AM
            try:
                set_time = curr_time + timedelta(hours=-3)
                time.sleep(0.5)
                pick_elem = '//*[contains(@class, "modal timepicker-modal open")]'
                time_pick = self.d.find_element(By.XPATH, pick_elem)
                picker_id = time_pick.get_attribute("id")
                am_elem = f'//*[@id="{picker_id}"]'\
                    '/div/div[1]/div/div[2]/div/div[1]'
                self.d.find_element(By.XPATH, am_elem).click()
                print(f"[CLICK] AM")
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
                    if hour.text == "12":
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
                position = self.get_minute_position(str(0))
                # 移動到此座標後點click()
                action.move_by_offset(position[0], position[1])
                action.click()
                action.perform()
                print(f"[CLICK] Minute: {str(0)}")
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
                time_elem = '//*[@id="time1"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_elem)))
                time_box = self.d.find_element(By.XPATH, time_elem)
                seted_t = time_box.get_property("value")
                chk_t = "12:00 AM"
                if seted_t != chk_t:
                    print(f"[FAIL] 設定的時間錯誤: {seted_t}")
                    return False
                print(f"[INFO] 已確認設定時間: {seted_t}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認設定時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_20_00_click_start_time_box()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 30_00.重做23_00, 點擊結束時間輸入框
    def test_30_00_redo_2300(self):
        """重做23_00, 點擊結束時間輸入框"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_23_00_set_end_time()
                print(f"[INFO] 已重做23_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做23_00時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 30_01.設定結束時間: 11:59 PM
    def test_30_01_restore_end_time(self):
        """設定結束時間"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 設定 PM
            try:
                time.sleep(0.5)
                pick_elem = '//*[contains(@class, "modal timepicker-modal open")]'
                time_pick = self.d.find_element(By.XPATH, pick_elem)
                picker_id = time_pick.get_attribute("id")
                pm_elem = f'//*[@id="{picker_id}"]'\
                    '/div/div[1]/div/div[2]/div/div[2]'
                self.d.find_element(By.XPATH, pm_elem).click()
                print(f"[CLICK] PM")
            except Exception as err:
                tf.catch_exc(f"設定PM時發生錯誤", 
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
                    if hour.text == "11":
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
                position = self.get_minute_position(str(59))
                # 移動到此座標後點click()
                action.move_by_offset(position[0], position[1])
                action.click()
                action.perform()
                print(f"[CLICK] Minute: {str(59)}")
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
                time_elem = '//*[@id="time2"]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_elem)))
                time_box = self.d.find_element(By.XPATH, time_elem)
                seted_t = time_box.get_property("value")
                chk_t = f"11:59 PM"
                if seted_t != chk_t:
                    print(f"[FAIL] 設定的時間錯誤: {seted_t}")
                    return False
                print(f"[INFO] 已確認設定時間: {seted_t}")
                return True
            except Exception as err:
                tf.catch_exc(f"確認設定時間時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.test_22_00_click_end_time_box()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 31_00.重做24_00,08_01, 儲存並刪除測試用的Scene
    def test_31_00_redo_0801(self):
        """重做08_01, 刪除測試用的Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_24_00_redo_1300_1400()
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
    tf.init_test(sce_04_not_run_scene)

 