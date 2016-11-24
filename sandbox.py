
from temperament import *


if False:
    
    print("### Equal temperament")
    temp = EqualTemperament("a",4,440)

    for i in range(3,6):
        for note in pitchlist_orig:
            print ("%s%i %f"%(note,i,temp.get_frequency(note,i)))



if True:

    print("### Mean-tone temperament")
    temp = MeanTone("d","a",4,415)

    for i in range(3,6):
        for note in pitchlist_orig:
            print ("%s%i %f"%(note,i,temp.get_frequency(note,i)))




