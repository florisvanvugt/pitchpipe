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

from temperament import *

temperaments = [ "quarter-comma meantone", "equal" ]



        

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


    
    def setpitch(self,pitch):
        """ 
        Update the frequency we should be playing (in Hz).
        Also, if base is not None then we also play the base note
        at the given frequency.
        """
        self.pitches = pitch
        print ("Currently playing: %s"%(" ".join([ "%.02f"%p for p in self.pitches ])))
        # Compute the factors (phase increase per unit of time
        self.factors  = [ float(pitch) * (2 * math.pi) / self.RATE for pitch in self.pitches ]
        if len(self.phase_offsets)!=len(self.factors):
            self.reset_phases()
        # TODO: instead of resetting phases we could do something smarter, namely
        # take the existing phases of oscillators we are keeping, and only
        # resetting phases of oscillators that are "new".
    



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




        
class Frame(wx.Frame):

    def __init__(self, title):
        self.player = PitchPlayer()
        self.selected_tone = None

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(600,850))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
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

        self.temperchoice = wx.RadioBox(panel,label = 'Temperament', 
                                        choices = temperaments ,
                                        majorDimension = 1)
        self.temperchoice.Bind(wx.EVT_RADIOBOX,self.onRootChange)
        self.temperament = "quarter-comma meantone"
        box.Add(self.temperchoice)

        topp = wx.BoxSizer(wx.HORIZONTAL)
        topp.Add( (10,-1) )

        rootp = wx.BoxSizer(wx.VERTICAL)
        rootp.Add( wx.StaticText(panel, -1, "Root") )

        octp = wx.BoxSizer(wx.HORIZONTAL)
        octp.Add( (10,-1) )
        octp.Add( wx.StaticText(panel, -1, "Octave") )
        self.octcorr = wx.TextCtrl(panel, -1, "4", size=(50, -1))
        self.octcorr.Bind( wx.EVT_TEXT, self.textChange)
        octp.Add( self.octcorr )
        self.incrb = wx.Button(panel,  wx.ID_ADD,"+",size=(25,-1))
        self.incrb.Bind(wx.EVT_BUTTON, self.onOctaveChange)
        self.decrb = wx.Button(panel, wx.ID_DELETE, "-",size=(25,-1))
        self.decrb.Bind(wx.EVT_BUTTON,  self.onOctaveChange)
        octp.Add( self.decrb )
        octp.Add( self.incrb )
        rootp.Add(octp)

        self.root_notes = []
        for i,pitch in enumerate(pitches):
            lbl = " %s "%pitch
            if i==0:
                rb = wx.RadioButton(panel,i, label =lbl,style = wx.RB_GROUP)
            else:
                rb = wx.RadioButton(panel,i, label =lbl)
            rb.Bind( wx.EVT_RADIOBUTTON,self.onRootChange)
            rb.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.root_notes.append(rb)
            #grid.Add( (15,-1) )
            rootp.Add( rb )
        topp.Add(rootp)
        topp.Add( (30,-1) )
        
        grid = wx.GridSizer(12,4,10,10)
        self.pitchnames = []
        self.freqrat    = []
        self.centlabels = []
        self.hzs        = []
        for i,pitch in enumerate(pitches):
            lbl = " %s "%pitch
            rb = wx.CheckBox(panel,i, label =lbl, size = (100,-1))
            #if i==0:
            #    rb = wx.RadioButton(panel,i, label =lbl,style = wx.RB_GROUP)
            #else:
            #    rb = wx.RadioButton(panel,i, label =lbl)
            rb.Bind( wx.EVT_CHECKBOX,self.onRadioGroup)
            rb.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            #grid.Add( (15,-1) )
            self.pitchnames.append( rb )
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

        topp.Add( grid )
        box.Add(topp)

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
        self.update_from_root()
        self.update_freqrat()



    def update_freqrat(self):
        """ 
        Updates the listed frequencies in the GUI.
        This assumes that self.candidate_notes is set correctly.
        Also, self.temperament should point to a working
        temperament object.
        You can run self.update_from_root() to do these.
        """
        self.freq = []
        for i,(note,octv) in enumerate(self.candidate_notes):
            hz = self.temperament.get_frequency(note,octv)
            self.freq.append(hz)
        self.freqrats = np.array(self.freq)/self.freq[0] # compute the frequency ratios relative to the first note
        logch = np.log2(self.freqrats)
        self.cents = logch*1200
        
        # Update the labels to reflect these new frequencies
        for i,pitch in enumerate(pitches):
            self.freqrat[i].SetLabel("%.03f ratio"%self.freqrats[i])
            self.centlabels[i].SetLabel("%.01f cents"%self.cents[i])
            self.hzs[i].SetLabel("%.01f Hz"%self.freq[i])

            
    def get_root_note(self):
        """ Return the currently selected root note (including its octave). """
        octave = self.get_current_octave()
        note   = self.get_current_root_name()
        return (note,octave)


    def get_current_octave(self):
        octcorr = 4 # the default octave
        try:
            # Find the octave correction
            octcorr = int(self.octcorr.GetValue().strip())
        except:
            print ("Can't determine octave: invalid value")

        return octcorr

    def get_current_root_name(self):
        """ Return (as string) the name of the current root note (not its octave)."""
        for root in self.root_notes:
            if root.GetValue():
                return pitchlist_orig[root.GetId()]


    def update_from_root(self):
        """ This should be called when the root note has changed.
        We will update the notes on the right hand side """
        (rootnote,octave) = self.get_root_note()
        rootidx = pitchlist_orig.index(rootnote)
        self.candidate_notes = []
        for i,pitchb in enumerate(self.pitchnames):
            j = (i+rootidx)
            idx = j%12
            nm = pitches[ idx ]
            octv=octave
            if j>=12: octv+=1
            self.candidate_notes.append( (pitchlist_orig[ idx ], octv) )
            pitchb.SetLabel(" %s%i "%(nm,octv))

        # Now let's create a temperament object, depending on which temperament
        # was chosen.
        refnote = "a"
        refoct = 4
        basepitch = self.get_base_pitch()
        
        temper = self.temperchoice.GetStringSelection()
        if temper=="equal":
            self.temperament = EqualTemperament(refnote,refoct,basepitch)
        elif temper=="quarter-comma meantone":
            self.temperament = MeanTone(rootnote,refnote,refoct,basepitch)
        else:
            print("Unknown temperament %s!"%temper)
            

    def onRootChange(self,e):
        """ This is when the root note changes (or its octave). """
        self.rootnote = self.get_root_note()
        self.update_from_root()
        self.update_freqrat()
        self.update_pitch()
        #print rb.GetId(),' is clicked from Radio Group' 


        
    def onRadioGroup(self,e): 
        rb = e.GetEventObject()
        self.selected_tone = rb.GetId()
        self.update_pitch()
        #print rb.GetId(),' is clicked from Radio Group' 

        


    def onCheckBox(self,e):
        self.update_pitch()



    def textChange(self,e):
        self.update_pitch()


    def get_base_pitch(self):
        basep = 415
        try:
            # Find the octave correction
            basep = float(self.basepitch.GetValue().strip())
        except:
            print ("Can't determine base pitch: invalid value")
            
        return basep
        


    def onOctaveChange(self,e):
        # When people click the button to change the octave

        octcorr = self.get_current_octave()

        if e.GetEventObject()==self.incrb:
            octcorr+=1
        if e.GetEventObject()==self.decrb:
            octcorr-=1

        self.octcorr.SetValue(str(octcorr))

        self.update_from_root()
        self.update_freqrat()
        self.update_pitch()




    def find_pitch(self):
        """ Find the pitch we should be playing, based on the current selections in the GUI """

        pitches = []
        for i,nm in enumerate(self.pitchnames): # iterate through the candidate notes
            if nm.GetValue(): # if this one is selected
                pitches.append( self.freq[ i ])
                
        return pitches


    def update_pitch(self):
        pitches = self.find_pitch()
        self.player.setpitch(pitches)


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
