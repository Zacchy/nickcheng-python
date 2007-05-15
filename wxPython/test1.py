import sys, os
import wx

class main_window (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, -1, title, size = (200, 200), style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
		self.control = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE)
		self.Show(True)

class App (wx.App):
	def OnInit(self):
		frame = main_window(None, -1, "wxPython: (A Demonstration)")
		self.SetTopWindow(frame)
		return True

app = App(0)
app.MainLoop()

