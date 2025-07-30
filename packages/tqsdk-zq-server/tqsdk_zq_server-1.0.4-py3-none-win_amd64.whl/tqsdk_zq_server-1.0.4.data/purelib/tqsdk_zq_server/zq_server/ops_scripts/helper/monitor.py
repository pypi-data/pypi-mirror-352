#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2022/8/9'

import os
import smtplib
import email
import socket
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from typing import List


class Monitor(object):
    def __init__(self, logger, title = ''):
        self.logger = logger
        self.title = title
        self.email_sender_user_name = ""
        self.email_sender_password = ""
        self.email_receivers = []

    def set_email_sender(self, user_name: str, password: str):
        self.email_sender_user_name = user_name
        self.email_sender_password = password

    def set_email_receivers(self, receivers: List):
        self.email_receivers = receivers

    def send_email(self, message):
        hostname = ('\n详细信息:\nStatic hostname: ' + os.popen('hostname').read())
        trigger_time = datetime.now().strftime("\n触发时间:%Y-%m-%d %H:%M:%S")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipaddr = ('IP Address: ' + s.getsockname()[0])
        s.close()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header('众期运维通知')
        msg['From'] = formataddr([self.title, self.email_sender_user_name])
        # list转为字符串
        msg['Message-id'] = email.utils.make_msgid()
        msg['Date'] = email.utils.formatdate()
        # 构建alternative的text/plain部分
        textplain = MIMEText(message+trigger_time+hostname+ipaddr, _subtype='plain', _charset='UTF-8')
        msg.attach(textplain)
        try:
            client = smtplib.SMTP_SSL('smtpdm.aliyun.com', 465)
            client.login(self.email_sender_user_name, self.email_sender_password)
            client.sendmail(self.email_sender_user_name, self.email_receivers, msg.as_string())
            client.quit()
            self.logger.info('邮件发送成功', sender=self.email_sender_user_name, receivers=self.email_receivers, pack=message)
        except Exception as e:
            self.logger.error('邮件发送异常', sender=self.email_sender_user_name, receivers=self.email_receivers,
                              pack=message, exception_info=str(e))
