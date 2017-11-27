
import os
import sys

from temperament import *
import re






# We have the option to supply a file that lists tone durations.
# This file has the following format:
# First line = duration of quarter note (in msec)
# Second line and on: each note to be played in the following format:
#  NOTE DURATION
# Where NOTE is the scientific notation of the pitch, i.e. c4 = middle C,
# a4 = the first A above the middle c.
# The duration uses Lilypond-like notation, i.e. 1=whole note, 2=half note,
# 4=quarter note, 8=eighth note, 4. = quarter note and a half.

def parse_script_file(fname):

    # Read the notes
    f = open(fname,'r')
    ls = [ l.strip() for l in f.readlines() ]
    f.close()

    if len(ls)==0:
        return None # no tempo specified
    quarter_duration = ls[0]
    if quarter_duration.isdigit():
        quarter_duration=int(quarter_duration)
    else:
        print("Cannot parse quarter note duration %s"%quarter_duration)
        return None
        
    
    if len(ls)==1:
        return None # No notes specified

    notes = []
    for l in ls[1:]:

        l = l.strip()
        print("Processing line '%s'"%l)
        
        if len(l)>0:
            note = l.split(" ")
            if len(note)!=2:
                print("Problem parsing note %s"%l)
                return None
            pitch,dur = tuple(note)

            # Parse the pitch
            if pitch=="r":
                pitch_oct = None
                pitch_name = "r"

            else:
                pitch_name,pitch_oct = pitch[:-1],pitch[-1:]
                if pitch_oct.isdigit():
                    pitch_oct = int(pitch_oct)
                else:
                    print("Error parsing octave %s"%pitch_oct)
                    return None
                if not pitch_name in pitchlist:
                    print("Unknown pitch %s"%pitch_name)
                    return None

            # Parse the duration
            plushalf = False
            dur_base = dur
            if dur[-1] == ".":
                plushalf = True
                dur_base = dur[:-1]

            if not dur_base.isdigit():
                print("Problem parsing duration %s"%dur)
                return None

            # Compute the duration
            dur_nquart = 4/float(dur_base)
            if plushalf:
                dur_nquart *= 1.5
            
            notes.append( {"pitch":pitch_name,
                           "octave":pitch_oct,
                           "duration.quarters":dur_nquart,
                           "duration.ms":dur_nquart*quarter_duration} )

    return notes





def relative_pitch(notename,refname,refoct):
    """ 
    Determine the octave of a particular note, given a reference. 
    This is following the lilypond convention. 
    """

    note_i = pitchlist_orig.index(notename)
    ref_i  = pitchlist_orig.index(refname)

    if abs(note_i-ref_i)<7:
        # The two notes are close enough in the octave, so we keep the same octave
        return refoct
    else:
        # We have to change octaves!
        if note_i<ref_i:
            return refoct+1
        else: # ref_i<note_i
            return refoct-1

    return refoct




def parse_yaml_file(yamlf):
    import yaml
    dat = yaml.load(open(yamlf,'r'))

    # Duration of quarter note (in ms)
    quarter_duration = dat["quarter_duration"]

    # Reference note
    refnote = dat["relative"].strip()
    # Convert into scientific notation
    refname = refnote[0] # e.g. c'
    octavemarkers = refnote[1:]
    ## TODO: actually parse the reference pitch
    if refnote=="c''":  
        refoct = 6
    else:
        print("Reference octave not understood!")
        exit()

    # So now we have refname,refpitch which tells us the current reference pitch

    # Let's start parsing!

    # The reference duration (we'll update it as we go along)
    refduration = 4

    notes = [] 
    for readnote in  dat["notes"].split():

        # We're currently reading this particular note "readnote"
        # Step 1. figure out its pitch

        # Step 1a. remove ties (TODO treat ties usefully)
        readnote = readnote.replace("(","").replace(")","").lower()
        

        """
        for readnote in allnotes:
            m = re.match(r'^([a-z]+)([\',]*)([\d]*)(\.?)$',readnote)
            if m:
                print(m.groups())
            else:
                print("Error %s"%readnote)
        """
        
        # Parse the note-notation
        m = re.match(r'^([a-z]+)([\',]*)([\d]*)(\.?)$',readnote)
        if not m:
            print("Error parsing note %s"%readnote)
            exit()
        grps = m.groups()
        print(grps)

        # If this is a rest, that's easy...
        if grps[0]=="r":
            pitch_oct = None
            pitch_name = "r"
        else:
            # Need to actually figure out the pitch

            pitch_name = grps[0]

            if pitch_name in recode.keys():
                pitch_name = recode[pitch_name]

            pitch_oct  = relative_pitch(pitch_name,refname,refoct)

            if grps[1]!="":  # there is an octave modifier (or multiple ones)
                for i in grps[1]:
                    if i=="'": pitch_oct+=1
                    if i==",": pitch_oct-=1

            # Now this note becomes the reference for the next note, if you see what I mean
            refname,refoct = pitch_name,pitch_oct
            #pitch_oct = 5
            #pitch_name = grps[0]

            # TODO: transposition of octaves (from '' and ,, markers)
            
        
        # Step 2. figure out the duration
        if grps[2]=="": # if there is no duration entered...
            dur_base = refduration # then we stick with the duration we had
        else:
            ## Need to actually parse the duration
            dur_base = grps[2]
            plushalf = grps[3]=="."

        refduration = dur_base
            
        # Compute the duration in msec
        dur_nquart = 4/float(dur_base)
        if plushalf:
            dur_nquart *= 1.5

            
        notes.append( {"pitch"            :pitch_name,
                       "octave"           :pitch_oct,
                       "duration.quarters":dur_nquart,
                       "duration.ms"      :dur_nquart*quarter_duration} )

        
    # If c'' then two octaves above the middle c (=C4), so...
    return notes


    
    return notes







import numpy as np
import wave
import struct

FRAMERATE      = 44100
NCHANNELS      = 1
SAMPLEWIDTH    = 2
STRUCTYPE      = "h"
MAX_AMPLITUDE  = 32767.0/2.


FADE_DURATION = FRAMERATE*.01


def fade(sound,ramp_length):
    # A linear ramp on and off
    # ramp_length is given in # of samples

    ramp_length = int(ramp_length)

    # Now we generate a "fade-in" and "fade-out", just linear to keep it simple
    for i in range(ramp_length):
        sound[i] =  sound[i]*i/ramp_length
    for i in range(ramp_length):
        sound[-i] = sound[-i]*i/ramp_length

    return sound






def sine_wave(frequency, framerate, amplitude, length):
    """ Generate a sine wave through a lookup table (this is quite fast)
    Courtesy of http://zacharydenton.com/generate-audio-with-python/
    """
    return np.array([ int(amplitude*np.sin(2.0*np.pi*i*frequency/framerate)) for i in range(int(length))])







def get_frequency(notename,octave):
    """ Given a note name, get its frequency. """

    # Find what the frequency ratio of that tone is relative to the currently
    # selected base pitch
    hz = temperament.get_frequency(notename,octave)

    return hz






def make_note(note):
    """ Given a note, create a wave that represents that note."""
    duration = note["duration.ms"]/1000.
    
    if note["pitch"]=="r":
        return np.array( [0]*int(duration*FRAMERATE) )
    else:        
        freq = get_frequency(note["pitch"],note["octave"])
        amplitude = MAX_AMPLITUDE/4
        return sine_wave(freq,FRAMERATE,amplitude,duration*FRAMERATE)
    



def sonify(notes):
    """ Given a sequence of notes, sonify them """
    wavs = [ fade(make_note(note),FADE_DURATION) for note in notes ]
    wv = np.concatenate( [np.array([ 0 ]*2*FRAMERATE) ]+wavs)
    return wv







def wave_to_file(sound,filename):
    # Given a wave stimulus, write it to a file.
    # Writing a simple wave file
    output = wave.open(filename, 'w')
    output.setparams((NCHANNELS, SAMPLEWIDTH, FRAMERATE, 0, 'NONE', 'not compressed'))
    value_str = struct.pack('%d%s'%(len(sound),STRUCTYPE),*sound)
    output.writeframes(value_str)
    output.close()
    

    



temperament = MeanTone('c','a',5,415)


# Check if a "note" script was given
if len(sys.argv)>1:

    fname = sys.argv[1]
    if os.path.isfile(fname):

        if fname.endswith('yaml'):
            ret = parse_yaml_file(fname)

        else:
            ret = parse_script_file(fname)
        if ret!=None:
            notes = ret
            for n in notes:
                print(n)

            wv = sonify(notes)
            print (wv)
            
            #import matplotlib.pyplot as plt
            #plt.plot(wv)
            #plt.show()
            
            fname = fname+".wav"
            wave_to_file(wv,fname)
            print("Output written to file %s"%fname)
    else:
        print("Cannot find file %s"%fname)


