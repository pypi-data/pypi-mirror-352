#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__date__ = '2022/8/17'

import os
import yaml
import pexpect
from helper.utils import DateUtils, Logger
from helper.monitor import Monitor


def dump_database(host, dbname, user, password, output_file):
    cmd = f"pg_dump --host={host} --dbname={dbname} --username={user} --file={output_file}"
    child = pexpect.spawn(cmd, timeout=3600)
    child.expect(f"Password:")
    child.sendline(password)
    result = child.expect([pexpect.EOF, pexpect.TIMEOUT,
                           f'pg_dump: error: connection to database "{dbname}" failed: FATAL:  password authentication failed for user "{user}"'])
    child.timeout = 3600
    if result == 0:
        # 执行成功
        pass
    elif result == 1:
        raise Exception(f"数据库归档超时, {child.before}")
    elif result == 2:
        raise Exception(f"数据库归档失败, 请确认数据库及登录信息是否正确.")
    else:
        raise Exception(f"数据库归档失败, {child.before}")


def sync_to_remote(srcfile, dest_ip, dest_path, dest_user, dest_password):
    cmd = f"rsync -avz -e ssh {srcfile} {dest_user}@{dest_ip}:{dest_path}"
    child = pexpect.spawn(cmd, timeout=3600)
    child.expect(f"{dest_user}@{dest_ip}'s password:")
    child.sendline(dest_password)
    result = child.expect([pexpect.EOF, pexpect.TIMEOUT, "Permission denied, please try again."])
    child.timeout = 3600
    if result == 0:
        # 执行成功
        pass
    elif result == 1:
        raise Exception(f"文件备份至远程服务器超时, {child.before}")
    elif result == 2:
        raise Exception(f"文件备份至远程服务器失败, 请确认用户名密码是否正确.")
    else:
        raise Exception(f"文件备份至远程服务器失败, {child.before}")


def main():
    config_file = os.path.join("/etc/zq-server", "ops_config.yaml")
    logger = Logger("database_backup")
    monitor = None
    try:
        with open(config_file, 'r', encoding='utf-8') as f:

            conf = yaml.safe_load(f)
            email_conf = conf['email']
            backup_config = conf['database_backup']
            backup_server_config = conf['backup_server']

            monitor = Monitor(logger, email_conf['title'])
            monitor.set_email_sender(email_conf['sender_name'], email_conf['sender_password'])
            monitor.set_email_receivers(email_conf['receivers'])

            date_util = DateUtils(logger)
            if not date_util.is_trading_day():
                logger.info("非交易日无需执行数据库备份")
                return

            for val in backup_config:
                backup_path = val['backup_path']
                if not os.path.exists(backup_path):
                    os.mkdir(backup_path)
                dump_file = os.path.join(backup_path, val["db_name"] + "." + str(date_util.get_today()) + ".dmp")
                dump_database(val["db_server"], val["db_name"], val["db_uid"], val["db_password"], dump_file)
                os.system("lzma -z %s" % dump_file)
                lzma_file_name = dump_file + ".lzma"
                mount_path = "/var/nas/backups/db_backup"
                if backup_server_config["enable"]:
                    if os.path.exists(mount_path):
                        os.system("mv %s %s" % (lzma_file_name, mount_path))
                    else:
                        sync_to_remote(lzma_file_name, backup_server_config["ip"], backup_server_config["dest_path"],
                                       backup_server_config["user"], backup_server_config["password"])
    except Exception as e:
        msg = f"数据库归档失败, {e}."
        logger.error(msg)
        if monitor:
            monitor.send_email(msg)


if __name__ == '__main__':
    main()