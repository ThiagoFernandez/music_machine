import os
import random
import time
from turtle import clear

import pygame
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from pypresence import Presence

import auxiliar
import playlists

client_id = "1505235525223841952"
RPC = None


def get_song_metadata(path):
    try:
        tags = ID3(path)
        title = tags["TIT2"].text[0] if "TIT2" in tags else None
        artist = tags["TPE1"].text[0] if "TPE1" in tags else None
        if title and artist:
            return title, artist
    except Exception:
        pass
    name = os.path.splitext(os.path.basename(path))[0]
    if " - " in name:
        parts = name.split(" - ", 1)
        return parts[1].strip(), parts[0].strip()
    return name, None


def get_song_duration(path):
    try:
        return int(MP3(path).info.length)  # segundos
    except Exception:
        return None


def connect_rpc():
    global RPC
    try:
        RPC = Presence(client_id)
        RPC.connect()
        print("Discord RPC connected")
    except Exception:
        RPC = None  # para q no te explote el programa si tenes ds close
        print("Discord RPC failed not available")


def update_rpc(title, artist=None, duration=None):
    if RPC:
        try:
            now = int(time.time())
            RPC.update(
                details=title,
                state=artist
                if artist
                else "noname",  # o sea, no todos los files van a tener su artista por ende pongo como un placeholder
                start=now,
                end=now + duration if duration else None,
                large_image="boombox_1_",
                large_text=title,
            )
        except Exception:
            pass


def clear_rpc():
    if RPC:
        try:
            RPC.clear()
        except Exception:
            pass


pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)
current_volume = 0.5

COMMANDS_HINT = (
    "Commands: pause | resume | previous | skip | restart | stop | up | down | mute"
)


def play_queue(queue, loop_on=False, previous_exits=False):
    if len(queue) > 1:
        print("Do you want to enable shuffe?")
        options = ["yes", "no"]
        auxiliar.show_options(options)
        rt = auxiliar.validate_number(options)
        if rt == -1:
            return
        if options[rt - 1] == "yes":
            random.shuffle(queue)
    while True:
        idx = 0
        while idx < len(queue):
            path = queue[idx]
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            title, artist = get_song_metadata(path)
            duration = get_song_duration(path)
            update_rpc(title or os.path.basename(path), artist, duration)
            paused = False
            print(f"\nNow playing: {title}")
            print(f"Queue position: [{idx + 1}/{len(queue)}]")
            print(COMMANDS_HINT)

            go_previous = False
            while pygame.mixer.music.get_busy() or paused:
                paused, rt = manage_commands(path, paused)
                if rt == -1:
                    return -1
                elif rt == -2:  # skip
                    break
                elif rt == -3:  # previous
                    if idx != 0:
                        pygame.mixer.music.stop()
                        go_previous = True
                        break
                    elif previous_exits:
                        pygame.mixer.music.stop()
                        return clear_rpc()
                    else:
                        print("Can't go back cuz ts is the 1st song")
                pygame.time.Clock().tick(10)

            idx = idx - 1 if go_previous else idx + 1

        if not loop_on:
            return clear_rpc()


def loop_status():
    print("LOOP STATUS")
    auxiliar.show_options(["On", "Off"])
    rt = auxiliar.validate_number(["On", "Off"])
    if rt == -1:
        return -1
    return "on" if rt == 1 else "off"


def manage_commands(path, paused):
    global current_volume
    command = auxiliar.check_input()
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
            current_volume = min(current_volume + 0.1, 1.0)
            pygame.mixer.music.set_volume(current_volume)
            print(f"Volume: {100 * current_volume:.0f}%")
        if command == "mute":
            current_volume = 0.0
            pygame.mixer.music.set_volume(0.0)
            print("Volume: 0%")
        if command == "down":
            current_volume = max(current_volume - 0.1, 0.0)
            pygame.mixer.music.set_volume(current_volume)
            print(f"Volume: {100 * current_volume:.0f}%")
        if command == "restart":
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
    return paused, None


def play_playlist():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    queue = [
        os.path.join(playlist, s)
        for s in os.listdir(playlist)
        if os.path.isfile(os.path.join(playlist, s)) and s.endswith(".mp3")
    ]
    lp = loop_status()
    if lp == -1:
        return -1
    play_queue(queue, loop_on=(lp == "on"))


def mix_mode():
    queue = []
    for p in os.listdir():
        if os.path.isdir(p):
            queue.extend(
                os.path.join(p, s)
                for s in os.listdir(p)
                if os.path.isfile(os.path.join(p, s)) and s.endswith(".mp3")
            )
    play_queue(queue, loop_on=False)


def search_song():
    string = auxiliar.validate_string_v2("Which song you want")
    if string == -1:
        return -1
    string = string.lower()
    matches = []
    for p in os.listdir():
        if os.path.isdir(p):
            for s in os.listdir(p):
                full = os.path.join(p, s)
                if os.path.isfile(full) and s.endswith(".mp3") and string in s.lower():
                    matches.append(full)
    if not matches:
        print("There are no matches")
        return -1
    auxiliar.show_options(matches)
    rt = auxiliar.validate_number(matches)
    if rt == -1:
        return -1
    lp = loop_status()
    if lp == -1:
        return -1
    play_queue([matches[rt - 1]], loop_on=(lp == "on"), previous_exits=True)
