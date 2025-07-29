#!python
###################################################
###
### filename : estimate.py
### python version : 3
### requirements : in requirements.txt
### written by : SK Park
### Date : 2022-09-23
### LICENSE : MIT
###
###################################################

import shutil
import os 
import importlib
from pathlib import Path
import argparse
from argparse import RawTextHelpFormatter
import traceback,time,copy,sys,uuid
import sys
import subprocess
import re
import json
import copy

sys.path.append(Path(__file__).resolve().parent.parent.__str__()) 

from painfacelib.config import INFO as info
import painfacelib.common as common 
import painfacelib.common.video as vp
import painfacelib.common.visualize as viz
from painfacelib.ml import Estimation, SequentialModels
import painfacelib.common.dataset as d

logger=common.logger.write
color= common.Color

### Estimation class 

# class AMGSEstimation(Estimation):
#     def __init__(self,*args,**kwargs):
#         super().__init__(*args,**kwargs)

### commands 

def GenerateSequentialModels(payload):
    # payload = {
    #     'fau_model_dir': args.fau_model_dir,
    #     'mgs_model_dir': args.mgs_model_dir
    # }    
    ## model dir listing
    model_dir_list = []
    model_dir_list.append(payload['fau_model_dir'])

    #mgs_dirs = list(map(str,(Path(payload['mgs_model_dir']).resolve().iterdir())))
    mgs_dirs = [x for x in Path(payload['mgs_model_dir']).iterdir() if x.is_dir()]
    model_dir_list += mgs_dirs
    smodels = SequentialModels()

    for m in model_dir_list:
        smodels.addModel(m)

    return smodels

def estimate(payload,backend=None):
    # payload = {
    #     'model_dir': args.fau_model_dir,
    #     'output_dir': args.output_dir,
    #     'data_path': args.dataset_path,
    #     'subject_type':args.subject_type,
    #     'study_type':args.study_type,
    #     'interval':args.interval,
    #     'visualize': args.visualize,
    #     'gpu':args.gpu,
    #     'dev':args.dev
    # }
    payload['dataset_path']=payload['data_path']
    estimator = Estimation()
    estimator.addPayload(payload)
    estimator.estimate()

def estimate_dataset(payload,backend=None):
    # payload = {
    #     'fau_model_dir': args.fau_model_dir,
    #     'mgs_model_dir': args.mgs_model_dir,
    #     'output_dir': args.output_dir,
    #     'data_path': args.video_path,
    #     'subject_type':args.subject_type,
    #     'study_type':args.study_type,
    #     'interval':args.interval,
    #     'visualize': args.visualize,
    #     'gpu':args.gpu,
    #     'dev':args.dev
    # }

    ## model dir listing
    model_dir_list = []
    model_dir_list.append(['FACE DETECTION',payload['fau_model_dir']])

    #mgs_dirs = list(map(str,(Path(payload['mgs_model_dir']).resolve().iterdir())))
    mgs_dirs = [["DETECTING {}".format(str(x).split('/')[-1].upper()),x] for x in Path(payload['mgs_model_dir']).iterdir() if x.is_dir()]
    model_dir_list += mgs_dirs
    if backend is not None: c,t = backend.get_state_meta()
    for idx, pair in enumerate(model_dir_list):
        state,m = pair
        if backend is not None: backend.update_state(state= state, meta={"current": c+idx+1,"total": t})
        pl = {
            'model_dir': m,
            'type' : 'datasetdir',
            'dataset_path': payload['output_dir'],
            'gpu': payload['gpu'],
            'dev': payload['dev'],
            'subject_type': payload['subject_type'],
            'study_type': payload['study_type']
        }
        estimator = Estimation()
        estimator.addPayload(pl)
        estimator.estimateDatasetDirectory()

    payload.setdefault('visualize',True)
    if payload['visualize']:
        viz.visualize_dataset_directory(payload['output_dir'], None, scale=0.75)

@common.measure_time
def estimate_video(payload,backend=None):
    # payload = {
    #     'fau_model_dir': args.fau_model_dir,
    #     'mgs_model_dir': args.mgs_model_dir,
    #     'output_dir': args.output_dir,
    #     'data_path': args.video_path,
    #     'subject_type':args.subject_type,
    #     'study_type':args.study_type,
    #     'interval':args.interval,
    #     'visualize': args.visualize,
    #     'gpu':args.gpu,
    #     'dev':args.dev
    # }

    ## generation of dataset
    v = vp.VideoProcessor(payload['data_path'])
    v.generateDataset(payload['output_dir'], payload['subject_type'], payload['study_type'], payload['interval'], output_base=None)

    payload['data_path']= payload['output_dir']
    estimate_dataset(payload,backend=backend)
    

    ## generate csv
    total_func=d.generalTotal
    if payload['subject_type']=='c57bl/6':
      total_func=d.bl6Total 

    scoredAu=d.scoredAu
    if payload['subject_type']=='c57bl/6':
      scoredAu=d.bl6scoredAu
    res = d.generate_result_from_datasetdir(payload['output_dir'], # dataset dir
                      Path(payload['output_dir']).joinpath('result'), # result output dir
                      study_type=payload['study_type'],
                      fieldmap=[["Subject Type","reference.subject_type",None],
                                ["Frame Index","reference.frame_index",None],
                                ["Timestamp(x)",d.timestamp,"func"],
                                ["Orbital","score.pain-mgs.orbital",None],
                                ["Nose","score.pain-mgs.nose",None],
                                ["Ears","score.pain-mgs.ears",None],
                                ["Whiskers","score.pain-mgs.whiskers",None],
                                ["Cheek","score.pain-mgs.cheek",None],
                                ["Total Grimace Score",total_func, "func"],
                                ["AU Scored",scoredAu, "func"],
                                ["Confidence(Orbital)", "score.prediction-info.pain-mgs.confidence.orbital",None],
                                ["Confidence(Nose)", "score.prediction-info.pain-mgs.confidence.nose",None],
                                ["Confidence(Ears)", "score.prediction-info.pain-mgs.confidence.ears",None],
                                ["Confidence(Whiskers)", "score.prediction-info.pain-mgs.confidence.whiskers",None],
                                ["Confidence(Cheek)", "score.prediction-info.pain-mgs.confidence.cheek",None],
                                ["Face Model","reference.model_id.fau",None],
                                ["MGS Model","reference.model_id.mgs",None]
                               ],
                      video_filename=None)

    return res


