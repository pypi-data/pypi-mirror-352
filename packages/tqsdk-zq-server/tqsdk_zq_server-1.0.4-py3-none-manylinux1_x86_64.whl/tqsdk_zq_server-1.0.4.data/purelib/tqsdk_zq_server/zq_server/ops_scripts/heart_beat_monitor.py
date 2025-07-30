#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import threading
import time
import yaml
import websocket

from datetime import datetime, timedelta, time as dtime
from helper.monitor import Monitor
from helper.utils import Logger

LOGGER = Logger("heart_beat_monitor")
last_heartbeat_time = datetime.now()
send_email_time = datetime.now()
last_heartbeat = ''
exit_flag = False
connected_once = False  # 标志是否成功连接过
retry_count = 0
max_retries = 3


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
        LOGGER.error(f"系统心跳检测异常: {e}.")
        if monitor:
            monitor.send_email(f"系统心跳检测异常: {e}.")


def check_heartbeat():
    global last_heartbeat_time, last_heartbeat, send_email_time, exit_flag
    while not exit_flag:
        current_time = datetime.now()
        if (current_time - last_heartbeat_time).total_seconds() > 35:
            LOGGER.info(f"Heartbeat log is too old. Last heartbeat: {last_heartbeat}")
            if (current_time - send_email_time).total_seconds() > 120:
                send_email_time = current_time
                LOGGER.info("Heartbeat log is too old. Sending alert email.")
                send_alert_email(f"心跳包检测超时, 上次心跳包: \n{last_heartbeat}")
            last_heartbeat_time = current_time  # 避免重复告警
        time.sleep(1)


def check_shutdown_time():
    global exit_flag
    while not exit_flag:
        current_time = datetime.now().time()
        if current_time >= dtime(19, 29) and current_time < dtime(19, 30):
            LOGGER.info("Closing script for daily restart.")
            exit_flag = True
            os._exit(0)
        time.sleep(30)  # 每30秒检查一次


def on_message(ws, message):
    global last_heartbeat_time, last_heartbeat
    LOGGER.info(f"recv message {message}")
    # 处理接收到的消息
    data = json.loads(message)

    if data.get('heart_beat') is not None:
        last_heartbeat_time = datetime.now()
        last_heartbeat = message
        LOGGER.info(f"Heartbeat detected at {last_heartbeat_time}")


def on_open(ws):
    global connected_once, retry_count  # 使用全局变量
    connected_once = True  # 标志成功连接
    retry_count = 0  # 重置重试计数

    def run(*args):
        # 发送心跳订阅请求
        ws.send(json.dumps({"aid": "heart_beat"}))

    # 使用线程来避免阻塞
    threading.Thread(target=run).start()
    # 启动心跳检查线程
    threading.Thread(target=check_heartbeat).start()


def on_close(ws, close_status_code, close_msg):
    global exit_flag, connected_once
    LOGGER.error(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")
    connected_once = False  # 重置连接状态以重新尝试连接


def on_error(ws, error):
    global exit_flag, connected_once
    LOGGER.error(f"WebSocket error: {error}")
    connected_once = False  # 重置连接状态以重新尝试连接


def start_websocket():
    websocket.enableTrace(False)
    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiI2ZTIzNmZjYi1mMTBiLTQyMmEtYTU4Mi03YmRkMDdkODk2ZTAiLCJleHAiOjE3MjEyODQ0OTYsIm5iZiI6MCwiaWF0IjoxNzIwNjc5Njk2LCJpc3MiOiJodHRwOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiYzliZjkyNTctMWEzZS00ZGJkLWFmZTgtMTBiNDk1OWFhN2Y3IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoic2hpbm55X3RxIiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiMDc0ODQ2MGUtZTNkYy00NWRhLWI3MTItMThmMGIwNGZjZjk3IiwiYWNyIjoiMSIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIiwiZ3JhbnRzIjp7ImZlYXR1cmVzIjpbImxtdF9pZHgiLCJmdXRyIiwiYWR2IiwidHFfbG10X2J0Il0sIm90Z19pZHMiOiIxMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEiLCJleHBpcnlfZGF0ZSI6IjAiLCJhY2NvdW50cyI6WyJjOWJmOTI1Ny0xYTNlLTRkYmQtYWZlOC0xMGI0OTU5YWE3ZjciLCIxMDAwMDQ4NjIiXX0sInNldG5hbWUiOnRydWUsIm1vYmlsZSI6IjE1NzM2MzM1MDUwIiwibW9iaWxlVmVyaWZpZWQiOiJ0cnVlIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2hhbnhpYW9sdSIsImlkIjoiYzliZjkyNTctMWEzZS00ZGJkLWFmZTgtMTBiNDk1OWFhN2Y3IiwidXNlcm5hbWUiOiJzaGFueGlhb2x1In0.lwHhGzwvKupDegjgCsKoUlSt9rOiARnKxwLelefVL8TBcynPrnal_ylvIha7iymhJEPhtJ8HJ5FHmZ944SIaiQ9-X_U8gpBwiuJbwIEG6u2sL14xYxXkPUujt4KQfeuPehz6Ni8Pr2QnIuNQSoR2vinOnNmTq3ePkxWNPrat3Ll5ILdcsNfDLQEYyWXg9qx1V9X2L5X0VOEqHwOBz1s77HxO-mF0klEBAeSOeCPVx0JtkHWakDxdDjU_A2PClIXFfIlBzeexlIrZjTS-6WN8CS5DHj6eb-UXuAJoR6AoTwYam94GQWydoZx58p8Y49bhpMvxvnVjM_MOl_4dWXoOmg"
    # 众期服务器地址
    ws_url = "ws://127.0.0.1:8765/trade"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error,
                                header=headers)
    ws.run_forever()


if __name__ == "__main__":
    # 启动定时检查关闭程序的线程
    threading.Thread(target=check_shutdown_time).start()

    last_log_time = datetime.now() - timedelta(minutes=2)
    while not exit_flag:
        if not connected_once:
            if retry_count < max_retries:
                try:
                    start_websocket()
                    retry_count += 1
                    time.sleep(10)  # 等待10秒后重试连接
                except Exception as e:
                    LOGGER.error(f"Failed to connect: {e}. Retrying {retry_count}/{max_retries}")
                    time.sleep(10)  # 等待10秒后重试连接
            else:
                current_time = datetime.now()
                if (current_time - last_log_time).total_seconds() > 120:  # 每两分钟发送一次告警邮件
                    LOGGER.error("Max retries reached. Sending alert email and retrying every 2 minutes.")
                    send_alert_email("心跳监控异常: WebSocket连接失败")
                    last_log_time = current_time
                time.sleep(10)  # 每10s重试连接
                start_websocket()
        else:
            time.sleep(1)  # 每秒检查一次连接状态
