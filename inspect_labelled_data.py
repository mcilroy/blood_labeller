import os
import numpy as np
import constants
import db


def main():
    """" save the entries corresponding training images to a file named FILE_NAME+cleaned.
    The new file is used to perform machine learning. """
    DATA_LOCATION = 'data'
    FILE_NAME = 'pc9_collages.npz'
    DB_NAME = 'cell_labeled1_paul.db'
    the_db = db.DB(os.path.join(DATA_LOCATION, DB_NAME), os.path.join(DATA_LOCATION, FILE_NAME), restart=False)
    entries = the_db.get_processed_clean_entries()

    neutrophils = create_np_array(entries, the_db, constants.NEUTROPHIL)
    monocytes = create_np_array(entries, the_db, constants.MONOCYTE)
    basophils = create_np_array(entries, the_db, constants.BASOPHIL)
    eosinophils = create_np_array(entries, the_db, constants.EOSINOPHIL)
    lymphocytes = create_np_array(entries, the_db, constants.LYMPHOCYTE)
    filename, ext = os.path.splitext(FILE_NAME)
    print("neutro", len(neutrophils), "mono", len(monocytes), "baso", len(basophils), "eosin", len(eosinophils),
          "lympho", len(lymphocytes))
    np.savez(os.path.join(DATA_LOCATION, filename+"_cleaned_paul"), neutrophils=neutrophils, monocytes=monocytes, basophils=basophils,
             eosinophils=eosinophils, lymphocytes=lymphocytes)


def create_np_array(entries, the_db, name):
    cells = np.zeros([len(entries), the_db.training_images[0].shape[1], the_db.training_images[0].shape[2],
                            the_db.training_images[0].shape[3]])
    count_cells = 0
    exclude_indexes = [15]  # exclude patient 15 because it looks weird!
    for i, val in enumerate(entries):
        if val.cell_type == name and val.patient_index not in exclude_indexes:
            cells[count_cells, :, :, :] = the_db.training_images[val.patient_index][val.index_in_array, :, :, :]
            count_cells += 1
    cells = cells[0:count_cells, :, :, :]
    return cells


main()
