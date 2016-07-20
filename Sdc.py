# coding=utf-8

"""
sdc - System Disk Check
@author  melody12ab@gmail.com
@Version 0.1
"""

import email.mime.multipart
import email.mime.text
import getopt
import smtplib
import socket
import subprocess
import sys


class Sdc:
    def __init__(self, argv):

        users = self.getSendUsers()

        try:
            opts, args = getopt.getopt(argv, "s:", ["help"])
        except getopt.GetoptError:
            print("argv error")

        for opt, arg in opts:
            if opt == '-f':
                result = self.getresult(int(arg))
                if len(result) < 2:
                    pass
                else:
                    for user in users:
                        self.sendEmail("***", "***", user, result, arg)
            if opt == '--help':
                helpinfo = '''
在同目录下创建user.properties，然后设置37行用户名和密码


--help      获取帮助
-s   <size>       指定报警阀值，如70（表示超过总磁盘的70%时候发送邮件）
                '''
                print(helpinfo)

    # 返回list，其中包含磁盘使用情况，然后是ip地址
    def getresult(self, threshold):
        result = []
        output = subprocess.Popen(["df -h"], stdout=subprocess.PIPE, shell=True)
        op = output.communicate()[0].decode()
        result.append(op.splitlines()[0].split())
        for line in op.splitlines():
            items = line.split()
            if items[0].find("sd") > 0:
                if int(items[4][:-1]) > threshold:
                    result.append(items)
                    # print(items)
        return result

    # 发送邮件的函数
    def sendEmail(self, fromuser, fpassword, touser, content, size):
        # 获取ip地址
        localip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
        msg = email.mime.multipart.MIMEMultipart()
        msg['from'] = fromuser
        msg['to'] = touser
        msg['subject'] = "磁盘报警通知"
        cont = "您好，您IP:" + localip + "的磁盘使用已经超过了" + size + "%，详细情况如下："
        for item in content:
            cont = cont + "\n\r"
            for line in item:
                cont = cont + line + "        "
        txt = email.mime.text.MIMEText(cont)
        msg.attach(txt)

        server = smtplib.SMTP("smtp.qq.com", 25)
        server.starttls()
        # server.set_debuglevel(1)
        server.login(fromuser, fpassword)
        server.sendmail(fromuser, touser, msg.as_string())
        server.quit()

    # 获取发给那些用户
    def getSendUsers(self):
        f = open("user.properties")
        users = []
        for line in f:
            users.append(line)
        f.close()
        return users


if __name__ == "__main__":
    Sdc(sys.argv[1:])
