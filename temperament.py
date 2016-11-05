import numpy as np





#pitches = "c c# d eb e f f# g g# a bb b".split(" ")
flat  = chr(0x266D) #unichr(0x266D)
sharp = chr(0x266F) #unichr(0x266F)
pitchlist = "a bes b c cis d ees e f fis g gis"
pitchlist_orig = pitchlist.split(" ")
pitches = pitchlist.replace('is',sharp).replace('es',flat).split(" ")
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
        



frequency_ratios = get_freq_ratios("quarter-comma meantone")


