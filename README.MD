# Music Machine 🎵

A terminal-based music player written in Python. Plays local MP3s organized in playlists, with Discord Rich Presence support and audio device selection.

---

## Features

- **Playlist management** — create, rename, delete playlists; move songs between them
- **Multiple play modes** — play a playlist, shuffle all songs, or search by name
- **Playback controls** — pause, resume, skip, previous, restart, stop, volume up/down, mute
- **Loop mode** — toggle per session
- **Shuffle** — optional per queue
- **Discord Rich Presence** — shows song title, artist and a countdown timer
- **Audio device selection** — choose your output device at startup
- **Song metadata** — reads ID3 tags (artist, title, duration); falls back to filename parsing
- **YouTube download** — download songs or full playlists directly into a playlist folder via yt-dlp

---

## Requirements

Python 3.10+ (uses `match/case`)

Install dependencies:

```bash
pip install pygame-ce mutagen pypresence yt-dlp
```

---

## Setup

**1. Clone the repo and enter the directory:**
```bash
git clone https://github.com/ThiagoFernandez/music_machine.git
cd music_machine 
```

**2. Create at least one playlist folder** in the same directory as the scripts. Each folder is a playlist and should contain `.mp3` files:
```
music_machine/
├── main.py
├── player.py
├── ...
└── My Playlist/
    ├── song1.mp3
    └── song2.mp3
```

**3. (Optional) Discord Rich Presence setup:**

To show what you're listening to on Discord:
1. Go to https://discord.com/developers/applications
2. Create a new application (e.g. "Music Machine")
3. Copy the **Application ID** and paste it as `client_id` in `player.py`
4. Under **Rich Presence → Art Assets**, upload an image and note the asset name
5. Set `large_image` in `update_rpc()` to that asset name

---

## Usage

```bash
python main.py
```

On startup you'll be asked:
1. Whether to enable Discord Rich Presence
2. Which audio output device to use

### Main menu

| Option | Description |
|---|---|
| Play Menu | Access playback modes |
| Playlist Menu | Create, rename, delete playlists |
| Files Menu | Download, rename, delete, move songs |

### Play modes

| Mode | Description |
|---|---|
| Select Playlist | Play songs from one playlist in order |
| All songs | Queue every song across all playlists |
| Search a song | Find a song by name and play it |

### Playback commands

Type any of these while a song is playing and press Enter:

| Command | Action |
|---|---|
| `pause` | Pause playback |
| `resume` | Resume playback |
| `skip` | Skip to next song |
| `previous` | Go back to previous song |
| `restart` | Restart current song |
| `stop` | Stop and return to menu |
| `up` | Volume +10% |
| `down` | Volume -10% |
| `mute` | Set volume to 0% |

---

## Project structure

```
music_machine/
├── main.py        # Entry point, startup options, menu routing
├── player.py      # Playback engine, queue logic, RPC, metadata
├── playlists.py   # Playlist CRUD
├── file.py        # Song download, rename, delete, move
├── audio.py       # Audio device listing and selection
├── auxiliar.py    # Shared input validation and UI helpers
└── .gitignore
```

---

## Notes

- Songs downloaded via **yt-dlp** with the `--embed-metadata` flag will have proper ID3 tags (artist, title). Songs downloaded without it fall back to filename parsing — the expected format is `Artist - Title.mp3`.
- Audio device selection uses `pygame._sdl2.audio`, available in pygame-ce 2.x+.
- Discord RPC requires Discord to be running on your machine. If it's closed, the app continues normally without presence.
