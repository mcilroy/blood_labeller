import os
import numpy as np
import constants
import db
import scipy
import numpy

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
    # r-squared - for each cell-type compute the r-squared, produces 6 r-squares
    # remove 10, 15, 17, not finished labeling
    indexes = np.array([10, 15, 29])
    for key in coulter_labels:
        mask = np.ones(len(coulter_labels[key]), dtype=bool)
        mask[indexes] = False
        coulter_labels[key] = coulter_labels[key][mask]
        manual_labels[key] = manual_labels[key][mask]
    #print(result)
    #print(manual_labels[constants.LYMPHOCYTE])
    #print(fit(coulter_labels[constants.LYMPHOCYTE][0:10], manual_labels[constants.LYMPHOCYTE][0:10]))

    r_valuel = polyfit(coulter_labels[constants.LYMPHOCYTE], manual_labels[constants.LYMPHOCYTE], 1)
    r_valuee = polyfit(coulter_labels[constants.EOSINOPHIL], manual_labels[constants.EOSINOPHIL], 1)
    r_valuen = polyfit(coulter_labels[constants.NEUTROPHIL], manual_labels[constants.NEUTROPHIL], 1)
    r_valuem = polyfit(coulter_labels[constants.MONOCYTE], manual_labels[constants.MONOCYTE], 1)
    r_valueb = polyfit(coulter_labels[constants.BASOPHIL], manual_labels[constants.BASOPHIL], 1)
    r_valuew = polyfit(coulter_labels['wbc'], manual_labels['wbc'], 1)
    #slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(coulter_labels[constants.LYMPHOCYTE], manual[constants.LYMPHOCYTE])
    print("lymph", r_valuel['determination'], "eosin", r_valuee['determination'], "neutro", r_valuen['determination'],
          "mono", r_valuem['determination'], "baso", r_valueb['determination'], "wbc", r_valuew['determination'])


def compute_stats(entries, num_patients):
    manual = dict()
    for c in CONSTANTS:
        for p in xrange(num_patients):
            for x in xrange(len(entries)):
                if entries[x].patient_index == p:
                    if entries[x].cell_type == c:
                        if c not in manual:
                            manual[c] = np.zeros((num_patients))  #[0] * num_patients
                            manual[c][p] = 1
                        else:
                            manual[c][p] += 1

    manual['wbc'] = np.zeros((num_patients))
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


# Polynomial Regression
def polyfit(x, y, degree):
    results = {}

    coeffs = numpy.polyfit(x, y, degree)

     # Polynomial Coefficients
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = numpy.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = numpy.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = numpy.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = numpy.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot

    return results


main()
