import os
import time

import hdf5storage
import numpy as np
import scipy.io as sio
from functions.dFC_funcs import *

os.environ["MKL_NUM_THREADS"] = "64"
os.environ["NUMEXPR_NUM_THREADS"] = "64"
os.environ["OMP_NUM_THREADS"] = "64"

print(
    "################################# subject-level dFC assessment CODE started running ... #################################"
)

################################# Parameters #################################
###### DATA PARAMETERS ######

input_root = "./"
output_root = "./"

################################# LOAD #################################

dFC_analyzer = np.load(input_root + "dFC_analyzer.npy", allow_pickle="TRUE").item()
data_loader = np.load(input_root + "data_loader.npy", allow_pickle="TRUE").item()

################################# LOAD FIT MEASURES #################################

if dFC_analyzer.MEASURES_fit_lst == []:
    ALL_RECORDS = os.listdir(input_root + "fitted_MEASURES/")
    ALL_RECORDS = [i for i in ALL_RECORDS if "MEASURE" in i]
    ALL_RECORDS.sort()
    MEASURES_fit_lst = list()
    for s in ALL_RECORDS:
        fit_measure = np.load(
            input_root + "fitted_MEASURES/" + s, allow_pickle="TRUE"
        ).item()
        MEASURES_fit_lst.append(fit_measure)
    dFC_analyzer.set_MEASURES_fit_lst(MEASURES_fit_lst)
    print("fitted MEASURES loaded ...")
    # np.save('./dFC_analyzer.npy', dFC_analyzer)

################################# LOAD DATA #################################

task_id = int(os.getenv("SGE_TASK_ID"))
subj_id = data_loader.SUBJECTS[task_id - 1]  # SGE_TASK_ID starts from 1 not 0

BOLD = data_loader.load(subj_id2load=subj_id)

################################# dFC ASSESSMENT #################################

tic = time.time()
print("Measurement Started ...")

print("dFCM estimation started...")
dFCM_dict = dFC_analyzer.subj_lvl_dFC_assess(time_series_dict=BOLD)
print("dFCM estimation done.")

print(f"Measurement required {time.time() - tic:0.3f} seconds.")

################################# SAVE DATA #################################

# folder = output_root+'dFC_assessed/SUBJ_'+str(subj_id)
# if not os.path.exists(folder):
#     os.makedirs(folder)

# for dFCM_id, dFCM in enumerate(dFCM_dict['dFCM_lst']):
#     np.save(folder+'/dFCM_'+str(dFCM_id)+'.npy', dFCM)

################################# SIMILARITY MEASUREMENT #################################

similarity_assessment = SIMILARITY_ASSESSMENT(dFCM_lst=dFCM_dict["dFCM_lst"])

tic = time.time()
print("Measurement Started ...")

print("Similarity measurement started...")
SUBJ_output = similarity_assessment.run(
    FILTERS=dFC_analyzer.hyper_param_info, downsampling_method="default"
)
print("Similarity measurement done.")

print(f"Measurement required {time.time() - tic:0.3f} seconds.")

# Save
folder = output_root + "similarity_measured"
if not os.path.exists(folder):
    os.makedirs(folder)

np.save(folder + "/SUBJ_" + str(subj_id) + "_output.npy", SUBJ_output)

#################################################################################
