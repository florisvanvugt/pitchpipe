import numpy as np




#pitches = "c c# d eb e f f# g g# a bb b".split(" ")

import sys
if sys.version_info >= (3, 0):
    flat  = chr(0x266D) # py3
    sharp = chr(0x266F) #py3
else:
    flat = unichr(0x266D) #py2
    sharp = unichr(0x266F) #py2
    
pitchlist = "c cis d ees e f fis g gis a bes b"
pitchlist_orig = pitchlist.split(" ")
pitches = pitchlist.replace('is',sharp).replace('es',flat).split(" ")

N_OCTAVE = len(pitchlist_orig)

# Recoding some note names (essentially allowing aliases)
recode = {'es':'ees',
          'dis':'cis',
          'eis':'f',
          'ges':'fis',
          'aes':'gis',
          'as':'gis',
          'aes':'gis',
          'ais':'bes',
          'bis':'c'
}



def label2note(l):
    # Convert note label into the internally used notation
    # (without odd characters for sharp and flat)
    return pitchlist_orig[ pitches.index(l) ]




def interval(base,octv,intvl):
    """ 
    Return a particular interval (in semitones) above a base note.
    base : a base pitch
    octv : the octave of the base note
    intvl : the interval (in semitones) that we want to be above the base pitch
    """
    base = canonical_pitch_name(base)
    basei = pitchlist_orig.index(base) # get the index of the base pitch
    targeti = basei+intvl
    return pitchlist_orig[targeti%N_OCTAVE],octv+int(targeti/N_OCTAVE)



def canonical_pitch_name(name):
    """ Given a pitch name, try to map it to its canonical name. """
    # TODO: ges -> fis etc.
    name = name.lower().strip()
    if name=="es": return "es"
    return name



def pitch_equals(a,b):
    # Whether two pitches are equal (they may be noted differently, i.e. gis=aes)
    return canonical_pitch_name(a)==canonical_pitch_name(b)


def pitch_in(a,lst):
    # Whether the pitch a is in some list
    is_in = [ pitch_equals(a,l) for l in lst ]
    return any(is_in)




def note_index_in_tonality(basename,note):
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




def notediff(na,octa,nb,octb):
    """
    Return the "upward" difference between two notes, A and B,
    in semitones (within the scale) and octaves.
    https://en.wikipedia.org/wiki/Scientific_pitch_notation
    The idea is that "semitones" is always positive, i.e.
    the notediff between C5 and B4 will be 11 semitones minus 1 octave.

    na   : note name of A
    octa : octave number of A (using scientific pitch notation)
    nb   : note name of B
    octb : octave number of B
    """

    na = canonical_pitch_name(na)
    nb = canonical_pitch_name(nb)

    a_i = pitchlist_orig.index(na)
    b_i = pitchlist_orig.index(nb)

    intvl = b_i-a_i # the interval in semitones 
    octdif = octb-octa

    if intvl<0:
        octdif-=1
        intvl+=12 # add one octave

    return (intvl,octdif)
    




    

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
        octave = int(octave)

        # All right, so we need to know how far this note is away from
        # the reference pitch.
        # So we want a number of semitones and a number of octaves.
        noct  = octave-self.refpitchoctave
        nsemi = pitchlist_orig.index(name)-self.refpitchindex

        pwr = np.float(noct+(nsemi/12.))
        print(pwr)
        mult = 2**pwr
        return mult*self.refpitchfrequency
        
    







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
        # Okay, so now we compute the frequency ratio between the reference pitch,
        # and the tonal root (where by convention we use the same octave as the reference pitch)
        self.root_freq_ratio = 1/self.get_ratio(self.refpitchname,self.refpitchoctave)
        # the ratio we need to apply to the frequency of the reference pitch to get to the root pitch (in the reference octave)
        

    def get_frequency(self,notename,octave):
        """ Get the frequency for a particular note and octave, e.g. G5 """

        # Get the frequency ratio relative to the tonal root
        freqrat = self.get_ratio(notename,octave)

        # To get the frequency: from the reference note, transfer to the tonal root pitch
        # in that octave, and from there, go up the interval to the desired note.
        freq = self.refpitchfrequency * self.root_freq_ratio * freqrat

        return freq


        

    def get_ratio(self,notename,octave):
        """ Return the frequency ratio of the given note (and its octave)
        relative to the current tonal root.
        The tonal root will be the self.tonalroot and its octave will be,
        according to convention, the octave of the reference pitch.
        """
        notename = canonical_pitch_name(notename)
        (nsemi,noct) = notediff(self.tonalroot,self.refpitchoctave,notename,octave)

        # Okay, now the rest is fairly early, we just convert the semitones into a frequency
        # ratio, and then also apply the difference in octaves!
        return self.freqrats[nsemi] * pow(2,noct)

        

        

        

    


class Classic:

    # Implements reasonably pure versions of all the intervals,
    # at the expense of a great dependence on what the root note is.
    # e.g. https://en.wikipedia.org/wiki/List_of_meantone_intervals

    temperament = "classic"

    # Convert from semitone interval to frequency ratio
    STEP_RATIO = [ 1, 16/15, 9/8, 6/5, 5/4, 4/3, 25/18, 3/2, 8/5, 5/3, 9/5, 15/8 ] 
    
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


        # Okay, so now we compute the frequency ratio between the reference pitch,
        # and the tonal root (where by convention we use the same octave as the reference pitch)
        self.root_freq_ratio = 1/self.get_ratio(self.refpitchname,self.refpitchoctave)
        # the ratio we need to apply to the frequency of the reference pitch to get to the root pitch (in the reference octave)
        
        


    def get_ratio(self,notename,octave):
        """ Return the frequency ratio of the given note (and its octave)
        relative to the current tonal root.
        The tonal root will be the self.tonalroot and its octave will be,
        according to convention, the octave of the reference pitch.
        """
        notename = canonical_pitch_name(notename)
        (nsemi,noct) = notediff(self.tonalroot,self.refpitchoctave,notename,octave)

        # Okay, now the rest is fairly early, we just convert the semitones into a frequency
        # ratio, and then also apply the difference in octaves!
        return self.STEP_RATIO[nsemi] * pow(2,noct)


    
    def get_frequency(self,notename,octave):
        """ Get the frequency for a particular note and octave, e.g. G5 """

        # Get the frequency ratio relative to the tonal root
        freqrat = self.get_ratio(notename,octave)

        # To get the frequency: from the reference note, transfer to the tonal root pitch
        # in that octave, and from there, go up the interval to the desired note.
        freq = self.refpitchfrequency * self.root_freq_ratio * freqrat

        return freq
  
