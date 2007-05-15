#!/usr/bin/env python
import urllib
def get_weather(city):
        url = "http://weather.tq121.com.cn/mapanel/index1_new.php?city=%s" % city
        s = urllib.urlopen(url)
        str = s.read();

        tmp = str.find('class="weather">')
        start = str.find('>', tmp) + 1
        end = str.find('</td>', tmp)

        res = [str[start:end]]

        tmp = str.find('class="weatheren">')
        start = str.find('>', tmp) + 1
        end = str.find('</td>', tmp)

        res.append(str[start:end])

        return res


if __name__ == "__main__" :
        print "City: ", 
        city = raw_input()
        w = get_weather(city);
        print w[0] , '\n',  w[1]
