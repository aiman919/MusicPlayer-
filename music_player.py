import os
import tkinter as tk
from tkinter import filedialog, Listbox, messagebox
from tkinter import ttk
import pygame
from mutagen.easyid3 import EasyID3


pygame.mixer.init()

class MusicFileExplorer:
    def __init__(self, root, initial_folder):
        """
        Initializes the Music Player application.

        :param root: The root window of the tkinter GUI.
        :type root: tkinter.Tk
        :param initial_folder: The folder where the music files are initially loaded from.
        :type initial_folder: str
        """
        self.root = root
        self.root.title("Music Player")
        self.playlist = []
        self.current_song_index = -1
        self.initial_folder = initial_folder
        self.volume = 0.5
        self.is_paused = False


        self.root.geometry("900x700")
        self.root.configure(bg="#1E1E2F")


        self.setup_ui()


        self.load_initial_music()

    def setup_ui(self):
        """
        Sets up the user interface for the music player.

        Creates labels, buttons, listboxes, and other widgets for the player controls.
        """

        title_label = tk.Label(self.root, text="🎵 Music Player 🎵", bg="#1E1E2F", fg="white",
                               font=("Helvetica", 28, "bold"))
        title_label.pack(pady=20)


        search_frame = tk.Frame(self.root, bg="#1E1E2F")
        search_frame.pack(pady=10)

        search_label = tk.Label(search_frame, text="Search:", bg="#1E1E2F", fg="white", font=("Helvetica", 16))
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame, font=("Helvetica", 14), width=40)
        self.search_entry.pack(side=tk.LEFT, padx=10)

        search_button = ttk.Button(search_frame, text="Search", command=self.search_song)
        search_button.pack(side=tk.LEFT, padx=5)


        playlist_frame = tk.Frame(self.root, bg="#1E1E2F")
        playlist_frame.pack(pady=20)

        self.listbox = Listbox(playlist_frame, selectmode=tk.SINGLE, width=60, height=20, font=("Helvetica", 14),
                               bg="#2E2E3F", fg="white", selectbackground="#007ACC", relief="flat", bd=0)
        self.listbox.pack(side="left", padx=10)

        scrollbar = ttk.Scrollbar(playlist_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")


        button_frame = tk.Frame(self.root, bg="#1E1E2F")
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="⏪ -10s", command=self.rewind_10s, width=15).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="▶ Play", command=self.play_song, width=15).grid(row=0, column=1, padx=10)

        self.pause_button = ttk.Button(button_frame, text="⏸ Pause", command=self.toggle_pause, width=15)
        self.pause_button.grid(row=0, column=2, padx=10)

        ttk.Button(button_frame, text="⏹ Stop", command=self.stop_song, width=15).grid(row=0, column=3, padx=10)
        ttk.Button(button_frame, text="⏩ +10s", command=self.forward_10s, width=15).grid(row=0, column=4, padx=10)
        ttk.Button(button_frame, text="📂 Add Folder", command=self.add_folder, width=15).grid(row=0, column=5, padx=10)


        volume_frame = tk.Frame(self.root, bg="#1E1E2F")
        volume_frame.pack(pady=10)

        volume_label = tk.Label(volume_frame, text="Volume:", bg="#1E1E2F", fg="white", font=("Helvetica", 14))
        volume_label.pack(side=tk.LEFT, padx=5)

        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient="horizontal", command=self.change_volume)
        self.volume_slider.set(self.volume)  # Set default volume
        self.volume_slider.pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="⏭ Next", command=self.next_song, width=15).grid(row=0, column=6, padx=10)

    def load_initial_music(self):
        """
        Loads music files from the specified initial folder and adds them to the playlist.

        :raises: messagebox.showerror if the initial folder is not found.
        """
        if not os.path.isdir(self.initial_folder):
            messagebox.showerror("Error", f"Initial folder not found: {self.initial_folder}")
            return

        for root, _, files in os.walk(self.initial_folder):
            for file in files:
                if file.endswith(".mp3"):
                    self.playlist.append(os.path.join(root, file))
        self.update_playlist()

    def add_folder(self):
        """
        Opens a folder dialog to select additional music folders, then adds the music files to the playlist.

        This function allows the user to select a folder containing music files. The selected folder is then scanned
        for `.mp3` files, which are added to the playlist.

        :raises:
            - messagebox.showerror: If no folder is selected or if the selected folder contains no `.mp3` files.
        """
        folder = filedialog.askdirectory()
        if not folder:
            messagebox.showerror("Error", "No folder selected!")
            return
        added_songs = False
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".mp3"):
                    self.playlist.append(os.path.join(root, file))
                    added_songs = True
        if added_songs:
            self.update_playlist()
        else:
            messagebox.showerror("Error", "No .mp3 files found in the selected folder.")

    def update_playlist(self):
        """
        Updates the playlist shown in the listbox widget with the current songs.
        """
        self.listbox.delete(0, tk.END)  # Clear existing list
        for song in self.playlist:
            title = os.path.splitext(os.path.basename(song))[0]
            self.listbox.insert(tk.END, title)

    def play_song(self):
        """
        Plays the selected song from the playlist or search results.

        This function loads the selected song from the playlist and starts playing it using pygame's mixer.
        It also fetches the song's duration and displays information about the song (title, artist, album, duration).

        If no song is selected, the first song in the playlist will be played. If a song from the search results is selected, it will be played.

        :raises:
            - messagebox.showerror: If no song is selected or the playlist is empty.
        """
        selected_index = self.listbox.curselection()
        if selected_index:
            if hasattr(self, 'filtered_playlist') and self.filtered_playlist:

                self.current_song_index = self.playlist.index(self.filtered_playlist[selected_index[0]])
            else:

                self.current_song_index = selected_index[0]
        elif self.current_song_index == -1:
            if self.listbox.size() == 0:
                messagebox.showerror("Error", "No songs in the playlist!")
                return
            self.current_song_index = 0

        song = self.playlist[self.current_song_index]
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        self.is_paused = False


        self.current_position = 0


        try:
            import mutagen
            audio_file = mutagen.File(song)
            self.song_duration = int(audio_file.info.length)  
        except Exception:
            self.song_duration = 0

        self.show_song_info(song)

    def next_song(self):
        """
        Plays the next song in the playlist.

        :raises: messagebox.showerror if the playlist is empty.
        """
        if not self.playlist:
            messagebox.showerror("Error", "No songs in the playlist!")
            return


        self.current_song_index += 1
        if self.current_song_index >= len(self.playlist):
            self.current_song_index = 0  # Loop back to the first song


        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.current_song_index)
        self.listbox.activate(self.current_song_index)


        self.play_song()

    def stop_song(self):
        """
        Stops the current song completely and resets the playback position.
        """
        pygame.mixer.music.stop()
        self.is_paused = False

    def toggle_pause(self):
        """
        Toggles between pausing and resuming the current song.

        If the song is currently playing, this function will pause it. If the song is paused, it will resume playing from where it left off.

        :raises:
            - messagebox.showerror: If no song is currently playing or if the song has been stopped.
        """
        if not pygame.mixer.music.get_busy() and not self.is_paused:
            messagebox.showerror("Error", "No song is currently playing or it has been stopped!")
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.pause_button.config(text="⏸ Pause")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_button.config(text="▶ Resume")

    def search_song(self):
        """
        Searches for a song in the playlist based on the user's input.

        :raises: messagebox.showerror if no songs match the search query.
        """
        search_query = self.search_entry.get().lower()
        if not search_query:
            return self.update_playlist()
        filtered_playlist = [
            song for song in self.playlist
            if search_query in os.path.basename(song).lower()
        ]
        self.filtered_playlist = filtered_playlist
        self.listbox.delete(0, tk.END)
        for song in filtered_playlist:
            title = os.path.splitext(os.path.basename(song))[0]
            self.listbox.insert(tk.END, title)

    def forward_10s(self):
        """
        Forward the current song by 10 seconds.

        :raises: messagebox.showerror if no song is currently playing.
        """
        if pygame.mixer.music.get_busy():
            if not hasattr(self, 'current_position'):
                self.current_position = 0

            self.current_position += 10
            self.current_position = min(self.current_position,
                                        self.song_duration)
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=self.current_position)
        else:
            messagebox.showerror("Error", "No song is currently playing!")

    def rewind_10s(self):
        """
        Rewind the current song by 10 seconds.

        :raises: messagebox.showerror if no song is currently playing.
        """
        if pygame.mixer.music.get_busy():
            if not hasattr(self, 'current_position'):
                self.current_position = 0

            self.current_position = max(0, self.current_position - 10)
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=self.current_position)
        else:
            messagebox.showerror("Error", "No song is currently playing!")

    def show_song_info(self, song):
        """
        Displays the current song's information (title, artist, album, duration) on the UI.

        This function retrieves metadata (title, artist, album) of the current song using the `mutagen` library and
        displays it on the user interface. The song's duration is also displayed in minutes and seconds.

        :param song: The file path of the song being played.
        :type song: str
        """
        try:
            audio = EasyID3(song)
            title = audio.get('title', ['Unknown'])[0]
            artist = audio.get('artist', ['Unknown'])[0]
            album = audio.get('album', ['Unknown'])[0]
        except Exception:
            title = os.path.basename(song)
            artist = "Unknown Artist"
            album = "Unknown Album"

        try:
            import mutagen
            audio_file = mutagen.File(song)
            duration = int(audio_file.info.length)
            duration_str = f"{duration // 60}:{duration % 60:02d}"
        except Exception:
            duration_str = "Unknown"

        if not hasattr(self, 'song_info_label'):
            self.song_info_label = tk.Label(self.root, text="", bg="#1E1E2F", fg="white", font=("Helvetica", 14))
            self.song_info_label.pack(pady=10)

        self.song_info_label.config(
            text=f"Now Playing: {title} | Artist: {artist} | Album: {album} | Duration: {duration_str}"
        )

    def change_volume(self, volume):
        """
        Adjusts the volume of the music.

        This function changes the music player's volume based on the input from the volume slider.

        :param volume: The volume level to set, between 0 (mute) and 1 (maximum volume).
        :type volume: float
        """
        self.volume = float(volume)
        pygame.mixer.music.set_volume(self.volume)


if __name__ == "__main__":
    initial_folder = "C:/song"

    root = tk.Tk()
    app = MusicFileExplorer(root, initial_folder)
    root.mainloop()
