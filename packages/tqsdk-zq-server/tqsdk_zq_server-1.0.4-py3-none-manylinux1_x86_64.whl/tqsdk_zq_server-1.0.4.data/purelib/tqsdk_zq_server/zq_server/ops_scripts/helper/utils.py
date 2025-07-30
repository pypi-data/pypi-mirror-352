#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2022/8/9'

import os
import json
import logging
import requests
from datetime import date, datetime, timedelta
import pytz
import shinny_structlog


def Logger(file_name: str = None):
    log_file_path = "/var/log/ef/zq_ops_monitor"
    if file_name is not None and not os.path.exists(log_file_path):
        os.mkdir(log_file_path)
    dt = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(log_file_path, file_name + "-" + dt + ".log")
    logger = logging.getLogger("zq_ops_monitor")
    handle = logging.StreamHandler() if file_name is None else logging.FileHandler(filename=log_file, encoding="UTF-8")
    handle.setLevel(logging.DEBUG)
    fmt = shinny_structlog.JSONFormatter
    handle.setFormatter(fmt())
    logger.addHandler(handle)
    return logger


class DateUtils(object):
    def __init__(self, logger):
        self.tz = pytz.timezone("Asia/Shanghai")
        self.now = datetime.now(self.tz)
        self.logger = logger
        self.holidays = self._get_holidays()

    def download_holiday_file(self):
        url = "https://files.shinnytech.com/shinny_chinese_holiday.json"
        try:
            rsp = requests.get(url, timeout=30, headers=None)
            if rsp.status_code == 200:
                with open("/etc/zq-server/shinny_chinese_holiday.json", "w") as f:
                    json.dump(rsp.json(), f)
                return True
            else:
                self.logger.error(f"Failed to download holiday list, status code: {rsp.status_code} | {rsp.text}")
                return False
        except Exception as e:
            self.logger.error(f"Exception occurred while downloading holiday list: {e}")
            return False

    def _get_holidays(self):
        # 尝试下载节假日表至本地
        if not self.download_holiday_file():
            self.logger.warning("Falling back to local file due to download failure.")

        # 尝试从本地文件加载
        try:
            with open("/etc/zq-server/shinny_chinese_holiday.json") as f:
                holidays = json.load(f)
            self.logger.info("Successfully loaded holiday list from local file!")
            return holidays
        except Exception as e:
            self.logger.error(f"Failed to load holiday list from local file! {e}")
            raise e

    def get_today(self) -> int:
        return int(self.now.strftime('%Y%m%d'))

    def get_now_hour(self) -> int:
        return self.now.hour

    def get_now(self) -> timedelta:
        return self.now

    def get_previous_day(self, day: datetime.date = None) -> datetime.date:
        return (self.now - timedelta(days=1)).date() if day is None else day - timedelta(days=1)

    def get_next_day(self, day: datetime.date = None) -> datetime.date:
        return (self.now + timedelta(days=1)).date() if day is None else day + timedelta(days=1)

    def get_next_trading_day(self) -> int:
        for i in range(1, 30):
            day = self.now + timedelta(days=i)
            if self.is_trading_day(day):
                return int(day.strftime('%Y%m%d'))
        raise Exception(f"获取下一交易日信息失败")

    def is_trading_day(self, day: date = None) -> bool:
        day = self.now if day is None else day
        return day.weekday() < 5 and not self.is_holidays(day)

    def is_holidays(self, day: date = None) -> bool:
        day = self.now if day is None else day
        return day.strftime('%Y-%m-%d') in self.holidays
