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

from tkinter import Tk, Label, Button, Entry
import tkinter.font as tkFont

import random

from player import *

import threading


FLIP_INTERVAL = 20 # how often we flip the pitches (in sec)

PITCH_CANDIDATES = ['fis','gis','a','b','cis','d','e'] # the options that are easily playable on duduk

# Based on a particular note, what are the possible continuations?
# This is coded as (interval,p) where p is some probability weight (not necessarily summing to one)
CONTINUATIONS = [ (7,5), # dominant (V)
                  (5,4), # subdominant (IV)
                  (2,3), # II
]



def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False, "Shouldn't get here"


class Accompany:
    
    def __init__(self, master,defaultfont):
        self.master = master
        master.title("Sone of a Pitch")

        row = 0
        self.label = Label(master, text='Not playing')
        self.label.grid(column=0,row=row)

        row+=1
        self.playb = Button(master, text="Play", command=self.play)
        self.playb.grid(column=0,row=row)
        
        self.nextb = Button(master, text="Next", command=self.tonext)
        self.nextb.grid(column=1,row=row)

        self.playing = False

        self.refnote = "a"
        self.refoct = 4
        self.basepitch = 440

        self.player = PitchPlayer()
        self.player.play() # play nothing
        self.current_note = None
        self.temperament = MeanTone('c',self.refnote,self.refoct,self.basepitch)


        
    def update_pitch(self):
        #note = label2note(self.pitch.get())
        #oct = int(self.octave.get())
        pitch = self.temperament.get_frequency(note,oct)
        self.player.setpitch([pitch])

    def change_params(self,e):
        # When something has changed
        self.update_temperament()
        self.update_pitch()


    def tonext(self):
        self.choose_pitch()
        

    def choose_pitch(self):
        # Pick a pitch to play
        if not self.current_note:
            self.current_note = random.choice(PITCH_CANDIDATES)
        else: # if there is already a current note
            # Define all possible continuations, with some relative probabilities
            options = [ (interval(self.current_note,0,i)[0],p)
                        for (i,p) in CONTINUATIONS ]
            # Restrict options to what is playable on the duduk
            options = [ (i,p) for (i,p) in options if pitch_in(i,PITCH_CANDIDATES) ]
            self.current_note = weighted_choice(options)
            print(self.current_note)
            
        basep,octv = self.current_note,3 # set the pitch
        self.temperament = MeanTone(basep,self.refnote,self.refoct,self.basepitch)
        pitches = [ (basep,octv-2),
            (basep,octv), interval(basep,octv,7)
        ]
        print(pitches)
        freqs = [ self.temperament.get_frequency(n,o) for (n,o) in pitches ]
        print(freqs)
        self.player.setpitch(freqs)
        self.label.configure(text=self.current_note)
        

        
    def play(self):
        if not self.playing:
            self.choose_pitch()
            self.playing = True
            self.player.play()
            self.playb.configure(text='Stop')
            self.thread = threading.Thread(target=regularflip)
            self.thread.start()
        else:
            self.current_note = None
            self.playing = False
            self.player.stop()
            self.playb.configure(text='Play')
            #if self.thread: # Thread should stop by itself
            #    self.thread.stop()



        

                
root = Tk()
            
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=22)

pp = Accompany(root,default_font)

def regularflip():
    t0 = time.time()
    while pp.playing:
        if time.time()-t0>FLIP_INTERVAL:
            print("Flipping pitches")
            pp.choose_pitch()
        time.sleep(.1) 


root.mainloop()
