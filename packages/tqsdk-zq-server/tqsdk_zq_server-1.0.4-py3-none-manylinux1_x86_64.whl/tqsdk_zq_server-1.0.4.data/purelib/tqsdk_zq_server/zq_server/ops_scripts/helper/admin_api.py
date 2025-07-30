#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2022/8/9'

import json
import requests


class AdminApi(object):
    def __init__(self, logger, base_url: str = ""):
        self.logger = logger
        self.base_url = base_url
        self.access_token = None

    def login(self, admin_id: str = "", admin_pwd: str = ""):
        data = json.dumps({
            "user_name": admin_id,
            "password": admin_pwd
        })
        rsp = self.request("POST", "/login", data)
        if rsp.status_code != 200:
            raise Exception(f"系统登录失败:{rsp.status_code}|{json.loads(rsp.text).get('message')}")
        self.access_token = json.loads(rsp.text).get("token", "")

    def front_core_status(self):
        rsp = self.request("GET", "/status", {})
        if rsp.status_code != 200:
            raise Exception(f"获取系统状态失败: {rsp.status_code}|{json.loads(rsp.text).get('message')}")
        status = json.loads(rsp.text).get("data")
        return (status['stage'], status['trading_day'])

    def get_traders_list(self):
        rsp = self.request("GET", "/accounts", {})
        if rsp.status_code != 200:
            raise Exception(f"获取交易账户清单失败: {rsp.status_code}|{json.loads(rsp.text).get('message')}")
        return json.loads(rsp.text).get("datas")

    def settle(self, settle_price_type: str):
        data = json.dumps({
            "price_type": settle_price_type
        })
        rsp = self.request("POST", "/status/settlement", data)
        if rsp.status_code != 200 and rsp.status_code != 400:
            raise Exception(f"结算执行失败: {rsp.status_code}|{json.loads(rsp.text).get('message')}")
        return json.loads(rsp.text).get("message")

    def init_trading_day(self, trading_day: int):
        data = json.dumps({
            "trading_day": trading_day
        })
        rsp = self.request("POST", "/status/tradingday", data)
        if rsp.status_code != 200:
            raise Exception(f"交易日初始化失败: {rsp.status_code}|{json.loads(rsp.text).get('message')}")
        return json.loads(rsp.text).get("data")

    def settlement_adjust_tradelog(self, user_name: str = "", trading_day: str = ""):
        data = json.dumps({
            "user_name": user_name,
            "trading_day": trading_day
        })
        rsp = self.request("POST", "/settlement-adjust-tradelog", data)
        if rsp.status_code != 200 and rsp.status_code != 400:
            raise Exception(f"更新交易记录手续费失败: {rsp.status_code}|{json.loads(rsp.text).get('message')}")
        return json.loads(rsp.text).get("message")
        
    def request(self, method, target, data):
        rsp = requests.request(method, self.base_url + target, headers=self.headers, data=data)
        self.logger.info(target, pack=json.loads(rsp.text), status_code=rsp.status_code, method=method,
                         payload=data)
        return rsp

    @property
    def headers(self):
        return {
            "Accept": "application/json",
            "Authorization": "Bearer %s" % self.access_token
        }
