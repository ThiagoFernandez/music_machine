import pygame
import pygame._sdl2.audio as sdl2_audio

import auxiliar


def list_devices():
    pygame.init()
    return sdl2_audio.get_audio_device_names(False)


def choose_device(devices):
    auxiliar.show_options(devices)
    opt = auxiliar.validate_number(devices)
    if opt == -1:
        return None
    return devices[opt - 1]
