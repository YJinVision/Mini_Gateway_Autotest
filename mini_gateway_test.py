import os
import sys
import json
import time
import random
import threading
import subprocess
import configparser
from datetime import datetime, timedelta
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as ec
from BeautifulReport import BeautifulReport
if getattr(sys, 'frozen', None):    # 如果是exe文件
    curr_path = sys._MEIPASS    # 如果是pyinstaller打包的exe檔就要指令路徑sys._MEIPASS
else:
    # curr_path = os.path.dirname(__file__)
    curr_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(curr_path)
sys.path.append(main_path)
import MiniGateway.ihub_web_test_function as tf
import mqtt_lite as mq
import udp_tester as udp

def main():
    # 取得測試內容
    test_suite, test_topics = tf.set_test_pattern()

    tf.get_info()

    report_path, report_name = tf.set_report()
    # 開始MQTT線程
    mq.sub_loop(broker=tf.gw_ip, 
                topic=["MIDDLE_TO_USER", "USER_TO_MIDDLE"], 
                daemon_flag=True)
    # 測試開始
    result = BeautifulReport(test_suite)
    result.report(description="mini_gateway_test", 
                  filename=report_name, 
                  log_path=report_path)
    # 測試完成後自動開啟報告
    subprocess.run(f"start {report_path}\\{report_name}.html", 
                   capture_output=True, 
                   shell=True)

if __name__ == "__main__":
    try:
        start_time = datetime.now()
        print(start_time)
        main()
        print(f"耗時: {datetime.now() - start_time}")
        input()
    except Exception as err:
        print(err)
        input()