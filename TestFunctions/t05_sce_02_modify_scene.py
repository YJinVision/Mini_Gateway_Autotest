#==============================================================================
# 程式功能: 測試修改Scene Name、Trigger、Task
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
# 09_00.新增測試用的Scene
# 10_00.點擊Scene
# 11_00.點擊名稱修改Edit
# 12_00.修改圖示及名稱
# 13_00.點擊Trigger修改Edit
# 14_00.修改Trigger
# 15_00.點擊Task修改Edit
# 16_00.修改Task
# 16_01.關閉彈窗
# 17_00.重做04_00, 05_00, 06_00, 跳至z-wave頁面
# 18_00.點擊plug
# 19_00.確認Toggle狀態
# 20_00.關閉彈窗
# 21_00.點擊siren
# 22_00.確認Toggle狀態
# 23_00.點擊Toggle switch
# 24_00.確認Switch MQTT訊息
# 25_00.重做22_00, 23_00, siren off
# 26_00.關閉彈窗
# 27_00.重做18_00, 19_00, 確認plug state
# 28_00.點擊Toggle switch, plug off
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

class sce_02_modify_scene(unittest.TestCase):
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
                        return True
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

# 10_00.點擊Scene
    def test_10_00_click_scene(self):
        """點擊Scene"""
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

# 11_00.點擊名稱修改Edit
    def test_11_00_click_name_edit(self):
        """點擊名稱修改Edit"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                edit_elem = '//*[@id="Scene_Setting_Modal"]'\
                    '/div/div[2]/div[1]/input[2]'
                edit_btn = self.d.find_element(By.XPATH, edit_elem)
                edit_btn.click()
                print(f"[CLICK] Name Edit")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊名稱修改Edit時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                name_elem = '//*[@id="scene-modal-body"]/input'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, name_elem)))
                print(f"[INFO] 已確認名稱修改頁面")
                return True
            except Exception as err:
                tf.catch_exc(f"確認名稱修改頁面時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 12_00.修改圖示及名稱
    def test_12_00_modify_icon_and_name(self):
        """修改圖示及名稱"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 選擇圖示
            try:
                icon_elem = '//*[@id="scene-modal-body"]'\
                    '/div/table/tbody/tr[1]/td[4]/div/label'
                WebDriverWait(self.d, 10).until(
                    EC.element_to_be_clickable((By.XPATH, icon_elem)))
                icon = self.d.find_element(By.XPATH, icon_elem)
                icon.click()
                print(f"[CLICK] Icon")
            except Exception as err:
                tf.catch_exc(f"選擇圖示時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 設定名稱
            try:
                name_elem = '//*[@id="scene-modal-body"]/input'
                name_box = self.d.find_element(By.XPATH, name_elem)
                name_box.clear()
                try:
                    # 當name box內有值並執行clear()會觸發名稱檢查
                    cls_elem = 'sys-setting-confirm-modal-closeBtn'
                    WebDriverWait(self.d, 1).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, cls_elem)))
                    self.d.find_element(By.CLASS_NAME, cls_elem).click()
                except:
                    pass
                name_box.send_keys("SirenOn-PlugOn")
                print(f"[SENDKEY] Scene名稱: SirenOn-PlugOn")
                time.sleep(1)
                # 點擊icon來fouse off來觸發名稱檢查
                # 確認名稱可用後Next按鍵才能clickable
                icon.click()
            except Exception as err:
                tf.catch_exc(f"修改名稱時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 點擊 Next
            try:
                next_elem = '//*[@id="Scene_AddScene_Modal"]'\
                    '/div/div[3]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, next_elem)))
                next_btn = self.d.find_element(By.XPATH, next_elem)
                next_btn.click()
                print(f"[CLICK] Next")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Next時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            global scene_name
            try:
                time.sleep(1)
                name_elem = '//*[@id="Scene_Setting_Modal"]'\
                    '/div/div[2]/div[1]/input[1]'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, name_elem)))
                name_box = self.d.find_element(By.XPATH, name_elem)
                if name_box.get_property("value") != "SirenOn-PlugOn":
                    print(f"[FAIL] 修改名稱失敗")
                    return False
                print(f"[INFO] 已確修改名稱")
                scene_name = "SirenOn-PlugOn"
                return True
            except Exception as err:
                tf.catch_exc(f"確名稱時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()
            self.test_10_00_click_scene()
            self.test_11_00_click_name_edit()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 13_00.點擊Trigger修改Edit
    def test_13_00_click_trigger_edit(self):
        """點擊Trigger修改Edit"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                edit_elem = '//*[@id="Scene_Setting_Modal"]'\
                    '/div/div[2]/div[2]/input'
                edit_btn = self.d.find_element(By.XPATH, edit_elem)
                edit_btn.click()
                print(f"[CLICK] Trigger Edit")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Trigger修改Edit時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                tri_elem = '//*[@id="scene-modal-body"]/table'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, tri_elem)))
                print(f"[INFO] 已確認Trigger修改頁面")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Trigger修改頁面時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 14_00.修改Trigger
    def test_14_00_modify_trigger(self):
        """修改Trigger"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():            
            # 選擇location
            try:
                locat_elem = '//*[@id="scene-modal-body"]'\
                    '/table/tbody/tr[1]/td[1]/div'
                locat = self.d.find_element(By.XPATH, locat_elem)
                locat.click()
                time.sleep(0.5) # 等待下拉選單展開
                ul_elem = '//*[@id="scene-modal-body"]'\
                    '/table/tbody/tr[1]/td[1]/div/div/ul'
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, 'li')
                flag = False
                for i in li:
                    if i.text == at_dev_room[tf.siren]:
                        i.click()
                        print(f"[CLICK] Location: {i.text}")
                        time.sleep(0.5) # 等待下拉選單收合
                        flag = True
                        break
                if not flag:
                    print(f"[FAIL] 下拉選單中沒有location '{at_dev_room[tf.siren]}'")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Trigger-location時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 選擇device name
            try:
                name_elem = '//*[@id="scene-modal-body"]'\
                    '/table/tbody/tr[1]/td[3]/div'
                name = self.d.find_element(By.XPATH, name_elem)
                name.click()
                time.sleep(0.5) # 等待下拉選單展開
                ul_elem = '//*[@id="scene-modal-body"]'\
                    '/table/tbody/tr[1]/td[3]/div/div/ul'
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, 'li')
                flag = False
                for i in li:
                    if i.text == at_dev_name[tf.siren]:
                        i.click()
                        print(f"[CLICK] device name: {i.text}")
                        time.sleep(0.5) # 等待下拉選單收合
                        flag = True
                        break
                if not flag:
                    print(f"[FAIL] 下拉選單中沒有device name '{at_dev_name[tf.siren]}'")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Trigger-device name時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 選擇event
            try:
                event_elem = '//*[@id="scene-modal-body"]'\
                    '/table/tbody/tr[1]/td[5]/div'
                event = self.d.find_element(By.XPATH, event_elem)
                event.click()
                time.sleep(0.5) # 等待下拉選單展開
                ul_elem = '//*[@id="scene-modal-body"]'\
                    '/table/tbody/tr[1]/td[5]/div/div/ul'
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, 'li')
                flag = False
                for i in li:
                    if i.text == "Binary switch on":
                        i.click()
                        print(f"[CLICK] event: {i.text}")
                        time.sleep(0.5) # 等待下拉選單收合
                        flag = True
                        break
                if not flag:
                    print(f"[FAIL] 下拉選單中沒有event: 'Binary switch on'")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Trigger-event時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 點擊 Save
            try:
                save_elem = '//*[@id="Scene_AddScene_Modal"]/div/div[3]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, save_elem)))
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
                time.sleep(1)
                trigger = {}
                trigger["Room"] = self.d.find_element(
                    By.XPATH, '//*[@id="Scene_Setting_Modal"]'\
                        '/div/div[2]/div[2]/table/tbody/tr/td[1]/span')
                trigger["Device"] = self.d.find_element(
                    By.XPATH, '//*[@id="Scene_Setting_Modal"]'\
                        '/div/div[2]/div[2]/table/tbody/tr/td[3]/span')
                trigger["Event"] = self.d.find_element(
                    By.XPATH, '//*[@id="Scene_Setting_Modal"]'\
                        '/div/div[2]/div[2]/table/tbody/tr/td[5]/span')
                # 檢查Trigger
                flag_tr = True
                if trigger["Room"].text == at_dev_room[tf.siren]:
                    print(f"[INFO] Trigger-location正確")
                else:
                    print(f"[FAIL] Trigger-location錯誤: {trigger["Room"].text}")
                    flag_tr = False
                if trigger["Device"].get_attribute("data-value") == at_dev_name[tf.siren]:
                    print(f"[INFO] Trigger-device name正確")
                else:
                    print(f"[FAIL] Trigger-device name錯誤: {trigger["Device"].text}")
                    flag_tr = False
                if trigger["Event"].get_attribute("data-value") == 'Binary switch on':
                    print(f"[INFO] Trigger-event正確")
                else:
                    print(f"[FAIL] Trigger-event錯誤: {trigger["Event"].text}")
                    flag_tr = False
                return flag_tr
            except Exception as err:
                tf.catch_exc(f"檢查Trigger時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()
            self.test_10_00_click_scene()
            self.test_13_00_click_trigger_edit()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 15_00.點擊Task修改Edit
    def test_15_00_click_task_edit(self):
        """點擊Task修改Edit"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                edit_elem = '//*[@id="Scene_Setting_Modal"]'\
                    '/div/div[2]/div[3]/input'
                edit_btn = self.d.find_element(By.XPATH, edit_elem)
                edit_btn.click()
                print(f"[CLICK] Task Edit")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Task修改Edit時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                task_elem = '//*[@id="task_sortable"]/tbody'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, task_elem)))
                print(f"[INFO] 已確認Task修改頁面")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Task修改頁面時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action, check)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_00.修改Task
    def test_16_00_modify_task(self):
        """修改Task"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            # 選擇location
            try:
                locat_elem = '//*[@id="task_sortable"]'\
                    '/tbody/tr[1]/td[1]/div/div'
                locat = self.d.find_element(By.XPATH, locat_elem)
                locat.click()
                time.sleep(0.5) # 等待下拉選單展開
                ul_elem = '//*[@id="task_sortable"]'\
                    '/tbody/tr[1]/td[1]/div/div/ul'
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, 'li')
                flag = False
                for i in li:
                    if i.text == at_dev_room[tf.plug]:
                        i.click()
                        print(f"[CLICK] Location: {i.text}")
                        time.sleep(0.5) # 等待下拉選單收合
                        flag = True
                        break
                if not flag:
                    print(f"[FAIL] 下拉選單中沒有location '{at_dev_room[tf.plug]}'")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Task-location時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 選擇device name
            try:
                name_elem = '//*[@id="task_sortable"]'\
                    '/tbody/tr[1]/td[3]/div/div'
                name = self.d.find_element(By.XPATH, name_elem)
                name.click()
                time.sleep(0.5) # 等待下拉選單展開
                ul_elem = '//*[@id="task_sortable"]'\
                    '/tbody/tr[1]/td[3]/div/div/ul'
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, 'li')
                flag = False
                for i in li:
                    if i.text == at_dev_name[tf.plug]:
                        i.click()
                        print(f"[CLICK] device name: {i.text}")
                        time.sleep(0.5) # 等待下拉選單收合
                        flag = True
                        break
                if not flag:
                    print(f"[FAIL] 下拉選單中沒有device name '{at_dev_name[tf.plug]}'")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Task-device name時發生錯誤", 
                             self._testMethodName,  err)
                return False

            # 選擇event
            try:
                event_elem = '//*[@id="task_sortable"]'\
                    '/tbody/tr[1]/td[5]/div/div'
                event = self.d.find_element(By.XPATH, event_elem)
                event.click()
                time.sleep(0.5) # 等待下拉選單展開
                ul_elem = '//*[@id="task_sortable"]'\
                    '/tbody/tr[1]/td[5]/div/div/ul'
                ul = self.d.find_element(By.XPATH, ul_elem)
                li = ul.find_elements(By.TAG_NAME, 'li')
                flag = False
                for i in li:
                    if i.text == "Binary switch on":
                        i.click()
                        print(f"[CLICK] event: {i.text}")
                        time.sleep(0.5) # 等待下拉選單收合
                        flag = True
                        break
                if not flag:
                    print(f"[FAIL] 下拉選單中沒有event: 'Binary switch on'")
                    return False
            except Exception as err:
                tf.catch_exc(f"設定Task-event時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
            # 點擊 Save
            try:
                save_elem = '//*[@id="Scene_AddScene_Modal"]'\
                    '/div/div[3]/input[2]'
                WebDriverWait(self.d, 5).until(
                    EC.element_to_be_clickable((By.XPATH, save_elem)))
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
                task = {}
                task["Room"] = self.d.find_element(
                    By.XPATH, '//*[@id="Scene_Setting_Modal"]'\
                        '/div/div[2]/div[3]/table/tbody/tr[2]/td[1]/span')
                task["Device"] = self.d.find_element(
                    By.XPATH, '//*[@id="Scene_Setting_Modal"]'\
                        '/div/div[2]/div[3]/table/tbody/tr[2]/td[3]/span')
                task["Event"] = self.d.find_element(
                    By.XPATH, '//*[@id="Scene_Setting_Modal"]'\
                        '/div/div[2]/div[3]/table/tbody/tr[2]/td[5]/span')
                # 檢查Task
                flag_ta = True
                if task["Room"].text == at_dev_room[tf.plug]:
                    print(f"[INFO] Task-location正確")
                else:
                    print(f"[FAIL] Task-location錯誤: {task["Room"].text}")
                    flag_ta = False
                if task["Device"].get_attribute("data-value") == at_dev_name[tf.plug]:
                    print(f"[INFO] Task-device name正確")
                else:
                    print(f"[FAIL] Task-device name錯誤: {task["Device"].text}")
                    flag_ta = False
                if task["Event"].get_attribute("data-value") == 'Binary switch on':
                    print(f"[INFO] Task-event正確")
                else:
                    print(f"[FAIL] Task-event錯誤: {task["Event"].text}")
                    flag_ta = False
                return flag_ta
            except Exception as err:
                tf.catch_exc(f"確認設定Task時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        def reset():
            self.d.refresh()
            self.test_02_00_wait_page_loading()
            self.test_05_00_wait_content_loading()
            self.test_10_00_click_scene()
            self.test_15_00_click_task_edit()

        success_flag = tf.execute(action, check, reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 16_01.關閉彈窗
    def test_16_01_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                cls_elem = '//*[@id="Scene_Setting_Modal"]/div/div[1]/div[3]/span'
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
                cls_elem = '//*[@id="Scene_Setting_Modal"]/div/div[1]/div[3]/span'
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

# 17_00.重做04_00, 05_00, 06_00, 跳至z-wave頁面
    def test_17_00_redo_0400_0500_0600(self):
        """重做04_00, 05_00, 06_00, 跳至z-wave頁面"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_04_00_click_zw()
                self.test_05_00_wait_content_loading()
                self.test_06_00_check_device_need()
                print(f"[INFO] 已重做04_00, 05_00, 06_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做04_00, 05_00, 06_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 18_00.點擊plug
    def test_18_00_click_plug(self):
        """點擊siren"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                plug_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_name"]'
                plug = self.d.find_element(By.XPATH, plug_elem)
                plug.click()
                print(f"[CLICK] {at_dev_name[tf.plug]}")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊plug時發生錯誤", 
                             self._testMethodName,  err)
                return False
        
        def check(info):
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
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

# 19_00.確認Toggle狀態
    def test_19_00_check_toggle_stat(self):
        """確認Toggle狀態"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, status_elem)))
                status = self.d.find_element(By.XPATH, status_elem)
                # 從toggle的class判斷目前開關狀態(它不能click): 
                # on: class="toggle-btn active"
                # off: class="toggle-btn"
                toggle_elem = './/*[starts-with(@class, "toggle-btn")]'
                toggle = status.find_element(By.XPATH, toggle_elem)
                if "active" in toggle.get_attribute("class"):
                    print(f"[INFO] 目前plug為On")
                    # 若目前plug為On, 需先將它Off
                    status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                        f'_Status_Tb"]/div/div/div'
                    status = self.d.find_element(By.XPATH, status_elem)
                    circle_elem = 'inner-circle'
                    circle = status.find_element(By.CLASS_NAME, circle_elem)
                    circle.click()
                    print(f"[CLICK] Toggle")
                else:
                    print(f"[INFO] 目前plug為Off")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Toggle狀態時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 20_00.關閉彈窗
    def test_20_00_close_pop(self):
        """關閉彈窗"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
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
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
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

# 21_00.點擊siren
    def test_21_00_click_siren(self):
        """點擊siren"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                siren_elem = f'//*[@id="All_dev_tb_{uuid}_{node}_name"]'
                siren = self.d.find_element(By.XPATH, siren_elem)
                siren.click()
                print(f"[CLICK] {at_dev_name[tf.siren]}")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊siren時發生錯誤", 
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

# 22_00.確認Toggle狀態
    def test_22_00_check_toggle_stat(self):
        """確認Toggle狀態"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                time.sleep(1)
                global toggle_stat
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                WebDriverWait(self.d, 5).until(
                    EC.presence_of_element_located((By.XPATH, status_elem)))
                status = self.d.find_element(By.XPATH, status_elem)
                # 從toggle的class判斷目前開關狀態(它不能click): 
                # on: class="toggle-btn active"
                # off: class="toggle-btn"
                toggle_elem = './/*[starts-with(@class, "toggle-btn")]'
                toggle = status.find_element(By.XPATH, toggle_elem)
                if "active" in toggle.get_attribute("class"):
                    toggle_stat = True
                    print(f"[INFO] 目前siren為On")
                    # 若目前siren為On, 需先將它Off
                    status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                        f'_Status_Tb"]/div/div/div'
                    status = self.d.find_element(By.XPATH, status_elem)
                    circle_elem = 'inner-circle'
                    circle = status.find_element(By.CLASS_NAME, circle_elem)
                    circle.click()
                    print(f"[CLICK] Toggle")
                else:
                    toggle_stat = False
                    print(f"[INFO] 目前siren為Off")
                return True
            except Exception as err:
                tf.catch_exc(f"確認Toggle狀態時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 23_00.點擊Toggle switch
    def test_23_00_click_toggle_switch(self):
        """點擊Toggle switch"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.siren], at_dev_id[tf.siren]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                status = self.d.find_element(By.XPATH, status_elem)
                mq.msg_que = []
                # # 從區塊中找到toggle裡的小圓球(它才能被click)
                circle_elem = 'inner-circle'
                circle = status.find_element(By.CLASS_NAME, circle_elem)
                circle.click()
                print(f"[CLICK] Toggle switch")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Toggle switch時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 24_00.確認Switch MQTT訊息
    def test_24_00_check_switch_on_mqtt_msg(self):
        """確認Switch MQTT訊息"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                keyword = ['"ZwCmd": "SWITCH_BINARY_REPORT"', 
                           f'"NodeID": "{node}"']
                
                msg = tf.wait_mqtt_msg(keyword)
                if "timeout" in msg:
                    print(f"[FAIL] 超時, 未收到Switch On/Off訊息")
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
                tf.catch_exc(f"確認Switch MQTT訊息時發生錯誤", 
                             self._testMethodName,  err)
                return False

        def reset():
            self.test_22_00_check_toggle_stat()
            self.test_23_00_click_toggle_switch()

        success_flag = tf.execute(action, reset=reset)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 25_00.重做22_00, 23_00, siren off
    def test_25_00_redo_2200_2300(self):
        """重做22_00, 23_00"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_22_00_check_toggle_stat()
                self.test_23_00_click_toggle_switch()
                print(f"[INFO] 已重做22_00, 23_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做22_00, 23_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 26_00.關閉彈窗
    def test_26_00_close_pop(self):
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

# 27_00.重做18_00, 19_00, 確認plug state
    def test_27_00_redo_2200_2300(self):
        """重做18_00, 19_00, 確認plug state"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_18_00_click_plug()
                self.test_19_00_check_toggle_stat()
                print(f"[INFO] 已重做18_00, 19_00")
                return True
            except Exception as err:
                tf.catch_exc(f"重做18_00, 19_00時發生錯誤", 
                             self._testMethodName,  err)
                return False
            
        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 28_00.點擊Toggle switch, plug off
    def test_28_00_click_toggle_switch(self):
        """點擊Toggle switch, plug off"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                uuid, node = at_dev_uuid[tf.plug], at_dev_id[tf.plug]
                # 先定位到status bar中toggle的所在區塊
                status_elem = f'//*[@id="Zw_Setting_{uuid}_{node}'\
                    f'_Status_Tb"]/div/div/div'
                status = self.d.find_element(By.XPATH, status_elem)
                mq.msg_que = []
                # # 從區塊中找到toggle裡的小圓球(它才能被click)
                circle_elem = 'inner-circle'
                circle = status.find_element(By.CLASS_NAME, circle_elem)
                circle.click()
                print(f"[CLICK] Toggle switch")
                return True
            except Exception as err:
                tf.catch_exc(f"點擊Toggle switch時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

# 29_00.重做26_00, 07_00-08_01, 刪除已測試的Scene
    def test_29_00_redo_2600_0700_to_0801(self):
        """重做26_00, 07_00-08_01, 刪除已測試的Scene"""
        # 如果前面測試失敗，就略過此測試
        if tf.flag_test_fail:
            self.skipTest(tf.fail_reason)
        def action():
            try:
                self.test_20_00_close_pop()
                self.test_07_00_click_scene()
                self.test_08_00_redo_0200_0500()
                self.test_08_01_check_scene()
                print(f"[INFO] 已重做26_00, 07_00-08_01")
                return True
            except Exception as err:
                tf.catch_exc(f"重做26_00, 07_00-08_01時發生錯誤", 
                             self._testMethodName,  err)
                return False

        success_flag = tf.execute(action)
        # 測試失敗時設定旗標，並跳過後面的步驟
        if not success_flag: 
            tf.set_fail(self._testMethodName, True)
        assert success_flag

if __name__ == "__main__":
    tf.init_test(sce_02_modify_scene)

