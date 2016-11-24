import numpy as np




#pitches = "c c# d eb e f f# g g# a bb b".split(" ")
flat  = chr(0x266D) #unichr(0x266D)
sharp = chr(0x266F) #unichr(0x266F)
pitchlist = "c cis d ees e f fis g gis a bes b"
pitchlist_orig = pitchlist.split(" ")
pitches = pitchlist.replace('is',sharp).replace('es',flat).split(" ")


# For each note in the 12-note scale, this encodes how many fifths it is away
# from the tonic, first note in the scale. 
fifth_distance = np.array([ 0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5 ])
# Similarly, for each note in the scale, this encodes the "octave correction" that makes
# it end up in the right place relative to the starting pitch.
sec_pow        = np.array([ 0, 3, -1, 2, -2, 1, -3, 0, 3, -1, 2, -2 ])
temp_perf_fifth = np.power(5,.25)




def canonical_pitch_name(name):
    """ Given a pitch name, try to map it to its canonical name. """
    # TODO
    if name=="es": return "es"
    return name



class EqualTemperament:

    
    def __init__(self,refpitchname,refpitchoctave,refpitchfrequency):
        """ 
        Initialise the temperament using some pitch reference (e.g. A4=440 Hz).
        
        Arguments
        refpitchname      : the canonical name of the note (as a string), e.g. "a", "fis", "bes"
        refpitchoctave    : the octave number of the note, using the Scientific Pitch Convention, where C4=middle C and octaves change between B and C
        refpitchfrequency : the frequency (in Hz) of the reference pitch.
        """
        self.refpitchname      = canonical_pitch_name(refpitchname)
        self.refpitchindex     = pitchlist_orig.index(self.refpitchname)
        self.refpitchoctave    = refpitchoctave
        self.refpitchfrequency = refpitchfrequency


    
    def get_frequency(self,notename,octave):
        """ Return the pitch (in Hz) of a particular note. 
        
        Arguments
        notename  : the canonical name of the note (as a string), e.g. "a", "fis", "bes"
        octave    : the octave number of the note, using the Scientific Pitch Convention, where C4=middle C and octaves change between B and C
        """
        name = canonical_pitch_name(notename)

        # All right, so we need to know how far this note is away from
        # the reference pitch.
        # So we want a number of semitones and a number of octaves.
        noct  = octave-self.refpitchoctave
        nsemi = pitchlist_orig.index(name)-self.refpitchindex

        return np.power(2,noct+(nsemi/12.))*self.refpitchfrequency
        
    




