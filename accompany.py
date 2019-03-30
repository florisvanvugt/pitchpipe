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
        pitch_candidates = ['b','fis','gis','a'] # the options
        basep,octv = random.choice(pitch_candidates),3 # pick a pitch
        self.temperament = MeanTone(basep,self.refnote,self.refoct,self.basepitch)
        pitches = [ (basep,octv-2),
            (basep,octv), interval(basep,octv,7)
        ]
        print(pitches)
        freqs = [ self.temperament.get_frequency(n,o) for (n,o) in pitches ]
        print(freqs)
        self.player.setpitch(freqs)
        
        
    def play(self):
        if not self.playing:
            self.choose_pitch()
            self.playing = True
            self.player.play()
            self.playb.configure(text='Stop')
        else:
            self.playing = False
            self.player.stop()
            self.playb.configure(text='Play')


root = Tk()
            
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=22)

pp = Accompany(root,default_font)
root.mainloop()
