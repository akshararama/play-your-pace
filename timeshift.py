
import wave
from playaudio import *
import array, math, time, argparse, sys
import numpy, pywt
from scipy import signal
from scipy.io import wavfile
import pdb
import matplotlib
from bpm import *
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

#SOLA method 
def timeScale(wavRead, startPos, endPos, scale):
    numFrames = endPos - startPos
    pieceSize = numFrames//20
    overlap = 1000
    #overlap = int((scale-1)*pieceSize)
    print(pieceSize, overlap)
    remainder = 1000
    #remainder = numFrames//pieceSize
    wavRead.setpos(startPos)
    newSound = wavRead.readframes(pieceSize)
    #print(newSound)
    datpos = startPos + pieceSize
    while datpos < endPos - remainder - pieceSize:
        wavRead.setpos(datpos-overlap)
        newSound +=wavRead.readframes(pieceSize+overlap)
        #print(pieceSize+overlap, wavRead.readframes(pieceSize+overlap))
        datpos += pieceSize
    # wavRead.setpos(datpos-overlap)
        newSound += wavRead.readframes(pieceSize+overlap+remainder)
    # play(newSong)
    return newSound

def modifyTime(filename, scale):
    ofile = wave.open(filename, 'rb')
    endlen = ofile.getnframes()
    # sound = ofile.readframes(-1)
    params = ofile.getparams()
    # endLen = len(sound)
    newSongName = "hihi"+filename
    newSong = wave.open("hihi"+filename, 'wb')
    newSong.setparams(params)
    newByteSong = timeScale(ofile, 0, endlen, scale)
    newSong.writeframes(newByteSong)
    #print(newByteSong)
    newSong.close()
    # print(newSong)
    print('here!')
    play(newSongName)

def modifyTime2(filename, factor):
    soundarray, fs = read_wav(filename)
    stretchedarray = timestretch(soundarray, 1024, factor)
    scipy.io.wavefile.write('new'+filename, fs, stretchedarray)
    newSongName = 'new'+filename
    play(newSongName)


'''

def modifyTime(filename, scale):
    ofile = wave.open(filename, 'rb')
    endlen = ofile.getnframes()
    # sound = ofile.readframes(-1)
    params = ofile.getparams()
    # endLen = len(sound)
    newByteSong = timeScale(ofile, 0, endlen, scale)
    #print(newByteSong)
    newSongName = "hihi"+filename
    newSong = wave.open("hihi"+filename, 'wb')
    newSong.setparams(params)
    newSong.writeframes(newByteSong)
    newSong.close()
    # print(newSong)
    play(newSongName)
'''