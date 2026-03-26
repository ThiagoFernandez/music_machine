import os
import sys
import select
import msvcrt

buffer = ""

def check_input():
    global buffer

    if sys.platform == "win32":
        if msvcrt.kbhit():
            while msvcrt.kbhit():
                char = msvcrt.getwche()
                if char == "\r": # this is the 'enter'
                    print() # ts the br
                    line = buffer
                    buffeer = ""
                    return line
                elif char == "\x08": # ts's the backspace
                    buffeer = buffeer[:-1]
                    print(" \b", end="", flush=True)
                else:
                    buffer += char
        return None
    else:
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.readline().strip()
        return None


def pick_song(playlist):

    all_song = [f for f in os.listdir(playlist) if f.endswith(".mp3")]
    show_options(all_song)
    song = validate_number(all_song)
    if song == -1:
        return -1
    else:
        return all_song[song-1]


def show_options(options):
    for idx, value in enumerate(options):
        print(f"{idx+1}. {value}")
    print(f"{len(options)+1}. Exit")

def validate_number(options):
    while True:
        try:
            option = int(input("Choose an option: "))
        except ValueError:
            print("The value must be a number | Try again")
        else:
            if option < 1 or option > len(options)+1:
                print(f"The option must be between 1-{len(options)+1} | Try again")
            elif option == len(options)+1:
                return -1
            else:
                return option

def validate_string(options, text, type):
    while True:
        string = input(f"{text}('*' to go back to the menu): ")
        if string.strip() == "":
            print("Only blank space as text is invalid | Try again")
        elif string.strip() == "*":
            return -1
        elif string in options:
            print("There is one with the same name | Try again")
        elif not string.endswith(".mp3") and type == 0: 
            print(f"The name needs to end with a '.mp3' | Try again")
        else:
            return string

def validate_command(options, text):
    while True:
        string = input(f"{text}('*' to go back to the menu): ")
        if string.strip() == "":
            print("Only blank space as text is invalid | Try again")
        elif string.strip() == "*":
            return -1
        elif string not in options:
            print("That's not a valid command | Try again")
        else:
            return string

def greeting_text(text):
    print(f"{' ' + text + ' ':-^60}")

def validate_string_v2(text):
    while True:
        string = input(f"{text}('*' to go back to the menu): ")
        if string.strip() == "":
            print("Only blank space as text is invalid | Try again")
        elif string.strip() == "*":
            return -1
        else:
            return string