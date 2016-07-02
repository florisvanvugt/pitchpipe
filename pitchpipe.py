#!/usr/bin/python
from __future__ import division #Avoid division problems in Python 2
#import wxversion
#wxversion.select("3.0")
import wx, wx.html
import sys
#import tkSnack

import math
import pyaudio
import sys

import time
import numpy as np

pitches = "c c# d eb e f f# g g# a bb b".split(" ")
basepitch = 415



import pickle


class PitchPlayer:

    # How big chunks should be written at one time
    #CHUNKSIZE = 4096
    #CHUNKSIZE = 88200

    #AMPLITUDE = 127
    #OFFSET = 128

    AMPLITUDE = .1

    # Sampling rate
    RATE = 44100

    def __init__(self):
        self.p = pyaudio.PyAudio()


    def get_chunk(self,frame_count):
        wav = self.AMPLITUDE*np.sin([ self.phase_offset + self.factor*x for x in xrange(frame_count) ])
        # Decide what the phase must be at the end of this buffer
        self.phase_offset = (self.phase_offset + frame_count*self.factor)%(2*math.pi)
        return wav.astype(np.float32)

    def callback(self,in_data, frame_count, time_info, status):
        chunk = self.get_chunk(frame_count)
        #print chunk
        self.allplayed.append(chunk)
        return (chunk, pyaudio.paContinue)

    def play(self,pitch):
        #data = ''.join([chr(int(math.sin(x/((RATE/pitch)/math.pi))*127+128)) for x in xrange(RATE)])
        self.phase_offset = 0 # the current phase of the sine wave
        self.frequency = pitch
        self.allplayed = []

        self.factor = float(self.frequency) * (math.pi * 2) / self.RATE

        self.stream = self.p.open(format          = pyaudio.paFloat32,
                                  channels        = 1,
                                  rate            = self.RATE,
                                  output          = True,
                                  stream_callback = self.callback
                              )


    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        #pickle.dump(self.allplayed,open('chunk.pickle','wb'))
        

    def close(self):
        self.p.terminate()




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
        self.player = PitchPlayer()

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
        
        m_text = wx.StaticText(panel, -1, "Sone of a pitch")
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
        self.player.play(415)

    def StopPlay(self, event):
        self.player.stop()
        #pass
    
        
    def OnClose(self, event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()  

app = wx.App() # redirect=True)   # Error messages go to popup window
top = Frame("Pitch Pipe")
top.Show()
app.MainLoop()
