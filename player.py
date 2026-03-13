import pygame
import aux
import playlists
import os
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)

def loop_status():
    print("LOOP STATUS")
    aux.show_options(["On", "Off"])
    rt = aux.validate_number(["On", "Off"])
    if rt == -1:
        return -1
    else:
        if rt == 1:
            return "on"
        else:
            return "off"

def manage_commands(path, paused):

    command = aux.check_input()

    if command:

        command = command.lower()

        if command == "skip":
            pygame.mixer.music.stop()
            return paused, -2

        if command == "pause":
            pygame.mixer.music.pause()
            paused = True

        if command == "resume":
            pygame.mixer.music.unpause()
            paused = False

        if command == "previous":
            return paused, -3

        if command == "stop":
            pygame.mixer.music.stop()
            return paused, -1

        if command == "up":
            vol=pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(min(vol + 0.1, 1.0))
            print(f"Volume: {100*pygame.mixer.music.get_volume():.2f}%")

        if command == "mute":
            vol=pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            print(f"Volume: {100*pygame.mixer.music.get_volume():.2f}%")   

        if command =="down":
            vol=pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(max(vol - 0.1, 0.0))
            print(f"Volume: {100*pygame.mixer.music.get_volume():.2f}%")

        if command == "restart":
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

    return paused, None

def play_playlist():

    playlist = playlists.pick_playlist()

    if playlist == -1:
        return -1

    list_songs = [
        s for s in os.listdir(playlist)
        if os.path.isfile(os.path.join(playlist, s)) and s.endswith(".mp3")
    ]
    lp = loop_status()
    if lp == -1:
        return -1
    else:
        if lp == "on":
            while True:
                for idx, p in enumerate(list_songs):

                    path = os.path.join(playlist, p)

                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()

                    paused = False

                    print(f"\nNow playing: {p}\nQueue position: [{idx+1}/{len(list_songs)}]")
                    print("Commands: pause | resume | previous | skip | stop | up | down | mute")

                    while pygame.mixer.music.get_busy() or paused:

                        paused, rt = manage_commands(path, paused)

                        if rt == -1:
                            return -1

                        elif rt == -2:
                            break
                        elif rt == -3:
                            if idx != 0:
                                path = os.path.join(playlist, list_songs[idx-1])
                                pygame.mixer.music.load(path)
                                pygame.mixer.music.play()    
                            else:
                                print("Can't go back cuz ts is the 1st song")

                        pygame.time.Clock().tick(10)
        else: # se que esto esta mal pero bueno, pajubi
            while True:
                for idx, p in enumerate(list_songs):

                    path = os.path.join(playlist, p)

                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()

                    paused = False

                    print(f"\nNow playing: {p}\nQueue position: [{idx+1}/{len(list_songs)}]")
                    print("Commands: pause | resume | previous | skip | stop | up | down | mute")

                    while pygame.mixer.music.get_busy() or paused:

                        paused, rt = manage_commands(path, paused)

                        if rt == -1:
                            return -1

                        elif rt == -2:
                            break
                        elif rt == -3:
                            if idx != 0:
                                path = os.path.join(playlist, list_songs[idx-1])
                                pygame.mixer.music.load(path)
                                pygame.mixer.music.play() 
                                idx-=1
                                print(f"\nNow playing: {p}\nQueue position: [{idx+1}/{len(list_songs)}]")
                                print("Commands: pause | resume | previous | skip | stop | up | down | mute") 
                            else:
                                print("Can't go back cuz ts is the 1st song")

                        pygame.time.Clock().tick(10)

def mix_mode():

    all_playlists = [d for d in os.listdir() if os.path.isdir(d)]

    all_songs = []

    for playlist in all_playlists:

        songs = [
            os.path.join(playlist, s)
            for s in os.listdir(playlist)
            if os.path.isfile(os.path.join(playlist, s)) and s.endswith(".mp3")
        ]

        all_songs.extend(songs)

    random.shuffle(all_songs)

    for idx, path in enumerate(all_songs):

        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        paused = False
        print(f"\nNow playing: {os.path.basename(path)}\nQueue position: [{idx+1}/{len(all_songs)}]")
        print("Commands: pause | resume | previous | skip | restart | stop | up | down")

        while pygame.mixer.music.get_busy() or paused:

            paused, rt = manage_commands(path, paused)

            if rt == -1:
                return -1

            elif rt == -2:
                break
            elif rt == -3:
                if idx != 0:
                    path = all_songs[idx-1]
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                    idx-=1
                    print(f"\nNow playing: {os.path.basename(path)}\nQueue position: [{idx+1}/{len(all_songs)}]")
                    print("Commands: pause | resume | previous | skip | stop | up | down")
                    continue
                else:
                    print("Can't go back cuz ts is the 1st song")

            pygame.time.Clock().tick(10)


def search_song():
    all_playlists = [p for p in os.listdir() if os.path.isdir(p)]
    string = aux.validate_string_v2("Which song you want")
    if string == 1:
        return -1
    else:
        matches = []
        for playlist in all_playlists:
            all_songs = [os.path.join(playlist, s)for s in os.listdir(playlist)if os.path.isfile(os.path.join(playlist, s)) and s.endswith(".mp3")]
            for song in all_songs:
                if string in song.lower():
                    matches.append(song)
        if len(matches) == 0:
            print("There are no matches ")
            return -1
        else:
            aux.show_options(matches)
            rt = aux.validate_number(matches)
            if rt == -1:
                return -1
            else:
                winner = matches[rt-1]
                pygame.mixer.music.load(winner)
                lp = loop_status()
                if lp == -1:
                    return -1
                else:
                    if rt == "on":
                        pygame.mixer.music.play(loops=-1)
                    else:
                        pygame.mixer.music.play()
                paused = False
                print(f"\nNow playing: {os.path.basename(winner)}")
                print("Commands: pause | resume | previous | skip | restart | stop | up | down")

                while pygame.mixer.music.get_busy() or paused:

                    paused, rt = manage_commands(winner, paused)

                    if rt == -1:
                        return -1

                    elif rt == -2:
                        break
                    elif rt == -3:
                        break
                    pygame.time.Clock().tick(10)
