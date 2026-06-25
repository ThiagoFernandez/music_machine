import os
import re

import requests
from mutagen.mp3 import MP3

import auxiliar


def clean_title(title):
    """
    Limpia adornos cosméticos del título pero respeta los markers
    de edits/mixes/alternates para no buscar versiones equivocadas.
    """
    if not title:
        return None

    # markers que indican una version no oficial → no buscamos
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

    # patrones cosmoticos a eliminar
    cosmetic = [
        # cualquier (Official...) o [Official...]
        r"\(\s*official[^)]*\)",
        r"\[\s*official[^\]]*\]",
        # featurings: (feat. X), (ft. X), (featuring X)
        r"\(\s*feat\.?[^)]*\)",
        r"\(\s*ft\.?[^)]*\)",
        r"\(\s*featuring[^)]*\)",
        r"\[\s*feat\.?[^\]]*\]",
        r"\[\s*ft\.?[^\]]*\]",
        r"\[\s*featuring[^\]]*\]",
        # otros adornos
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
        # adornos de versión
        r"\(\s*remaster(ed)?[^)]*\)",
        r"\[\s*remaster(ed)?[^\]]*\]",
        r"\(\s*\d{4}\s+remaster[^)]*\)",
        r"\[\s*\d{4}\s+remaster[^\]]*\]",
        r"\(\s*deluxe[^)]*\)",
        r"\[\s*deluxe[^\]]*\]",
        r"\(\s*explicit[^)]*\)",
        r"\[\s*explicit[^\]]*\]",
        r"\(\s*hd\s*remaster[^)]*\)",
        r"\[\s*hd\s*remaster[^\]]*\]",
    ]
    for p in cosmetic:
        title = re.sub(p, "", title, flags=re.IGNORECASE)

    # puntuacion final que confunde al matching de la API
    title = title.rstrip("?!.").strip()

    return title or None


def clean_artist(artist):
    """
    Normaliza el artist:
    - reemplaza comas CJK (japonesa/china) por comas normales
    - si hay múltiples artistas (coma, &, feat, ft), toma solo el primero
    """
    if not artist:
        return None
    # caracteres CJK que YouTube/YT Music a veces meten (la coma esa ponja)
    artist = artist.replace("，", ",").replace("、", ",")
    # tomar solo el primer artista
    for sep in [",", "&", " feat.", " ft.", " featuring", " x ", " X "]:
        if sep in artist:
            artist = artist.split(sep, 1)[0]
            break
    return artist.strip() or None


def fetch_from_lrclib(artist, title, duration=None, interactive=False):
    if not title:
        return None
    title = clean_title(title)
    if not title:
        return None
    artist = clean_artist(artist)
    print(f"  [debug] artist={artist!r}, title={title!r}, duration={duration}")

    # primer intento con el titulo limpio
    result = _try_lrclib(artist, title, duration, interactive)
    if result:
        return result

    # retry: si el titulo todavia tiene parentesis o corchetes
    # (probable subtitulo de la cancion), probar sin eso
    stripped = re.sub(r"\s*\([^)]*\)\s*", " ", title).strip()
    stripped = re.sub(r"\s*\[[^\]]*\]\s*", " ", stripped).strip()
    if stripped and stripped != title:
        result = _try_lrclib(artist, stripped, duration, interactive)
        if result:
            return result

    return None


def _try_lrclib(artist, title, duration, interactive):
    # 1. search (rápido, fuzzy, siempre responde)
    try:
        params = {"track_name": title}
        if artist:
            params["artist_name"] = artist
        r = requests.get("https://lrclib.net/api/search", params=params, timeout=10)
        if r.status_code != 200:
            return None
        results = r.json()
    except Exception:
        return None

    if not results:
        return None

    # filtrar por duration ±5s
    if duration:
        close = [
            res
            for res in results
            if res.get("duration") and abs(res["duration"] - duration) <= 5
        ]
        if close:
            results = close

    if len(results) == 1:
        return _extract_lyrics(results[0])

    if interactive:
        return _ask_user_to_pick(results, title)

    for item in results:
        result = _extract_lyrics(item)
        if result:
            return result
    return None


def _extract_lyrics(item):
    if item.get("instrumental"):
        return "[Instrumental]"
    return item.get("plainLyrics") or None


def _ask_user_to_pick(results, query_title):
    """Muestra opciones al usuario para elegir entre múltiples matches."""
    options = [
        f"{r.get('artistName', '?')} - {r.get('trackName', '?')}"
        f" [{r.get('duration', '?')}s] - {r.get('albumName', '?')}"
        for r in results[:10]
    ]
    print(f"\nMultiple matches for '{query_title}':")
    auxiliar.show_options(options)
    choice = auxiliar.validate_number(options)
    if choice == -1:
        return None
    return _extract_lyrics(results[choice - 1])


def save_lyrics(mp3_path, lyrics_text):
    try:
        txt_path = os.path.splitext(mp3_path)[0] + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(lyrics_text)
        return True
    except Exception:
        return False


def load_lyrics(mp3_path):
    txt_path = os.path.splitext(mp3_path)[0] + ".txt"
    if not os.path.exists(txt_path):
        return None
    try:
        with open(txt_path, encoding="utf-8") as f:
            return f.read() or None
    except Exception:
        return None


def ensure_lyrics_for_folder(folder, get_metadata_fn, interactive=False):
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
        lyrics_text = fetch_from_lrclib(
            artist, title, duration, interactive=interactive
        )
        processed += 1
        if lyrics_text:
            save_lyrics(mp3_path, lyrics_text)
            found += 1
            print(f"  ✓ {title}")
        elif clean_title(title) is None:
            print(f"  ~ {title}  (edit/mix, skipped)")
        else:
            print(f"  ✗ {title}  (not found)")
    return processed, found
