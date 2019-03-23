# Making a TK interface for the Pitch Pipe

from __future__ import division #Avoid division problems in Python 2

import tkinter #py3

import sys

import math
import pyaudio
import sys

import time
import numpy as np
import pickle

from temperament import *

temperaments = [ "quarter-comma meantone", "equal" ]

from tkinter import Tk, Label, Button
import tkinter.font as tkFont



class PitchPlayer:

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
        if self.stop_now:
            print("Stopping")
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
            print("Opening audio")
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



octaves = '1 2 3 4 5 6'.split()

class PitchPipe:
    
    def __init__(self, master):
        self.master = master
        master.title("Sone of a Pitch")

        row = 0
        self.label = Label(master, text='Root')
        self.label.grid(column=0,row=row)

        row+=1
        self.pitch = tkinter.StringVar(master)
        self.pitch.set('a') # default value
        self.pitches = tkinter.OptionMenu(master, self.pitch, *pitches,command=self.change_params)#"one", "two", "three")
        self.pitches.grid(column=0,row=row)

        self.octave = tkinter.StringVar(master)
        self.octave.set('4') # default value
        self.octaves = tkinter.OptionMenu(master, self.octave, *octaves, command=self.change_params)#"one", "two", "three")
        self.octaves.grid(column=1,row=row)

        

        row+=1

        self.playb = Button(master, text="Play", command=self.play)
        self.playb.grid(column=0,row=row)

        self.playing = False

        self.refnote = "a"
        self.refoct = 4
        self.basepitch = 415
        self.rootnote = 'a'
        self.temperament = MeanTone(self.rootnote,self.refnote,self.refoct,self.basepitch)

        self.player = PitchPlayer()
        self.update_pitch()


        
    def update_pitch(self):
        i = pitches.index(self.pitch.get())
        oct = int(self.octave.get())
        pitch = self.temperament.get_frequency(pitchlist_orig[i],oct)

        self.player.setpitch([pitch])



    def change_params(self,e):
        # When something has changed
        self.update_pitch()
        
        
    def play(self):
        if not self.playing:
            self.playing = True
            self.player.play()
            self.playb.configure(text='Stop')
        else:
            self.playing = False
            self.player.stop()
            self.playb.configure(text='Play')

root = Tk()

default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=18)

pp = PitchPipe(root)
root.mainloop()
