import pyaudio
import wave
import os
import numpy as np
import decimal
from bpm import *
from timeshift import *
import sys
from numpy import *
import scipy.io.wavfile
from playaudio import *
import array, math, time, argparse
import numpy, pywt

def load_wav(filename):
    filename = "/Users/aramakrishnan/Desktop/15-112/TP/" +filename
    wavedata=scipy.io.wavfile.read(filename)
    samplerate=int(wavedata[0])
    smp=wavedata[1]
    if len(smp.shape)>1: #convert to mono
        smp=(smp[:,0]+smp[:,1])*0.5
    return samplerate,smp

def timestretch(sound, factor, window_size, h):
    """ Stretches/shortens a sound, by some factor. """
    phase = np.zeros(window_size)
    han= np.hanning(window_size)
    result = np.zeros(int(len(sound) / factor + window_size))

    for i in np.arange(0, len(sound) - (window_size + h), h*factor):
        i = int(i)
        a1 = sound[i: i + window_size]
        a2 = sound[i + h: i + window_size + h]
        s1 = np.fft.fft(han * a1)
        s2 = np.fft.fft(han * a2)
        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(j*phase))
        i2 = int(i/factor)
        result[i2: i2 + window_size] += han*a2_rephased.real
    # normalize (16bit)
    result = ((2**(16-4)) * result/result.max())

    return result.astype('int16')

def soundarraytofile(filename, rate):
    samplingrate, samps = load_wav(filename)
    #slowed = stretch(samps, rate, 2**13, 2**11)
    slowed = timestretch(samps, 0.75, 1024, 256)
    scipy.io.wavfile.write('changed50'+filename, samplingrate, slowed)
    print('done')

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

def play(file):
    wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    # start the stream (4)
    stream.start_stream()

    # wait for stream to finish (5)
    while stream.is_active():
        time.sleep(0.1)

    # stop stream (6)
    stream.stop_stream()
    stream.close()
    wf.close()

    # close PyAudio (7)
    p.terminate()



