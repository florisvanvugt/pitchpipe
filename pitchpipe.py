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
flat  = chr(0x266D) #unichr(0x266D)
sharp = chr(0x266F) #unichr(0x266F)
pitchlist = "a bes b c cis d ees e f fis g gis"
pitchlist = pitchlist.replace('is',sharp).replace('es',flat)
pitches = pitchlist.split(" ")
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
# Also, some cool sound examples https://en.wikipedia.org/wiki/Just_intonation

def get_freq_ratios(temperament):
    if temperament == "quarter-comma meantone":
        return np.power(temp_perf_fifth,fifth_distance)*np.power(2.,sec_pow)
    if temperament == "equal":
        # Equal temperament
        return np.power(2.,np.arange(0,12)/12.)
        




        

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

        # These control the playing of the sound. Each wave corresponds to an entry in all three lists
        self.pitches       = []  # the pitch (in Hz)
        self.factors       = []  # the factor: phase increment as a function of frame
        self.phase_offsets = []  # the current phase (when playing is active)





    def get_chunk(self,frame_count):
        # The wave associated with the scale note
        wav = np.zeros(frame_count)

        for (offset,factor) in zip(self.phase_offsets,self.factors):
            wav += self.AMPLITUDE*np.sin([ offset + factor*x for x in range(frame_count) ])

        # Update the phases: advance by factor*time for each
        self.phase_offsets = [ (offs + frame_count*fact)%(2*math.pi) for offs,fact in zip(self.phase_offsets,self.factors) ]

        return wav.astype(np.float32)



    def callback(self,in_data, frame_count, time_info, status):
        chunk = self.get_chunk(frame_count)
        #print chunk
        #self.allplayed.append(chunk)
        #print(chunk)
        if self.stop_now:
            return (chunk, pyaudio.paComplete)
        else:
            return (chunk, pyaudio.paContinue)


    
    def setpitch(self,pitch,base=None):
        """ 
        Update the frequency we should be playing (in Hz).
        Also, if base is not None then we also play the base note
        at the given frequency.
        """
        self.pitches = [pitch]
        if base!=None and base!=pitch:
            self.pitches.append(base)
        print ("Currently playing: %s"%(" ".join([ "%.02f"%p for p in self.pitches ])))
        # Compute the factors (phase increase per unit of time
        self.factors  = [ float(pitch) * (2 * math.pi) / self.RATE for pitch in self.pitches ]
        if len(self.phase_offsets)!=len(self.factors):
            self.reset_phases()

    



    def play(self):
        """ Starts playing, assuming that a correct pitch has been set. """
        #data = ''.join([chr(int(math.sin(x/((RATE/pitch)/math.pi))*127+128)) for x in xrange(RATE)])
        if self.stop_now: # only start a new stream if we aren't already playing
            self.stop_now = False
            self.reset_phases()
            self.stream = self.p.open(format          = pyaudio.paFloat32,
                                      channels        = 1,
                                      rate            = self.RATE,
                                      output          = True,
                                      stream_callback = self.callback
                                  )


    def reset_phases(self):
        self.phase_offsets = [ 0. for _ in self.pitches ]



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

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(400,750))
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
        topp.Add( wx.StaticText(panel, -1, "A4 (Hz) = ") )
        self.basepitch = wx.TextCtrl(panel, -1, "415", size=(175, -1))
        self.basepitch.Bind( wx.EVT_TEXT, self.textChange)
        topp.Add( self.basepitch )

        box.Add( (-1, 10) )
        box.Add( topp )

        topp = wx.BoxSizer(wx.HORIZONTAL)
        topp.Add( (10,-1) )
        self.sound_base = wx.CheckBox(panel, label = 'Play A sound too')
        self.sound_base.Bind(wx.EVT_CHECKBOX,self.onCheckBox)
        topp.Add(self.sound_base)
        box.Add( topp)

        box.Add( (-1, 10) )

        topp = wx.BoxSizer(wx.HORIZONTAL)
        topp.Add( (10,-1) )
        topp.Add( wx.StaticText(panel, -1, "Octave (0 for base) = ") )
        self.octcorr = wx.TextCtrl(panel, -1, "4", size=(100, -1))
        self.octcorr.Bind( wx.EVT_TEXT, self.textChange)
        topp.Add( self.octcorr )
        self.incrb = wx.Button(panel,  wx.ID_ADD,"+",size=(25,-1))
        self.incrb.Bind(wx.EVT_BUTTON, self.onOctaveChange)
        self.decrb = wx.Button(panel, wx.ID_DELETE, "-",size=(25,-1))
        self.decrb.Bind(wx.EVT_BUTTON,  self.onOctaveChange)
        topp.Add( self.decrb )
        topp.Add( self.incrb )
        box.Add(topp)

        self.temperchoice = wx.RadioBox(panel,label = 'Temperament', 
                                        choices = temperaments ,
                                        majorDimension = 1)
        self.temperchoice.Bind(wx.EVT_RADIOBOX,self.onTemperChoice)
        self.temperament = "quarter-comma meantone"
        box.Add(self.temperchoice)

        grid = wx.GridSizer(12,5,10,10)
        self.freqrat    = []
        self.centlabels = []
        self.hzs        = []
        for i,pitch in enumerate(pitches):
            lbl = " %s "%pitch
            if i==0:
                rb = wx.RadioButton(panel,i, label =lbl,style = wx.RB_GROUP)
            else:
                rb = wx.RadioButton(panel,i, label =lbl)
            rb.Bind( wx.EVT_RADIOBUTTON,self.onRadioGroup)
            rb.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            grid.Add( (15,-1) )
            grid.Add( rb )
            rat = wx.StaticText(panel, -1, pitch) 
            self.freqrat.append ( rat )
            grid.Add( rat )

            rat = wx.StaticText(panel, -1, pitch) 
            self.centlabels.append( rat)
            grid.Add( rat )

            rat = wx.StaticText(panel, -1, pitch) 
            self.hzs.append( rat)
            grid.Add( rat )
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
        # Update the frequencies associated with the steps in the scale
        self.freqrats = get_freq_ratios(self.temperament)
        logch = np.log2(self.freqrats)
        self.cents = logch*1200
        hzs = self.freqrats*self.get_base_pitch()

        # Update the labels to reflect these new frequencies
        for i,pitch in enumerate(pitches):
            self.freqrat[i].SetLabel("%.03f ratio"%self.freqrats[i])
            self.centlabels[i].SetLabel("%.01f cents"%self.cents[i])
            self.hzs[i].SetLabel("%.01f Hz"%hzs[i])


    def onRadioGroup(self,e): 
        rb = e.GetEventObject()
        self.selected_tone = rb.GetId()
        self.update_pitch()
        #print rb.GetId(),' is clicked from Radio Group' 


    def onTemperChoice(self,e):
        # Possibly a new temperament has been chosen
        self.temperament = self.temperchoice.GetStringSelection()
        self.update_freqrat()
        self.update_pitch()
        

    def onCheckBox(self,e):
        self.update_pitch()



    def textChange(self,e):
        self.update_pitch()


    def get_current_octave(self):
        octcorr = 4
        try:
            # Find the octave correction
            octcorr = int(self.octcorr.GetValue().strip())
        except:
            print ("Can't determine octave: invalid value")

        return octcorr



    def get_base_pitch(self):
        basep = 415
        try:
            # Find the octave correction
            basep = float(self.basepitch.GetValue().strip())
        except:
            print ("Can't determine base pitch: invalid value")

        octcorr = self.get_current_octave()
        return basep * np.power(2.,(octcorr-4))
        


    def onOctaveChange(self,e):
        # When people click the button to change the octave

        octcorr = self.get_current_octave()

        if e.GetEventObject()==self.incrb:
            octcorr+=1
        if e.GetEventObject()==self.decrb:
            octcorr-=1

        self.octcorr.SetValue(str(octcorr))

        self.update_freqrat()
        self.update_pitch()




    def find_pitch(self):
        """ Find the pitch we should be playing, based on the current selections in the GUI """

        # Find the current base pitch
        basepitch = self.get_base_pitch()

        # Now find the selected tone in the scale
        tone = self.selected_tone if self.selected_tone != None else 0

        # Find what the frequency ratio of that tone is relative to the currently
        # selected base pitch
        freqrat = self.freqrats[tone]
        freq = basepitch * freqrat

        if not self.sound_base.GetValue(): # if people checked the box that we should also play the base sound
            basepitch=None

        return (freq,basepitch)


    def update_pitch(self):
        freq,base = self.find_pitch()
        self.player.setpitch(freq,base)


    def ClickPlay(self, event):
        self.update_pitch()
        self.player.play()

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
