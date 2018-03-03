from __future__ import division

"""

Python 3



The purpose here is to build an application that
allows training pitches.

It will display a pitch and then you need to play that one.
Then it will listen to the mike to see whether you actually play that.

"""


# Frequency estimation methods: a great listing with code examples is here:
# https://gist.github.com/endolith/255291

# Alternatively, you can use SWIG-wrapped aubio libraries apparently, as in here:
# https://stackoverflow.com/questions/2648151/python-frequency-detection
import numpy as np
from numpy.fft import rfft
from numpy import argmax, mean, diff, log

from scipy.signal import blackmanharris, fftconvolve
from numpy import polyfit, arange

def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.
   
    f is a vector and x is an index for that vector.
   
    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.
   
    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.
   
    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
   
    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
   
    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)



def freq_from_fft(sig, fs):
    """
    Estimate frequency from peak of FFT
    """
    # Compute Fourier transform of windowed signal
    windowed = sig * blackmanharris(len(sig))
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f))  # Just use this for less-accurate, naive version
    true_i = i
    #true_i = parabolic(log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / len(windowed)





#
#
# RECORDING AUDIO
#
#

import pyaudio
FORMAT = pyaudio.paInt16
CHANNELS = 1 # just record MONO
RATE = 44100
BUFFER=22050  # frames per buffer

import struct

class Recorder:

    def __init__(self):
        self._pa = pyaudio.PyAudio()
    
    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format            =FORMAT,
                                     channels          =CHANNELS,
                                     rate              =RATE,
                                     input             =True,
                                     frames_per_buffer =BUFFER,
                                     stream_callback   =self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            # We are receiving input data. So we will try to find the fundamental frequency.
            frames = np.fromstring(in_data,dtype=np.int16)
            f0 = freq_from_fft(frames,RATE)
            self.receiver.set("f0 = %f"%f0)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()




        

recorder = Recorder()




        
import tkinter as tk

font=("Helvetica", 16)

root = tk.Tk()  
root.title("Pitch trainer")

w = tk.Label(root, text="Frequency estimation: ",font=font)
w.pack()

freqest = tk.StringVar()
tk.Label(root, textvariable=freqest,font=font).pack()

recorder.receiver = freqest
recorder.start_recording()



root.mainloop()




if False: # showing an image
    from PIL import Image,ImageTk  
    root = tk.Tk()  
    root.title("display image")  
    im=Image.open("screenshot.png")  #This is the correct location and spelling for my image location
    photo=ImageTk.PhotoImage(im)  
    cv = tk.Canvas()  
    cv.pack(side='top', fill='both', expand='yes')  
    cv.create_image(10, 10, image=photo, anchor='nw')  
    root.mainloop()
