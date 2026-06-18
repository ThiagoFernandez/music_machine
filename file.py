import os
import subprocess
import sys

from mutagen.id3 import ID3

import auxiliar
import lyrics
import playlists


def get_song_metadata(path):
    title = None
    artist = None
    try:
        tags = ID3(path)
        title = (
            tags["TIT2"].text[0] if "TIT2" in tags else None
        )  # antes manejaba mal el titulo y el artista
        artist = tags["TPE1"].text[0] if "TPE1" in tags else None
    except Exception:
        pass

    # yt-dlp con YouTube mete el titulo del video crudo en TIT2.
    # Si tiene " - ", splittear para separar artist y title.
    if title and " - " in title:
        parts = title.split(" - ", 1)
        artist = parts[
            0
        ].strip()  # por lo q vi, por norma general ponen el nombre del artista antes
        title = parts[1].strip()

    if title:
        return title, artist

    # Fallback final: filename
    name = os.path.splitext(os.path.basename(path))[0]
    if " - " in name:
        parts = name.split(" - ", 1)
        return parts[1].strip(), parts[0].strip()
    return name, None


def show_report(playlist, interactive=False):
    print("\nFetching lyrics...")
    processed, found = lyrics.ensure_lyrics_for_folder(
        playlist, get_song_metadata, interactive=interactive
    )
    print(f"Lyrics: {found}/{processed} found\n")


def download_music():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    else:
        while True:
            try:
                option = int(
                    input(f"1 -> song\n2 -> playlist\n3 -> exit\nChoose an option: ")
                )
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

                            subprocess.run(
                                [
                                    sys.executable,
                                    "-m",
                                    "yt_dlp",
                                    "--no-playlist",
                                    "--embed-thumbnail",
                                    "--embed-metadata",
                                    "--parse-metadata",
                                    "title:^(?P<artist>.+?) - (?P<title>.+)$",
                                    "--parse-metadata",
                                    "%(artist|uploader)s:^(?P<artist>.+?)(?:\\s*-\\s*Topic\\s*)?$",
                                    "-x",
                                    "--audio-format",
                                    "mp3",
                                    "--audio-quality",
                                    "0",
                                    "-o",
                                    output_path,
                                    url,
                                ]
                            )
                            show_report(playlist, interactive=True)
                        else:
                            url = input(
                                "Copy the link from youtube\n"
                                "To paste use 'ctrl + shift + v'\n>>>: "
                            ).strip()

                            output_path = os.path.join(playlist, "%(title)s.%(ext)s")

                            subprocess.run(
                                [
                                    sys.executable,
                                    "-m",
                                    "yt_dlp",
                                    "--embed-thumbnail",
                                    "--embed-metadata",
                                    "--parse-metadata",
                                    "title:^(?P<artist>.+?) - (?P<title>.+)$",
                                    "-x",
                                    "--audio-format",
                                    "mp3",
                                    "--audio-quality",
                                    "0",
                                    "-o",
                                    output_path,
                                    url,
                                ]
                            )
                            show_report(playlist, interactive=False)

            except ValueError:
                print("The option must be a number | Try again")


def rename_song():
    playlist = playlists.pick_playlist()
    if playlist == -1:
        return -1
    else:
        song = auxiliar.pick_song(playlist)
        if song == -1:
            return -1
        else:
            new_name = auxiliar.validate_string(
                [song], "Write the new name for the song", 0
            )
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
        song = auxiliar.pick_song(playlist)
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
        song = auxiliar.pick_song(playlist)
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
