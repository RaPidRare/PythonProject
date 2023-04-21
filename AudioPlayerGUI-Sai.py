import random
from tkinter import *
import mutagen.mp3
import pygame
from PIL import Image, ImageTk
from queue import *
from pygame import mixer
#import music_tag as music
import os
import json
import re
from ToolTip import CreateToolTip

# TODO: Implement Shuffle and Loop options, don't use methods, add shuffle to _startPlaylist() and loop to nextSong() or SongEnd()
# TODO: get playlist creator working, use os.list_dir, already have some code in place, add check for empty playlists
# TODO: get non-corrupted songs, make sure the downloaded version play using the windows media player #Can download songs from royalty free music sites.
# TODO: maybe add album and/or artist labels, would need to move buttons down more
# TODO: try to get lyrics working with another toplevel
# I can go through all the code later this weekend to clean everything up and make it presentable

root = Tk()

arial12 = ("Arial", 12)

pauseImage = ImageTk.PhotoImage(Image.open(r"Images/pause.png").resize((30, 47)))
playImage = ImageTk.PhotoImage(Image.open(r"Images/play.png").resize((30, 47)))
nextImage = ImageTk.PhotoImage(Image.open(r"Images/forward.png").resize((30, 30)))
previousImage = ImageTk.PhotoImage(Image.open(r"Images/reverse.png").resize((30, 30)))
rewindImage = ImageTk.PhotoImage(Image.open(r"Images/skip-15-seconds-back.png").resize((30, 30)))
skipImage = ImageTk.PhotoImage(Image.open(r"Images/skip-ahead-15-seconds.png").resize((30, 30)))
restartImage = ImageTk.PhotoImage(Image.open(r"Images/restart.png").resize((30, 30)))
defaultArt = ImageTk.PhotoImage(Image.open(r"Images/DefaultArt.png"), "192x192")

scrub_time = 0
current_song = None
next_song = None
queue = Queue()
shuffle = BooleanVar(value=False)
loop = BooleanVar(value=False)
replay = BooleanVar(value=False)
loadedSongData = {
    "title": Variable(value="-"),
    "album": Variable(value="-"),
    "artist": Variable(value="-")
}

albumArt = None


def main():
    global albumArt
    root.title("MP3 Player")
    pygame.init()
    mixer.init()
    mixer.music.set_endevent(pygame.USEREVENT + 1)

    albumArt = Label(image=defaultArt)
    albumArt.grid(row=0, column=0, padx=10, pady=10, columnspan=6)

    title = Label(textvariable=loadedSongData["title"])
    title.grid(row=1, column=0, pady=5, columnspan=5)

    # button

    plauseButton = Button(root, image=pauseImage, borderwidth=0)
    plauseButton.config(command=lambda: plause(plauseButton))
    nextButton = Button(root, image=nextImage, command=nextSong, borderwidth=0)
    previousButton = Button(root, image=previousImage, command=reverse, borderwidth=0)
    rewind = Button(root, image=rewindImage, command=reverse, borderwidth=0)
    skip = Button(root, image=skipImage, command=forward, borderwidth=0)
    restartButton = Button(root, image=restartImage, command=restart, borderwidth=0)
    replayButton = Checkbutton(root, text="loop", command=replay)
    playlistButton = Button(root, text="Playlists", font=("Arial", 13), command=openPlaylists)
    lyricButton = Button(root, text="Lyrics", command=getLyrics)
    albumButton = Button(root, text="Album", command=tempcommand2)

    previousButton.grid(row=2, column=0, pady=5)
    rewind.grid(row=2, column=1, pady=5)
    plauseButton.grid(row=2, column=2, pady=5)
    skip.grid(row=2, column=3, pady=5)
    nextButton.grid(row=2, column=4, pady=5)
    restartButton.grid(row=3, column=0, pady=5)
    replayButton.grid(row=3, column=4, pady=5)
    playlistButton.grid(row=3, column=1, pady=5, columnspan=3)
    lyricButton.grid(row=4, column=1, pady=5)
    albumButton.grid(row=4, column=2, pady=5)
    checkEvent()
    root.mainloop()


def checkEvent():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT + 1:
            print('music end event')
            songEnd()
        else:
            print("other event")

    root.after(100, checkEvent)


def playSong(file):
    global scrub_time, albumArt
    print("unloading song")
    mixer.music.unload()
    print("loading new song")
    mixer.music.load(file)
    print("playing song")
    mixer.music.play()
    scrub_time = 0
    loadData(file)


def loadData(file):
    """
    file: Must be absolute or relative path"""
    global loadedSongData, albumArt
    print("loading song data...")
    songData = music.load_file(file)
    loadedSongData["title"].set(songData["tracktitle"])
    loadedSongData["artist"].set(songData["artist"])
    loadedSongData["lyrics"].set(songData["lyrics"])
    loadedSongData["album"].set(songData["album"])
    if songData["artwork"].first is not None:
        art = songData["artwork"].first.thumbnail([192, 192])
        art = ImageTk.PhotoImage(art)
        loadedSongData["artwork"] = art
    else:
        art = defaultArt
    albumArt.config(image=art)
    print("finished loading song data")


def songEnd():
    global current_song, next_song, scrub_time
    print("starting next song...")
    if loop.get():
        queue.put(current_song)
    current_song = next_song
    if not queue.empty():
        next_song = queue.get()
    else:
        next_song = None
    print("calling playSong()")
    playSong(current_song)
    print("done")



def forward():
    global scrub_time
    time = mixer.music.get_pos() / 1000
    mixer.music.play(start=time + 15 + scrub_time)
    scrub_time += 15


def reverse():
    global scrub_time
    time = mixer.music.get_pos() / 1000
    mixer.music.play(start=time - 15 + scrub_time)
    scrub_time -= 15


def nextSong():
    global scrub_time, next_song, current_song
    if next_song is not None:
        scrub_time = 0
        mixer.music.load(next_song)
        mixer.music.play()
        if loop.get():
            queue.put(current_song)
            current_song = next_song

        current_song = next_song
        if not queue.empty():
            next_song = queue.get()
    else:
        scrub_time = 0
        mixer.music.rewind()


def plause(button):
    if mixer.music.get_busy():
        button.config(image=playImage)
        mixer.music.pause()
    else:
        button.config(image=pauseImage)
        mixer.music.unpause()


def restart():
    global scrub_time
    scrub_time = 0
    mixer.music.rewind()
    return


def replay():
    return


def shuffle():
    if queue.empty():
        tempTop = Toplevel()
        tempTop.title("tried to shuffle")
        tempLabel = Label(tempTop, text="Could not shuffle queue, add songs to queue")
        return
    else:

        return

def getLyrics():
    lyricTop = Toplevel()
    lyricTop.title("Lyrics")
    tempLabel2 = Label(lyricTop, text=str(loadedSongData["lyrics"]))
    tempLabel2.pack()

def getAlbum():
    albumTop = Toplevel()
    albumTop.title("Album and Artist")
    albumLabel = Label(albumTop, text=str(loadedSongData["album"]))
    albumLabel.pack()
    artistLabel = Label(albumTop, text=str(loadedSongData["artist"]))
    artistLabel.pack()

def openPlaylists():
    global current_song, next_song
    playlistsVar = Variable()
    playlistsList = _findPlaylists(playlistsVar)

    win = Toplevel()
    win.title("Playlist Selector")

    def _startPlaylist():
        global current_song, next_song
        select = playlists.curselection()
        if len(select) > 0:
            while not queue.empty():
                queue.get()
        playlist = playlistsList[select[0]]
        for song in playlist["songs"]:
            queue.put(f"Songs/{song}")
        current_song = queue.get()
        if not queue.empty():
            next_song = queue.get()
        win.destroy()
        mixer.music.load(current_song)
        playSong(current_song)

    directions = Label(win, text="Select a Playlist:", font=("Arial", 15))
    directions.grid(row=0, column=0, columnspan=2, pady=5)

    shuffleToggle = Checkbutton(win, text="Shuffle")
    shuffleToggle.grid(row=1, column=0, pady=5)

    loopToggle = Checkbutton(win, text="Loop")
    loopToggle.grid(row=1, column=1, pady=5)

    playlists = Listbox(win, width=30, listvariable=playlistsVar)
    playlists.grid(row=3, column=0, columnspan=2, pady=5, padx=10)

    doneButton = Button(win, text="Done", font=arial12, command=_startPlaylist)
    doneButton.grid(row=4, column=1, pady=5)

    cancelButton = Button(win, text="Cancel", font=arial12, command=win.destroy)
    cancelButton.grid(row=4, column=0, pady=5)

    createPlaylistButton = Button(win, text="Create Playlist", font=arial12, command=_createPlaylist)
    createPlaylistButton.grid(row=5, column=0, columnspan=2, pady=5)


def _findPlaylists(playlistVar):
    playlists = []
    tempList = []
    fileList = os.listdir("Playlists")
    fileList = list(filter(lambda x: ".json" in x, fileList))
    for file in fileList:
        with open(f"Playlists/{file}") as jsonFile:
            jsonFile = json.load(jsonFile)
        playlistItem = {
            "file": file,
            "title": jsonFile["title"],
            "songs": list(jsonFile["songs"])
        }
        tempList.append(jsonFile["title"])
        playlists.append(playlistItem)
    playlistVar.set(tempList)
    return playlists


def _createPlaylist():
    win2 = Toplevel()

    songs = _findAllSongs()
    for item in songs:
        print(item)

    titleDirections = Label(win2, text="Enter a title:", font=arial12)
    titleDirections.grid(row=0, column=0, columnspan=2, pady=5)

    titleEntry = Entry(win2)
    titleEntry.grid(row=1, column=0, columnspan=2, pady=5)

    songDirections = Label(win2, text="Choose your songs:", font=arial12)
    songDirections.grid(row=2, column=0, columnspan=2)

    songList = Listbox(win2, width=40, selectmode=EXTENDED)
    songList.grid(row=3, column=0, columnspan=2, pady=5, padx=10)

    cancelButton2 = Button(win2, text="Cancel", font=arial12, command=win2.destroy)
    cancelButton2.grid(row=4, column=0, pady=5)

    doneButton2 = Button(win2, text="Done", font=arial12)
    doneButton2.grid(row=4, column=1, pady=5)


def _findAllSongs():
    songs = []
    fileList = os.listdir("Songs")
    fileList = list(filter(lambda x: ".mp3" in x, fileList))
    for file in fileList:
        try:
            song = music.load_file(f"Songs/{file}")
        except mutagen.mp3.HeaderNotFoundError:
            print(f"Possible corrupt file found: {file}")
            continue
        if song["title"].first is not None:
            title = song["title"].first
        else:
            title = file

        if song["artist"].first is not None:
            artist = song["artist"].first
        else:
            artist = "Unknown"
        songItem = {
            "file": file,
            "title": title,
            "artist": artist
        }
        songs.append(songItem)
    return songs


main()