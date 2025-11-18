#!/usr/bin/env python3
"""
NCurses Music Player

A terminal-based music player with a cyberpunk-themed interface that:
- Scans for M3U8 playlist files in ~/Music/playlists/
- Displays playlists in an interactive ncurses interface
- Plays songs using mpv with full control (play, pause, next, previous)
- Shows real-time progress bar and song information
- Supports shuffle mode with randomization
- Features a cyberpunk color scheme matching the desktop theme

Requirements:
- Python 3.x with curses support
- mpv media player
- playerctl (optional, for progress bar)
- ffprobe (optional, for metadata extraction)
"""

import os
import sys
import curses
import subprocess
import random
import re
import signal
import json
import socket
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple

# ============================================================================
# Configuration
# ============================================================================

# Directory containing M3U8 playlist files
PLAYLISTS_DIR = Path.home() / "Music" / "playlists"

# Media player command (can be changed to mpg123, mplayer, etc.)
PLAYER_CMD = "mpv"


# ============================================================================
# MusicPlayer Class
# ============================================================================

class MusicPlayer:
    """
    Main music player class that handles playlist management, playback control,
    and the ncurses user interface.
    
    Attributes:
        stdscr: Curses window object
        playlists: List of available playlist names
        current_playlist: Name of currently playing playlist
        current_song_index: Index of current song in playlist
        songs: List of song file paths in current playlist
        shuffle: Whether shuffle mode is enabled
        player_process: Subprocess object for mpv
        current_song_info: Formatted string "Artist - Title"
        selected_index: Index of selected playlist in UI
        paused: Whether playback is currently paused
        ipc_socket: Path to mpv IPC socket for control
    """
    def __init__(self, stdscr):
        """
        Initialize the music player with ncurses interface.
        
        Args:
            stdscr: Curses standard screen window object
        """
        # UI state
        self.stdscr = stdscr
        self.selected_index = 0
        
        # Playlist management
        self.playlists = []
        self.current_playlist = None
        self.songs = []
        self.current_song_index = 0
        self.shuffle = False
        
        # Playback control
        self.player_process = None
        self.ipc_socket = None  # Path to mpv IPC socket for control
        self.paused = False
        self.current_song_info = ""
        
        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()  # Use terminal default colors
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.timeout(200)  # Refresh every 200ms to reduce flickering
        
        # Track screen size for efficient redraws
        self._last_height = None
        self._last_width = None
        
        # Initialize cyberpunk color scheme
        # Color pairs are used throughout the UI for consistent theming
        # Pair 1: Selected item - Magenta background with black text
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        # Pair 2: Playing indicator - Neon green
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        # Pair 3: Shuffle indicator - Neon yellow
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        # Pair 4: Normal text - Neon cyan
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        # Pair 5: Title - Bright cyan
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        # Pair 6: Paused indicator - Red
        curses.init_pair(6, curses.COLOR_RED, -1)
        # Pair 7: Progress bar filled - Cyan
        curses.init_pair(7, curses.COLOR_CYAN, -1)
        # Pair 8: Progress bar unfilled - Dim cyan for visibility
        curses.init_pair(8, curses.COLOR_CYAN, -1)
        
    def load_playlists(self):
        """
        Scan the playlists directory for M3U8 files.
        
        Returns:
            List of playlist names (filenames without .m3u8 extension),
            sorted alphabetically. Returns empty list if directory doesn't exist.
        """
        if not PLAYLISTS_DIR.exists():
            return []
        
        playlists = []
        # Find all .m3u8 files in the playlists directory
        for file in PLAYLISTS_DIR.glob("*.m3u8"):
            # Use stem to get filename without extension
            playlists.append(file.stem)
        
        return sorted(playlists)
    
    def parse_m3u8(self, playlist_name: str) -> List[str]:
        """
        Parse an M3U8 playlist file and extract song file paths.
        
        Handles both absolute and relative paths. For relative paths, tries:
        1. Relative to the playlists directory
        2. Relative to ~/Music/
        
        Args:
            playlist_name: Name of the playlist (without .m3u8 extension)
        
        Returns:
            List of absolute file paths to songs that exist. Empty list if
            playlist file doesn't exist or contains no valid songs.
        """
        playlist_path = PLAYLISTS_DIR / f"{playlist_name}.m3u8"
        if not playlist_path.exists():
            return []
        
        songs = []
        with open(playlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Skip comments (lines starting with #) and empty lines
                if line and not line.startswith('#'):
                    # Handle absolute paths (starting with /)
                    if os.path.isabs(line):
                        song_path = Path(line)
                    else:
                        # Try relative to playlist directory first
                        song_path = PLAYLISTS_DIR / line
                        if not song_path.exists():
                            # Fallback: try relative to Music directory
                            song_path = Path.home() / "Music" / line
                    
                    # Only add songs that actually exist
                    if song_path.exists():
                        songs.append(str(song_path))
        
        return songs
    
    def get_song_info(self, song_path: str) -> str:
        """
        Extract artist and title information from a song file.
        
        Tries multiple methods in order:
        1. Extract from metadata using ffprobe (if available)
        2. Parse from filename in "Artist - Title" format
        3. Parse from filename in "Artist_Title" format
        4. Use filename as-is
        
        Args:
            song_path: Path to the song file
        
        Returns:
            Formatted string "Artist - Title" or filename if extraction fails
        """
        try:
            # Method 1: Try to get metadata using ffprobe (if available)
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', song_path],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    format_info = data.get('format', {}).get('tags', {})
                    # Try different tag name variations
                    artist = format_info.get('artist') or format_info.get('ARTIST') or 'Unknown Artist'
                    title = format_info.get('title') or format_info.get('TITLE') or 'Unknown Title'
                    return f"{artist} - {title}"
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                # ffprobe not available or failed, continue to fallback
                pass
            
            # Method 2: Extract from filename
            filename = Path(song_path).stem  # Get filename without extension
            # Try to parse "Artist - Title" format
            if ' - ' in filename:
                parts = filename.split(' - ', 1)
                return f"{parts[0]} - {parts[1]}"
            # Try to parse "Artist_Title" format
            elif '_' in filename:
                parts = filename.split('_', 1)
                return f"{parts[0]} - {parts[1]}"
            # Use filename as-is
            else:
                return filename
        except Exception:
            # Final fallback: just return the filename
            return Path(song_path).stem
    
    def start_playlist(self, playlist_name: str):
        """
        Load and start playing a playlist.
        
        If shuffle is enabled, randomizes the song order. Otherwise plays
        songs in the order they appear in the playlist file.
        
        Args:
            playlist_name: Name of the playlist to play (without .m3u8 extension)
        """
        self.current_playlist = playlist_name
        self.songs = self.parse_m3u8(playlist_name)
        
        if not self.songs:
            return  # No songs found in playlist
        
        # Apply shuffle if enabled
        if self.shuffle:
            random.shuffle(self.songs)
        
        # Start from the beginning
        self.current_song_index = 0
        self.play_current_song()
    
    def play_current_song(self):
        """
        Start playing the song at the current index.
        
        Stops any currently playing song, extracts song information, and
        launches mpv with IPC enabled for control. The IPC socket allows
        us to pause/resume and query playback state.
        """
        if not self.songs or self.current_song_index >= len(self.songs):
            return  # No songs or invalid index
        
        # Stop any currently playing song
        self.stop_playback()
        
        # Get song information for display
        song_path = self.songs[self.current_song_index]
        self.current_song_info = self.get_song_info(song_path)
        self.paused = False  # Reset pause state when starting new song
        
        # Create unique IPC socket path using process ID
        # This allows multiple instances to run without conflicts
        self.ipc_socket = str(Path(tempfile.gettempdir()) / f"mpv_music_player_{os.getpid()}.sock")
        
        # Start mpv in background with IPC enabled
        try:
            self.player_process = subprocess.Popen(
                [
                    PLAYER_CMD,
                    '--no-terminal',      # Don't show terminal output
                    '--no-video',          # Audio-only mode
                    '--input-ipc-server=' + self.ipc_socket,  # Enable IPC for control
                    song_path
                ],
                stdout=subprocess.DEVNULL,  # Suppress output
                stderr=subprocess.DEVNULL    # Suppress errors
            )
            # Give mpv a moment to start the IPC server before we try to use it
            time.sleep(0.1)
        except FileNotFoundError:
            self.current_song_info = f"Error: {PLAYER_CMD} not found"
    
    def stop_playback(self):
        """
        Stop the currently playing song and clean up resources.
        
        Gracefully terminates the mpv process, and if that fails, kills it.
        Also removes the IPC socket file to prevent file system clutter.
        """
        if self.player_process:
            try:
                # Try graceful termination first
                self.player_process.terminate()
                self.player_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                # If process doesn't respond, force kill it
                self.player_process.kill()
            except ProcessLookupError:
                # Process already terminated
                pass
            self.player_process = None
        
        # Clean up IPC socket file
        if self.ipc_socket and Path(self.ipc_socket).exists():
            try:
                Path(self.ipc_socket).unlink()
            except OSError:
                # File may have been removed already, ignore
                pass
        self.ipc_socket = None
    
    def next_song(self):
        """
        Skip to the next song in the playlist.
        
        Wraps around to the beginning if at the end of the playlist.
        """
        if not self.songs:
            return
        
        # Use modulo to wrap around to beginning
        self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        self.play_current_song()
    
    def previous_song(self):
        """
        Go back to the previous song in the playlist.
        
        Wraps around to the end if at the beginning of the playlist.
        """
        if not self.songs:
            return
        
        # Use modulo to wrap around to end
        self.current_song_index = (self.current_song_index - 1) % len(self.songs)
        self.play_current_song()
    
    def toggle_shuffle(self):
        """
        Toggle shuffle mode on/off.
        
        If shuffle is enabled while a playlist is playing, reshuffles only
        the remaining songs (keeps already played songs in order).
        """
        self.shuffle = not self.shuffle
        
        # If currently playing, reshuffle remaining songs only
        if self.songs and self.current_song_index < len(self.songs):
            # Keep songs up to current index, shuffle the rest
            remaining = self.songs[self.current_song_index + 1:]
            if remaining:
                random.shuffle(remaining)
                self.songs = self.songs[:self.current_song_index + 1] + remaining
    
    def toggle_play_pause(self):
        """
        Toggle playback pause state.
        
        Uses mpv's IPC interface to send pause/play commands. Falls back to
        process signals (SIGSTOP/SIGCONT) if IPC is unavailable. Updates the
        internal pause state to match mpv's actual state.
        """
        # Check if player is running
        if not self.player_process or self.player_process.poll() is not None:
            return  # Not playing, can't pause
        
        # Fallback: Use process signals if IPC socket not available
        if not self.ipc_socket or not Path(self.ipc_socket).exists():
            try:
                if self.paused:
                    # Resume: send continue signal
                    self.player_process.send_signal(signal.SIGCONT)
                    self.paused = False
                else:
                    # Pause: send stop signal
                    self.player_process.send_signal(signal.SIGSTOP)
                    self.paused = True
            except (ProcessLookupError, OSError):
                # Process no longer exists
                self.player_process = None
                self.paused = False
            return
        
        # Primary method: Use mpv IPC interface
        try:
            # Connect to mpv IPC socket (Unix domain socket)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.ipc_socket)
            
            # Send cycle pause command (toggles pause state in mpv)
            command = {"command": ["cycle", "pause"]}
            sock.send((json.dumps(command) + "\n").encode('utf-8'))
            
            # Read response and query actual pause state
            response = sock.recv(1024).decode('utf-8')
            try:
                result = json.loads(response)
                # Query mpv's actual pause state to sync our UI
                status_cmd = {"command": ["get_property", "pause"]}
                sock.send((json.dumps(status_cmd) + "\n").encode('utf-8'))
                status_resp = sock.recv(1024).decode('utf-8')
                status_result = json.loads(status_resp)
                
                # Update our state to match mpv's state
                if 'data' in status_result:
                    self.paused = status_result['data']
                else:
                    # If we can't get state, just toggle
                    self.paused = not self.paused
            except (json.JSONDecodeError, KeyError):
                # If parsing fails, just toggle our state
                self.paused = not self.paused
            
            sock.close()
        except (ConnectionRefusedError, FileNotFoundError, OSError, socket.error):
            # IPC failed, fallback to signals
            try:
                if self.paused:
                    self.player_process.send_signal(signal.SIGCONT)
                    self.paused = False
                else:
                    self.player_process.send_signal(signal.SIGSTOP)
                    self.paused = True
            except (ProcessLookupError, OSError):
                self.player_process = None
                self.paused = False
    
    def get_progress(self) -> Tuple[float, float, float]:
        """
        Get current song playback progress information.
        
        Uses mpv IPC to query the current song's position and duration directly.
        This ensures we get the progress of the current song, not the playlist.
        
        Returns:
            Tuple of (position, duration, percentage) in seconds.
            Returns (0, 0, 0) if player not running or IPC unavailable.
        """
        if not self.player_process or self.player_process.poll() is not None:
            return (0, 0, 0)
        
        if not self.ipc_socket or not Path(self.ipc_socket).exists():
            return (0, 0, 0)
        
        try:
            # Connect to mpv IPC socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Short timeout to avoid blocking
            sock.connect(self.ipc_socket)
            
            # Get current position (time-pos in seconds)
            pos_cmd = {"command": ["get_property", "time-pos"]}
            sock.send((json.dumps(pos_cmd) + "\n").encode('utf-8'))
            pos_response = sock.recv(1024).decode('utf-8')
            pos_result = json.loads(pos_response)
            
            # Get duration (duration in seconds)
            dur_cmd = {"command": ["get_property", "duration"]}
            sock.send((json.dumps(dur_cmd) + "\n").encode('utf-8'))
            dur_response = sock.recv(1024).decode('utf-8')
            dur_result = json.loads(dur_response)
            
            sock.close()
            
            # Extract position and duration from responses
            position = 0.0
            duration = 0.0
            
            if 'data' in pos_result and pos_result['data'] is not None:
                position = float(pos_result['data'])
            
            if 'data' in dur_result and dur_result['data'] is not None:
                duration = float(dur_result['data'])
            
            if duration > 0:
                # Calculate percentage, clamped between 0 and 100
                percentage = min(100, max(0, (position / duration) * 100))
                return (position, duration, percentage)
            
        except (ConnectionRefusedError, FileNotFoundError, OSError, socket.error, 
                json.JSONDecodeError, KeyError, ValueError, TimeoutError):
            # IPC failed or invalid data, return zeros
            pass
        
        return (0, 0, 0)
    
    def check_player_status(self):
        """
        Check if the player process is still running.
        
        If the process has finished (song ended), automatically advances
        to the next song in the playlist.
        """
        if self.player_process:
            # poll() returns None if process is still running
            # Returns exit code if process has finished
            if self.player_process.poll() is not None:
                # Song finished, play next song automatically
                self.next_song()
    
    def draw(self):
        """
        Render the complete user interface.
        
        Draws all UI elements including title, shuffle indicator, playlist list,
        current song info, progress bar, and help text. Uses cyberpunk color
        scheme throughout.
        """
        height, width = self.stdscr.getmaxyx()
        
        # Only clear screen if size changed, otherwise just refresh
        if not hasattr(self, '_last_height') or not hasattr(self, '_last_width') or \
           self._last_height != height or self._last_width != width:
            self.stdscr.clear()
            self._last_height = height
            self._last_width = width
        # Don't clear/erase every frame - just redraw over existing content
        
        # Title - Cyberpunk style with neon cyan
        title = "╔═══ MUSIC PLAYER ═══╗"
        title_x = (width - len(title)) // 2
        self.stdscr.addstr(0, title_x, title, curses.color_pair(5) | curses.A_BOLD)
        
        # Shuffle indicator - Neon yellow
        shuffle_text = "▶ [S]huffle: " + ("ON" if self.shuffle else "OFF")
        # Clear the line first to avoid leftover characters
        try:
            self.stdscr.addstr(1, 2, " " * (width - 4))  # Clear the line
        except curses.error:
            pass
        try:
            self.stdscr.addstr(1, 2, shuffle_text, curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass
        
        # Playlists list
        # Start after title and shuffle indicator
        list_start_y = 3
        # Adjust list end to leave space for song info, progress bar, and help
        list_end_y = height - 7  # Leave space: song info (height-5), progress (height-4), help (height-1)
        
        for i, playlist in enumerate(self.playlists):
            y = list_start_y + i
            if y >= list_end_y:
                break
            
            # Highlight selected item with magenta background
            if i == self.selected_index:
                attr = curses.color_pair(1) | curses.A_BOLD
            else:
                attr = curses.color_pair(4)
            
            # Show playing indicator with green
            if playlist == self.current_playlist:
                prefix = "▶ "
                prefix_attr = curses.color_pair(2) | curses.A_BOLD
            else:
                prefix = "  "
                prefix_attr = curses.color_pair(4)
            
            text = f"{prefix}{playlist}"
            
            # Truncate if too long
            if len(text) > width - 4:
                text = text[:width - 7] + "..."
            
            # Draw prefix and playlist name separately for color coding
            self.stdscr.addstr(y, 2, prefix, prefix_attr)
            playlist_name = playlist
            if len(playlist_name) > width - 6:
                playlist_name = playlist_name[:width - 9] + "..."
            self.stdscr.addstr(y, 2 + len(prefix), playlist_name, attr)
        
        # Current song info
        if self.current_song_info:
            info_y = height - 5
            if self.paused:
                status = "⏸ PAUSED"
                status_color = curses.color_pair(6) | curses.A_BOLD  # Red for paused
            else:
                status = "▶ PLAYING"
                status_color = curses.color_pair(2) | curses.A_BOLD  # Green for playing
            
            info_text = f"{status} ─ {self.current_song_info}"
            # Truncate if too long
            if len(info_text) > width - 4:
                info_text = info_text[:width - 7] + "..."
            
            # Draw status and song info separately for color coding
            self.stdscr.addstr(info_y, 2, status, status_color)
            song_info_x = 2 + len(status) + 3  # 3 for " ─ "
            song_info_text = self.current_song_info
            if len(song_info_text) > width - song_info_x - 2:
                song_info_text = song_info_text[:width - song_info_x - 5] + "..."
            self.stdscr.addstr(info_y, song_info_x, song_info_text, curses.color_pair(4))
        
        # Progress bar
        if self.current_song_info:
            progress_y = height - 4
            position, duration, percentage = self.get_progress()
            
            # Clear the progress bar line first
            try:
                self.stdscr.addstr(progress_y, 2, " " * (width - 4))
            except curses.error:
                pass
            
            if duration > 0:
                # Format time as MM:SS
                def format_time(seconds):
                    mins = int(seconds // 60)
                    secs = int(seconds % 60)
                    return f"{mins:02d}:{secs:02d}"
                
                time_text = f"{format_time(position)} / {format_time(duration)}"
                time_width = len(time_text)
                
                # Calculate bar width (leave space for time on the right)
                bar_width = width - time_width - 8  # 8 for margins and spacing
                if bar_width < 10:
                    bar_width = width - 4  # Fallback if too narrow
                    time_text = ""  # Hide time if no space
                    time_width = 0
                
                # Calculate filled portion based on percentage
                filled = int((percentage / 100.0) * bar_width)
                filled = max(0, min(bar_width, filled))
                
                # Draw progress bar
                bar_start_x = 2
                
                # Draw filled portion
                if filled > 0:
                    filled_chars = "█" * filled
                    try:
                        self.stdscr.addstr(progress_y, bar_start_x, filled_chars, curses.color_pair(7) | curses.A_BOLD)
                    except curses.error:
                        pass
                
                # Draw unfilled portion
                if filled < bar_width:
                    unfilled_chars = "░" * (bar_width - filled)
                    try:
                        self.stdscr.addstr(progress_y, bar_start_x + filled, unfilled_chars, curses.color_pair(8))
                    except curses.error:
                        pass
                
                # Draw time on the right
                if time_text and bar_start_x + bar_width + 3 + time_width <= width - 2:
                    try:
                        self.stdscr.addstr(progress_y, bar_start_x + bar_width + 3, time_text, curses.color_pair(4) | curses.A_BOLD)
                    except curses.error:
                        pass
        
        # Help text - Cyberpunk style border
        help_y = height - 1
        help_text = "↑↓ Navigate | Enter Play | Space Play/Pause | S Shuffle | N Next | P Prev | Q Quit"
        if len(help_text) > width - 2:
            help_text = help_text[:width - 3]
        # Draw with subtle styling
        self.stdscr.addstr(help_y, 1, help_text, curses.color_pair(4))
        
        self.stdscr.refresh()
    
    def run(self):
        """
        Main event loop that handles user input and updates the display.
        
        Continuously checks player status, redraws the UI, and processes
        keyboard input. Exits when user presses 'q' or ESC.
        """
        # Load playlists at startup
        self.playlists = self.load_playlists()
        
        # Show message if no playlists found
        if not self.playlists:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"No M3U8 playlists found in {PLAYLISTS_DIR}")
            self.stdscr.addstr(2, 0, "Press any key to exit...")
            self.stdscr.refresh()
            self.stdscr.nodelay(0)  # Blocking input
            self.stdscr.getch()
            return
        
        # Main event loop
        while True:
            # Check if current song finished and advance if needed
            self.check_player_status()
            
            # Redraw the entire UI
            self.draw()
            
            # Get keyboard input (non-blocking, returns -1 if no input)
            key = self.stdscr.getch()
            
            if key == -1:
                continue  # No input, continue loop
            
            # Handle keyboard shortcuts
            if key == ord('q') or key == ord('Q') or key == 27:  # Q or ESC - quit
                break
            elif key == curses.KEY_UP or key == ord('k'):  # Navigate up
                self.selected_index = (self.selected_index - 1) % len(self.playlists)
            elif key == curses.KEY_DOWN or key == ord('j'):  # Navigate down
                self.selected_index = (self.selected_index + 1) % len(self.playlists)
            elif key == ord('\n') or key == ord('\r'):  # Enter - play selected playlist
                selected_playlist = self.playlists[self.selected_index]
                self.start_playlist(selected_playlist)
            elif key == ord('s') or key == ord('S'):  # Toggle shuffle
                self.toggle_shuffle()
            elif key == ord(' '):  # Space - play/pause
                self.toggle_play_pause()
            elif key == ord('n') or key == ord('N'):  # Next song
                self.next_song()
            elif key == ord('p') or key == ord('P'):  # Previous song
                self.previous_song()
        
        # Clean up on exit
        self.stop_playback()


# ============================================================================
# Dependency Checking Functions
# ============================================================================

def check_dependencies():
    """
    Check if all required dependencies are available.
    
    Checks for:
    - mpv media player installation
    - Playlists directory existence
    - Presence of .m3u8 playlist files
    
    Returns:
        List of issue dictionaries, each containing:
        - 'type': Issue category (mpv, directory, playlists)
        - 'message': Description of the issue
        - 'fix': Instructions on how to fix the issue
    """
    issues = []
    
    # Check if mpv is installed and accessible
    try:
        subprocess.run(
            [PLAYER_CMD, '--version'], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            timeout=1
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        issues.append({
            'type': 'mpv',
            'message': f'{PLAYER_CMD} is not installed or not in PATH',
            'fix': f'Install {PLAYER_CMD}:\n  Arch: sudo pacman -S mpv\n  Debian/Ubuntu: sudo apt install mpv\n  Fedora: sudo dnf install mpv'
        })
    
    # Check if playlists directory exists
    if not PLAYLISTS_DIR.exists():
        issues.append({
            'type': 'directory',
            'message': f'Playlists directory does not exist: {PLAYLISTS_DIR}',
            'fix': f'Create the directory:\n  mkdir -p {PLAYLISTS_DIR}'
        })
    else:
        # Check if there are any .m3u8 playlist files
        m3u8_files = list(PLAYLISTS_DIR.glob("*.m3u8"))
        if not m3u8_files:
            issues.append({
                'type': 'playlists',
                'message': f'No .m3u8 playlist files found in {PLAYLISTS_DIR}',
                'fix': f'Add .m3u8 playlist files to:\n  {PLAYLISTS_DIR}\n\nExample playlist format:\n  #EXTM3U\n  /path/to/song1.mp3\n  /path/to/song2.mp3'
            })
    
    return issues


def show_dependency_info(stdscr, issues):
    """
    Display a formatted info box showing missing dependencies and how to fix them.
    
    Creates a cyberpunk-styled dialog box that lists all dependency issues
    with clear instructions on how to resolve them. The box is centered on
    screen and handles text wrapping for long lines.
    
    Args:
        stdscr: Curses standard screen window
        issues: List of issue dictionaries from check_dependencies()
    """
    # Initialize curses settings
    curses.curs_set(0)  # Hide cursor
    curses.use_default_colors()
    
    # Initialize color pairs (same as MusicPlayer for consistency)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)
    curses.init_pair(6, curses.COLOR_RED, -1)
    curses.init_pair(7, curses.COLOR_CYAN, -1)
    curses.init_pair(8, curses.COLOR_CYAN, -1)
    
    height, width = stdscr.getmaxyx()
    
    # Calculate box dimensions (ensure minimum size and fit on screen)
    max_width = min(80, max(40, width - 4))
    # Calculate needed height based on content
    needed_height = 5 + sum(3 + len(issue['fix'].split('\n')) for issue in issues)
    box_height = min(max(needed_height, 10), height - 4, 30)
    
    # Calculate box position (centered, but ensure it fits on screen)
    box_y = max(1, (height - box_height) // 2)
    box_x = max(1, (width - max_width) // 2)
    
    stdscr.clear()
    
    # Draw box border with cyberpunk style (box-drawing characters)
    box_title = "╔═══ DEPENDENCY CHECK ═══╗"
    title_x = box_x + (max_width - len(box_title)) // 2
    
    # Draw top border and title
    stdscr.addstr(box_y, box_x, "╔" + "═" * (max_width - 2) + "╗", curses.color_pair(5) | curses.A_BOLD)
    stdscr.addstr(box_y + 1, title_x, box_title, curses.color_pair(6) | curses.A_BOLD)
    stdscr.addstr(box_y + 2, box_x, "╠" + "═" * (max_width - 2) + "╣", curses.color_pair(5) | curses.A_BOLD)
    
    # Draw content area
    y_offset = box_y + 3
    content_width = max_width - 4
    
    stdscr.addstr(y_offset, box_x + 2, "Missing Dependencies:", curses.color_pair(6) | curses.A_BOLD)
    y_offset += 2
    
    # Display each issue with its fix instructions
    for i, issue in enumerate(issues):
        # Issue type and message
        issue_text = f"[{issue['type'].upper()}] {issue['message']}"
        if len(issue_text) > content_width:
            issue_text = issue_text[:content_width - 3] + "..."
        stdscr.addstr(y_offset, box_x + 2, issue_text, curses.color_pair(6))
        y_offset += 1
        
        # Fix instructions with word wrapping
        fix_lines = issue['fix'].split('\n')
        for line in fix_lines:
            if y_offset >= box_y + box_height - 3:
                break  # Don't overflow the box
            if len(line) > content_width:
                # Wrap long lines by splitting on words
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= content_width:
                        current_line += (" " if current_line else "") + word
                    else:
                        # Output current line and start new one
                        if current_line:
                            stdscr.addstr(y_offset, box_x + 4, current_line, curses.color_pair(4))
                            y_offset += 1
                        current_line = word
                if current_line:
                    stdscr.addstr(y_offset, box_x + 4, current_line, curses.color_pair(4))
                    y_offset += 1
            else:
                # Line fits, output as-is
                stdscr.addstr(y_offset, box_x + 4, line, curses.color_pair(4))
                y_offset += 1
        y_offset += 1  # Space between issues
    
    # Draw bottom border
    stdscr.addstr(box_y + box_height - 2, box_x, "╚" + "═" * (max_width - 2) + "╝", curses.color_pair(5) | curses.A_BOLD)
    
    # Instructions for user
    help_text = "Press any key to exit..."
    help_x = box_x + (max_width - len(help_text)) // 2
    stdscr.addstr(box_y + box_height - 1, help_x, help_text, curses.color_pair(4))
    
    stdscr.refresh()
    
    # Wait for key press (blocking)
    stdscr.nodelay(0)
    stdscr.getch()


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """
    Main entry point for the music player application.
    
    First checks all dependencies. If any are missing, displays an info box
    with instructions and exits. Otherwise, starts the music player interface.
    """
    # Check dependencies before starting
    issues = check_dependencies()
    
    if issues:
        # Show dependency info box if issues found
        try:
            curses.wrapper(lambda stdscr: show_dependency_info(stdscr, issues))
        except KeyboardInterrupt:
            pass
        sys.exit(1)
    
    # All dependencies met, start the music player
    try:
        curses.wrapper(lambda stdscr: MusicPlayer(stdscr).run())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass


if __name__ == "__main__":
    main()

