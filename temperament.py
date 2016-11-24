import numpy as np




#pitches = "c c# d eb e f f# g g# a bb b".split(" ")
flat  = chr(0x266D) #unichr(0x266D)
sharp = chr(0x266F) #unichr(0x266F)
pitchlist = "c cis d ees e f fis g gis a bes b"
pitchlist_orig = pitchlist.split(" ")
pitches = pitchlist.replace('is',sharp).replace('es',flat).split(" ")




def canonical_pitch_name(name):
    """ Given a pitch name, try to map it to its canonical name. """
    # TODO: ges -> fis etc.
    name = name.lower().strip()
    if name=="es": return "es"
    return name





class EqualTemperament:


    temperament = "equal"
    
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
        
    







class MeanTone:

    # Implements a meantone temperament.
    # When you look at this, it makes sense: https://en.wikipedia.org/wiki/Quarter-comma_meantone
    # Also, some cool sound examples https://en.wikipedia.org/wiki/Just_intonation

    temperament = "quarter-comma meantone"

    
    # For each note in the 12-note scale, this encodes how many fifths it is away
    # from the tonic, first note in the scale. 
    fifth_distance = np.array([ 0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5 ])
    # Similarly, for each note in the scale, this encodes the "octave correction" that makes
    # it end up in the right place relative to the starting pitch.
    sec_pow        = np.array([ 0, 3, -1, 2, -2, 1, -3, 0, 3, -1, 2, -2 ])
    temp_perf_fifth = np.power(5,.25)




    def note_index_in_tonality(self,basename,note):
        """ Returns the index of a given note in a particular tonality,
        i.e. the number of semitones you need to go up from the given
        base note to reach the given note.
        e.g. if base=D and note=E then the index is 2.
        
        Arguments
        basename : the name of the tonality root
        note : the name of the note whose position you want to know
        """

        # Find the indices
        b_i = pitchlist_orig.index(basename)
        n_i = pitchlist_orig.index(note)

        if n_i<b_i:
            return 12+(n_i-b_i)
        else:
            return (n_i-b_i)
        

    
    
    def __init__(self,tonalroot,refpitchname,refpitchoctave,refpitchfrequency):
        """ 
        Initialise the temperament using some pitch reference (e.g. A4=440 Hz).
        
        Arguments
        tonalroot         : the note that is the root of the tonal system (e.g. "a")
        refpitchname      : the canonical name of the note (as a string), e.g. "a", "fis", "bes"
        refpitchoctave    : the octave number of the note, using the Scientific Pitch Convention, where C4=middle C and octaves change between B and C
        refpitchfrequency : the frequency (in Hz) of the reference pitch.
        """
        self.refpitchname      = canonical_pitch_name(refpitchname)
        self.refpitchindex     = pitchlist_orig.index(self.refpitchname)
        self.refpitchoctave    = refpitchoctave
        self.refpitchfrequency = refpitchfrequency
        self.tonalroot         = canonical_pitch_name(tonalroot)

        # TODO: right here we can compute the distance from the tonal root
        # and perhaps compute the tuning of the tonal root?

        # These are the frequency ratios from the tonal root.
        self.freqrats = np.power(self.temp_perf_fifth,self.fifth_distance)*np.power(2.,self.sec_pow)

        # The ratio associated with the reference pitch (e.g. if A is the reference pitch
        # but D is the tonal root, then this variable tells us what the ratio is that we need
        # to divide A by to get to D).
        self.refpitchratio = self.freqrats[ self.note_index_in_tonality(self.tonalroot,
                                                                        self.refpitchname) ]

        

        


        
    def get_frequency(self,notename,octave):
        """ Return the pitch (in Hz) of a particular note. 
        
        Arguments
        notename  : the canonical name of the note (as a string), e.g. "a", "fis", "bes"
        octave    : the octave number of the note, using the Scientific Pitch Convention, where C4=middle C and octaves change between B and C
        """
        name = canonical_pitch_name(notename)

        # Find what the index of the note is in the given tonality
        rat = self.freqrats[ self.note_index_in_tonality(self.tonalroot,name) ]

        # All right, so we need to know how far this note is away from
        # the reference pitch.
        # So we want a number of semitones and a number of octaves.
        noct  = 0 # TODO

        return np.power(2,noct)*(rat/self.refpitchratio)*self.refpitchfrequency
        
    


    
