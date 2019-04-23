import devices
import wx
import config

class PropEditor(wx.Frame):
    
    def __init__(self,*args,**kw):
        kw['size']=(540,420)
        kw['style']= wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX
        super(PropEditor,self).__init__(*args,**kw)
        #devices.init_supported()
        #devices.dump_supported()
        self.initUI()
        self.initEvents()
        self.CenterOnScreen()
        
    def set_config(self,c):
        self.config=c
        
    def initUI(self):
        self.pnl=wx.Panel(self)
        self.font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.font.SetPointSize(14)
        
        main = wx.BoxSizer(wx.VERTICAL) # Main sizer
        self.tabs = wx.Notebook(self.pnl) # Tab Notebook
        main.Add(self.tabs,proportion=1,flag= wx.EXPAND,border=5)

        # Buttons
        grid=wx.GridSizer(1,3,15,15)
        self.but_exit=wx.Button(self.pnl,wx.ID_ANY,label="X exit")
        #self.but_exit.SetBackgroundColour(wx)
        self.but_reset=wx.Button(self.pnl,wx.ID_ANY,label="Factory reset")
        self.but_save= wx.Button(self.pnl,wx.ID_ANY,label="Send ->")
        self.but_save.SetForegroundColour("blue")
        grid.AddMany([(self.but_exit,1,wx.ALIGN_CENTER),
                      (self.but_reset,1,wx.ALIGN_CENTER),
                      (self.but_save,1,wx.ALIGN_CENTER)])
        main.Add(grid,proportion=1,flag= wx.EXPAND | wx.CENTER, border=5)
        self.pnl.SetSizer(main)

    def initEvents(self):
        self.but_exit.Bind(wx.EVT_BUTTON,self.onExit)
        self.but_reset.Bind(wx.EVT_BUTTON,self.onReset)
        self.but_save.Bind(wx.EVT_BUTTON,self.onSave)

    def onSave(self,e):
        cmds=[]
        for tab in self.device_spec['tabs']:
            for f in tab['cmds']:
                if f.validate():
                    #print(f.get_caption() +"->" + str(f.value_to_device()))
                    cmds.append(f.get_id() + " " + str(f.value_to_device()))
                else:
                    wx.MessageBox("Invalid value in '" + tab['name'] +"->" +f.get_caption() + "'.","Invalid input",wx.OK | wx.ICON_ERROR)
                    return
        # Now send the configuration
        failed_in=""
        total=len(cmds)
        p_total=0
        prog = wx.ProgressDialog(title="Progress",message="...",maximum=total,parent=self)
        prog.Show()
        for cmd in cmds:
            prog.Update(p_total+1,"Sending " + str(p_total+1) + " of " + str(len(cmds)))
            result,l= self.config.do_cmd(cmd)
            if result:
                p_total=p_total + 1
                total=total-1 
            else:
                failed_in=cmd
                break
        if(total>0):
            prog.Update(len(cmds))
            wx.MessageBox("Configuration not saved. Error reported by the device [" + failed_in +"].","Config not saved",wx.OK | wx.ICON_ERROR)
        else:
            prog.Update(len(cmds))
            wx.MessageBox("Configuration saved.","Saved",wx.OK | wx.ICON_INFORMATION)
                     

    def onExit(self,e):
        self.Close()

    def onReset(self,e):
        wx.MessageBox("TODO","TODO",wx.OK | wx.ICON_ERROR)

    def initUITabs(self):
        self.tab_pnl =[]
        for tab in self.device_spec['tabs']:
            pnl=wx.Panel(self.tabs)
            self.tab_pnl.append(pnl)
            self.tabs.AddPage(pnl,tab['name'])
            fg= wx.FlexGridSizer(rows=len(tab['cmds']),cols=2,gap=(5,5))
            fg.AddGrowableCol(1,1)
            pnl.SetSizer(fg)
            for cmd in tab['cmds']:
                f= cmd.wxGet(pnl)
                label=wx.StaticText(pnl,label=cmd.caption)
                fg.AddMany([
                    (label),(f,1,wx.EXPAND)
                ])


    def load_by_signature(self,pro,mod,ver):
        self.device_spec= devices.get_board(pro,mod,ver)
        if self.device_spec is not None:
            self.initUITabs()


    def load_val(self,key,value,from_device=False):
        if self.device_spec is None: return
        for tab in self.device_spec['tabs']:
            for field in tab['cmds']:
                if field.is_id(key): 
                    if from_device:
                        field.setV_from_device(value)
                    else:
                        field.setV(value)

    def load_values(self,attrs,from_device=False):
        if self.device_spec is None: return
        for a in attrs:
            self.load_val(a,attrs[a],from_device)

    def from_device(self):
        if self.device_spec is not None:
            attrs=self.config.get_config(self.device_spec['show_cmd'])
            self.load_values(attrs,True)

