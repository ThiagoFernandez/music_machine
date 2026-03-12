import os
import aux
import shutil

def create_playlist():
    new_playlist = input("Write the name of your new playlist: ").strip()
    playlist_path = os.path.join(new_playlist)

    if os.path.exists(playlist_path):
        print(f"The playlist - {new_playlist} already exists")
    else:
        os.mkdir(playlist_path)
        print(f"The playlist - {new_playlist} was created")
    return None

def pick_playlist():

    all_playlist = [d for d in os.listdir() if os.path.isdir(d)]
    aux.show_options(all_playlist)
    playlist = aux.validate_number(all_playlist)
    if playlist == -1:
        return -1
    else:
        return all_playlist[playlist-1]

def rename_playlist():
    playlist = pick_playlist()
    if pick_playlist == -1:
        return -1
    else:
        new_name = aux.validate_string([playlist], "Write the new name of the playlist", 1)
        if new_name == -1:
            return -1
        else:
            os.rename(playlist, new_name)

def delete_playlist():
    playlist = pick_playlist()
    if pick_playlist == -1:
        return -1
    else:
        shutil.rmtree(playlist)