#!/usr/bin/env python

import pymsn
import pymsn.event

import logging
import gobject

logging.basicConfig(level=logging.DEBUG)

finished = False
def get_proxies():
    import urllib
    proxies = urllib.getproxies()
    result = {}
    if 'https' not in proxies and \
            'http' in proxies:
        url = proxies['http'].replace("http://", "https://")
        result['https'] = pymsn.Proxy(url)
    for type, url in proxies.items():
        if type == 'no': continue
        result[type] = pymsn.Proxy(url)
    return result

class Client(pymsn.Client, pymsn.event.ClientEventInterface):
    def __init__(self, account, quit, http_mode=False):
        server = ('messenger.hotmail.com', 1863)
        self.quit = quit
        self.account = account
        if http_mode:
            from pymsn.transport import HTTPPollConnection
            pymsn.Client.__init__(self, server, get_proxies(), HTTPPollConnection)
        else:
            pymsn.Client.__init__(self, server, proxies = get_proxies())
        self.register_events_handler(self)
        gobject.idle_add(self._connect)

    def _connect(self):
        self.login(*self.account)
        return False

    def on_client_state_changed(self, state):
        if state == pymsn.event.ClientState.CLOSED:
            self.quit()
        elif state == pymsn.event.ClientState.OPEN:
            self.profile.presence = pymsn.Presence.ONLINE
            self.profile.display_name = "Kimbix"
            self.profile.personal_message = "Testing pymsn, and freeing the pandas!"

    def on_client_error(self, error_type, error):
        print "ERROR :", error_type, " ->", error


def main():
    import sys
    import getpass
    import signal

    if "--http" in sys.argv:
        http_mode = True
        sys.argv.remove('--http')
    else:
        http_mode = False

    if len(sys.argv) < 2:
        account = raw_input('Account: ')
    else:
        account = sys.argv[1]

    if len(sys.argv) < 3:
        passwd = getpass.getpass('Password: ')
    else:
        passwd = sys.argv[2]

    mainloop = gobject.MainLoop(is_running=True)

    def quit():
        mainloop.quit()

    def sigterm_cb():
        gobject.idle_add(quit)

    signal.signal(signal.SIGTERM, sigterm_cb)

    n = Client((account, passwd), quit, http_mode)

    while mainloop.is_running():
        try:
            mainloop.run()
        except KeyboardInterrupt:
            quit()

if __name__ == '__main__':
    main()
