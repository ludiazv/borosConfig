import  string
import  wx
import  wx.lib.intctrl
import  re

class ConfigCommand:
    def __init__(self,**kw):
        if (kw is not None) and ('id' in kw) and ('val' in kw):
            self.id=kw['id']
            self.val=kw['val']
            self.wxg=None
            self.caption=""
            if 'caption' in kw:
                self.caption=kw['caption'] 
        else:
            raise "Invalid parameter for command: id && val keys are required"

    def is_id(self,id):
        return self.id == id
    
    def get_id(self):
        return self.id

    def get_caption(self):
        return self.caption

    def caption(self):
        return self.caption

    def is_set(self):
        return True

    def validate(self):
        return True

    def value(self):
        self.val= self.fromWx()
        return self.val

    def value_to_device(self):
        return str(self.value())
    
    def setV(self,v):
        self.val=v

    def setV_from_device(self,v):
        self.setV(v)
    
    def wxGet(self,continer,**kwargs):
        pass

    def toWx(self):
        if self.wxg is not None:
            self.wxg.SetValue(self.val)
    
    def fromWx(self):
        if self.wxg is not None:
            return self.wxg.GetValue()
    

class CCText(ConfigCommand):

    def __init__(self,**kw):
        super().__init__(**kw)
        if 'maxlen' in kw:
            self.maxlen = kw['maxlen']
        else:
            self.maxlen=32

    def setV(self,v):
        if len(v) > self.maxlen:
            self.val= v[:self.maxlen]
        else:
            self.val=v
        self.toWx()

    def wxGet(self,container,**kwargs):
        self.wxg=wx.TextCtrl(container,wx.ID_ANY)
        self.wxg.SetMaxLength(self.maxlen)
        return self.wxg
    

class CCHex(ConfigCommand):

    def check_hex(self,v):
        return all(c in string.hexdigits for c in v)

    def invert(self,v):
        r= re.compile("[" +string.hexdigits + "]["+string.hexdigits+"]")
        inv = re.findall(r,v)
        if len(inv) > 0:
            return ''.join(inv[::-1])
        else:
            return ''
    
    def __init__(self,**kw):
        super().__init__(**kw)
        if 'maxlen' in kw:
            self.maxlen = kw['maxlen']*2
        else:
            self.maxlen=4
        
        if 'lsb' in kw:
            self.lsb = kw['lsb']
        else:
            self.lsb  = False

    def setV(self,v):
        if self.check_hex(v):
            self.val= v
        self.toWx()

    def value_to_device(self):    
        if self.lsb:
            return self.invert(self.value())
        else:
            return self.value()

    def setV_from_device(self,v):
        if self.lsb:
            self.setV(self.invert(v))
        else:
            self.setV(v)

    def validate(self):
        return self.check_hex(self.value())

    def wxGet(self,container,**kwargs):
        self.wxg=wx.TextCtrl(container,wx.ID_ANY)
        self.wxg.SetMaxLength(self.maxlen)
        return self.wxg
    

class CCChoice(ConfigCommand):

    def __init__(self,**kw):
        super().__init__(**kw)
        if 'default' in kw:
            self.selected=kw['default']
        else:
            self.selected=0
    
    def value(self):
        return self.val[self.selected]['val']
    
    def setV(self,val):
        v=int(val)
        i=0
        for n in self.val:
            if n['val'] == v:
                self.selected = i
                self.wxg.SetSelection(i)
                break
            i=i+1
                
    def wxEvent(self,e):
        n=e.GetEventObject().GetSelection()
        if n != wx.NOT_FOUND :
            self.selected=n

    def wxGet(self,container,**kwargs):
        cho=[c['desc'] for c in self.val]
        self.wxg=wx.Choice(container,wx.ID_ANY,choices=cho)
        self.wxg.SetSelection(self.selected)
        self.wxg.Bind(wx.EVT_CHOICE,self.wxEvent)
        return self.wxg



class CCBool(CCChoice):

    boolChoice = [ { 'desc':'No' , 'val': 0 } , {'desc': 'Yes', 'val': 1} ]

    def __init__(self,**kw):
        kw['val'] = CCBool.boolChoice
        super().__init__(**kw)


class CCInt(ConfigCommand):

    def __init__(self,**kw):
        super().__init__(**kw)
        if 'vmin' in kw:
            self.min=kw['vmin']
        else:
            self.min=0
        if 'vmax' in kw:
            self.max=kw['vmax']
        else:
            self.max=255

    def setV(self,val):
        self.val=int(val)
        self.toWx()

    def validate(self):
        return (self.val >= self.min and self.val <= self.max)

    def wxGet(self,container,**kwargs):
        self.wxg= wx.lib.intctrl.IntCtrl(container,id=wx.ID_ANY,
                        value= self.val,
                        min=self.min,max=self.max, allow_none=False,
                        limited=True,allow_long=True)
        #self.wxg.ChangeValue(self.val)
        return self.wxg
    

supported_devices= []

def init_supported():
    # Boros Reed
    # ----------------------------------------
    borosreed_common= [
            CCBool(id="inv",caption="Invert reed",default=0),
            CCBool(id="led",caption="Enable Led",default=0),
            CCBool(id="eint",caption="Enable Ext Int",default=0),
            CCInt( id="id", caption="Device Id",val=0,vmin=0,vmax=65536),
            CCInt( id="repo", caption="Periodic report",val=0,vmin=0,vmax=65536),
            #CCInt( id="acc",  caption="Sensor Accuracy",val=0,vmin=0,vmax=255),
            CCText( id="tpl", caption="Payload template", val="", maxlen=64)
    ]
    
    borosreed24_general_tab= {
        'name': 'general',
        'layout': 'vertical',
        'cmds': borosreed_common + [   
                    CCChoice( id="mode", caption="Radio Mode", default=0, val=[
                      { 'val': 0 , 'desc':'Plain RF24'},
                      { 'val': 1 , 'desc':'RF24 Mesh' }
                    ])
                ]   
    }

    borosreed24_rf_common = [
        CCChoice( id="txp", caption="Radio Tx Power", default=1, val=[
                      { 'val': 0 , 'desc':'Min'},
                      { 'val': 1 , 'desc':'Low' },
                      { 'val': 2 , 'desc':'High'},
                      { 'val': 3 , 'desc':'Max'},
                      { 'val': 4 , 'desc':'Ultra'}
                 ]),
        CCChoice( id="rate", caption="Date rate", default=1, val=[
                      { 'val': 3 , 'desc':'250Kbps'},
                      { 'val': 0 , 'desc':'1Mbps' },
                      { 'val': 2 , 'desc':'2Mbps'}
                 ]),
        CCInt( id="cha",  caption="Radio Channel",val=76,vmin=1,vmax=126)
        
    ]

    borosreed24_rf_common_tab = {
        'name': 'Channel/Power/DataRate',
        'layout': 'vertical',
        'cmds' : borosreed24_rf_common
    }

    borosreed24_rf_plain= [
        CCChoice( id="psz", caption="Address length", default=3, val=[
                      { 'val': 3 , 'desc':'3 bytes'},
                      { 'val': 4 , 'desc':'4 bytes' },
                      { 'val': 5 , 'desc':'5 bytes'}
                 ]),
        CCHex(    id="pipe", caption="Destination Address", val="AABBCCDDEE", maxlen=5, lsb=True),
        CCInt(    id="dsz",  caption="Payload size",val=32,vmin=1,vmax=32),
        CCBool(   id="ack", caption="Ack",default=1),
        CCChoice( id="crc", caption="CRC", default=2, val=[
                      { 'val': 0 , 'desc':'Disabled'},
                      { 'val': 1 , 'desc':'8bit CRC' },
                      { 'val': 2 , 'desc':'16bit CRC'}
                 ]),
        CCInt(    id="retr",caption="# retries",val=6,vmin=0,vmax=15),
        CCInt(    id="retd",caption="Retry delay",val=8,vmin=0,vmax=15)

    ]
    borosreed24_rf_plain_tab={
        'name': 'NRF24L01 Plain',
        'layout': 'vertical',
        'cmds': borosreed24_rf_plain
    }
   
    borosreed24_rf_mesh = [
         CCInt(   id="mnid",caption="NodeID",val=1,vmin=1,vmax=254),
         CCInt(   id="mdst",caption="Destination NodeID",val=0,vmin=0,vmax=254),
         CCInt(   id="mfid",caption="Frame ID",val=42,vmin=0,vmax=255),
         CCBool(  id="mfor",caption="Force Mesh renew",default=0)
    ]
    borosreed24_rf_mesh_tab = {
        'name': 'RF24 Mesh',
        'layout': 'vertical',
        'cmds': borosreed24_rf_mesh
    }

    borosreed24 = {
        'signature': ('BR','24M',3),
        'show_cmd': 'show',
        'factory_cmd': 'fac',
        'tabs': [ 
            borosreed24_general_tab,
            borosreed24_rf_common_tab,
            borosreed24_rf_plain_tab,
            borosreed24_rf_mesh_tab
        ]
    }

    supported_devices.append(borosreed24)

    # Boros Reed TTN
    borosreedTTN_general_tab= {
        'name': 'General',
        'layout': 'vertical',
        'cmds': borosreed_common + [   
                    CCChoice( id="mode", caption="Radio Mode", default=0, val=[
                      { 'val': 2 , 'desc':'The things Network LoRaWan'}
                    ])
                ]   
    }

    borosreedTTN_rf_lorawan=[
        CCHex(    id="dui", caption="Device EUI", val="1122334455667788", maxlen=8, lsb=True),
        CCHex(    id="aui", caption="Application EUI", val="1122334455667788", maxlen=8, lsb=True),
        CCHex(    id="apk", caption="Application Key", val="00112233445566778899AABBCCDDEEFF", maxlen=16, lsb=False),
        CCInt(    id="por", caption="Port",val=1,vmin=0,vmax=255),
        CCChoice( id="cha", caption="Force channel", default=0, val=[
                      { 'val': 255 , 'desc':'Not forced'},
                      { 'val': 0   , 'desc':'1st of subband' },
                      { 'val': 1   , 'desc':'2nd of subband'},
                      { 'val': 2   , 'desc':'3rd of subband'},
                      { 'val': 3   , 'desc':'4th of subband'},
                      { 'val': 4   , 'desc':'5th of subband'},
                      { 'val': 5   , 'desc':'6th of subband'},
                      { 'val': 6   , 'desc':'7th of subband'},
                      { 'val': 7   , 'desc':'8th of subband'},
                 ]),
        
        CCChoice( id="sf", caption="Spread Factor", default=0, val=[
                      { 'val': 255 , 'desc':'Not forced'},  
                      { 'val': 7 , 'desc':'7'},
                      { 'val': 8 , 'desc':'8'},
                      { 'val': 9 , 'desc':'9'},
                      { 'val': 10 , 'desc':'10'},
                      { 'val': 11 , 'desc':'11'},
                      { 'val': 12 , 'desc':'12'},
            ]),

        CCChoice( id="jsf", caption="Join Spread Factor", default=0, val=[
                      { 'val': 255 , 'desc':'Not forced'},
                      { 'val': 7 , 'desc':'7'},
                      { 'val': 8 , 'desc':'8'},
                      { 'val': 9 , 'desc':'9'},
                      { 'val': 10 , 'desc':'10'},
                      { 'val': 11 , 'desc':'11'},
                      { 'val': 12 , 'desc':'12'},
            ]),            
    ]

    borosreedTTN_rf_lorawan_tab= {
        'name': 'LoRaWan',
        'layout': 'vertical',
        'cmds': borosreedTTN_rf_lorawan 
    }

    borosreedTTN = {
        'signature': ('BR','TTN',3),
        'show_cmd': 'show',
        'factory_cmd': 'fac',
        'tabs': [ 
            borosreedTTN_general_tab,
            borosreedTTN_rf_lorawan_tab
        ]
    }
    supported_devices.append(borosreedTTN)
    # ----------
    # Boros Met24
    borosmet_common= [
            #CCBool(id="inv",caption="Invert reed",default=0),
            CCBool(id="led",caption="Enable Led",default=0),
            CCBool(id="eint",caption="Enable Ext Int",default=0),
            CCInt( id="id", caption="Device Id",val=0,vmin=0,vmax=65536),
            CCInt( id="repo", caption="Periodic report",val=0,vmin=0,vmax=65536),
            CCInt( id="acc",  caption="Sensor Accuracy",val=0,vmin=0,vmax=255),
            CCText( id="tpl", caption="Payload template", val="", maxlen=64)
    ]

    # Boros Met TTN
    borosmetTTN_general_tab= {
        'name': 'General',
        'layout': 'vertical',
        'cmds': borosmet_common + [   
                    CCChoice( id="mode", caption="Radio Mode", default=0, val=[
                      { 'val': 2 , 'desc':'The things Network LoRaWan'}
                    ])
                ]   
    }

    borosmetTTN = {
        'signature': ('BM','TTN',3),
        'show_cmd': 'show',
        'factory_cmd': 'fac',
        'tabs': [ 
            borosmetTTN_general_tab,
            borosreedTTN_rf_lorawan_tab
        ]
    }
    supported_devices.append(borosmetTTN)





def get_board(product,model,version):
    for sp in supported_devices:
        pro,mod,ver = sp['signature']
        if pro==product and mod==model and ver==version:
            return sp 
    return None

def is_supported(product,model,version):
    return (get_board(product,model,version) is not None)

def dump_supported():
    print(supported_devices)