#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2022/9/16'

import re
import os
import yaml
import psutil
from time import sleep
from helper.utils import Logger
from helper.monitor import Monitor


def main():
    logger = Logger("base_monitor")
    monitor = None
    config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            email_conf = conf['email']

            monitor = Monitor(logger, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])

            disk = psutil.disk_partitions()
            for dev in disk:
                s = re.match(r'/dev/(.*)', dev.device)
                disk_name = s.group(1)
                disk_mounted = dev.mountpoint
                disk_use = psutil.disk_usage(dev.mountpoint)
                disk_total = round(float(disk_use.total) / 1024 / 1024 / 1024, 2)
                disk_used = round(float(disk_use.used) / 1024 / 1024 / 1024, 2)
                disk_free = round(float(disk_use.free) / 1024 / 1024 / 1024, 2)
                disk_pct = round(disk_use.percent, 2)
                if disk_pct >= 80:
                    disk_msg = f"磁盘分区使用率超过 80%\n分区名：{disk_name}\n挂载点：{disk_mounted}\n磁盘使用率：{disk_pct}\n" \
                               f"磁盘总计：{disk_total}GB\n磁盘已使用：{disk_used}GB\n磁盘空闲：{disk_free}GB\n"
                    monitor.send_email(disk_msg)

    except Exception as e:
        logger.error(f"基础监控异常: {e}.")
        if monitor:
            monitor.send_email(f"基础监控异常: {e}.")


if __name__ == '__main__':
    main()
