#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2024/3/29'

import os
import yaml
import time
from helper.utils import Logger
from helper.monitor import Monitor


def main():
    logger = Logger("crash_monitor")
    monitor = None
    config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            email_conf = conf['email']

            monitor = Monitor(logger, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])

            directory_to_watch = '/var/log/ef/coredump'  # 监控core-dump文件的目录
            if not os.path.exists(directory_to_watch):
                directory_to_watch = '/var/log/coredump'
            file_prefix = 'core'  # core-dump文件的前缀
            files = set(os.listdir(directory_to_watch))
            for file in files:
                if file.startswith(file_prefix):
                    monitor.send_email(
                        f"系统产生core-dump文件, 请及时查看!\nDetected new file: {os.path.join(directory_to_watch, file)}")
                    break

    except Exception as e:
        logger.error(f"系统崩溃监控异常: {e}.")
        if monitor:
            monitor.send_email(f"系统崩溃监控异常: {e}.")


if __name__ == '__main__':
    main()
