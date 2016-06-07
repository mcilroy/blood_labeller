import numpy as np
import os

import constants
import db


def main():
    """" save the entries corresponding training images to a file named FILE_NAME+cleaned"""
    DATA_LOCATION = '../../AlanFine'
    FILE_NAME = 'monocytes_neutrophils.npz'
    the_db = db.DB(os.path.join(DATA_LOCATION, FILE_NAME))
    entries = the_db.get_processed_clean_entries()

    neutrophils = np.zeros([len(entries), the_db.training_images.shape[1], the_db.training_images.shape[2],
                            the_db.training_images.shape[3]])
    count_neutrophils = 0
    for i, val in enumerate(entries):
        if val.cell_type == constants.NEUTROPHIL:
            neutrophils[i, :, :, :] = the_db.training_images[val.index_in_array, :, :, :]
            count_neutrophils += 1
    neutrophils = neutrophils[0:count_neutrophils, :, :, :]

    monocytes = np.zeros([len(entries), the_db.training_images.shape[1], the_db.training_images.shape[2],
                         the_db.training_images.shape[3]])
    count_monocytes = 0
    for i, val in enumerate(entries):
        if val.cell_type == constants.NEUTROPHIL:
            monocytes[i, :, :, :] = the_db.training_images[val.index_in_array, :, :, :]
            count_monocytes += 1
    monocytes = monocytes[0:count_monocytes, :, :, :]

    np.savez("data/"+FILE_NAME+"_cleaned", neutrophils=neutrophils, monocytes=monocytes)


main()
