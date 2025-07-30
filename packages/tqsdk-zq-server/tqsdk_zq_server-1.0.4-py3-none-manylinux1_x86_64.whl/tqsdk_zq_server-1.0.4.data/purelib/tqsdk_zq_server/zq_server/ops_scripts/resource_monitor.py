import subprocess
import psutil
import os
import time
import yaml
import threading

from datetime import datetime, timedelta, time as dtime
from helper.monitor import Monitor
from helper.utils import Logger

logger = Logger("resource_monitor")
last_send_time = datetime.now() - timedelta(seconds=90)

cpu_alert_count = 0  # 用于记录连续超过CPU阈值的次数
memory_alert_count = 0  # 用于记录连续超过内存阈值的次数
alert_threshold = 10  # 连续触发报警的阈值次数

def send_alert_email(message):
    monitor = None
    config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            email_conf = conf['email']

            monitor = Monitor(logger, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])
            monitor.send_email(message)

    except Exception as e:
        logger.error(f"系统资源占用检测异常: {e}.")
        if monitor:
            monitor.send_email(f"系统资源占用检测异常: {e}.")


def find_pid_by_name(process_name):
    """查找并返回第一个与给定名称匹配的进程的PID。"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None


def get_cpu_and_memory_usage(pid):
    """使用top命令来获取指定PID进程的CPU和内存使用情况，并记录日志。"""
    if pid is None:
        logger.error("No PID provided. Skipping monitoring cycle.")
        return
    try:
        process = subprocess.Popen(['top', '-b', '-n', '1', '-p', str(pid)], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        out, err = process.communicate()
        global last_send_time, cpu_alert_count, memory_alert_count
        if process.returncode == 0:
            for line in out.splitlines():
                if str(pid) in line:
                    parts = line.split()
                    cpu_usage = float(parts[8])  # CPU使用率
                    memory_usage_kb = float(parts[5])  # 内存使用量（KB）
                    memory_usage_gb = round(memory_usage_kb / (1024 ** 2), 2)  # 转换为GB
                    memory_percent = float(parts[9])

                    info_message = f"PID {pid}: CPU {cpu_usage}%, Memory {memory_percent}% ({memory_usage_gb}GB)"
                    logger.info(info_message)
                    if cpu_usage > 80:
                        cpu_alert_count += 1
                        logger.warning(f"High CPU usage detected ({cpu_alert_count}/{alert_threshold}): {info_message}")
                    else:
                        cpu_alert_count = 0  # 重置计数器

                    if memory_percent > 80:  # 设置内存使用警告阈值
                        memory_alert_count += 1
                        logger.warning(
                            f"High memory usage detected ({memory_alert_count}/{alert_threshold}): {info_message}")
                    else:
                        memory_alert_count = 0  # 重置计数器

                    if (cpu_alert_count >= alert_threshold or memory_alert_count >= alert_threshold) and (
                            datetime.now() - last_send_time).total_seconds() > 120:
                        message = f"CPU or Memory usage alert (zq_server): {info_message},cpu_alert_count:{cpu_alert_count},memory_alert_count:{memory_alert_count}\n"
                        send_alert_email(message)
                        last_send_time = datetime.now()
                    break
        else:
            logger.error(f"Error running top: {err}")
    except Exception as e:
        logger.error(f"Failed to execute top command: {e}")


def monitor_process(process_name, interval):
    """定期监控给定进程的CPU和内存使用情况。"""
    while True:
        current_time = datetime.now().time()
        if dtime(19, 29) <= current_time < dtime(19, 30):
            logger.info("Closing script for daily restart.")
            os._exit(0)
        pid = find_pid_by_name(process_name)
        if pid:
            get_cpu_and_memory_usage(pid)
        else:
            logger.error(f"No process found with name {process_name}")
        time.sleep(interval)  # 间隔时间，例如5秒


def start_monitoring():
    process_name = 'zq_server'
    interval = 5  # 每5秒检查一次
    threading.Thread(target=monitor_process, args=(process_name, interval)).start()


if __name__ == "__main__":
    start_monitoring()
