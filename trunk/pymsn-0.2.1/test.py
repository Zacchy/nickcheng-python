import pymsn
import pymsn.msnp2p
import asyncore, getpass
import logging
import time
import gobject
import signal
import urllib
import re

logging.basicConfig(level=logging.DEBUG)

finished = False
def getproxies():
    proxies = urllib.getproxies()
    result = {}
    for type, url in proxies.items():
        url = url.split('@',1)
        if len(url) == 1:
            auth = ":"
            host = url[0].split('://', 1)[-1]
        else:
            auth = url[0].split('://', 1)[-1]
            host = url[1]
        host, port = host.split(':',1)
        username, password = auth.split(':',1)
        if port[-1] == '/': port = port[0:-1]
        result[type] = pymsn.network.ProxyInfos(host, port, type, username, password)
    return result

class NS(pymsn.Client):
    def __init__(self, server, account):
        pymsn.Client.__init__(self, server, account, proxies=getproxies())
        gobject.idle_add(self.connect_cb)

    def connect_cb(self):
        self.login()
        return False

    def on_connect_failure(self, proto):
        print "Connect failed"

    def on_login_failure(self, proto):
        print "Login failed"

    def on_login_success(self, proto):
        self.dp_fetched = False
        gobject.timeout_add(5000, self.__find_contact)
        
    def __find_contact(self):
        for contact in self._protocol._contacts.values():
            passport = contact.get_property("passport")
            presence = contact.get_property("presence")
            if presence != pymsn.PresenceStatus.OFFLINE:
                print "Contact %s is online" % contact.get_property("passport")
                
                gobject.idle_add(self.__fetch_dp, contact)
                return False

        return True

    def __fetch_dp(self, contact):
        if self.dp_fetched:
            return False
        
        self.dp_fetched = True
        
        dpc = pymsn.msnp2p.DisplayPictureCall(self)
        dpc.request(contact, self.__on_dp_request_done)
        
        return False
    
    def __on_dp_request_done(self, result):
        if result == None:
            print "_on_dp_request_done: Failed to fetch DP"
            return
        
        print "_on_dp_request_done: Got DP! %d bytes of data" % len(result)


def main():
    account = raw_input('Account: ')
    passwd = getpass.getpass('Password: ')

    n = NS(('messenger.hotmail.com', 1863), (account, passwd))

    mainloop = gobject.MainLoop()

    def quit_cb():
        mainloop.quit()

    def sigterm_cb():
        gobject.idle_add(quit_cb)

    signal.signal(signal.SIGTERM, sigterm_cb)

    while mainloop.is_running():
        try:
            mainloop.run()
        except KeyboardInterrupt:
            quit_cb()

if __name__ == '__main__':
    main()
