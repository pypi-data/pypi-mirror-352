#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2023/1/10'

import os
import yaml
from datetime import time
from helper.utils import DateUtils, Logger
from helper.admin_api import AdminApi
from helper.monitor import Monitor

"""
将每天的交易时间分为了三个时间段
凌晨夜盘 (00:00 - 02:30)
白盘 (08:30 - 15:30)
晚夜盘 (20:30 - 23:59)

判断当前时间是否是交易时间，处于哪个时间段。
1.今天如果是节假日或者星期天，直接跳过三个时间段

2.今天是交易日，前一天不是交易日，那么跳过凌晨夜盘 (00:00 - 02:30) 
例：周一、 2023-5-4 周四为交易日，前一天是节假日。

3.今天是交易日，明天是节假日，那么跳过晚夜盘(20:30 - 23:59) 
例: 今天周五，明天是节假日

4.今天不是交易日，也不是节假日.
    4.1 前一天是交易日。那么只判断 凌晨夜盘 (00:00 - 02:30)
        例: 今天星期六，前一天是交易日
    4.2 前一天不是交易日。直接跳过三个时间段
        例: 今天星期六，前一天是节假日
"""


def is_in_time_period(now_time, periods):
    for start, end in periods:
        if start <= now_time <= end:
            return True
    return False


# 检查时间段函数
def check_time_period(date_util):
    # 获取今天,前一天,后一天的日期
    today = date_util.get_now().date()
    previous_day = date_util.get_previous_day()
    next_day = date_util.get_next_day()

    # 定义三个标准时间段
    periods = [
        (time(0, 0), time(2, 30)),
        (time(8, 30), time(15, 30)),
        (time(20, 30), time(23, 59, 59))
    ]

    if date_util.is_holidays(today) or today.weekday() == 6:
        return False

    if date_util.is_trading_day(today) and not date_util.is_trading_day(previous_day):
        periods = periods[1:]

    if date_util.is_trading_day(today) and date_util.is_holidays(next_day):
        periods = periods[:-1]

    if not date_util.is_trading_day(today) and not date_util.is_holidays(today):
        if date_util.is_trading_day(previous_day):
            periods = [periods[0]]
        else:
            return False

    now_time = date_util.get_now().time()
    return is_in_time_period(now_time, periods)


def main():
    logger = Logger("backend_login_status")
    monitor = None
    try:
        config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            admin_conf = conf['admin']
            email_conf = conf['email']

            monitor = Monitor(logger, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])

            date_util = DateUtils(logger)
            if not check_time_period(date_util):
                logger.info("非交易时间段无需执行账户登录状态检查,退出程序.")
                return
            else:
                logger.info("当前时间在交易时间段内,执行账户登录状态检查.")

            admin_api = AdminApi(logger, admin_conf["admin_base_url"])
            admin_api.login(admin_conf["admin_id"], admin_conf["admin_pwd"])
            account_list = admin_api.get_traders_list()
            skip_account_list = email_conf['skip_accounts']
            msg = f"交易账户已离线!\n"
            offline = False
            for account in account_list:
                if account["account_name"] in skip_account_list:
                    continue
                if account["account_type"] == "BACKEND" and account["status"] == "DISCONNECTED":
                    msg += f"离线账户: {account['account_name']} \n"
                    msg += f"账户状态: {account['status_msg']} \n"
                    offline = True
            if offline:
                monitor.send_email(msg)
                logger.info(msg)
    except Exception as e:
        logger.error(f"账号登录状态监控失败: {e}.")
        if monitor:
            monitor.send_email(f"账号登录状态监控失败: {e}.")


if __name__ == '__main__':
    main()
