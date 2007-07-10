from BeautifulSoup import *
from unittest import TestCase
from scraper import Scraper

__author__ = "cenyongh@gmail.com"
__version__ = "0.1"
__license__ = "PSF"
class ScraperTest(TestCase):
    def setUp(self):
        pass
    
    def testMatchByType(self):
        # test simple tag
        pattern = "<a></a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same type
        actual = BeautifulSoup("<a></a>")
        self.assertTrue(_scraper.matchByType(exp.contents[0], actual.contents[0]))
        
        # different type
        actual = BeautifulSoup("text")
        self.assertFalse(_scraper.matchByType(exp.contents[0], actual.contents[0]))        
        
        
    def testMatchTagWithoutAttribute(self):
        # test simple tag
        pattern = "<a></a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same tag
        actual = BeautifulSoup("<a></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # different tag name
        actual = BeautifulSoup("<b></b>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # different child count
        actual = BeautifulSoup("<a><b></b></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
    def testMatchTagWithAttribute(self):
        pattern = "<a name='abc'></a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same tag
        actual = BeautifulSoup('''<a name="abc"></a>''')
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # different attribute name
        actual = BeautifulSoup("<a age='abc'></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # different attribute value
        actual = BeautifulSoup("<a name='abcd'></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # more attributes
        actual = BeautifulSoup("<a name='abc' address='111'></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
    def testMatchTagWithText(self):
        pattern = "<a>text</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same tag
        actual = BeautifulSoup("<a>text</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # withtou text content
        actual = BeautifulSoup("<a></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # with sub tag
        actual = BeautifulSoup("<a><b></b></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
    
    def testMatchTagWithSubTag(self):
        pattern = "<a><b></b></a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same tag
        actual = BeautifulSoup("<a><b></b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # sub tag with different name
        actual = BeautifulSoup("<a><c></c></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # sub tag with more sub tag
        actual = BeautifulSoup("<a><b><c></c></b></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
    def testMatch(self):
        pattern = "<a><b></b></a>"
        _scraper = Scraper(pattern)
        
        # one match
        actual = BeautifulSoup("<a><b></b></a>")
        self.assertEqual(1, len(_scraper.match(actual)))
        
        # one match
        actual = BeautifulSoup("<div><a><b></b></a></div>")
        self.assertEqual(1, len(_scraper.match(actual)))
        
        # one match
        actual = BeautifulSoup("<a><a><b></b></a></a>")
        self.assertEqual(1, len(_scraper.match(actual)))        
        
        # two match
        actual = BeautifulSoup("<a><b></b></a><a><b></b></a>")
        self.assertEqual(2, len(_scraper.match(actual)))
        
        # two match
        actual = BeautifulSoup("<a><b></b></a><c><a><b></b></a></c>")
        self.assertEqual(2, len(_scraper.match(actual)))
    
    def testExtractTag(self):
        pattern = "<a name='$name'></a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # one attribute
        actual = BeautifulSoup("<a name='abc'></a>")
        self.assertEqual('abc', _scraper.extractTag(exp.contents[0], actual.contents[0])['name'])
        
        # one attribute
        actual = BeautifulSoup("<a name='abc' age='27'></a>")
        self.assertEqual('abc', _scraper.extractTag(exp.contents[0], actual.contents[0])['name'])
        
        # two attributes
        pattern = "<a name='$name' age='$age'></a>"
        exp = BeautifulSoup(pattern)
        actual = BeautifulSoup("<a name='abc' age='27'></a>")
        ret =  _scraper.extractTag(exp.contents[0], actual.contents[0])
        self.assertEqual(2, len(ret))
        self.assertEqual('abc', ret['name'])
        self.assertEqual('27', ret['age'])
        
        # get attribute from sub tag
        pattern = "<a><b name='$name'></b></a>"
        exp = BeautifulSoup(pattern)
        
        # one attribute
        actual = BeautifulSoup("<a><b name='abc'></b></a>")
        self.assertEqual('abc', _scraper.extractTag(exp.contents[0], actual.contents[0])['name'])
        
    def testExtractText(self):
        pattern = "<a>$text</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # one text
        actual = BeautifulSoup("<a>hello world</a>")
        self.assertEqual('hello world', _scraper.extractText(exp.contents[0], actual.contents[0])['text'])

    def testExtract(self):
        pattern = "<a name='$name'>$text</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # text in sub tag        
        actual = BeautifulSoup("<a name='abc'>hello world</a>")
        ret = _scraper.extract(actual.contents[0])
        self.assertEqual('hello world', ret['text'])
        
    def testMatchTagWithAsterisk(self):
        pattern = "<a>*</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same tag
        actual = BeautifulSoup("<a>*</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))        
        
        # asterisk can match anything
        actual = BeautifulSoup("<a><b></b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))        
        
        # asterisk can match null
        actual = BeautifulSoup("<a></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))        
        
        # restricted asterisk,only accept tag b, text or null
        pattern = "<a>*(b)</a>"
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        actual = BeautifulSoup("<a>text</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        actual = BeautifulSoup("<a><b></b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        actual = BeautifulSoup("<a><b></b><b></b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        actual = BeautifulSoup("<a><c></c><b></b></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # restricted asterisk,only accept tag b,tab c, text or null
        pattern = "<a>*(b,c)</a>"
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><c></c><b></b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        actual = BeautifulSoup("<a><c></c><b></b><d></d></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # restricted prefix asterisk
        pattern = "<a>*<b></b></a>"
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><c></c><b></b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # no tag should appear after tag b
        actual = BeautifulSoup("<a><c></c><b></b><d></d></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        
    def testPartlyMatchTag(self):
        pattern = "<a><b></b>*</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
         
        # same tag
        actual = BeautifulSoup("<a><b></b>*</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # asterisk match the remaining
        actual = BeautifulSoup("<a><b></b><c></c></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # asterisk match the remaining tag c
        pattern = "<a><b></b>*(c)</a>"        
        exp = BeautifulSoup(pattern)
        actual = BeautifulSoup("<a><b></b><c></c></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # only c is accepted
        pattern = "<a><b></b>*(c)</a>"        
        exp = BeautifulSoup(pattern)
        actual = BeautifulSoup("<a><b></b><d></d></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
    def testMatchTagWithMoreThenOneAsterisk(self):
        pattern = "<a><b>*</b>*</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # same tag
        actual = BeautifulSoup("<a><b>*</b>*</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # asterisk can match the remaining
        actual = BeautifulSoup("<a><b>*</b><c></c></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # asterisk can match the remaining
        pattern = "<a><b>*</b>*(c)</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><b>*</b><c></c></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # only c is accepted
        pattern = "<a><b>*</b>*(c)</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><b>*</b><d></d></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
    def testMatchAndExtract(self):
        pattern = "<a name='$name'></a>"
        _scraper = Scraper(pattern)        
        
        # same tag
        actual = BeautifulSoup("<a name='abc'></a>")
        ret = _scraper.match(actual)
        self.assertEqual(1, len(ret))

        ret = _scraper.extract(ret[0])
        
        self.assertEqual(1, len(ret))
        self.assertEqual('abc', ret['name'])
        
        
        pattern = "<a name='$name'>*</a>"
        _scraper = Scraper(pattern)        
        
        # same tag
        actual = BeautifulSoup("<a name='abc'><b></b></a>")
        ret = _scraper.match(actual)
        self.assertEqual(1, len(ret))

        ret = _scraper.extract(ret[0])
        
        self.assertEqual(1, len(ret))
        self.assertEqual('abc', ret['name'])
        
    def testExtractAsteriskValue(self):
        pattern = "<a>*$content</a>"
        _scraper = Scraper(pattern)
        exp = BeautifulSoup(pattern)
        
        # extract text
        actual = BeautifulSoup("<a>hello world</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        self.assertEqual('hello world', _scraper.extractTag(exp.contents[0], actual.contents[0])['content'][0])        

        pattern = "<a>*(b)$content</a>"
        _scraper = Scraper(pattern)    
        exp = BeautifulSoup(pattern)
        
        # asterisk only restrict on tag but not text
        actual = BeautifulSoup("<a>hello world</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        self.assertEqual('hello world', _scraper.extractTag(exp.contents[0], actual.contents[0])['content'][0])        
        
        # asterisk restrict tag
        actual = BeautifulSoup("<a><c></c></a>")
        self.assertFalse(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        
        # asterisk restrict tag
        actual = BeautifulSoup("<a><b>hello world</b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        self.assertEqual(BeautifulSoup('<b>hello world</b>').contents[0], _scraper.extractTag(exp.contents[0], actual.contents[0])['content'][0])
        
        # asterisk restrict tag
        actual = BeautifulSoup("<a><b>hello</b><b>world</b></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        ret = _scraper.extractTag(exp.contents[0], actual.contents[0])
        self.assertEqual(BeautifulSoup('<b>hello</b>').contents[0], ret['content'][0])        
        self.assertEqual(BeautifulSoup('<b>world</b>').contents[0], ret['content'][1])
        
        # prefix asterisk
        pattern = "<a>*(b)<c></c>$content</a>"
        _scraper = Scraper(pattern)    
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><b></b><b></b><c></c>hello world</a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        ret = _scraper.extractTag(exp.contents[0], actual.contents[0])
        self.assertEqual('hello world', ret['content'])

        # prefix asterisk
        pattern = "<a>*(b)<c></c>*$content</a>"
        _scraper = Scraper(pattern)    
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><b></b><c></c><d>hello world</d></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        ret = _scraper.extractTag(exp.contents[0], actual.contents[0])
        self.assertEqual(BeautifulSoup('<d>hello world</d>').contents[0], ret['content'][0])
        
        actual = BeautifulSoup("<a><b></b><c></c><d>hello</d><d>world</d></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        ret = _scraper.extractTag(exp.contents[0], actual.contents[0])
        self.assertEqual(BeautifulSoup('<d>hello</d>').contents[0], ret['content'][0])
        self.assertEqual(BeautifulSoup('<d>world</d>').contents[0], ret['content'][1])
        
        # prefix asterisk
        pattern = "<a>*<c></c>*$content</a>"
        _scraper = Scraper(pattern)    
        exp = BeautifulSoup(pattern)
        
        actual = BeautifulSoup("<a><b></b>some text<c></c><d>hello world</d></a>")
        self.assertTrue(_scraper.matchTag(exp.contents[0], actual.contents[0]))
        ret = _scraper.extractTag(exp.contents[0], actual.contents[0])
        
        self.assertEqual(BeautifulSoup('<d>hello world</d>').contents[0], ret['content'][0])
        