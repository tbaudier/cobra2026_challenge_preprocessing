import os
import yaml
import glob
from datetime import datetime

patients = []
with open("/export/home/tbaudier/simon/extractPatientXvi/good_patient.txt", "r") as f:
    for line in f:
        patients += [line[:-1]]

output_data_dir = "/export/home/tbaudier/simon/extractPatientXvi/data/"
config_yaml = '/export/home/tbaudier/simon/extractPatientXvi/cobra2026_challenge_preprocessing/configs/clb_config.yaml'

if os.path.exists(config_yaml):
    os.remove(config_yaml)

id_patient = 0
dict = {}
for patient in patients[:150]:

    #get first cbct
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
    cbct_filename = glob.glob(filepath + "/**/*.SCAN", recursive=True)[0]
    projections_path = os.path.dirname(os.path.dirname(cbct_filename))

    #get info from INI file
    ini_files = glob.glob(filepath + "/**/*.INI", recursive=True)
    if len(ini_files) == 0:
        print(filepath + " no INI file found")
        break
    p = "/".join(filepath.split('/')[-3:])
    dict[p] = { }
    for ini_file in ini_files:
        with open(ini_file, 'r', encoding='utf-8') as f:
            try:
                for line in f:
                    if line.startswith("FloodImageFilterNorm="):
                        dict[p]["FloodImageFilterNorm"] = float(line.split("=")[1][:-1])
                    elif line.startswith("FloodImageOpenNorm="):
                        dict[p]["FloodImageOpenNorm"] = float(line.split("=")[1][:-1])
                    elif line.startswith("FloodImageFilterMA="):
                        dict[p]["FloodImageFilterMA"] = float(line.split("=")[1][:-1])
                    elif line.startswith("FloodImageFilterMS="):
                        dict[p]["FloodImageFilterMS"] = float(line.split("=")[1][:-1])
                    elif line.startswith("FloodImageOpenMA="):
                        dict[p]["FloodImageOpenMA"] = float(line.split("=")[1][:-1])
                    elif line.startswith("FloodImageOpenMS="):
                        dict[p]["FloodImageOpenMS"] = float(line.split("=")[1][:-1])
                    elif line.startswith("TubeMA="):
                        dict[p]["TubeMA"] = float(line.split("=")[1][:-1])
                    elif line.startswith("TubeKVLength="):
                        dict[p]["TubeKVLength"] = float(line.split("=")[1][:-1])
                    elif line.startswith("TubeKV="):
                        dict[p]["TubeKV"] = float(line.split("=")[1][:-1])
                    elif line.startswith("FOV="):
                        dict[p]["FOV"] = line.split("=")[1][:-1]
                    elif line.startswith("ReferenceUID="):
                        dict[p]["ct_ReferenceUID"] = line.split("=")[1][:-1]
                    elif line.startswith("IsocX="):
                        dict[p]["IsocX"] = float(line.split("=")[1][:-1])
                    elif line.startswith("IsocY="):
                        dict[p]["IsocY"] = float(line.split("=")[1][:-1])
                    elif line.startswith("IsocZ="):
                        dict[p]["IsocZ"] = float(line.split("=")[1][:-1])
            except:
                continue

    #get ct images
    ct_images = glob.glob(os.path.dirname(cbct_filename) + "/../../../CT_SET/" + dict[p]["ct_ReferenceUID"] + "/CT_IMAGE_*.DCM")

    center = "C"
    id = center + str(id_patient).zfill(3)
    
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
                'framesxml': os.path.join(projections_path, '_Frames.xml'),
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

