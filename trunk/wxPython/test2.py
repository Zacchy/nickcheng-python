#!/bin/python
import sys, os
import wx
import string

# Process the command line. Not much to do:
# just get the name of the project file if it's given. Simple:
projfile = 'Unnamed'
if len(sys.argv) > 1:
	projfile = sys.argv[1]

def MsgBox(window, string):
	dlg = wx.MessageDialog(window, string, 'wxProject', wx.OK)
	dlg.ShowModal()
	dlg.Destroy()

class main_window (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, -1, title, size = (500, 500), style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

		# -------
		# Set up menu bar for the program.
		# -------
		self.mainmenu = wx.MenuBar()  # Create menu bar.
		mainwindow = self

		menu = wx.Menu()  # Make a menu (will be the Project menu)

		exitID = wx.NewId()  # Make a new ID for a menu entry.
		menu.Append(exitID, 'Open', 'Open project')  # Name the ID by adding it to the menu.
		wx.EVT_MENU(self, exitID, self.OnProjectOpen)  # Create and assign a menu event.
		exitID = wx.NewId()
		menu.Append(exitID, 'New', 'New project')
		wx.EVT_MENU(self, exitID, self.OnProjectNew)
		exitID = wx.NewId()
		menu.Append(exitID, 'Exit', 'Exit program')
		wx.EVT_MENU(self, exitID, self.OnProjectExit)

		self.mainmenu.Append(menu, 'Project')  # Add the project menu to the menu bar.

		menu = wx.Menu()  # Make a menu (will be the File menu)

		exitID = wx.NewId()
		menu.Append(exitID, 'Add', 'Add file to project')
		wx.EVT_MENU(self, exitID, self.OnFileAdd)
		exitID = wx.NewId()
		menu.Append(exitID, 'Remove', 'Remove file from project')
		wx.EVT_MENU(self, exitID, self.OnFileRemove)
		exitID = wx.NewId()
		menu.Append(exitID, 'Open', 'Open file for editing')
		wx.EVT_MENU(self, exitID, self.OnFileOpen)
		exitID = wx.NewId()
		menu.Append(exitID, 'Save', 'Save file')
		wx.EVT_MENU(self, exitID, self.OnFileSave)

		self.mainmenu.Append(menu, 'File')  # Add the file menu to the menu bar.

		self.SetMenuBar(self.mainmenu)  # Attach the menu bar to the window.

		# -------
		# Create the splitter window.
		# -------
		splitter = wx.SplitterWindow(self, -1, style = wx.NO_3D | wx.SP_3D)
		splitter.SetMinimumPaneSize(1)

		# -------
		# Create the tree on the left.
		# -------
		tID = wx.NewId()
		self.tree = wx.TreeCtrl(splitter, tID, style = wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS | wx.TR_HAS_VARIABLE_ROW_HEIGHT)
		wx.EVT_TREE_BEGIN_LABEL_EDIT(self.tree, tID, self.OnTreeLabelEdit)
		wx.EVT_TREE_END_LABEL_EDIT(self.tree, tID, self.OnTreeLabelEditEnd)
		wx.EVT_TREE_ITEM_ACTIVATED(self.tree, tID, self.OnTreeItemActivated)

		# -------
		# Create the editor on the right.
		# -------
		self.editor = wx.TextCtrl(splitter, -1, style = wx.TE_MULTILINE)
		self.editor.Enable(0)

		# -------
		# Install the tree and the editor
		# -------
		splitter.SplitVertically(self.tree, self.editor)
		splitter.SetSashPosition(180, True)

		self.Show(True)

		# Some global state variables.
		self.projectdirty = False

	# -------
	# Some nice little handlers.
	# -------

	def project_open(self, project_file):
		try:
			input = open(project_file, 'r')

			self.tree.DeleteAllItems()

			self.project_file = project_file
			name = replace(input.readline(), '\n', '')
			self.SetTitle(name)
			self.root = self.tree.AddRoot(name)
			self.activeitem = self.root
			for line in input.readlines():
				self.tree.AppendItem(self.root, replace(line, '\n', ''))
			input.close()
			self.tree.Expand(self.root)

			self.editor.Clear()
			self.editor.Enable(False)

			self.projectdirty = False
		except IOError:
			pass

	def project_save(self):
		try:
			output = open(self.project_file, 'w+')
			output.write(self.tree.GetItemText(self.root) + '\n')

			count = self.tree.GetChildrenCount(self.root)
			iter = 0
			child = ''
			for i in range(count):
				if i == 0:
					(child, iter) = self.tree.GetFirstChild(self.root, iter)
				else:
					(child, iter) = self.tree.GetNextChild(self.root, iter)
				output.write(self.tree.GetItemText(child) + '\n')
			output.close()
			self.projectdirty = False
		except IOError:
			dlg_m = wx.MessageDialog(self, 'There was an error saving the project file.', 'Error!', wx.OK)
			dlg_m.ShowModal()
			dlg_m.Destroy()

	# -------
	# Event handlers from here on out.
	# -------
	def OnProjectOpen(self, event):
		open_it = True
		if self.projectdirty:
			dlg = wx.MessageDialog(self, 'The project has been changed. Save?', 'wxProject', wx.YES_NO | wx.CANCEL)
			result = dlg.ShowModal()
			if result == wx.ID_YES:
				self.project_save()
			if result == wx.ID_CANCEL:
				open_it = False
			dlg.Destroy()
		if open_it:
			dlg = wx.FileDialog(self, 'Choose a project to open', '.', '', '*.wxp', wx.OPEN)
			if dlg.ShowModal() == wx.ID_OK:
				self.project_open(dlg.GetPath())
			dlg.Destroy()

	def OnProjectNew(self, event):
		open_it = True
		if self.projectdirty:
			dlg = wxMessageDialog(self, 'The project has been changed. Save?', 'wxProject', wx.YES_NO | wx.CANCEL)
			result = dlg.ShowModal()
			if result == wx.ID_YES:
				self.project_save()
			if result == wx.ID_CANCEL:
				open_it = False
			dlg.Destroy()
		if open_it:
			dlg = wx.TextEntryDialog(self, 'Name for new project:', 'New Project', 'New project', wx.OK | wx.CANCEL)
			if dlg.ShowModal() == wx.ID_OK:
				newproj = dlg.GetValue()
				dlg.Destroy()
				dlg = wx.FileDialog(self, 'Place to store new project', '.', '', '*.wxp', wx.SAVE)
				if dlg.ShowModal() == wx.ID_OK:
					try:
						proj = open(dlg.GetPath(), 'w')
						proj.write(newproj + '\n')
						proj.close()
						self.project_open(dlg.GetPath())
					except IOError:
						dlg_m = wx.MessageDialog(self, 'There was an error saving the new project file.', 'Error!', wx.OK)
						dlg_m.ShowModal()
						dlg_m.Destroy()
		dlg.Destroy()

	def OnProjectExit(self, event):
		close = True
		if self.projectdirty:
			dlg = wx.MessageDialog(self, 'The project has been changed. Save?', 'wxProject', wx.YES_NO | wx.CANCEL)
			result = dlg.ShowModal()
			if result == wx.ID_YES:
				self.project_save()
			if result == wx.ID_CANCEL:
				close = False
			dlg.Destroy()
		if close:
			self.Close()

	def OnFileAdd(self, event):
		dlg = wx.FileDialog(self, 'Choose a file to add', '.', '', '*.*', wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			path = os.path.split(dlg.GetPath())
			self.tree.AppendItem(self.root, path[1])
			self.tree.Expand(self.root)
			self.project_save()

	def OnFileRemove(self, event):
		item = self.tree.GetSelection()
		if item != self.root:
			self.tree.Delete(item)
			self.project_save()

	def OnFileOpen(self, event):
		item = self.tree.GetSelection()

	def OnFileSave(self, event):
		if self.activeitem != self.root:
			self.editor.SaveFile(self.tree.GetItemText(self.activeitem))

	def OnTreeLabelEdit(self, event):
		item = event.GetItem()
		if item != self.root:
			event.Veto()

	def OnTreeLabelEditEnd(self, event):
		self.projectdirty = True

	def OnTreeItemActivated(self, event):
		go_ahead = True
		if self.activeitem != self.root:
			if self.editor.IsModified():
				dlg = wx.MessageDialog(self, 'The edited file has changed. Save it?', 'wxProject', wx.YES_NO | wx.CANCEL)
				result = dlg.ShowModal()
				if result == wx.ID_YES:
					self.editor.SaveFile(self.tree.GetItemText(self.activeitem))
				if result == wx.ID_CANCEL:
					go_ahead = False
				dlg.Destroy()
			if go_ahead:
				self.tree.SetItemBold(self.activeitem, 0)

		if go_ahead:
			item = event.GetItem()
			self.acitveitem = item
			if item != self.root:
				self.tree.SetItemBold(item, 1)
				self.editor.Enable(1)
				self.editor.LoadFile(self.tree.GetItemText(item))
				self.editor.SetInsertionPoint(0)
				self.editor.SetFocus()
			else:
				self.editor.Clear()
				self.editor.Enable(0)

class App (wx.App):
	def OnInit(self):
		frame = main_window(None, -1, 'wxProject - ' + projfile)
		self.SetTopWindow(frame)
		if (projfile != 'Unnamed'):
			frame.project_open(projfile)
		return True

app = App(0)
app.MainLoop()
