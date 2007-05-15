#!/usr/bin/env python
#coding=utf-8
import wx


#定义来自about和exit菜单项的消息编号
ID_ABOUT = 101 
ID_EXIT  = 102 

class MyFrame(wx.Frame): 
    def __init__(self, parent, ID, title): 

       #参数顺序:
        wx.Frame.__init__(self, parent, ID, title, wx.DefaultPosition, wx.Size(200, 150)) 
        self.CreateStatusBar() #创建状态栏
        self.SetStatusText("This is the statusbar") #设置状态栏信息
         
        menu = wx.Menu() #创建菜单项
        menu.Append(wx.ID_ABOUT, "&About","More information about this program") #增加菜单项
        menu.AppendSeparator() #分割线
        menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program") #增加exit项.
         
        menuBar = wx.MenuBar() #创建菜单栏
        menuBar.Append(menu, "&File"); #创建顶层菜单
         
        self.SetMenuBar(menuBar) 
         
         
class MyApp(wx.App): 
    def OnInit(self): 
        frame = MyFrame(None, -1, "Hello from wxPython") 
        frame.Show(True) 
        self.SetTopWindow(frame) 
        return True 

app = MyApp(0) 
app.MainLoop() 

