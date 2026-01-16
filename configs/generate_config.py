import os
import yaml
import glob
from datetime import datetime

patients = []
with open("/export/home/tbaudier/simon/extractPatientXvi/good_patient.txt", "r") as f:
    for line in f:
        patients += [line[:-1]]

output_data_dir = "/export/home/roo/thomas/data/"
config_yaml = '/export/home/tbaudier/simon/extractPatientXvi/cobra2026_challenge_preprocessing/configs/clb_config.yaml'

if os.path.exists(config_yaml):
    os.remove(config_yaml)

id_patient = 0
for patient in patients:

    #get and sort cbct
    cbct_series = glob.glob(patient + "/IMAGES/img_*")
    cbct_series_sorted = {}
    for cbct_serie in cbct_series:
        scan_files = glob.glob(cbct_serie + "/Reconstruction/*.SCAN")
        if len(scan_files) ==0:
            break
        ini_files = glob.glob(cbct_serie + "/Reconstruction/*.INI")
        for ini_file in ini_files:
            with open(ini_file, 'r', encoding='utf-8') as f:
              try:
                for line in f:
                  if line.startswith("AcquisitionDate="):
                    date=line[:-1].split("=")[1]
                    date_obj =  datetime.strptime(date, "%d.%m.%Y").date()
                    cbct_series_sorted[cbct_serie] = date_obj
                    break
              except:
                continue
    cbct_series_sorted_list = sorted(cbct_series_sorted, key=lambda item:item[1])
    filepath = cbct_series_sorted_list[0]

    #get the first cbct containing all necessary infos from INI file
    found_cbct = False
    cbct_index = 0
    ct_ReferenceUID = ""
    while (not found_cbct) and (cbct_index < len(cbct_series_sorted_list)):
        filepath = cbct_series_sorted_list[cbct_index]
        ini_files = glob.glob(filepath + "/**/*.INI*", recursive=True)
        if len(ini_files) == 0:
            print(filepath + " no INI file found")
            break
        dict_cbct = { 
            "ct_ReferenceUID": False,
            "OnlineToRefTransformCorrection": False
        }
        for ini_file in ini_files:
            with open(ini_file, 'r', encoding='utf-8') as f:
                try:
                    for line in f:
                        if line.startswith("ReferenceUID="):
                            dict_cbct["ct_ReferenceUID"] = True
                            ct_ReferenceUID = line.split("=")[1][:-1]
                        if line.startswith("OnlineToRefTransformCorrection="):
                            dict_cbct["OnlineToRefTransformCorrection"] = True

                except:
                    continue
        if not all(dict_cbct.values()):
            cbct_index += 1
        else:
            found_cbct = True

    if cbct_index == cbct_series_sorted_list:
        print("not found all INI infos")

    #get the right cbct path and projection path
    filepath = cbct_series_sorted_list[cbct_index]
    cbct_filename = glob.glob(filepath + "/**/*.SCAN", recursive=True)[0]
    projections_path = os.path.dirname(os.path.dirname(cbct_filename))

    #get ct images
    ct_images = glob.glob(os.path.dirname(cbct_filename) + "/../../../CT_SET/" + ct_ReferenceUID + "/CT_IMAGE_*.DCM")

    #Get the right Frames.xml
    frames_files = glob.glob(projections_path + "/_Frames.xm*", recursive=False)
    if len(frames_files) == 1:
        frames_file = frames_files[0]
    else:
        tmp = sorted(frames_files, key=lambda item:len(item))
        frames_file = tmp[-1]

    #patient id
    center = "C"
    id = center + str(id_patient).zfill(3)
    
    #config file
    config = {
        id: {
            'general': { 
                'center': center,
                'vendor': 'Elekta',
                },
            'data': {
                'projections': projections_path,
                'clinical_recon': cbct_filename,
                'ct': ct_images[0],
                'output': os.path.join(output_data_dir, id, 'output'),
                'framesxml': frames_file,
                'reconstruction_dir': os.path.dirname(cbct_filename),
                },
            'settings': {
                'correct_orientation': True,
                }
        }
    }
    
    with open(config_yaml, 'a') as f: 
        yaml.dump(config, f)
    
    id_patient += 1

