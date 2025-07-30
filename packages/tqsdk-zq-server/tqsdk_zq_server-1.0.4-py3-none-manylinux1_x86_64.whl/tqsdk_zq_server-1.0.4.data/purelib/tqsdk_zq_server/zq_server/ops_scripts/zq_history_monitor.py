#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import time
import yaml
import subprocess

from datetime import datetime, time as dtime
from helper.monitor import Monitor
from helper.utils import Logger

LOGGER = Logger("zq_history_monitor")
exit_flag = False


def send_alert_email(message):
    monitor = None
    config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            email_conf = conf['email']

            monitor = Monitor(LOGGER, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])
            monitor.send_email(message)

    except Exception as e:
        LOGGER.error(f"众期历史服务检测异常: {e}.")
        if monitor:
            monitor.send_email(f"众期历史服务检测异常: {e}.")

def check_shutdown_time():
    global exit_flag
    while not exit_flag:
        current_time = datetime.now().time()
        if current_time >= dtime(19, 29) and current_time < dtime(19, 30):
            LOGGER.info("Closing script for daily restart.")
            exit_flag = True
            os._exit(0)
        time.sleep(30)  # 每30秒检查一次

def check_service_status():
    global exit_flag
    while not exit_flag:
        result = subprocess.run(["systemctl", "status", "zq-history.service"], capture_output=True, text=True)
        if "Active: active (running)" not in result.stdout:
            LOGGER.info("zq-history.service is not running.")
            send_alert_email(f"警告: zq-history.service 未正常运行")
        time.sleep(120)


if __name__ == "__main__":
    # 启动定时检查关闭脚本的线程
    threading.Thread(target=check_shutdown_time).start()
    # 启动zq-history状态检查线程
    threading.Thread(target=check_service_status).start()
