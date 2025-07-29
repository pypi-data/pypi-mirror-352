
import numpy as np
import os, json,random,argparse,cv2,time,datetime,pprint,sys, shutil, traceback, csv, time
from pathlib import Path
import importlib.util

sys.path.append(Path(__file__).resolve().parent.parent.__str__())

import painfacelib.common.module as modulelib
import painfacelib.common as common
import painfacelib.common.video as vp

logger=common.logger.write
color= common.Color

class SequentialModels(object):
    def __init__(self,*args,**kwargs):
        self.models=[] # preloaded models in order for apply

    def addModel(self, model_dir, gpu_index=0):
        module_dir=Path(model_dir).joinpath('codes').joinpath('estimation').resolve().__str__()
        modules=modulelib.load_module_from_directory(module_dir)
        Estimator=modules['estimator']['module'].Estimator 
        estimator = Estimator(model_dir,gpu_index)
        self.models.append(estimator)

    def applyModels(self, payload):
        for estimator in self.models:
            estimator.estimate(payload)

class Estimation(object):
    def __init__(self,*args,**kwargs):
        self.payload_list=[]
        self.modules=[]

    def setPayloads(self, payload_list):
        self.payload_list = payload_list

    def addPayload(self,payload):
        self.payload_list.append(payload)

    def estimate(self):
        payload_list=self.payload_list
        for payload in payload_list:
            module_dir=Path(payload['model_dir']).joinpath('codes').joinpath('estimation').resolve().__str__()
            modules=modulelib.load_module_from_directory(module_dir)

            Estimator=modules['estimator']['module'].Estimator 

            estimator = Estimator(payload['model_dir'],payload['gpu'],dev=payload['dev'])
            estimator.estimate(payload) 

    def estimateDatasetDirectory(self):
        payload_list=self.payload_list
        for payload in payload_list:
            module_dir=Path(payload['model_dir']).joinpath('codes').joinpath('estimation').resolve().__str__()
            modules=modulelib.load_module_from_directory(module_dir)

            Estimator=modules['estimator']['module'].Estimator 

            estimator = Estimator(payload['model_dir'],payload['gpu'],dev=payload['dev'])
            estimator.estimate(payload)    

