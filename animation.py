# Updated Animation Starter Code
import pyaudio
import wave
import os
import sys
import numpy as np
import decimal
from tkinter import * 
import os
from cvcolortracking import *
from bpm import *
#from playaudio import *
import random 
import threading
import scipy
#stop thread later in the future, join tells you to not do anything until the thread is done. 

def play(file, pause):
    wf = wave.open(file, 'rb')

# instantiate PyAudio (1)
    p = pyaudio.PyAudio()
    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
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
        if pause == True:
            stream.stop_stream()

    # stop stream (6)
    stream.stop_stream()
    stream.close()
    wf.close()

    # close PyAudio (7)
    p.terminate()

def stopMusicThread(musicThread):
    musicThread.stop_stream()

def changeSpeed(fileName, changeRate):
    CHANNELS = 1
    signalwidth = 2
    ofile = wave.open(fileName, 'rb')
    RATE=ofile.getframerate()
    sound = ofile.readframes(-1) 
    newrate = int(RATE*changeRate*2)
    newFileName = "changed"+fileName
    wf = wave.open(newFileName, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(signalwidth)
    wf.setframerate(newrate)
    wf.writeframes(sound)
    wf.close()

def modifyMusic(fileName, newbpm):
    data, fs = read_wav(fileName)
    data = data[:100000]
    origbpm  = bpm_detector(data, fs)
    changeRate = newbpm/origbpm
    #to make sure it is not chipmunking too too much.
    if changeRate>2:
        changeRate = changeRate//2
    if changeRate <0.5:
        changeRate = changeRate * 2
    print(origbpm)
    changeSpeed(fileName, changeRate)
    print('done!')
# Other codeee

def getSongs(path):
    listOfSongs = []
    for songName in os.listdir(path):
        if songName.endswith('.wav'):
            listOfSongs.append(songName)
        if songName.startswith('changed'):
            listOfSongs.remove(songName)
    if '.DS_Store' in listOfSongs: 
        listOfSongs.remove('.DS_Store')
    return listOfSongs

def findClosestMatch(newbpm, bpmsonglist):
    newbpm = int(newbpm)
    smallestdiff = newbpm
    closestSong = None
    for song in bpmsonglist: 
        currbpm = song[1]
        if abs(newbpm-currbpm)<smallestdiff:
            smallestdiff = newbpm-currbpm
            closestSong = song[0]
    return closestSong

def getBpmSongList(listOfSongs):
    bpmSongList = []
    for song in listOfSongs: 
        data, fs = read_wav(song)
        if len(data)<200000:
            data = data[:100000] #cuts the data to the first part of the song, to shorten analysis time
        else:
            data = data[100000:200000]
        origbpm  = bpm_detector(data, fs)
        secondsSong = findLenOfSong(data, fs)
        bpmSongList.append((song, origbpm, secondsSong))
    return bpmSongList


#framework from 15-112 website
def init(data):
    data.state = 'startPage'
    data.margin = 10 
    data.numCols = 1
    data.inputbpm = 0
    data.song = None
    data.songsList = getSongs('/Users/aramakrishnan/Desktop/15-112/TP')
    data.t1 = None
    data.icon = PhotoImage(file = "leftarrow.gif")
    data.reversiblestates = ['paceOptions', 'songOptions', 'enterPace', 'pickSong', 'playSong', 'randomSong', 'bpmDisplay']
    data.notvalidbpm = False
    data.isplaying = False
    data.pausebutton = PhotoImage(file = "pausebutton.gif")
    data.reload = PhotoImage(file = "reload.gif")
    data.paused = False
    data.bpmList = getBpmSongList(data.songsList)
    data.threadList = []
    data.color = 'blue'
    data.colorcoord = None
    data.paused = False

def mousePressed(event, data):
    # if data.isplaying == True: 
    #     stopMusicThread(data.threadList[0])
    if data.state == 'startPage' and 300<event.y<350 and 300<event.x<500:
        if 300<event.y<350:
            if 300<event.x<350:
                data.color, data.colorcoord = 'blue', (300,300)
            if 350<event.x<400:
                data.color, data.colorcoord = 'green', (350,300)
            if 400<event.x<450:
                data.color, data.colorcoord = 'yellow', (400, 300)
            if 450<event.x<500:
                data.color, data.colorcoord = 'red', (450, 300)
    elif 705<event.x<735 and 450<event.y<480:
        if data.isplaying == True:
            data.threadList[0].join(5)
            data.threadList.pop(0)
            data.isplaying = False
            data.state = 'songOptions'
            data.song = None
            print('pressed')
    elif 740<event.x<770 and 450<event.y<480:
        if data.isplaying == True:
            data.paused = True
    elif 30<event.x<60 and 450<event.y<480:
        if data.state == 'enterPace':
            data.state = 'paceOptions'
        elif data.state == 'paceOptions':
            data.state = 'startPage'
        elif data.state == 'songOptions':
            data.state = 'enterPace'
        elif data.state == 'pickSong':
            data.state = 'songOptions'
        elif data.state == 'bpmDisplay':
            data.state = 'paceOptions'
        elif data.state == 'playSong':
            data.state = 'songOptions'
    elif data.state == 'startPage':
        data.state = 'paceOptions'
    elif data.state == 'paceOptions':
        if event.x<data.width//2: 
            data.state = 'cvPace'
        elif event.x>data.width//2:
            data.state = 'enterPace'
    elif data.state == 'songOptions':
        if event.x<data.width//2: 
            data.state = 'pickSong'
        elif event.x>data.width//2:
            # selection = random.randint(0, len(data.songsList)-1)
            # data.song = data.songsList[selection]
            data.song = findClosestMatch(data.inputbpm, data.bpmList)
            data.state = 'randomSong'
    elif data.state == 'pickSong':
        index = (event.y)/(data.height/len(data.songsList))
        index = int(index)
        data.song = data.songsList[index]
        data.state = 'playSong'
        modifyMusic(data.song, int(data.inputbpm))

    elif data.state == 'randomSong':
        modifyMusic(data.song, int(data.inputbpm))
        data.state = 'playSong'
    elif data.state == 'bpmDisplay':
        data.state = 'songOptions'
    elif data.state == 'playSong' and data.isplaying == False:
        data.isplaying = True
        newThread = threading.Thread(target = musicThread, args = [data])
        data.threadList.append(newThread)
        for thr in data.threadList:
            thr.start()
    print(data.inputbpm)


def keyPressed(event, data):
    # use event.char and event.keysym

    if data.state == 'enterPace':
        if event.keysym.isdigit() and data.inputbpm==0:
            data.inputbpm = event.keysym
            data.inputbpm = int(data.inputbpm)
        elif event.keysym.isdigit() and len(str(data.inputbpm))<3:
            data.inputbpm= str(data.inputbpm) + event.keysym
            data.inputbpm = int(data.inputbpm)
        if event.keysym == "space" and len(str(data.inputbpm))>1 and 50<int(data.inputbpm)<250:
            data.state = 'songOptions'
        elif event.keysym == "space" and not 50<int(data.inputbpm)<250:
            data.notvalidbpm = True
        if event.keysym == 'BackSpace' and (data.inputbpm)>1 and len(str(data.inputbpm))>0:
            data.inputbpm = str(data.inputbpm)[:-1]
            data.inputbpm = int(data.inputbpm)
            if 50<int(data.inputbpm)<400:
                data.notvalidbpm = False
        if event.keysym == 'BackSpace' and data.inputbpm<10:
            data.inputbpm = 0

def timerFired(data): 
    pass

def drawPlayScreen(canvas,data):
    canvas.create_rectangle(0,0,data.width, data.height, fill = 'pink')

def redrawAll(canvas, data):
    if data.state == 'startPage': 
        canvas.create_rectangle(100, 100, 700, 400, fill = 'pink')
        canvas.create_text(400, 175, 
                    text="Welcome to ", fill="white",
                    font="Courier 26 bold")
        canvas.create_text(400, 225, 
                        text=" PLAY YOUR PACE", fill="white",
                        font="Courier 40 bold")
        canvas.create_text(400, 275, text = "pick your color!", fill ='white',
            font = 'Courier 12 ')

        canvas.create_rectangle( 300, 300, 350, 350, fill = 'blue')
        canvas.create_rectangle( 350, 300, 400, 350, fill = 'green')
        canvas.create_rectangle( 400, 300, 450, 350, fill = 'yellow')
        canvas.create_rectangle( 450, 300, 500, 350, fill = 'red')
        if data.colorcoord !=None and data.color != None:
            canvas.create_rectangle(data.colorcoord[0], data.colorcoord[1],
                                data.colorcoord[0]+50, data.colorcoord[1]+50,
                                fill = data.color, width = 4 )

    if data.state == 'paceOptions':
        canvas.create_rectangle(data.margin, data.margin, data.width//2-data.margin, data.height, fill = "yellow")
        canvas.create_rectangle(data.width//2+data.margin, data.margin, data.width-data.margin, data.height, fill = "lightblue")
        canvas.create_text(data.width//4, data.height//2, 
                        text="Find my pace", fill="black",
                        font="Courier  25 bold")
        canvas.create_text(data.width*3//4, data.height//2, 
                        text="Choose your BPM", fill="black",
                        font="Courier 25 bold")


    if data.state == 'songOptions':
        canvas.create_rectangle(data.margin, data.margin, data.width//2-data.margin, data.height-data.margin, fill = "seagreen1")
        canvas.create_rectangle(data.width//2+data.margin, data.margin, data.width-data.margin, data.height-data.margin, fill = "purple2")
        canvas.create_text((1/4)*data.width, (1/2)*data.height, 
                        text="Pick your song", fill="black",
                        font="Courier 16 bold")
        canvas.create_text((3/4)*data.width, (1/2)*data.height, 
                        text="Closest Tempo Change", fill="black",
                        font="Courier 16 bold")
    if data.state == 'enterPace':
        canvas.create_text((1/2)*data.width, (1/4)*data.height,
                            text = "Enter your bpm!", fill = 'black',
                        font="Courier 22 bold")
        canvas.create_text((1/2)*data.width, (1/4)*data.height+50,
                            text = "(between 50 and 250)", fill = 'black',
                        font="Courier 16 bold")
        canvas.create_text((1/2)*data.width, (1/2)*data.height, 
                        text="bpm: " + str(data.inputbpm), fill="black",
                        font="Courier 16 bold")
        canvas.create_text((1/2)*data.width, (1/2)*data.height+100, 
                        text="Press Space when done", fill="black",
                        font="Courier 12 bold")
        if data.notvalidbpm == True: 
            canvas.create_text((1/2)*data.width, (3/4)*data.height+50,
                            text = "not a valid bpm", fill = 'black',
                        font="Courier 12 bold")

    if data.state == 'pickSong':
        songsLength = len(data.songsList)
        for i in range (songsLength):
            canvas.create_rectangle(data.margin, data.margin+i*(data.height//songsLength), data.width-data.margin,
                data.height+(i+1)*(data.height//songsLength), fill ="pink")
            canvas.create_text(data.width//2, data.margin + ((i+0.5)*(data.height//songsLength)),
                    text = data.songsList[i][:-4], fill = "white",
                        font="Courier 15")

    if data.state == 'cvPace':
        data.inputbpm = int(vidRoll(data.color))
        data.state = 'bpmDisplay'

    if data.state == 'playSong': 
        canvas.create_text(data.width//2, data.height//2, text = "playing your song:", fill = "purple", font = 'Courier 18')
        canvas.create_text(data.width//2, data.height//2+50, text = data.song[0:-4], fill = "seagreen1", font = 'Courier 28')
        canvas.create_text(data.width//2, data.height//2+100, text = "at "+str(data.inputbpm)+ " beats per minute!", fill = "purple", font = 'Courier 22')
        data.newSongName = 'changed'+data.song

    if data.state == 'randomSong':
        canvas.create_text(data.width//2, data.height//2, text = "here's your song: " + data.song, font = 'Courier 22')

    if data.state == 'bpmDisplay':
        canvas.create_text(data.width//2, data.height//2+100, text = "here's your calculated bpm: " + str(data.inputbpm), font = 'Courier 22')

    if data.state in data.reversiblestates :
        canvas.create_image(30, 450, anchor=NW, image=data.icon)

    if data.isplaying == True: 
        canvas.create_image(740, 450, anchor=NW, image=data.pausebutton)
        canvas.create_image(705, 450, anchor=NW, image=data.reload)
def musicThread(data):
    newSongName = 'changed' + data.song

    if data.isplaying:
        try:
            play(newSongName, data.paused)
        except:
            play(data.song, data.paused)


####################################
# use the run function as-is       #
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)

        canvas.update()    
    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):

        timerFired(data)
        redrawAllWrapper(canvas, data)

        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 1000 # milliseconds
    root = Tk()
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800,500)




