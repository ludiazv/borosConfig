import serial
import serial.tools.list_ports as port_list
from time import sleep
import re

def get_ports():
    return port_list.comports()

class BorosConfig:

    def __init__(self,port,prompt=b'>'):
        self.ser=serial.Serial(port,9600,timeout=0.5)
        self.port=port
        self.prompt= prompt
        self.found_prompt=False
        sleep(0.5)
        self.ser.dtr=True
        sleep(0.1)
        self.ser.dtr=False
        sleep(0.5)
        if not self.wait_prompt(prompt): raise Exception('Devide is not responding')

    def wait_prompt(self,prompt):
        c=' '
        self.found_prompt=False
        while c!=b'':
            c=self.ser.read()
            if c==b'\n' and self.ser.read()==prompt:
                 self.found_prompt=True
                 break

        return self.found_prompt
        
    def do_cmd(self,cmd):
        if not self.found_prompt: raise Exception('Device is not ready')
        self.ser.write(cmd.encode('utf-8')+b'\n')
        sleep(0.1)
        lines=[]
        result = False
        self.found_promt=False
        for l in self.ser.readlines():
            l=l.strip()
            self.found_prompt= l==self.prompt
            if (l==b'' or l==cmd.encode('utf-8') or l==self.prompt): continue
            self.found_prompt= l==self.prompt
            if l==b'[OK]' or l==b'[ERROR]':
                result=(l==b'[OK]')
            else:
                lines.append(l.decode('utf-8'))
        return (result,lines)        
                
    def get_version(self):
        res,lines=self.do_cmd('ver')
        if res==True and len(lines)==1:
                m=re.match(r'(.+)\[(.+)<(.+)>V(.+)(\].+)',lines[0])
                if m is not None: return (True,m.group(2),m.group(3),int(m.group(4)))
        
        return (False,None,None,0)
        

    def get_config(self,cmd='show'):
        ok,attrs= self.do_cmd(cmd)
        if not ok: raise Exception("can't retrieve configuration")
        cnf={}
        for a in attrs:
            m= re.match(r'^\[(.+)\].*:(.+)',a)
            if m is not None: cnf[m.group(1)]=m.group(2)
        return cnf
