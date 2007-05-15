#!/usr/bin/env python
#coding=utf-8

import httplib
import re

#
pattern = '<?xml version="1.0" encoding="UTF-8"?><Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsse="http://schemas.xmlsoap.org/ws/2003/06/secext" xmlns:saml="urn:oasis:names:tc:SAML:1.0:assertion" xmlns:wsp="http://schemas.xmlsoap.org/ws/2002/12/policy" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing" xmlns:wssc="http://schemas.xmlsoap.org/ws/2004/04/sc" xmlns:wst="http://schemas.xmlsoap.org/ws/2004/04/trust"><Header><ps:AuthInfo xmlns:ps="http://schemas.microsoft.com/Passport/SoapServices/PPCRL" Id="PPAuthInfo"><ps:HostingApp>{7108E71A-9926-4FCB-BCC9-9A9D3F32E423}</ps:HostingApp><ps:BinaryVersion>4</ps:BinaryVersion><ps:UIVersion>1</ps:UIVersion><ps:Cookies></ps:Cookies><ps:RequestParams>AQAAAAIAAABsYwQAAAAzMDg0</ps:RequestParams></ps:AuthInfo><wsse:Security><wsse:UsernameToken Id="user"><wsse:Username>%s</wsse:Username><wsse:Password>%s</wsse:Password></wsse:UsernameToken></wsse:Security></Header><Body><ps:RequestMultipleSecurityTokens xmlns:ps="http://schemas.microsoft.com/Passport/SoapServices/PPCRL" Id="RSTS"><wst:RequestSecurityToken Id="RST0"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>http://Passport.NET/tb</wsa:Address></wsa:EndpointReference></wsp:AppliesTo></wst:RequestSecurityToken><wst:RequestSecurityToken Id="RST1"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>messengerclear.live.com</wsa:Address></wsa:EndpointReference></wsp:AppliesTo><wsse:PolicyReference URI="MBI_KEY_OLD"></wsse:PolicyReference></wst:RequestSecurityToken></ps:RequestMultipleSecurityTokens></Body></Envelope>'
content = pattern % ('chengnick@hotmail.com','1738517385')

#
h=httplib.HTTPS('loginnet.passport.com')
h.putrequest('POST', '/RST.srf')
h.putheader('Accept','text/*')
h.putheader('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; IDCRL 4.100.313.1; IDCRL-cfg 4.0.5633.0; App msnmsgr.exe, 8.1.178.0, {7108E71A-9926-4FCB-BCC9-9A9D3F32E423})')
h.putheader('Host', 'loginnet.passport.com')
h.putheader('Content-Length', str(len(content)))
h.putheader('Connection', 'Keep-Alive')
h.putheader('Cache-Control', 'no-cache')
h.endheaders()

h.send(content)
errcode, errmsg, headers = h.getreply()

print errcode
print errmsg.decode('utf-8')
for i in headers:
    print i
reply = h.file.read()
print reply

sToken = re.findall(r'"Compact1">([^<]*)', reply)[0]
pToken = re.findall(r'wst:BinarySecret>([^<]*)', reply)[-2]
print sToken
print pToken
####
#ls = httplib.HTTPSConnection(login_host)
#ls.request('GET', login_server, '', headers)