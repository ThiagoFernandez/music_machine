import subprocess
import os
import aux
import playlists
import sys


def download_music():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    else:
        while True:
            try:
                option = int(input(f"1 -> song\n2 -> playlist\n3 -> exit\nChoose an option: "))
                if option == 3:
                    return None
                else:
                    if option < 1 or option > 3:
                        print("The option must be between 1-3 | Try again")
                    else:
                        if option == 1:
                            url = input(
                                "Copy the link from youtube\n"
                                "To paste use 'ctrl + shift + v'\n>>>: "
                            ).strip()

                            output_path = os.path.join(playlist, "%(title)s.%(ext)s")

                            subprocess.run([
                                sys.executable,
                                "-m", "yt_dlp",
                                "--no-playlist", # para el file settings lo mas probable
                                "-x",
                                "--audio-format", "mp3",
                                "--audio-quality", "0",
                                "-o", output_path,
                                url
                            ])
                        else:
                            url = input(
                                "Copy the link from youtube\n"
                                "To paste use 'ctrl + shift + v'\n>>>: "
                            ).strip()

                            output_path = os.path.join(playlist, "%(title)s.%(ext)s")

                            subprocess.run([
                                sys.executable,
                                "-m", "yt_dlp",
                                "-x",
                                "--audio-format", "mp3",
                                "--audio-quality", "0",
                                "-o", output_path,
                                url
                            ])
            except ValueError:
                print("The option must be a number | Try again")

def rename_song():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    else:
        song = aux.pick_song(playlist)
        if song == -1:
            return -1
        else:
            new_name = aux.validate_string([song], "Write the new name for the song", 0)
            if new_name == -1:
                return -1
            else:
                old_path = os.path.join(playlist, song)
                new_path = os.path.join(playlist, new_name)
                os.rename(old_path, new_path)

def delete_song():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    else:
        song = aux.pick_song(playlist)
        if song == -1:
            return -1
        else:
            path = os.path.join(playlist, song)
            os.remove(path)

def move_song():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    else:
        song = aux.pick_song(playlist)
        if song == -1:
            return -1
        else:
            new_playlist = playlists.pick_playlist()
            if new_playlist == playlist:
                print("This song is already in this playlist")
            elif new_playlist == -1:
                return -1
            else:
                old_path = os.path.join(playlist, song)
                new_path = os.path.join(new_playlist, song)
                os.rename(old_path, new_path)