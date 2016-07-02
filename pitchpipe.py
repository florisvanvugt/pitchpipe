#!/usr/bin/python
from __future__ import division #Avoid division problems in Python 2
import wxversion
wxversion.select("3.0")
import wx, wx.html
import sys
import tkSnack

import math
import pyaudio
import sys

pitches = "c c# d eb e f f# g g# a bb b".split(" ")
basepitch = 415



def playpitch(pitch):

    PyAudio = pyaudio.PyAudio
    RATE = 44100
    data = ''.join([chr(int(math.sin(x/((RATE/pitch)/math.pi))*127+128)) for x in xrange(RATE)])
    p = PyAudio()

    stream = p.open(format =
                    p.get_format_from_width(1),
                    channels = 1,
                    rate = RATE,
                    output = True)
    for DISCARD in xrange(5):
        stream.write(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    



aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>""" 

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())
        
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About <<project>>",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,600))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)
        
        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        
        m_text = wx.StaticText(panel, -1, "Pitch Pipe")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text.SetSize(m_text.GetBestSize())
        box.Add(m_text, 0, wx.ALL, 10)

        grid = wx.GridSizer(12,3,10,10)
        for i,pitch in enumerate(pitches):
            if i==0:
                rb = wx.RadioButton(panel,11, label = pitch,style = wx.RB_GROUP)
            else:
                rb = wx.RadioButton(panel,11, label = pitch)
            grid.Add( rb )
            grid.Add( wx.StaticText(panel, -1, pitch) )
            grid.Add( wx.StaticText(panel, -1, pitch) )
        box.Add(grid)

        m_play = wx.Button(panel, wx.ID_CLOSE, "Play")
        m_play.Bind(wx.EVT_BUTTON, self.ClickPlay)
        box.Add(m_play, 0, wx.ALL, 10)

        m_stop = wx.Button(panel, wx.ID_CLOSE, "Stop")
        m_stop.Bind(wx.EVT_BUTTON, self.StopPlay)
        box.Add(m_stop, 0, wx.ALL, 10)
        
        m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        box.Add(m_close, 0, wx.ALL, 10)
        
        panel.SetSizer(box)
        panel.Layout()


    def ClickPlay(self, event):
        playpitch(415)

    def StopPlay(self, event):
        pass
    
        
    def OnClose(self, event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()  

app = wx.App(redirect=True)   # Error messages go to popup window
top = Frame("Pitch Pipe")
top.Show()
app.MainLoop()
