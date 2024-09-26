from easydict import EasyDict as edict
from iv2_utils.iv2 import pickle_read
import pandas as pd
import os

pred_mapping = {'a': 'augment', 'r': 'regular', 'g': 'gif87', 's': 'stock100'}
averaged = 100

def generate_settings(file_path):
    if '/' in file_path:
        file_path = file_path.split('/')[-1]

    if '.pkl' not in file_path:
        print(file_path)
    assert('.pkl' in file_path)
    file_path = file_path.split('.pkl')[0]

    indicator = file_path[0]
    window_size = int(file_path[1:])

    return edict({'subfolder': pred_mapping[indicator], 'windowsize': window_size})

class Accessor:
    def __init__(self):
        self.access = edict()
        self.varieties = edict()

    def add(self, category, window_size, data):
        if category not in self.access:
            self.access[category] = edict()

        if category not in self.varieties:
            self.varieties[category] = []

        self.access[category][str(window_size)] = data
        self.varieties[category].append(window_size)

    def get(self, category, window_size):
        try:
            return self.access[category][str(window_size)]
        except:
            print("Doesn't exist, try again.")
            return -1

    def __str__(self) -> str:
        return str(self.varieties)

    def __call__(self, category, window_size):
        return self.get(category, window_size)

def load_data():
    models = list(filter(lambda x: x not in ['config.py', '.DS_Store', '__init__.py', '__pycache__'], os.listdir('jar')))
    data = edict()
    for model in models:
        data[model] = Accessor()
        for file in os.listdir(os.path.join('jar', model)):
            if file == '.DS_Store': continue
            settings = generate_settings(file)
            read_data = pickle_read(os.path.join('jar', model, file))

            data[model].add(settings.subfolder, settings.windowsize, read_data)

    raw_data = pd.read_csv('anno_backflip.csv')
    data_k600 = []
    for index, row in raw_data.iterrows():
        data_k600.append((row['ID'], eval('[' + row['Frame(s)'] + ']')))

    data.k600 = data_k600
    data.gif87 = pickle_read('rustyjar/GIF87.pkl')

    data.stock100 = pickle_read('rustyjar/STOCK100-testing.pkl')
    # for video, phrase, frames in pickle_read('rustyjar/STOCK100.pkl'):
    #     data.stock100.append((int(video.split('/')[-1].split('.')[0]), frames))

    return data
