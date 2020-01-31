import playlist as pl
import datetime
import time

FILE_PLAYLIST_SOURCE = "playlists/playlists.txt"
FILE_PLAYLIST_CHANNEL = "playlists/playlist.m3u8"
FILE_PLAYLIST_RESULT = "playlists/urls"

playlist_source = pl.playlist_source_load(FILE_PLAYLIST_SOURCE)
channels = pl.playlist_channel_load(FILE_PLAYLIST_CHANNEL)
channel_url_dict = pl.playlist_channel_url_find(playlist_source, channels)

today = datetime.datetime.today()
dt = today.strftime("_%d_%m_%Y__%H_%M_%S")
file = FILE_PLAYLIST_RESULT + dt + ".txt"

print("Начало сохранения файла \"{0}\"".format(file))

for channel in channel_url_dict:
    pl.playlist_write(channel, channel_url_dict[channel], file)

print("Сохранение файла \"{0}\" окончено.".format(file))
