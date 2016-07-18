import os
import numpy as np
import constants
import db

DATA_LOCATION = 'data'
FILE_NAME = 'venous_vs_capillary.npz'
FILE_NAME2 = 'pc9_collages.npz'
DB_NAME = 'cells.db'


def main():
    """" save the entries corresponding training images to a file named FILE_NAME+cleaned.
    The new file is used to perform machine learning. """

    the_db = db.DB(os.path.join(DATA_LOCATION, DB_NAME), os.path.join(DATA_LOCATION, FILE_NAME), restart=False)
    images = the_db.load_from_multiple_files([os.path.join(DATA_LOCATION, FILE_NAME), os.path.join(DATA_LOCATION,
                                                                                                   FILE_NAME2)])
    entries = the_db.get_processed_clean_entries()

    neutrophils = create_np_array(entries, images, constants.NEUTROPHIL)
    monocytes = create_np_array(entries, images, constants.MONOCYTE)
    basophils = create_np_array(entries, images, constants.BASOPHIL)
    eosinophils = create_np_array(entries, images, constants.EOSINOPHIL)
    lymphocytes = create_np_array(entries, images, constants.LYMPHOCYTE)
    strange_eosinophils = create_np_array(entries, images, constants.STRANGE_EOSINOPHIL)
    no_cells = create_np_array(entries, images, constants.NO_CELL)

    filename, ext = os.path.splitext(FILE_NAME)
    print("neutro", len(neutrophils), "mono", len(monocytes), "baso", len(basophils), "eosin", len(eosinophils),
          "lympho", len(lymphocytes), "strange_eosin", len(strange_eosinophils), "no_cells", len(no_cells))
    print("total: " + str(sum([len(neutrophils), len(monocytes), len(basophils), len(eosinophils), len(lymphocytes), len(strange_eosinophils), len(no_cells)])))
    np.savez(os.path.join(DATA_LOCATION, "labelled_data/pc9_with_vvc_7classes"), neutrophils=neutrophils, monocytes=monocytes,
             basophils=basophils, eosinophils=eosinophils, lymphocytes=lymphocytes,
             strange_eosinophils=strange_eosinophils, no_cells=no_cells)


def create_np_array(entries, images, name):
    cells = np.zeros([len(entries), images[FILE_NAME][0].shape[1], images[FILE_NAME][0].shape[2],
                      images[FILE_NAME][0].shape[3]])
    count_cells = 0
    exclude_indexes = []  # don't exclude anything anymore
    for i, val in enumerate(entries):
        if val.cell_type == name and val.patient_index not in exclude_indexes:
            cells[count_cells, :, :, :] = images[val.file_name][val.patient_index][val.index_in_array, :, :, :]
            count_cells += 1
    cells = cells[0:count_cells, :, :, :]
    return cells


main()
