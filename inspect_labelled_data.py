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
    #save_file("labelled_data/pc9_with_vvc_7classes_training", entries, images, 'pc9_collages.npz')
    save_file("labelled_data/pc9_with_vvc_7classes_validation", entries, images, 'venous_vs_capillary.npz')


def save_file(filename, entries, images, specific_file=""):
    neutrophils, neutro_patients = create_np_array(entries, images, constants.NEUTROPHIL, specific_file)
    monocytes, mono_patients = create_np_array(entries, images, constants.MONOCYTE, specific_file)
    basophils, baso_patients = create_np_array(entries, images, constants.BASOPHIL, specific_file)
    eosinophils, eosin_patients = create_np_array(entries, images, constants.EOSINOPHIL, specific_file)
    lymphocytes, lymp_patients = create_np_array(entries, images, constants.LYMPHOCYTE, specific_file)
    strange_eosinophils, strange_eosin_patients = create_np_array(entries, images, constants.STRANGE_EOSINOPHIL, specific_file)
    no_cells, no_cell_patients = create_np_array(entries, images, constants.NO_CELL, specific_file)

    print("neutro", len(neutrophils), "mono", len(monocytes), "baso", len(basophils), "eosin", len(eosinophils),
          "lympho", len(lymphocytes), "strange_eosin", len(strange_eosinophils), "no_cells", len(no_cells))
    print("total: " + str(sum([len(neutrophils), len(monocytes), len(basophils), len(eosinophils), len(lymphocytes), len(strange_eosinophils), len(no_cells)])))
    np.savez(os.path.join(DATA_LOCATION, filename), neutrophils=neutrophils, monocytes=monocytes,
             basophils=basophils, eosinophils=eosinophils, lymphocytes=lymphocytes,
             strange_eosinophils=strange_eosinophils, no_cells=no_cells)
    np.savez(os.path.join(DATA_LOCATION, filename+"_patients"), neutro_patients=neutro_patients,
             mono_patients=mono_patients, baso_patients=baso_patients, eosin_patients=eosin_patients,
             lymp_patients=lymp_patients, strange_eosin_patients=strange_eosin_patients,
             no_cell_patients=no_cell_patients)


def create_np_array(entries, images, name, specific_file=""):
    cells = np.zeros([len(entries), images[FILE_NAME][0].shape[1], images[FILE_NAME][0].shape[2],
                      images[FILE_NAME][0].shape[3]])
    patient_indexes = np.zeros([len(entries), 1])

    count_cells = 0
    exclude_indexes = []  # don't exclude anything anymore
    for i, val in enumerate(entries):
        if val.file_name != specific_file and specific_file != "":
            continue
        if val.cell_type == name and val.patient_index not in exclude_indexes:
            cells[count_cells, :, :, :] = images[val.file_name][val.patient_index][val.index_in_array, :, :, :]
            patient_indexes[count_cells, 0] = val.patient_index
            count_cells += 1
    cells = cells[0:count_cells, :, :, :]
    patient_indexes = patient_indexes[0:count_cells, 0]
    return cells, patient_indexes


main()
