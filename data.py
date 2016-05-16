import numpy as np
import os
import sqlite3
from entry import Entry


class Data:
    def __init__(self):
        self.conn = sqlite3.connect('cells.db')
        self.idx = 0
        self.training_images, self.file_name = load_data()

    def create_db(self):
        self.conn = sqlite3.connect('cells.db')

    def create_table_if_not_exists(self):
        c = self.conn.cursor()
        # Create table
        c.execute('''CREATE TABLE IF NOT EXISTS cells
                     (file_name TEXT, index_in_array INTEGER, type TEXT, cutoff INTEGER, more_than_one INTEGER,
                     no_cell INTEGER, obstructions INTEGER, processed INTEGER, PRIMARY KEY (file_name, index_in_array))''')
        self.conn.commit()

    def close_db(self):
        self.conn.close()

    def init_table(self):
        c = self.conn.cursor()
        datas = []
        for i in range(self.training_images.shape[0]):
            datas.append((file_name, i, None, None, None, None, None, 0))
        c.executemany(''' INSERT INTO cells(file_name, index_in_array, type, cutoff, more_than_one, no_cell,
                        obstructions, processed) VALUES(?,?,?,?,?,?,?,?)''', datas)
        self.conn.commit()

    def check_if_data_seen_before(self):
        c = self.conn.cursor()
        c.execute('''SELECT EXISTS(SELECT 1 FROM cells WHERE file_name="monocytes_neutrophils.npz" LIMIT 1)''')
        data = c.fetchall()

        # c.execute('''SELECT * FROM cells''')
        # data = c.fetchall()
        # for d in data:
        #     print(d[0])
        if len(data) == 0:
            self.init_table()

    def get_unprocessed_entries(self):
        entries = []
        c = self.conn.cursor()
        c.execute('''SELECT * FROM cells where processed=?''', (0,))
        rows = c.fetchall()
        for row in rows:
            entries.append(Entry(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        return entries

    def get_entries_array(self, entry):
        image = self.training_images[entry.index_in_array, :, :, :]
        return image

    def available(self, entries):
        if self.idx >= len(entries):
            return False
        else:
            return True

    def get_next_entry(self, entries):
        next = entries[self.idx]
        self.idx += 1
        return next


def load_data():
    DATA_LOCATION = '../../AlanFine'
    FILE_NAME = 'monocytes_neutrophils.npz'
    train_val = np.load(os.path.join(DATA_LOCATION, FILE_NAME))
    # stored as batch, depth, height, width. Tensorflow wants -> batch, height, width, depth
    neutrophils = np.rollaxis(train_val['neutrophils'], 1, 4)
    monocytes = np.rollaxis(train_val['monocytes'], 1, 4)
    training_images = np.concatenate([neutrophils, monocytes])
    return training_images, FILE_NAME
