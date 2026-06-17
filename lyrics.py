import os
import re

import requests
from mutagen.id3 import ID3
from mutagen.mp3 import MP3


def clean_title(title):
    """
    Limpio los adornos estilo official o cosas asi pero no los titutlos alternativos para evitar mismatches
    """
    if not title:
        return None

    # si el título contiene marcadores de edit/mix/alternate, no buscamos
    skip_markers = [
        "extended",
        "alternate",
        "mashup",
        "mix",
        "edit",
        "remix",
        "fan made",
        "fanmade",
        "leak",
        "but it ",
        "but you ",
        "if it ",
        " x ",
        "~",
    ]
    lower = title.lower()
    if any(marker in lower for marker in skip_markers):
        return None

    # los q si!!!
    cosmetic = [
        r"\(\s*official[^)]*\)",
        r"\[\s*official[^\]]*\]",
        r"\(\s*music\s+video\s*\)",
        r"\(\s*lyric\s+video\s*\)",
        r"\(\s*lyrics?\s*\)",
        r"\(\s*audio\s*\)",
        r"\(\s*hd\s*\)",
        r"\(\s*4k\s*\)",
        r"\[\s*music\s+video\s*\]",
        r"\[\s*lyric\s+video\s*\]",
        r"\[\s*lyrics?\s*\]",
        r"\[\s*audio\s*\]",
        r"\[\s*hd\s*\]",
        r"\[\s*4k\s*\]",
    ]
    for p in cosmetic:
        title = re.sub(p, "", title, flags=re.IGNORECASE)

    return title.strip() or None


def fetch_from_lrclib(artist, title, duration=None):
    """Pega a LRCLIB. Devuelve lyrics planas, [Instrumental], o None."""
    if not artist or not title:
        return None
    title = clean_title(title)
    if not title:
        # print("Not an official version | Couldn't find a exact match for this")
        return None
    try:
        params = {"artist_name": artist, "track_name": title}
        if duration:
            params["duration"] = duration
        r = requests.get("https://lrclib.net/api/get", params=params, timeout=5)
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("instrumental"):
            return "[Instrumental]"
        return data.get("plainLyrics") or None
    except Exception:
        return None


def save_lyrics(mp3_path, lyrics_text):
    """Guarda lyrics como .txt al lado del MP3."""
    try:
        txt_path = os.path.splitext(mp3_path)[0] + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(lyrics_text)
        return True
    except Exception:
        return False


def load_lyrics(mp3_path):
    """Lee lyrics cacheadas de disco (o None si no existe)."""
    txt_path = os.path.splitext(mp3_path)[0] + ".txt"
    if not os.path.exists(txt_path):
        return None
    try:
        with open(txt_path, encoding="utf-8") as f:
            return f.read() or None
    except Exception:
        return None


def ensure_lyrics_for_folder(folder, get_metadata_fn):
    """
    Recorre todos los .mp3 de una carpeta. Para los que no tengan .txt asociado,
    busca en LRCLIB y guarda. get_metadata_fn(path) -> (title, artist).
    Devuelve (procesados, encontrados).
    """
    processed = 0
    found = 0
    for filename in os.listdir(folder):
        if not filename.endswith(".mp3"):
            continue
        mp3_path = os.path.join(folder, filename)
        txt_path = os.path.splitext(mp3_path)[0] + ".txt"
        if os.path.exists(txt_path):
            continue
        title, artist = get_metadata_fn(mp3_path)
        duration = None
        try:
            duration = int(MP3(mp3_path).info.length)
        except Exception:
            pass
        lyrics = fetch_from_lrclib(artist, title, duration)
        processed += 1
        if lyrics:
            save_lyrics(mp3_path, lyrics)
            found += 1
            print(f"  ✓ {title}")
        elif clean_title(title) is None:
            print(f"  ~ {title}  (edit/mix, skipped)")
        else:
            print(f"  ✗ {title}  (not found)")
    return processed, found
