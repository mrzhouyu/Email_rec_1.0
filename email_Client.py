# -*- coding: utf-8 -*-
'''
@File  : email_Client.py
@Author: YuChou
@Date  : 2019/3/18 10:06
'''

# import smtplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
import os
import sys
import re
import time
# import shutil
'''
配置文件
'''
email = "********.com"
password = "password"
pop3_server = "pop.qiye.163.com"


class Myemail:

    global L

    def __init__(self, eAdrr, Pwd,  ServerUrl):
        self.eAdrr = eAdrr
        self.Pwd = Pwd
        self.ServerUrl = ServerUrl
        self.Con = self.login()
        self.oldNum = self.read_Old_num()

    def login(self):
        try:
            self.Con = poplib.POP3(self.ServerUrl)
        except:
            print("connect to server faild")
            return

        try:
            self.Con.user(self.eAdrr)
            self.Con.pass_(self.Pwd)
        except:
            print("login faild")
            return
        # self.Con.set_debuglevel(1)
        return self.Con

    # 原始内容 返回新的邮件数量
    def get_New_MailsLen(self):
        resp, mails, octest = self.Con.list()
        L = len(mails)
        return L

    # 得到邮件初始内容
    def get_Content(self, page):
        resp, lines, octests = self.Con.retr(page)
        try:
            lines = b'\r\n'.join(lines).decode("utf-8")
            msg = Parser().parsestr(lines)
            return msg
        except:
            return None

    #读取配置文件 查看 旧的邮件长度
    def read_Old_num(self):
        try:
            with open("old_length.txt", "r", encoding="utf8") as f:
                old_num = int(f.read())
                f.close()
            return old_num
        except:
            with open("old_length.txt", "w", encoding="utf8") as f:
                f.write(str(self.get_New_MailsLen()))
                f.close()
            return int(self.get_New_MailsLen())

    #保存邮件
    def save_Email(self, path, content):

        with open(path, "a", encoding="utf8") as f:
            f.write(content + "\n")


    # 解码器类型
    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    # 解码内容
    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    # 格式化和输出
    def print_info(self, msg, path ,indent=0):
        if indent == 0:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')

                if value:
                    if header == 'Subject':
                        value = self.decode_str(value)
                    else:
                        hdr, addr = parseaddr(value)
                        name = self.decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                # print('%s%s: %s' % ('  ' * indent, header, value))
                self.save_Email(path,'%s%s: %s' % ('  ' * indent, header, value) )
                # print("分割线**********************************************")
        if (msg.is_multipart()):
            parts = msg.get_payload()

            for n, part in enumerate(parts):
                # print('%spart %s' % ('  ' * indent, n))
                self.save_Email(path, '%spart %s' % ('  ' * indent, n))
                # print('%s--------------------' % ('  ' * indent))
                self.save_Email(path,'%s--------------------' % ('  ' * indent))
                # print("分割线**********************************************")
                self.print_info(part, path=path, indent=indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                content = msg.get_payload(decode=True)
                charset = self.guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                # print('%sText: %s' % ('  ' * indent, content + '...'))
                self.save_Email(path,'%sText: %s' % ('  ' * indent, content + '...') )
                # print("分割线**********************************************")
            else:
                # print('%sAttachment: %s' % ('  ' * indent, content_type))
                self.save_Email(path, '%sAttachment: %s' % ('  ' * indent, content_type))
                # print("分割线**********************************************")


    def __del__(self):
        self.Con.quit()

    # 判断老的邮件是否已经被删除 是的话根据配置文件先下载旧的邮件
    def save_OldMail(self):
        #获取当前目录下所有的文件
        all_First_List = os.listdir(".")
        #查看旧的email是否都存在该目录下
        for i in range(1, self.oldNum+1):
            name = str(i) + "_email.txt"
            if name in all_First_List: #没有的旧文件 先下载
                continue
            else:
                cont = self.get_Content(i)
                if cont:
                    self.print_info(msg=cont, path=name)
                else:

                    cont = "无法解码的文档"
                    with open(name, "a", encoding="utf-8") as f:
                        f.write(cont)
                    # self.print_info(msg=cont, path=name)




    def main(self):
        self.save_OldMail()#每次先看看有没有旧的邮件
        New_length = self.get_New_MailsLen()
        if New_length == self.oldNum:
            return None
        else:
            new = New_length - self.oldNum
            for i in range(new): #下载新的邮件
                cont = self.get_Content(New_length - i)
                path = str(New_length - i) + "_email.txt"
                if cont:
                    self.print_info(msg=cont, path = path)
                else:
                    cont = "无法解码的文档"
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(cont)
                    # self.print_info(msg=cont, path=path)


if __name__ == "__main__":
    if os.path.exists("MailFile"):
        os.chdir("MailFile")
    else:
        os.mkdir("MailFile")
        os.chdir("MailFile")

    while True:
        Client = Myemail(email, password, pop3_server)
        Client.main()
        time.sleep(100)
