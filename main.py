import subprocess
import aux
import file
import playlists
import os

def show_menu(menu, lista_opt, lista_funciones):
    while True:
        print(f"{' Welcome to the ' + menu+" ":-^60}")
        aux.show_options(lista_opt)
        result = aux.validate_number(lista_opt)
        if result == -1:
            return
        lista_funciones[result-1]()

def show_main_menu():
    while True:
        print(f"{' Welcome to the main menu ':-^60}")
        aux.show_options(["Play Menu", "Playlist Menu", "Files Menu"])
        result = aux.validate_number(["Play Menu", "Playlist Menu", "Files Menu"])
        if result == -1:
            return
        else:
            match result:
                case 1:
                    lista_opt_n = ["Select Playlist", "All songs"]
                    lista_fun_n = [select_playlist, mix_mode]
                    menu_f = "play menu"
                    show_menu(menu_f, lista_opt_n, lista_fun_n)
                case 2:
                    lista_opt_c = ["Create a playlist", "Delete a playlist", "Rename a playlist"]
                    lista_fun_c = [playlists.create_playlist, playlists.delete_playlist, playlists.rename_playlist]
                    menu_c = "playlist menu"
                    show_menu(menu_c, lista_opt_c, lista_fun_c)
                case 3:
                    lista_opt_t = ["Download a song", "Rename a song", "Delete a song"]
                    lista_fun_t = [file.download_music, file.rename_song, file.delete_song]
                    menu_t = "FIles menu"
                    show_menu(menu_t, lista_opt_t, lista_fun_t)

# m.p


show_main_menu()