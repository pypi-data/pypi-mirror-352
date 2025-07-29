import json
from pathlib import Path
import csv
import shutil

from . import utils as u
import painfacelib.common as common

logger=common.logger.write 
color= common.Color


def get_dataset_dir(dataset_dir): #returns a generator [score, image]
    p = Path(dataset_dir).glob("*.json")
    return ([x, x.with_suffix('.jpeg')] for x in p)


def timestamp(x):
  fps=x['reference.fps']
  frameindex = x['reference.frame_index']
  return frameindex/fps

def bl6Total(x):
  res =0;
  fields = ['score.pain-mgs.orbital','score.pain-mgs.nose','score.pain-mgs.ears','score.pain-mgs.whiskers']
  for fld in fields:
    v = x[fld]
    try:
      v = int(v)
    except:
      return 'NA'
    if v >= 0:
      res = res + v
    else:
      return 'NA'
  return res 

def generalTotal(x):
  res =0;
  fields = ['score.pain-mgs.orbital','score.pain-mgs.nose','score.pain-mgs.ears','score.pain-mgs.whiskers','score.pain-mgs.cheek']
  for fld in fields:
    v = x[fld]
    try:
      v = int(v)
    except:
      return 'NA'
    if v >= 0:
      res = res + v
    else:
      return 'NA'
  return res 

def scoredAu(x):
  res =0;
  fields = ['score.pain-mgs.orbital','score.pain-mgs.nose','score.pain-mgs.ears','score.pain-mgs.whiskers','score.pain-mgs.cheek']
  for fld in fields:
    if x[fld] >= 0:
      res = res + 1
  return res    

def bl6scoredAu(x):
  res =0;
  fields = ['score.pain-mgs.orbital','score.pain-mgs.nose','score.pain-mgs.ears','score.pain-mgs.whiskers']
  for fld in fields:
    if x[fld] >= 0:
      res = res + 1
  return res      

def generate_csv_from_dataset(scores, fieldmap: list, outputpath):
    scores = sorted(scores, key=lambda x: x['reference']['frame_index'])

    with open(outputpath,'w') as fp:
        csvwriter=csv.writer(fp)
        csvwriter.writerow(list(map(lambda x: x[0],fieldmap)))
        for s in scores:
            doc = u.flatten_dict(s)
            row=[]
            for k,f,t in fieldmap:
                if t is None:
                    try:
                        row.append(doc[f])
                    except Exception as e:
                        row.append("NA")
                else:
                    try:
                        row.append(f(doc))
                    except:
                        row.append("NA")         
            csvwriter.writerow(row)

def generate_result_from_datasetdir(dataset_dir, 
                    outputdir, 
                    study_type,
                    fieldmap=[["Frame Index","reference.frame_index",None],  
                            ## title, key for value or unary function on flattened document, 
                            ##  None for normal field  'func' for function
                              ["Orbital","score.pain-mgs.orbital",None],
                              ["Nose","score.pain-mgs.nose",None],
                              ["Ears","score.pain-mgs.ears",None],
                              ["Whiskers","score.pain-mgs.whiskers",None],
                              ["Cheek","score.pain-mgs.cheek",None]], 
                    video_filename=None):
    dataset_dir = Path(dataset_dir)
    datagen = get_dataset_dir(dataset_dir)
    scores=[]
    for scorepath, imagepath in datagen:
        with open(scorepath,'r') as f:
            scores.append(json.load(f))

    dataset = {
        "info": {
            "dataset_id": scores[0]['dataset_id'],
            'dataset_type': 'prediction',
            'source_type': 'video'
        },
        "scores":scores
    }
    file_id = u.get_uuid()
    outputdir = Path(outputdir)
    outputdir.mkdir(exist_ok=True,parents=True)

    output_csv_path=outputdir.joinpath("result.csv")
    generate_csv_from_dataset(scores, fieldmap, output_csv_path)

    logger("fileid:{}".format(output_csv_path.__str__()))
    res={
      "filename" : output_csv_path.__str__(),
      "datetime": u.get_timestamp_iso()
    }
    return res 

