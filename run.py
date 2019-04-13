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


from player import *



octaves = '1 2 3 4 5 6 7'.split()

class PitchPipe:
    
    def __init__(self, master,defaultfont):
        self.master = master
        master.title("Sone of a Pitch")

        row = 0
        self.label = Label(master, text='Mean-tone')
        self.label.grid(column=0,row=row)

        row+=1
        self.label = Label(master, text='Root')
        self.label.grid(column=0,row=row)
        self.rootnote = tkinter.StringVar(master)
        self.rootnote.set(pitches[0]) # default value
        self.root_sel = tkinter.OptionMenu(master, self.rootnote,*pitches,command=self.change_params)#"one", "two", "three")
        self.root_sel.configure(width=10)
        self.root_sel.grid(column=1,row=row)
        master.nametowidget(self.root_sel.menuname).config(font=defaultfont)
        
        row+=1
        self.label = Label(master, text='Base a4=')
        self.label.grid(column=0,row=row)

        self.basea = tkinter.StringVar(master)
        self.basea.set('415')
        self.e_basea = Entry(master,textvariable=self.basea)
        self.e_basea.grid(column=1,row=row)
        
        self.label = Label(master, text='Hz')
        self.label.grid(column=2,row=row)

        self.updateb = Button(master,text='update',command=self.update_temperament)
        self.updateb.grid(column=3,row=row)
        
        row+=1
        self.pitch = tkinter.StringVar(master)
        self.pitch.set(pitches[0]) # default value
        self.pitches = tkinter.OptionMenu(master, self.pitch,*pitches,command=self.change_params)#"one", "two", "three")
        self.pitches.configure(width=10)
        self.pitches.grid(column=0,row=row)
        master.nametowidget(self.pitches.menuname).config(font=defaultfont)

        octavep = tkinter.Frame(master)
        octavep.grid(column=1,row=row)
        self.octave = tkinter.StringVar(master)
        self.octave.set('4') # default value
        self.octaves = tkinter.OptionMenu(octavep, self.octave, *octaves, command=self.change_params)#"one", "two", "three")
        master.nametowidget(self.octaves.menuname).config(font=defaultfont)
        self.octaves.pack(side=tkinter.LEFT)
        self.octupb   = Button(octavep,text='+',command=self.upoct)
        self.octdownb = Button(octavep,text='-',command=self.downoct)
        self.octupb.pack(side=tkinter.LEFT)
        self.octdownb.pack(side=tkinter.LEFT)

        row+=1

        self.playb = Button(master, text="Play", command=self.play)
        self.playb.grid(column=0,row=row)

        self.playing = False

        self.refnote = "a"
        self.refoct = 4

        self.player = PitchPlayer()
        self.update_temperament()
        #self.update_pitch()


    def upoct(self):
        opt = self.octave.get()
        o = octaves.index(opt)
        if o<len(octaves)-1: o+=1
        self.octave.set(octaves[o])
        self.change_params(None)

    def downoct(self):
        opt = self.octave.get()
        o = octaves.index(opt)
        if o>0: o-=1
        self.octave.set(octaves[o])
        self.change_params(None)

    def update_temperament(self):
        try:
            self.basepitch = float(self.basea.get())
        except:
            pass
        rootnote = label2note(self.rootnote.get())
        self.temperament = MeanTone(rootnote,self.refnote,self.refoct,self.basepitch)
        
        
    def update_pitch(self):
        note = label2note(self.pitch.get())
        oct = int(self.octave.get())
        pitch = self.temperament.get_frequency(note,oct)

        self.player.setpitch([pitch])



    def change_params(self,e):
        # When something has changed
        self.update_temperament()
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
default_font.configure(size=22)

pp = PitchPipe(root,default_font)
root.mainloop()
