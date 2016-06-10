import ntpath
import sqlite3

import numpy as np

import constants
from entry import Entry


class DB:
    def __init__(self, file_path, restart=False):
        self.conn = sqlite3.connect('data/cells.db')
        self.idx = 0
        self.load_data(file_path)
        self.entries = []
        if restart:
            self.restart()
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
                      obstructions INTEGER, processed INTEGER, modified INTEGER, PRIMARY KEY (file_name, index_in_array))''')
        self.conn.commit()

    def check_if_data_seen_before(self):
        c = self.conn.cursor()
        c.execute('''SELECT EXISTS(SELECT 1 FROM cells WHERE file_name=? LIMIT 1)''', (self.file_name,))
        data = c.fetchone()
        if data[0] == 0:
            self.init_table()

    def init_table(self):
        self.init_row(self.neutrophils.shape[0], self.offset_neutro, constants.NEUTROPHIL)
        self.init_row(self.monocytes.shape[0], self.offset_mono, constants.MONOCYTE)
        self.init_row(self.eosinophils.shape[0], self.offset_eosinophils, constants.EOSINOPHIL)
        self.init_row(self.basophils.shape[0], self.offset_basophils, constants.BASOPHIL)

    def init_row(self, cell_length, offset, cell_type):
        c = self.conn.cursor()
        data_entries = []
        for i in range(cell_length):
            data_entries.append((self.file_name, i+offset, cell_type, None, None, None, 0, 0))
        c.executemany(''' INSERT INTO cells(file_name, index_in_array, cell_type, cut_off, more_than_one, obstructions,
                        processed, modified) VALUES(?,?,?,?,?,?,?,?)''', data_entries)
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

    def get_processed_clean_entries(self):
        entries = []
        c = self.conn.cursor()
        c.execute('''SELECT index_in_array, cell_type FROM cells where file_name=? AND (cell_type=? OR cell_type=? OR
        cell_type=? OR cell_type=? OR cell_type=?) AND cut_off=0 AND more_than_one=0 AND obstructions=0 AND processed=1
        ''', (self.file_name, constants.NEUTROPHIL, constants.LYMPHOCYTE, constants.MONOCYTE, constants.EOSINOPHIL,
              constants.BASOPHIL))
        rows = c.fetchall()
        for row in rows:
            entries.append(Entry(self.file_name, row[0], row[1], 0, 0, 0, 1))
        return entries

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

    def save(self, cell_type, cut_off, more_than_one, obstructions, processed, modified):
        c = self.conn.cursor()
        current_entry = self.entries[self.idx-1]
        c.execute('''UPDATE cells SET cell_type=?, cut_off=?, more_than_one=?, obstructions=?, processed=?, modified=?
            WHERE file_name=? AND index_in_array=?''', (cell_type, cut_off, more_than_one, obstructions, processed,
                                                        modified, self.file_name, current_entry.index_in_array))
        self.conn.commit()

    def save_entries(self, entries):
        data_entries = []
        for entry in entries:
            data_entries.append((entry.cell_type, entry.cutoff, entry.more_than_one, entry.obstructions, entry.processed, entry.modified, entry.file_name, entry.index_in_array))
        c = self.conn.cursor()
        c.executemany('''UPDATE cells SET cell_type=?, cut_off=?, more_than_one=?, obstructions=?, processed=?, modified=?
            WHERE file_name=? AND index_in_array=?''', data_entries)
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
            print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    def close_db(self):
        self.conn.close()

    def get_entries(self):
        self.entries = []
        self.idx = 0
        c = self.conn.cursor()
        c.execute('''SELECT * FROM cells''')
        rows = c.fetchall()
        for row in rows:
            self.entries.append(Entry(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        return self.entries

    def get_cell_types(self):
        c = self.conn.cursor()
        c.execute('''SELECT DISTINCT cell_type FROM cells''')
        rows = c.fetchall()
        names = []
        for row in rows:
            names.append(row[0])
        return names

    def get_currently_displayed_images(self, entries):
        images = np.zeros([len(entries), 81, 81, 3], dtype="uint8")
        for i, entry in enumerate(entries):
            image = self.training_images[entry.index_in_array, :, :, :]
            images[i, :, :, :] = image
        return images

    def load_data(self, file_path):
        self.file_name = ntpath.basename(str(file_path))
        #DATA_LOCATION = '../../AlanFine'
        #FILE_NAME = 'monocytes_neutrophils.npz'
        train_val = np.load(str(file_path))
        # stored as batch, depth, height, width. Tensorflow wants -> batch, height, width, depth
        self.offset_neutro = 0
        self.neutrophils = np.rollaxis(train_val['neutrophils'], 1, 4)#[0:101, :, :, :]
        self.offset_mono = self.neutrophils.shape[0]
        self.monocytes = np.rollaxis(train_val['monocytes'], 1, 4)#[0:101, :, :, :]
        self.offset_basophils = self.neutrophils.shape[0] + self.monocytes.shape[0]
        self.basophils = np.rollaxis(train_val['basophils'], 1, 4)
        self.offset_eosinophils = self.neutrophils.shape[0] + self.monocytes.shape[0] + self.basophils.shape[0]
        self.eosinophils = np.rollaxis(train_val['eosinophils'], 1, 4)
        self.training_images = np.concatenate([self.neutrophils, self.monocytes, self.basophils, self.eosinophils])
        #return neutrophils, monocytes, file_name
