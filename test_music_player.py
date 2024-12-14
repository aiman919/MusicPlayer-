import unittest
from unittest.mock import patch, MagicMock
import os
from music_player import MusicFileExplorer


class TestMusicFileExplorer(unittest.TestCase):

    @patch("os.path.isdir", return_value=True)
    @patch("os.walk")
    def test_load_initial_music(self, mock_os_walk, mock_isdir):
        mock_os_walk.return_value = [
            ('/music', [], ['song1.mp3', 'song2.mp3', 'song3.mp3'])
        ]
        mock_root = MagicMock()
        app = MusicFileExplorer(mock_root, '/music')
        self.assertEqual(len(app.playlist), 3)
        self.assertTrue(any("song1.mp3" in song for song in app.playlist))
        self.assertTrue(any("song2.mp3" in song for song in app.playlist))
        self.assertTrue(any("song3.mp3" in song for song in app.playlist))

    @patch("os.path.isdir", return_value=True)
    @patch("os.walk")
    def test_load_initial_music_empty_folder(self, mock_os_walk, mock_isdir):
        mock_os_walk.return_value = [
            ('/music', [], [])
        ]
        mock_root = MagicMock()
        app = MusicFileExplorer(mock_root, '/music')
        self.assertEqual(len(app.playlist), 0)

    @patch("os.path.isdir", return_value=True)
    @patch("pygame.mixer.music.load")
    @patch("pygame.mixer.music.play")
    def test_play_song(self, mock_play, mock_load, mock_isdir):
        playlist_files = [
            os.path.normpath('/music/song1.mp3'),
            os.path.normpath('/music/song2.mp3'),
            os.path.normpath('/music/song3.mp3')
        ]
        mock_root = MagicMock()
        app = MusicFileExplorer(mock_root, '/music')
        app.playlist = playlist_files
        app.listbox.curselection = MagicMock(return_value=[1])
        app.play_song()
        mock_load.assert_called_once_with(playlist_files[1])
        mock_play.assert_called_once()

    @patch("os.path.isdir", return_value=True)
    @patch("pygame.mixer.music.load")
    @patch("pygame.mixer.music.play")
    def test_play_song_no_selection(self, mock_play, mock_load, mock_isdir):
        playlist_files = [
            os.path.normpath('/music/song1.mp3'),
            os.path.normpath('/music/song2.mp3'),
            os.path.normpath('/music/song3.mp3')
        ]
        mock_root = MagicMock()
        app = MusicFileExplorer(mock_root, '/music')
        app.playlist = playlist_files
        app.listbox.curselection = MagicMock(return_value=[])
        app.play_song()
        mock_load.assert_called_once_with(playlist_files[0])
        mock_play.assert_called_once()

    @patch("pygame.mixer.music.stop")
    @patch("music_player.MusicFileExplorer.load_initial_music")
    def test_stop_song(self, mock_load_initial_music, mock_stop):
        mock_root = MagicMock()
        app = MusicFileExplorer(mock_root, '/music')
        app.is_paused = True
        app.stop_song()
        mock_stop.assert_called_once()
        self.assertFalse(app.is_paused)


if __name__ == "__main__":
    unittest.main()
