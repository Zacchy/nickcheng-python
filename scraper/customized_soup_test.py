from unittest import TestCase
from customized_soup import CustomizedSoup
from BeautifulSoup import *

__author__ = "cenyongh@gmail.com"
__version__ = "0.1"
__license__ = "PSF"
class CustomizedSoupTest(TestCase):
    def setUp(self):
        pass
    
    def testIgnoreComment(self):
        exp = '''<html></html>'''
        
        # ignore the comment
        actual = '''<html><!--some comment--></html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())
        
    def testIgnoreScript(self):
        exp = '''<html></html>'''
        
        # ignore the script
        actual = '''<html><script type="text/javascript" src="http://image2.sina.com.cn/home/sinaflash.js"></script></html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())
        
        # ignore the script
        actual = '''<html><SCRIPT type="text/javascript" src="http://image2.sina.com.cn/home/sinaflash.js"></script></html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())
        
        # ignore the script and its content
        actual = '''<html><script type="text/javascript">funcion some(){}</script></html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())
        
    def testIgnoreStyle(self):
        exp = '''<html></html>'''
        
        # ignore the style
        actual = '''<html><style type="text/css"></style></html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())
        
         # ignore the style and its content
        actual = '''<html><style type="text/css">body {some style}</style></html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())
        
    def testIgnoreEmpytString(self):
        exp = '''<html></html>'''
        
        # ignore the style
        actual = '''<html>\n\n\n\n</html>'''
        doc = CustomizedSoup(actual)
        self.assertEqual(exp, doc.renderContents())


        exp = '''
            <html>
                <head>some text
                </head>
            </html>
            '''
        
        # ignore the style
        actual = '''<html><head>some text</head></html>'''
        
        
        self.assertEqual(CustomizedSoup(exp), CustomizedSoup(actual))