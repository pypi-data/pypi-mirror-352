#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2022/9/16'

import os
import yaml
from helper.utils import Logger
from helper.monitor import Monitor
from datetime import datetime
from OpenSSL import crypto

def main():
    logger = Logger("ssl_monitor")
    monitor = None
    config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            email_conf = conf['email']

            monitor = Monitor(logger, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])

            cert_file = "/etc/api-gateway/domain.crt"
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file).read())
            issuer = cert.get_issuer()
            expired = cert.has_expired()
            start_date = datetime.strptime(cert.get_notBefore().decode('UTF-8'), '%Y%m%d%H%M%SZ')
            end_date = datetime.strptime(cert.get_notAfter().decode('UTF-8'), '%Y%m%d%H%M%SZ')
            remaining = (end_date - datetime.now()).days
            message = f"证书信息：\nCountryName:{issuer.C}\nLocality:{issuer.L}\n" \
                      f"Organization:{issuer.O}\nOrganizationalUnit:{issuer.OU}\nCommonName:{issuer.CN}\n" \
                      f"证书有效期:{start_date}\n证书失效期:{end_date}\n证书是否过期:{expired}\n"

            if expired:
                monitor.send_email(f"CA证书已过期，请及时更换证书！\n{message}")
            elif remaining <= 30:
                monitor.send_email(f"CA证书即将过期，请及时更换证书！\n{message}")

    except Exception as e:
        logger.error(f"证书监控异常: {e}.")
        if monitor:
            monitor.send_email(f"证书监控异常: {e}.")


if __name__ == '__main__':
    main()
