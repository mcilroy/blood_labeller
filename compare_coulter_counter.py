import os
import numpy as np
import constants
import db

CONSTANTS = {constants.LYMPHOCYTE, constants.EOSINOPHIL, constants.BASOPHIL, constants.MONOCYTE, constants.NEUTROPHIL}


def main():
    """" compare the manually labelled data to the coulter counter counts to see how accurate our manual labelling is
    compared with the coulter counter. """
    DATA_LOCATION = 'data'
    FILE_NAME = 'pc9_collages.npz'
    DB_NAME = 'cell_labeled1.db'
    COUNT_FILE_NAME = 'PC9_WBC_cc_scaled.npz'

    the_db = db.DB(os.path.join(DATA_LOCATION, DB_NAME), os.path.join(DATA_LOCATION, FILE_NAME), restart=False)
    entries = the_db.get_processed_clean_entries()

    counts = np.load(os.path.join(DATA_LOCATION, COUNT_FILE_NAME))
    coulter_labels = dict()
    coulter_labels[constants.LYMPHOCYTE] = counts['lymph']
    coulter_labels[constants.EOSINOPHIL] = counts['eosi']
    coulter_labels[constants.NEUTROPHIL] = counts['neut']
    coulter_labels[constants.MONOCYTE] = counts['mono']
    coulter_labels[constants.BASOPHIL] = counts['baso']
    coulter_labels['wbc'] = counts['wbc']

    num_patients = get_num_patients(entries)
    manual_labels = compute_stats(entries, num_patients)
    for x in xrange(num_patients):
        print("patient: "+str(x))
        for key in coulter_labels:
            coulter = coulter_labels[key][x]
            manual = manual_labels[key][x]
            diff = coulter-manual
            print(key + " coulter:"+"{:.2f}".format(coulter)+" manual:"+"{:.2f}".format(manual) +
                  " diff:"+"{:.2f}".format(diff))
        print("")


def compute_stats(entries, num_patients):
    manual = dict()
    for c in CONSTANTS:
        for p in xrange(num_patients):
            for x in xrange(len(entries)):
                if entries[x].patient_index == p:
                    if entries[x].cell_type == c:
                        if c not in manual:
                            manual[c] = [0] * num_patients
                            manual[c][p] = 1
                        else:
                            manual[c][p] += 1

    manual['wbc'] = [0] * num_patients
    for x in xrange(num_patients):
        single_patient = 0
        for key in manual:
            single_patient += manual[key][x]
        manual['wbc'][x] = single_patient
    return manual


def get_num_patients(entries):
    nums = []
    for x in xrange(len(entries)):
        nums.append(entries[x].patient_index)
    return len(np.unique(nums))

main()
