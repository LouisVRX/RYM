# Realtime sound spectrograph built with Python, PyAudio, NumPy and OpenCV
# Cosmin Gorgovan <cosmin AT linux-geek.org>, Apr 16 2011
# Released into the public domain by the copyright holder

import pyaudio
import sys
import numpy
import scipy.signal
from cv import *

# No. of input samples used for a single FFT
CHUNK_SIZE = 2048

# Sampling rate
RATE = 48000

# Spectrogram's width in pixels
WINDOW_WIDTH = 1000

# Don't change. Spectrogram's height in pixels
HEIGHT = CHUNK_SIZE/2

#filtering
# spell out the args that were passed to the Matlab function
N=50
Fc=100
Fs=RATE
a=1
b=scipy.signal.firwin( numtaps=N, cutoff=Fc, window = "hamming", nyq=Fs/2)


p = pyaudio.PyAudio()

stream = p.open(format = pyaudio.paInt16,
                channels = 1,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK_SIZE,
                output_device_index = 0,
                input_device_index = 0)


spectrogram = CreateImage((WINDOW_WIDTH, HEIGHT), IPL_DEPTH_16U, 1)
Set(spectrogram, 0)

while (True):

    errorcount = 0 
    try:
    	data = stream.read(CHUNK_SIZE)
    except IOError as e:                                      
	errorcount += 1                                     
        #print( "(%d) Error recording: %s"%(errorcount,e) )  
        noisycount = 1     
    
    data = numpy.fromstring(data, 'int16')
    
    data=scipy.signal.lfilter( b, a, data)    
    freq = numpy.fft.rfft(data)
    
    tmp = CreateImage((WINDOW_WIDTH, HEIGHT), IPL_DEPTH_16U, 1)
    
    # Copy last WIDTH-1 columns from spectogram to the first WIDTH-1 columns in tmp
    SetImageROI(tmp, (0, 0, WINDOW_WIDTH-1, HEIGHT))
    SetImageROI(spectrogram, (1, 0, WINDOW_WIDTH-1, HEIGHT))
    Copy(spectrogram, tmp)
    ResetImageROI(tmp)
    
    for i in range(1, CHUNK_SIZE/2):
      rvalue = abs(int(numpy.real(freq[i])))
      
      Line(tmp, (WINDOW_WIDTH-1, HEIGHT-i), (WINDOW_WIDTH-1, HEIGHT-i),  rvalue)
      #freq = int(RATE * (max_index / float(chunk)))
    spectrogram = tmp
    
    ShowImage("Spectograph", spectrogram)
    if (WaitKey(10) == ord('q')):
      break
      
stream.stop_stream()
stream.close()
p.terminate()
