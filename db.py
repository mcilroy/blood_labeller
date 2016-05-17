import numpy as np
import os
import sqlite3
from entry import Entry


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('cells.db')
        self.idx = 0
        self.training_images, self.file_name = load_data()
        self.entries = []
        #self.restart()
        self.create_table_if_not_exists()
        self.check_if_data_seen_before()

    def restart(self):
        c = self.conn.cursor()
        c.execute('''DROP TABLE IF EXISTS cells''')
        self.conn.commit()

    def create_table_if_not_exists(self):
        c = self.conn.cursor()
        # Create table
        c.execute('''CREATE TABLE IF NOT EXISTS cells
                     (file_name TEXT, index_in_array INTEGER, cell_type TEXT, cut_off INTEGER, more_than_one INTEGER,
                      obstructions INTEGER, processed INTEGER, PRIMARY KEY (file_name, index_in_array))''')
        self.conn.commit()

    def check_if_data_seen_before(self):
        c = self.conn.cursor()
        c.execute('''SELECT EXISTS(SELECT 1 FROM cells WHERE file_name=? LIMIT 1)''', (self.file_name,))
        data = c.fetchone()
        if data[0] == 0:
            self.init_table()

    def init_table(self):
        c = self.conn.cursor()
        data_entries = []
        for i in range(self.training_images.shape[0]):
            data_entries.append((self.file_name, i, None, None, None, None, 0))
        c.executemany(''' INSERT INTO cells(file_name, index_in_array, cell_type, cut_off, more_than_one, obstructions,
                        processed) VALUES(?,?,?,?,?,?,?)''', data_entries)
        self.conn.commit()

    def get_unprocessed_entries(self):
        self.entries = []
        self.idx = 0
        c = self.conn.cursor()
        c.execute('''SELECT * FROM cells where processed=?''', (0,))
        rows = c.fetchall()
        for row in rows:
            self.entries.append(Entry(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        if len(self.entries) > 0:
            return True
        else:
            return False

    def get_entries_array(self, entry):
        image = self.training_images[entry.index_in_array, :, :, :]
        return image

    def more_entries_available(self, reverse=False):
        if not reverse:
            if self.idx >= len(self.entries):
                return False
            else:
                return True
        else:
            if self.idx-2 < 0:
                return False
            else:
                return True

    def get_next_entry(self):
        next_entry = self.entries[self.idx]
        self.idx += 1
        return next_entry

    def get_previous_entry(self):
        previous = self.entries[self.idx-2]
        self.idx -= 1
        return previous

    def save(self, cell_type, cut_off, more_than_one, obstructions, processed):
        c = self.conn.cursor()
        current_entry = self.entries[self.idx-1]
        c.execute('''UPDATE cells SET cell_type=?, cut_off=?, more_than_one=?, obstructions=?, processed=?
            WHERE file_name=? AND index_in_array=?''', (cell_type, cut_off, more_than_one, obstructions, processed,
                                                        self.file_name, current_entry.index_in_array))
        self.conn.commit()

    def unprocess_previous(self):
        c = self.conn.cursor()
        previous_entry = self.entries[self.idx-2]
        c.execute('''UPDATE cells SET processed=? WHERE file_name=? AND index_in_array=?''', (False, self.file_name,
                                                                                   previous_entry.index_in_array))
        self.conn.commit()

    def print_entries(self):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM cells''')
        rows = c.fetchall()
        for row in rows:
            #self.entries.append(Entry(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    def close_db(self):
        self.conn.close()


def load_data():
    DATA_LOCATION = '../../AlanFine'
    FILE_NAME = 'monocytes_neutrophils.npz'
    train_val = np.load(os.path.join(DATA_LOCATION, FILE_NAME))
    # stored as batch, depth, height, width. Tensorflow wants -> batch, height, width, depth
    neutrophils = np.rollaxis(train_val['neutrophils'], 1, 4)
    monocytes = np.rollaxis(train_val['monocytes'], 1, 4)
    training_images = np.concatenate([neutrophils, monocytes])[0:5, :, :, :]
    return training_images, FILE_NAME
