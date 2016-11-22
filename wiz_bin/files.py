# -*- coding: utf-8 -*-


import os, wx
from wx.lib.mixins import listctrl as LC

from dbr.buttons    import ButtonAdd
from dbr.buttons    import ButtonBrowse
from dbr.buttons    import ButtonClear
from dbr.buttons    import ButtonDel
from dbr.custom import OpenDir
from dbr.language   import GT
from globals.ident  import ID_FILES


ID_pin = 100
ID_fin = 101
ID_pout = 102

ID_AddDir = 140
ID_AddFile = 141
ID_Refresh = 142

home = os.getenv(u'HOME')


class DList(wx.ListCtrl, LC.ListCtrlAutoWidthMixin):#LC.TextEditMixin):
    """Creates a ListCtrl class in which every column's text can be edited"""
    def __init__(self, parent, ID=wx.ID_ANY):
        wx.ListCtrl.__init__(self, parent, ID, style=wx.BORDER_SIMPLE|wx.LC_REPORT)
        #LC.TextEditMixin.__init__(self)
        LC.ListCtrlAutoWidthMixin.__init__(self)


class Panel(wx.ScrolledWindow):
    """Class defining controls for the "Paths" page"""
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_FILES, name=GT(u'Files'))
        
        self.SetScrollbars(20, 20, 0, 0)
        
        # Create a Context Menu
        self.menu = wx.Menu()
        
        self.add_dir = wx.MenuItem(self.menu, ID_AddDir, GT(u'Add Folder'))
        self.add_file = wx.MenuItem(self.menu, ID_AddFile, GT(u'Add File'))
        self.refresh = wx.MenuItem(self.menu, ID_Refresh, GT(u'Refresh'))
        
        wx.EVT_MENU(self, ID_AddDir, self.AddPath)
        wx.EVT_MENU(self, ID_AddFile, self.AddPath)
        wx.EVT_MENU(self, ID_Refresh, self.OnRefresh)
        
        self.menu.AppendItem(self.add_dir)
        self.menu.AppendItem(self.add_file)
        self.menu.AppendSeparator()
        self.menu.AppendItem(self.refresh)
        
        # Directory listing for importing files and folders
        self.dir_tree = wx.GenericDirCtrl(self, -1, home, size=(300,20))
        
        wx.EVT_CONTEXT_MENU(self.dir_tree, self.OnRightClick)
        
        # ----- Add/Remove/Clear buttons
        path_add = ButtonAdd(self)
        path_remove = ButtonDel(self)
        button_clear = ButtonClear(self)
        
        wx.EVT_BUTTON(path_add, -1, self.AddPath)
        wx.EVT_BUTTON(path_remove, -1, self.DelPath)
        wx.EVT_BUTTON(button_clear, -1, self.ClearAll)
        
        # ----- Destination path
        # choices of destination
        self.radio_bin = wx.RadioButton(self, -1, u'/bin', style=wx.RB_GROUP)
        self.radio_usrbin = wx.RadioButton(self, -1, u'/usr/bin')
        self.radio_usrlib = wx.RadioButton(self, -1, u'/usr/lib')
        self.radio_locbin = wx.RadioButton(self, -1, u'/usr/local/bin')
        self.radio_loclib = wx.RadioButton(self, -1, u'/usr/local/lib')
        self.radio_cst = wx.RadioButton(self, -1, GT(u'Custom'))
        self.radio_cst.SetValue(True)
        
        # group buttons together
        self.radio_group = (self.radio_bin, self.radio_usrbin, self.radio_usrlib, self.radio_locbin, self.radio_loclib, self.radio_cst)
        
        # create an event to enable/disable custom widget
        for item in self.radio_group:
            wx.EVT_RADIOBUTTON(item, -1, self.SetDestination)
        
        # make them look pretty
        radio_sizer = wx.GridSizer(3, 2, 5, 5)
        for item in self.radio_group:
            radio_sizer.Add(item, 0)
        self.radio_border = wx.StaticBox(self, -1, GT(u'Target'), size=(20,20))
        radio_box = wx.StaticBoxSizer(self.radio_border, wx.HORIZONTAL)
        radio_box.Add(radio_sizer, 0)
        
        self.prev_dest_value = u'/usr/bin'
        self.dest_cust = wx.TextCtrl(self, -1, self.prev_dest_value)
        wx.EVT_KEY_DOWN(self.dest_cust, self.GetDestValue)
        wx.EVT_KEY_UP(self.dest_cust, self.CheckDest)
        cust_sizer = wx.BoxSizer(wx.VERTICAL)  # put the textctrl in own sizer so expands horizontally
        cust_sizer.Add(self.dest_cust, 1, wx.EXPAND)
        
        self.dest_browse = ButtonBrowse(self, ID_pout)
        
        wx.EVT_BUTTON(self.dest_browse, -1, self.OnBrowse)
        
        self.path_dict = {ID_pout: self.dest_cust}
        
        path_add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_add_sizer.Add(path_add, 0)
        path_add_sizer.Add(path_remove, 0)
        path_add_sizer.Add(button_clear, 0, wx.ALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(cust_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(self.dest_browse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        
        
        # Display area for files added to list
        self.dest_area = DList(self, -1)
        
        # List that stores the actual paths to the files
        self.list_data = []
        
        # Set the width of first column on creation
        parent_size = self.GetGrandParent().GetSize()
        parent_width = parent_size[1]
        self.dest_area.InsertColumn(0, GT(u'File'), width=parent_width/3-10)
        self.dest_area.InsertColumn(1, GT(u'Target'))
        
        wx.EVT_KEY_DOWN(self.dest_area, self.DelPath)
        
        LMR_sizer = wx.BoxSizer(wx.HORIZONTAL)
        LMR_sizer.Add(self.dest_area, 1, wx.EXPAND)
        
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page_sizer.AddSpacer(10)
        page_sizer.Add(radio_box, 0, wx.ALL, 5)
        page_sizer.Add(path_add_sizer, 0, wx.EXPAND|wx.ALL, 5)
        page_sizer.Add(LMR_sizer, 5, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        sizer = wx.FlexGridSizer(1, 2)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(1, 2)
        sizer.Add(self.dir_tree, 1, wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        sizer.Add(page_sizer, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        
        # Lists of widgets that change language
        self.setlabels = {	self.dest_browse: u'Custom' }
    
    
    def OnRightClick(self, event):
        # Show a context menu for adding files and folders
        path = self.dir_tree.GetPath()
        if os.path.isdir(path):
            self.add_dir.Enable(True)
            self.add_file.Enable(False)
        elif os.path.isfile(path):
            self.add_dir.Enable(False)
            self.add_file.Enable(True)
        self.dir_tree.PopupMenu(self.menu)
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event):
        main_window = wx.GetApp().GetTopWindow()
        
        if main_window.cust_dias.IsChecked() == True:
            dia = OpenDir(self)
            if dia.DisplayModal() == True:
                self.dest_cust.SetValue(dia.GetPath())
        else:
            dia = wx.DirDialog(self, GT(u'Choose Target Directory'), os.getcwd(), wx.DD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                self.dest_cust.SetValue(dia.GetPath())
    
    
    ## TODO: Doxygen
    def GetDestValue(self, event):
        if self.dest_cust.GetValue() != wx.EmptyString:
            if self.dest_cust.GetValue()[0] == u'/':
                self.prev_dest_value = self.dest_cust.GetValue()
        event.Skip()
    
    
    ## TODO: Doxygen
    def CheckDest(self, event):
        if self.dest_cust.GetValue() == wx.EmptyString:
            self.dest_cust.SetValue(self.prev_dest_value)
            self.dest_cust.SetInsertionPoint(-1)
        elif self.dest_cust.GetValue()[0] != u'/':
            self.dest_cust.SetValue(self.prev_dest_value)
            self.dest_cust.SetInsertionPoint(-1)
        event.Skip()
    
    
    ## TODO: Doxygen
    def AddPath(self, event):
        total_files = 0
        pin = self.dir_tree.GetPath()
        
        for item in self.radio_group:
            if self.radio_cst.GetValue() == True:
                pout = self.dest_cust.GetValue()
            elif item.GetValue() == True:
                pout = item.GetLabel()
        if os.path.isdir(pin):
            for root, dirs, files in os.walk(pin):
                for FILE in files:
                    total_files += 1
            
            if total_files: # Continue if files are found
                cont = True
                count = 0
                msg_files = GT(u'Getting files from {}')
                loading = wx.ProgressDialog(GT(u'Progress'), msg_files.format(pin), total_files, self,
                                            wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)
                for root, dirs, files in os.walk(pin):
                    for FILE in files:
                        if cont == (False,False):  # If "cancel" pressed destroy the progress window
                            break
                        else:
                            sub_dir = root.split(pin)[1] # remove full path to insert into listctrl
                            if sub_dir != wx.EmptyString:
                                # Add the sub-dir to dest
                                dest = u'{}{}'.format(pout, sub_dir)
                                #self.list_data.insert(0, (u'{}/{}'.format(root, FILE), u'{}/{}'.format(sub_dir[1:], FILE), dest))
                                self.list_data.insert(0, (u'{}/{}'.format(root, FILE), FILE, dest))
                                self.dest_area.InsertStringItem(0, FILE)
                                self.dest_area.SetStringItem(0, 1, dest)
                            else:
                                self.list_data.insert(0, (u'{}/{}'.format(root, FILE), FILE, pout))
                                self.dest_area.InsertStringItem(0, FILE)
                                self.dest_area.SetStringItem(0, 1, pout)
                            count += 1
                            cont = loading.Update(count)
                            if os.access(u'{}/{}'.format(root,FILE), os.X_OK):
                                self.dest_area.SetItemTextColour(0, u'red')
        
        elif os.path.isfile(pin):
            FILE = os.path.split(pin)[1]
            FILE = FILE.encode(u'utf-8')
            self.list_data.insert(0, (pin, FILE, pout))
            self.dest_area.InsertStringItem(0, FILE)
            self.dest_area.SetStringItem(0, 1, pout)
            if os.access(pin, os.X_OK):
                self.dest_area.SetItemTextColour(0, u'red')
    
    
    ## TODO: Doxygen
    def OnRefresh(self, event):
        path = self.dir_tree.GetPath()
#		if isfile(path):
#			path = os.path.split(path)[0]
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(path)
    
    
    ## TODO: Doxygen
    def SelectAll(self):
        total_items = self.dest_area.GetItemCount()
        count = -1
        while count < total_items:
            count += 1
            self.dest_area.Select(count)
    
    
    ## TODO: Doxygen
    def DelPath(self, event):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode == wx.WXK_DELETE:
            selected = [] # Items to remove from visible list
            toremove = [] # Items to remove from invisible list
            total = self.dest_area.GetSelectedItemCount()
            current = self.dest_area.GetFirstSelected()
            if current != -1:
                selected.insert(0, current)
                while total > 1:
                    total = total - 1
                    prev = current
                    current = self.dest_area.GetNextSelected(prev)
                    selected.insert(0, current)
            for path in selected:
                # Remove the item from the invisible list
                for item in self.list_data:
                    FILE = self.dest_area.GetItemText(path)
                    dest = self.dest_area.GetItem(path, 1).GetText()
                    if FILE.encode(u'utf-8') == item[1].decode(u'utf-8') and dest.encode(u'utf-8') == item[2].decode(u'utf-8'):
                        toremove.append(item)
                    
                self.dest_area.DeleteItem(path) # Remove the item from the visible list
            
            for item in toremove:
                self.list_data.remove(item)
            
        elif keycode == 65 and modifier == wx.MOD_CONTROL:
            self.SelectAll()
    
    
    ## TODO: Doxygen
    def ClearAll(self, event):
        confirm = wx.MessageDialog(self, GT(u'Clear all files?'), GT(u'Confirm'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.dest_area.DeleteAllItems()
            self.list_data = []
    
    
    ## TODO: Doxygen
    def SetDestination(self, event):
        # Event handler that disables the custom destination if the corresponding radio button isn't selected
        if self.radio_cst.GetValue() == True:
            self.dest_cust.Enable()
            self.dest_browse.Enable()
        else:
            self.dest_cust.Disable()
            self.dest_browse.Disable()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.radio_cst.SetValue(True)
        self.SetDestination(None)
        self.dest_cust.SetValue(u'/usr/bin')
        self.dest_area.DeleteAllItems()
        self.list_data = []
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        # Clear files list
        self.list_data = []
        self.dest_area.DeleteAllItems()
        files_data = data.split(u'\n')
        if int(files_data[0]):
            # Get file count from list minus first item "1"
            files_total = len(files_data)
            
            # Store missing files here
            missing_files = []
            
            while files_total > 1:
                files_total -= 1
                src = (files_data[files_total].split(u' -> ')[0], False)
                
                # False changes to true if src file is executable
                if src[0][-1] == u'*':
                    src = (src[0][:-1], True) # Set executable flag and remove "*"
                FILE = files_data[files_total].split(u' -> ')[1]
                dest = files_data[files_total].split(u' -> ')[2]
                
                # Check if files still exist
                if os.path.exists(src[0]):
                    self.dest_area.InsertStringItem(0, FILE)
                    self.dest_area.SetStringItem(0, 1, dest)
                    self.list_data.insert(0, (src[0], FILE, dest))
                    # Check if file is executable
                    if src[1]:
                        self.dest_area.SetItemTextColour(0, u'red') # Set text color to red
                else:
                    missing_files.append(src[0])
            
            # If files are missing show a message
            if len(missing_files):
                alert = wx.Dialog(self, -1, GT(u'Missing Files'))
                alert_text = wx.StaticText(alert, -1, GT(u'Could not locate the following files:'))
                alert_list = wx.TextCtrl(alert, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
                alert_list.SetValue(u'\n'.join(missing_files))
                button_ok = wx.Button(alert, wx.ID_OK)
                
                alert_sizer = wx.BoxSizer(wx.VERTICAL)
                alert_sizer.AddSpacer(5)
                alert_sizer.Add(alert_text, 1)
                alert_sizer.Add(alert_list, 3, wx.EXPAND)
                alert_sizer.Add(button_ok, 0, wx.ALIGN_RIGHT)
                
                alert.SetSizerAndFit(alert_sizer)
                alert.Layout()
                
                alert.ShowModal()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        file_list = []
        item_count = self.dest_area.GetItemCount()
        if item_count > 0:
            count = 0
            while count < item_count:
                item_file = self.dest_area.GetItemText(count)
                item_dest = self.dest_area.GetItem(count, 1).GetText()
                for item in self.list_data:
                    # Decode to unicode
                    i0 = item[0].encode(u'utf-8')
                    i1 = item[1].decode(u'utf-8')
                    i2 = item[2].encode(u'utf-8')
                    if i1 == item_file and i2.decode(u'utf-8') == item_dest:
                        item_src = i0
                # Populate list with tuples of ('src', 'file', 'dest')
                if self.dest_area.GetItemTextColour(count) == (255, 0, 0):
                    file_list.append((u'{}*'.format(item_src), item_file, item_dest))
                else:
                    file_list.append((item_src, item_file, item_dest))
                count += 1
        
            return_list = []
            for FILE in file_list:
                f0 = u'{}'.encode(u'utf-8').format(FILE[0])
                f1 = u'{}'.encode(u'utf-8').format(FILE[1])
                f2 = u'{}'.encode(u'utf-8').format(FILE[2])
                return_list.append(u'{} -> {} -> {}'.format(f0, f1, f2))
            return u'<<FILES>>\n1\n{}\n<</FILES>>'.format(u'\n'.join(return_list))
        else:
            # Place a "0" in FILES field if we are not saving any files
            return u'<<FILES>>\n0\n<</FILES>>'