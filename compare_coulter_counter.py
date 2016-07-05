import os
import numpy as np
import constants
import db
import numpy

CONSTANTS = {constants.LYMPHOCYTE, constants.EOSINOPHIL, constants.BASOPHIL, constants.MONOCYTE, constants.NEUTROPHIL}
COUNT_FILE_NAME = 'PC9_WBC_cc_scaled.npz'


class Stats:
    """" compare the manually labelled data to the coulter counter counts to see how accurate our manual labelling is
    compared with the coulter counter. """
    def __init__(self, data_location, db_name):
        counts = np.load(os.path.join(data_location, COUNT_FILE_NAME))
        self.coulter_labels = dict()
        self.coulter_labels[constants.LYMPHOCYTE] = counts['lymph']
        self.coulter_labels[constants.EOSINOPHIL] = counts['eosi']
        self.coulter_labels[constants.NEUTROPHIL] = counts['neut']
        self.coulter_labels[constants.MONOCYTE] = counts['mono']
        self.coulter_labels[constants.BASOPHIL] = counts['baso']
        self.coulter_labels['wbc'] = counts['wbc']
        self.num_patients = 0
        self.manual_labels = dict()
        self.data_location = data_location
        self.file_name = ""
        self.db_name = db_name
        #self.indexes = np.array([10, 15, 29])  # remove 1 outlier (15) and 2 that don't have coulter counts
        self.nan_indexes = dict()
        for key in self.coulter_labels:
            mask = np.ones(len(self.coulter_labels[key]), dtype=bool)
            self.nan_indexes[key] = [i for i, v in enumerate(self.coulter_labels[key]) if np.isnan(v)]
            mask[self.nan_indexes[key]] = False
            #self.coulter_labels[key] = self.coulter_labels[key][mask]

    def re_calculate(self, file_name):
        self.file_name = file_name
        the_db = db.DB(os.path.join(self.data_location, self.db_name), os.path.join(self.data_location, self.file_name),
                       restart=False)
        entries = the_db.get_processed_clean_entries()
        self.num_patients = get_num_patients(entries)
        self.orig_indexes = np.arange(0, self.num_patients)
        self.manual_labels = self.compute_manual_labeled_stats(entries)
        for key in self.manual_labels:
            mask = np.ones(len(self.manual_labels[key]), dtype=bool)
            mask[self.nan_indexes[key]] = False
            #self.manual_labels[key] = self.manual_labels[key][mask]

    def print_all_stats(self):
        for x in xrange(self.num_patients):
            print("patient: "+str(x))
            print(self.display_single_patient(x))
            print("")
        print(self.display_global_patient_stats())

    def display_single_patient(self, cur_patient):
        msg = ""
        for key in self.coulter_labels:
            if cur_patient in self.nan_indexes[key]:
                msg += key + "\nNo coulter counter data available\n\n"
            else:
                coulter = self.coulter_labels[key][cur_patient]
                manual = self.manual_labels[key][cur_patient]
                diff = np.abs(coulter-manual)
                rel_error = np.abs((coulter-manual)/(1+coulter))*100.0
                msg += key + "\ncoulter counter:"+"{:.2f}".format(coulter)+" manual labeling:"+"{:.2f}".format(manual) + \
                    "\nabsolute error:"+"{:.2f}".format(diff)+" relative error percentage:"+"{:.2f}".format(rel_error)+"\n\n"
        return msg

    def display_global_patient_stats(self):
        temp_man_labels = dict()
        for key in self.manual_labels:
            mask = np.ones(len(self.manual_labels[key]), dtype=bool)
            mask[self.nan_indexes[key]] = False
            temp_man_labels[key] = self.manual_labels[key][mask]
        temp_coulter_labels = dict()
        for key in self.coulter_labels:
            mask = np.ones(len(self.coulter_labels[key]), dtype=bool)
            mask[self.nan_indexes[key]] = False
            temp_coulter_labels[key] = self.coulter_labels[key][mask]
        # r-squared - for each cell-type compute the r-squared, produces 6 r-squares
        r_valuel = polyfit(temp_coulter_labels[constants.LYMPHOCYTE], temp_man_labels[constants.LYMPHOCYTE], 1)
        r_valuee = polyfit(temp_coulter_labels[constants.EOSINOPHIL], temp_man_labels[constants.EOSINOPHIL], 1)
        r_valuen = polyfit(temp_coulter_labels[constants.NEUTROPHIL], temp_man_labels[constants.NEUTROPHIL], 1)
        r_valuem = polyfit(temp_coulter_labels[constants.MONOCYTE], temp_man_labels[constants.MONOCYTE], 1)
        r_valueb = polyfit(temp_coulter_labels[constants.BASOPHIL], temp_man_labels[constants.BASOPHIL], 1)
        r_valuew = polyfit(temp_coulter_labels['wbc'], temp_man_labels['wbc'], 1)
        return ">0.95 is ideal\n\nneutrophils:%f\nlymphocytes:%f\nmonocytes:%f\neosinophils:%f\nbasophils:%f\nwhite bool cells:%f" % \
               (r_valuen['determination'], r_valuel['determination'], r_valuem['determination'],
                r_valuee['determination'], r_valueb['determination'], r_valuew['determination'])

    def export_computed_global_patient_stats(self, path):
        if not path:
            return
        with open(path, 'w') as f:
            f.write('Patient, Cell Type, Coulter Counter, Manually labeled, Absolute difference, Relative difference percentage\n')
            for x in xrange(self.num_patients):
                for key in self.coulter_labels:
                    coulter = self.coulter_labels[key][x]
                    manual = self.manual_labels[key][x]
                    diff = np.abs(coulter-manual)
                    rel_error = np.abs((coulter-manual)/(1+coulter))*100.0
                    f.write(','.join([str(x), key, str(coulter), str(manual), str(diff), str(rel_error)]) + '\n')

            f.write('Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, White blood cells\n')
            temp_man_labels = dict()
            for key in self.manual_labels:
                mask = np.ones(len(self.manual_labels[key]), dtype=bool)
                mask[self.nan_indexes[key]] = False
                temp_man_labels[key] = self.manual_labels[key][mask]
            temp_coulter_labels = dict()
            for key in self.coulter_labels:
                mask = np.ones(len(self.coulter_labels[key]), dtype=bool)
                mask[self.nan_indexes[key]] = False
                temp_coulter_labels[key] = self.coulter_labels[key][mask]
            # r-squared - for each cell-type compute the r-squared, produces 6 r-squares
            r_valuel = polyfit(temp_coulter_labels[constants.LYMPHOCYTE], temp_man_labels[constants.LYMPHOCYTE], 1)
            r_valuee = polyfit(temp_coulter_labels[constants.EOSINOPHIL], temp_man_labels[constants.EOSINOPHIL], 1)
            r_valuen = polyfit(temp_coulter_labels[constants.NEUTROPHIL], temp_man_labels[constants.NEUTROPHIL], 1)
            r_valuem = polyfit(temp_coulter_labels[constants.MONOCYTE], temp_man_labels[constants.MONOCYTE], 1)
            r_valueb = polyfit(temp_coulter_labels[constants.BASOPHIL], temp_man_labels[constants.BASOPHIL], 1)
            r_valuew = polyfit(temp_coulter_labels['wbc'], temp_man_labels['wbc'], 1)
            f.write(','.join([str(r_valuen['determination']), str(r_valuel['determination']),
                              str(r_valuem['determination']), str(r_valuee['determination']),
                              str(r_valueb['determination']), str(r_valuew['determination'])]) + '\n')

    def export_raw_global_patient_stats(self, path, data):
        if not path:
            return
        with open(path, 'w') as f:
            f.write('Patient, Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, Unsure, No Cell, Unlabelled\n')
            for i, x in enumerate(data):
                f.write(','.join(['%i' % (i+1)] + ['%i' % len(xi) for xi in x]) + '\n')

    def compute_manual_labeled_stats(self, entries):
        manual = dict()
        for c in CONSTANTS:
            for p in xrange(self.num_patients):
                for x in xrange(len(entries)):
                    if entries[x].patient_index == p:
                        if entries[x].cell_type == c:
                            if c not in manual:
                                manual[c] = np.zeros(self.num_patients)  #[0] * num_patients
                                manual[c][p] = 1
                            else:
                                manual[c][p] += 1

        manual['wbc'] = np.zeros(self.num_patients)
        for x in xrange(self.num_patients):
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


def main():
    stats = Stats()
    stats.print_all_stats()

if __name__ == "__main__":
    main()
