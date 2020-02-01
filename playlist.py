import requests
import time
import os


def playlist_source_load(playlist_path):
    # загрузка источников загрузки плейлистов
    playlist_source = []
    try:
        with open(playlist_path, "r", encoding='utf-8') as file:
            for url in file:
                url = url.rstrip('\n')  # удаляем переход на новую строку
                url = url.strip()
                playlist_source.append(url)
    except FileNotFoundError:
        print("Не удалось загрузить источники плейлистов!")
    except Exception as e:
        print("Исключение при загрузке источников плейлистов: {0}".format(e))

    return playlist_source


def playlist_channel_load(playlist_path):
    # загрузка каналов из действующего плейлиста
    channels = []

    try:
        with open(playlist_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.rstrip('\n')

                if line.find("#EXTINF:") == -1:
                    continue

                param_list = line.split(',')
                if len(param_list) == 0:
                    continue

                channel = param_list[-1]
                channel = channel.strip()
                channel = channel.rstrip('\n')
                channel = channel.rstrip('\r')
                channels.append(channel)
    except FileNotFoundError:
        print("Не удалось открыть файл: \"{0}\"".format(playlist_path))
    except Exception as e:
        print("При открытии файла \"{0}\" возникла ошибка - {1}".format(playlist_path, e))

    return channels


def playlist_load_file(urls):
    # функция для скачивания файлов плейлистов
    playlist_file_list = []
    path = "playlists/dumps"

    if not os.path.isdir(path):
        os.mkdir(path)

    for url in urls:
        try:
            request = requests.get(url)
        except Exception:
            print("Не удалось скачать плейлист: {0}".format(url))
            continue

        if request.status_code == 200:
            param_list = url.split('/')
            name = param_list[-1].strip().rstrip('\n').rstrip('\r')

            pl_path = "{0}/{1}".format(path, name)

            print("Запись плейлиста: {0}".format(pl_path))
            with open(pl_path, "w", encoding='utf-8') as file:
                file.write(request.text)
                playlist_file_list.append(pl_path)

    return playlist_file_list


def playlist_channel_url_find(urls, channels):
    # Функция поиска ссылок по каналам
    channel_dict = dict()

    for channel in channels:
        for url in urls:
            print("Поиск канала \"{0}\" в плейлисте \"{1}\"".format(channel, url))
            with open(url, "r", encoding='utf-8') as file:
                lines = file.read().split('\n')
                rows = len(lines)
                row = 0

                channel_list = set()

                while row < rows:
                    line = lines[row]
                    if line.startswith("#EXTINF:"):
                        channel_cur = line.split(',')[-1].strip().rstrip('\n').rstrip('\r')
                        if channel.upper() == channel_cur.upper():
                            row += 1
                            while row < rows:
                                line = lines[row]
                                if line.startswith("http:") or line.startswith("https:"):
                                    line = line.strip()
                                    line = line.rstrip('\n')
                                    line = line.rstrip('\r')
                                    channel_list.add(line)
                                    break
                                row += 1
                    row += 1

                if channel_list:
                    channel_dict[channel] = channel_list

    return channel_dict


def playlist_write(name, channels, path):
    # Функция записи результатов поиска ссылок в файл + добавление времени отклика ссылки
    with open(path, "a", encoding='utf-8') as file:
        file.write("Канал \"{0}\":\n".format(name))

        count = 0  # счетчик рабочих ссылок
        for channel in channels:
            time_url = playlist_url_time(channel)
            if time_url > 0.0:
                file.write("{0} - {1}сек.\n".format(channel, time_url))
                count += 1

        if not count:
            file.write("Нет валидных ссылок\n")
        file.write('\n' * 2)


def playlist_url_time(url):
    # Функця замера времени отклика ссылки
    result = 0
    count = 5  # количество попыток пинга ссылки
    crash = 0
    i = 0
    while i < 5:
        start = time.time()
        try:
            request = requests.get(url)
            if request.status_code == 200:
                result += round(time.time() - start, 3)
        except Exception:
            print("Попытка №{0}: ресурс \"{1}\" недоступен".format(crash + 1, url))
            crash += 1
        finally:
            i += 1
    return round(result / count, 3)
