#modified from github
# https://github.com/scaperot/the-BPM-detector-python


import wave, array, math, time, argparse, sys
import numpy, pywt
from scipy import signal
import pdb
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def read_wav(filename):
    #open file, get metadata for audio
    wavRead = wave.open(filename,'rb')
    # typ = choose_type( wf.getsampwidth() ) #TODO: implement choose_type
    frames = wavRead.getnframes()
    framespersecond = wavRead.getframerate()
    samps = list(array.array('i',wavRead.readframes(frames)))
    return samps, framespersecond
    
# simple peak detection
def peakDetection(data):
    max_val = numpy.amax(abs(data)) 
    peak_ndx = numpy.where(data==max_val)
    if len(peak_ndx[0]) == 0: #if nothing found then the max must be negative
        peak_ndx = numpy.where(data==-max_val)
    return peak_ndx

#from stackoverflow 
def bpm_detector(data,fs):
    cA = [] 
    cD = []
    correl = []
    cD_sum = []
    levels = 4
    max_decimation = 2**(levels-1);
    min_ndx = 60./ 220 * (fs/max_decimation)
    max_ndx = 60./ 40 * (fs/max_decimation)
    
    for loop in range(0,levels):
        cD = []
        # 1) DWT
        if loop == 0:
            [cA,cD] = pywt.dwt(data,'db4');
            cD_minlen = len(cD)/max_decimation+1;
            cD_minlen = int(cD_minlen)
            cD_sum = numpy.zeros(cD_minlen);
        else:
            [cA,cD] = pywt.dwt(cA,'db4');
        # 2) Filter
        cD = signal.lfilter([0.01],[1 -0.99],cD);

        # 4) Subtractargs.filename out the mean.

        # 5) Decimate for reconstruction later.
        cD = abs(cD[::(2**(levels-loop-1))]);
        cD = cD - numpy.mean(cD);
        # 6) Recombine the signal before ACF
        #    essentially, each level I concatenate 
        #    the detail coefs (i.e. the HPF values)
        #    to the beginning of the array
        cD_sum = cD[0:cD_minlen] + cD_sum;

    if [b for b in cA if b != 0.0] == []:
        return no_audio_data()
    # adding in the approximate data as well...    
    cA = signal.lfilter([0.01],[1 -0.99],cA);
    cA = abs(cA);
    cA = cA - numpy.mean(cA);
    cD_sum = cA[0:cD_minlen] + cD_sum;
    
    # ACF
    correl = numpy.correlate(cD_sum,cD_sum,'full') 
    
    midpoint = len(correl) // 2
    correl_midpoint_tmp = correl[midpoint:]
    peak_ndx = peakDetection(correl_midpoint_tmp[int(min_ndx):int(max_ndx)]);
        
    peak_ndx_adjusted = peak_ndx[0]+min_ndx;
    bpm = 60./ peak_ndx_adjusted * (fs/max_decimation)
    print()
    return int(bpm)

def findLenOfSong(samps, framespersecond):
    lenOfSamps = len(samps)
    lenOfSong = lenOfSamps//framespersecond
    return lenOfSong

