import wx
import config
import editor
import devices


class DeviceSelector(wx.Frame):

    def __init__(self,*args,**kw):
        kw['size']=(350,200)
        kw['style']= wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX
        super(DeviceSelector,self).__init__(*args,**kw)
        self.ports= config.get_ports()
        self.initUI()
        self.initEvents()
        self.CenterOnScreen()

    def initUI(self):
        self.pnl=wx.Panel(self)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(14)
        vbox = wx.BoxSizer(wx.VERTICAL)
        fila1 = wx.BoxSizer(wx.HORIZONTAL)
        fila3 = wx.BoxSizer(wx.HORIZONTAL)

        fg= wx.FlexGridSizer(rows=3,cols=2,gap=(10,10))
        label = wx.StaticText(self.pnl,label='Serial interface:' )
        self.info= wx.StaticText( self.pnl,label='#' )
        label.SetFont(font)
        serials=[c.device for c in self.ports]
        self.combo = wx.Choice(self.pnl,wx.ID_ANY,choices=serials)
        self.but   = wx.Button(self.pnl,wx.ID_ANY,label="Open")
        if len(serials) > 0: self.combo.SetSelection(0)
    
        fila1.Add(self.info,0,flag=wx.ALL | wx.EXPAND , border=2)
        fg.AddMany([
           (label),(self.combo,1,wx.EXPAND)     
        ])
        fila3.Add(self.but,flag= wx.CENTER | wx.ALL,border=2)
   
        
        vbox.Add(fg, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        vbox.Add(fila1)
        vbox.Add(fila3, proportion=1 ,flag=wx.CENTER)
        self.pnl.SetSizer(vbox)
        self.onChoice(None)

    def initEvents(self):
        self.combo.Bind(wx.EVT_CHOICE,self.onChoice)
        self.but.Bind(wx.EVT_BUTTON,self.onOpen)
    
    def onChoice(self,e):
        i=self.combo.GetSelection()
        if i != wx.NOT_FOUND:
            self.info.SetLabel('VID-PID:%s-%s | info:%s' % (self.ports[i].vid, self.ports[i].pid , self.ports[i].description ))
    
    def onOpen(self,e):
        devices.init_supported()
        i=self.combo.GetSelection()
        if i != wx.NOT_FOUND:
            prog = wx.ProgressDialog(title="Progress",message="...",maximum=2,parent=self)
            prog.Show()
            prog.Update(0,"Retrieve device ID...")
            self.config=config.BorosConfig(self.ports[i].device)
            found,product,model,version= self.config.get_version()
            if found:
                if devices.is_supported(product,model,version):
                    prog.Update(1,"Loading config...")
                    self.editor = editor.PropEditor(None,title="" + product + "-" + model + "V" + str(version))
                    self.editor.set_config(self.config)
                    self.editor.load_by_signature(product,model,version)
                    self.editor.from_device();
                    self.editor.Show()
                    prog.Update(2)
                else:
                    prog.Update(2)
                    wx.MessageBox("Device not supported. Update program","Error",wx.OK | wx.ICON_ERROR)
            else:
                prog.Update(2)
                wx.MessageBox("Device is not responding.Check device's connection",'Error',wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("No device selected",'Error',wx.OK | wx.ICON_ERROR)

def main():
    app = wx.App()
    ss  = DeviceSelector(None, title="Boros Configuration Tool")
    ss.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
