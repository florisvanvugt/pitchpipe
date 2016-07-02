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
import pickle

#pitches = "c c# d eb e f f# g g# a bb b".split(" ")
pitches = "a bb b c c# d eb e f f# g g#".split(" ")
basepitch = 415

temperaments = [ "quarter-comma meantone", "equal" ]


# For each note in the 12-note scale, this encodes how many fifths it is away
# from the tonic, first note in the scale. 
fifth_distance = np.array([ 0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5 ])
# Similarly, for each note in the scale, this encodes the "octave correction" that makes
# it end up in the right place relative to the starting pitch.
sec_pow        = np.array([ 0, 3, -1, 2, -2, 1, -3, 0, 3, -1, 2, -2 ])
temp_perf_fifth = np.power(5,.25)

# When you look at this, it makes sense: https://en.wikipedia.org/wiki/Quarter-comma_meantone


def get_freq_ratios(temperament):
    if temperament == "quarter-comma meantone":
        return np.power(temp_perf_fifth,fifth_distance)*np.power(2.,sec_pow)



class PitchPlayer:

    # How big chunks should be written at one time
    #CHUNKSIZE = 4096
    #CHUNKSIZE = 88200

    #AMPLITUDE = 127
    #OFFSET = 128

    AMPLITUDE = .25

    # Sampling rate
    RATE = 44100

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stop_now = True

    def get_chunk(self,frame_count):
        wav = self.AMPLITUDE*np.sin([ self.phase_offset + self.factor*x for x in xrange(frame_count) ])
        # Decide what the phase must be at the end of this buffer
        self.phase_offset = (self.phase_offset + frame_count*self.factor)%(2*math.pi)
        return wav.astype(np.float32)

    def callback(self,in_data, frame_count, time_info, status):
        chunk = self.get_chunk(frame_count)
        #print chunk
        self.allplayed.append(chunk)
        if self.stop_now:
            return (chunk, pyaudio.paComplete)
        else:
            return (chunk, pyaudio.paContinue)

    
    def setpitch(self,pitch):
        """ Update the frequency we should be playing (in Hz) """
        print("Setting pitch to",pitch)
        self.frequency = pitch
        self.allplayed = []
        self.factor = float(self.frequency) * (math.pi * 2) / self.RATE
        


    def play(self,pitch):
        #data = ''.join([chr(int(math.sin(x/((RATE/pitch)/math.pi))*127+128)) for x in xrange(RATE)])
        if self.stop_now: # only start a new stream if we aren't already playing
            self.stop_now = False
            self.phase_offset = 0 # the current phase of the sine wave
            self.setpitch(pitch)
            self.stream = self.p.open(format          = pyaudio.paFloat32,
                                      channels        = 1,
                                      rate            = self.RATE,
                                      output          = True,
                                      stream_callback = self.callback
                                  )

    def stop(self):
        #self.stream.stop_stream()
        self.stop_now = True
        #self.stream.close()
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
        self.selected_tone = None

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(400,700))
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

        topp = wx.BoxSizer(wx.HORIZONTAL)
        topp.Add( (10, -1) )
        topp.Add( wx.StaticText(panel, -1, "A (Hz) = ") )
        self.basepitch = wx.TextCtrl(panel, -1, "415", size=(175, -1))
        self.basepitch.Bind( wx.EVT_TEXT, self.textChange)
        topp.Add( self.basepitch )

        box.Add( (-1, 10) )
        box.Add( topp )


        topp = wx.BoxSizer(wx.HORIZONTAL)
        box.Add( (-1, 10) )

        topp.Add( wx.StaticText(panel, -1, "Octave (0 for base) = ") )
        self.octcorr = wx.TextCtrl(panel, -1, "0", size=(175, -1))
        self.octcorr.Bind( wx.EVT_TEXT, self.textChange)
        topp.Add( self.octcorr )
        box.Add(topp)

        self.temperchoice = wx.RadioBox(panel,label = 'Temperament', 
                                        choices = temperaments ,
                                        majorDimension = 1)
        box.Add(self.temperchoice)

        grid = wx.GridSizer(12,4,10,10)
        self.freqrat = []
        for i,pitch in enumerate(pitches):
            if i==0:
                rb = wx.RadioButton(panel,i, label = pitch,style = wx.RB_GROUP)
            else:
                rb = wx.RadioButton(panel,i, label = pitch)
            rb.Bind( wx.EVT_RADIOBUTTON,self.onRadioGroup)
            rb.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            grid.Add( (15,-1) )
            grid.Add( rb )
            rat = wx.StaticText(panel, -1, pitch) 
            self.freqrat.append ( rat )
            grid.Add( rat )
            grid.Add( wx.StaticText(panel, -1, pitch) )
        box.Add(grid)

        butp = wx.BoxSizer(wx.HORIZONTAL)

        m_play = wx.Button(panel, wx.ID_CLOSE, "Play")
        m_play.Bind(wx.EVT_BUTTON, self.ClickPlay)
        butp.Add(m_play, 0, wx.ALL, 10)

        m_stop = wx.Button(panel, wx.ID_CLOSE, "Stop")
        m_stop.Bind(wx.EVT_BUTTON, self.StopPlay)
        butp.Add(m_stop, 0, wx.ALL, 10)
        
        m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        butp.Add(m_close, 0, wx.ALL, 10)
        box.Add(butp)
        
        panel.SetSizer(box)
        panel.Layout()
        self.update_freqrat()



    def update_freqrat(self):
        self.freqrats = get_freq_ratios("quarter-comma meantone")
        for i,pitch in enumerate(pitches):
            self.freqrat[i].SetLabel("%03f"%self.freqrats[i])


    def onRadioGroup(self,e): 
        rb = e.GetEventObject()
        self.selected_tone = rb.GetId()
        self.update_pitch()
        #print rb.GetId(),' is clicked from Radio Group' 


    def textChange(self,e):
        self.update_pitch()


    def find_pitch(self):
        """ Find the pitch we should be playing, based on the current selections in the GUI """

        # Find the current base pitch
        basepitch = float(self.basepitch.GetValue().strip())

        # Find the octave correction
        octcorr = float(self.octcorr.GetValue().strip())

        # Now find the selected tone in the scale
        tone = self.selected_tone if self.selected_tone != None else 0

        # Find what the frequency ratio of that tone is relative to the currently
        # selected base pitch
        freqrat = self.freqrats[tone]
        freq = basepitch * freqrat * np.power(2.,octcorr)

        print("Playing frequency = %.2f Hz"%freq)
        return freq


    def update_pitch(self):
        freq = self.find_pitch()
        self.player.setpitch(freq)


    def ClickPlay(self, event):
        freq = self.find_pitch()
        self.player.play(freq)

    def StopPlay(self, event):
        self.player.stop()
    
        
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
