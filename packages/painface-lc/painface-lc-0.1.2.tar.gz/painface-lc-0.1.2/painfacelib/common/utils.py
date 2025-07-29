import cv2
import os
import io
import uuid
import time
import traceback
import sys
import json
import datetime
from pathlib import Path
from collections.abc import MutableMapping
import re
import painfacelib.common as common 

def add_timestamp(doc):
    doc["updated_at"]=common.get_timestamp_iso()
    return doc

def add_uuid(doc):
    doc["_id"]=str(uuid.uuid4())
    return doc


def load_application_data():
    filepath = Path(__file__).parent.parent.joinpath('data/application_data.json')
    return json.load(open(filepath,'r'))

def remove_specials(text):
    res = re.sub("[$/:\\!&()]","",text) 
    return res


def update_states(backend,state,meta):
    if backend is not None:
      backend.update_state(state=state,meta=meta)

def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str ='.') -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)    

### utilities

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  

def get_timestamp_iso():
    return datetime.datetime.now().isoformat() 

def get_fd_classes_for_subject_type(subject_type, study_type,application_data):
    faus=application_data['subject_templates'][subject_type][study_type]['annotations']
    return list(map(lambda x: x['class'],faus))

def get_ps_classes_for_subject_type(subject_type, study_type,application_data):
    faus=application_data['subject_templates'][subject_type][study_type]['scores']
    return list(map(lambda x: x['class'],faus))

def get_uuid():
    return str(uuid.uuid4())

# def dataTemplate(source):
#     return {
#                  "dataset_id" : "system",
#                  "image_source" : source,  ## remote_image, remote_video, local_image, local_video
#                  "image_path" : "",
#                  "score" : {
#                  },
#                  "annotations" :{
#                     "type" : "custom",
#                     "regions" : []
#                  },
#                  "reference":{
#                     "date" : "NA",
#                     "camera" : "NA",
#                     "video_filename" : "",
#                     "frame_index" : -1,
#                     "fps": -1,
#                     "number_of_frames" : -1,
#                     "time_in_seconds" : -1,
#                     "scorer" : "Anonymous",
#                     "data_source" : "",
#                     "subject_type" : "c57bl/6"
#                  },
#                  "status" : "pending"   ## [pending , confirmed, removed] , default value is "pending"
#             }



def make_dataset(data_arr,working_dir,dataset_id="NA"):
    tmp=data_arr.copy()
    data={
            "info" : {
                "working_dir" : str(working_dir),
                "last_index" : 0,
                "source_type" : "image",  # normal images, video
                "image_source": "local_image",
                "dataset_id" : dataset_id
            },
            
            "scores" : data_arr 
    }
    return data 

def data_template(source):
    return {
                 "dataset_id" : "system",
                 "image_source" : source,  ## remote_image, remote_video, local_image, local_video
                 "image_path" : "", ## this is for dataset (videoname/frameidx)
                 "score" : {
                 },
                 "annotations" :{
                    "type" : "custom",
                    "regions" : []
                 },
                 "reference":{
                    "date" : "NA",
                    "camera" : "NA",
                    "video_filename" : "",
                    "video_storage": "custom",
                    "frame_index" : -1,
                    "fps": -1,
                    "number_of_frames" : -1,
                    "time_in_seconds" : -1,
                    "scorer" : "",
                    "data_source" : "",
                    "subject_type" : ""
                 },
                 "status" : "pending",   ## [pending , confirmed, removed] , default value is "pending"
                 "granted_institutions": [],
                 "updated_by":None,
                 "updated_at":None,
                 "inserted_by": None         
            }

def generateSample(subject_type, study_type):
    doc = data_template('evaluation')
    application_data = load_application_data()
    score={}
    score[study_type]={}
    score['prediction-info']={}
    score['prediction-info'][study_type]={}
    score['prediction-info'][study_type]['confidence']={}
    for v in application_data['subject_templates'][subject_type][study_type]['scores']:
        score[study_type][v['class']]=v['value'][0]
        score['prediction-info'][study_type]['confidence'][v['class']]=None

    doc['score']=score
    doc['image_source']='local_image'
    doc['image_path']= ''
    doc['reference']['video_filename'] = ''
    doc['reference']['fps'] = ''
    doc['reference']['frame_index'] = ''
    doc['reference']['video_storage']='system'
    doc['reference']['number_of_frames']= ''
    doc['reference']['subject_type'] = subject_type 
    doc['updated_by'] = 'system'
    doc['inserted_by'] = 'system'

    doc = add_timestamp(doc)
    doc = add_uuid(doc)
    return doc

def error_message(msg,status_code=500):
    return status_code, {"type" : "error", "message" : msg ,"status_code":status_code}
    
def classIndexToScore(cidx):  ## returns (classname, score)
    if cidx==0: return 'body' , None    
    if cidx==1: return 'face' , None
    cls=[2,5,8,11]
    clsnames=['orbital','nose','ears','whiskers',"cheek"]
    for c in cls:
        cn=clsnames.pop(0)
        for s in [0,1,2]:  
            if cidx==c+s:
                return cn, s 

def classIndex(cidx):  ## returns (classname, score)
    if cidx==0: return 'body' , None    
    if cidx==1: return 'face' , None
    cns=['body','face','orbital','nose','ears','whiskers','cheek']
    return cns[cidx], None 

def iou(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou

def rectCenter(coordinates):
    x1,y1,x2,y2=coordinates
    return (x1+x2)/2, (y1+y2)/2

def filterOverlaps(region): ## filter overlapped bounding boxes

    res=region.copy()
    #print(res)
    for idx in range(len(region)):
        r=region[idx]
        for idx2 in range(idx+1,len(region)):
            r2=region[idx2]
            if r2["class"]==r["class"]:
                if iou(r2["coordinates"], r["coordinates"]) > 0 :
                    if r2 in res:
                        res.remove(r2)
            else:
                if (r2['class'] not in ['face','body']) and (r['class'] not in ['face','body']):
                    if iou(r2["coordinates"], r["coordinates"]) > 0.1:
                        if r2['model_score'] < r['model_score']:
                            if r2 in res:
                                res.remove(r2)
                        else :
                            if r in res:
                                res.remove(r)

    #print(res)
    return res 

def _faceFilter(regions,classmap={"body":1,"face":1,"orbital":2,"nose":1,"ears":2,"whiskers":2,"cheek":2}): 
    ### this filters redundant facial element (second nose, third eyes, ..)
    res=[]
    regionmap={}
    for c,n in classmap.items():
        tmp=[x for x in regions if c==x["class"]][0:n]
        if len(tmp)>0 : regionmap[c]=tmp[0]
        res+=tmp 
    ### geometrical filtering
    res2=[]
    for r in res:
        ## everything should be in body
        shouldRemove=False
        if "body" in regionmap and iou(r["coordinates"], regionmap["body"]["coordinates"]) > 0:
            if "face" in regionmap and iou(r["coordinates"], regionmap["face"]["coordinates"]) >0:
                # if r["class"]=="whiskers":
                #     cx,cy=rectCenter(r["coordinates"])
                #     for sr in [x for x in res if x["class"] in ["orbital","ears"]]:
                #         x,y=rectCenter(sr["coordinates"])
                #         if cy < y :
                #             shouldRemove=True
                pass
            else: shouldRemove=True
        else: shouldRemove=True

        if not shouldRemove:                    
            res2.append(r)
    #return res2
    return _adjustAnnotations(res2)

def _adjustAnnotations(regions):
    ### face adjustment to cover all the facial elements
    regcopy=regions.copy()
    for idx,r in enumerate(regcopy):
        c=r["class"]
        if c=="face":
            facecomp=["orbital","nose","ears","whiskers","cheek"]
            rlist=[x for x in regions if x["class"] in facecomp]
            fx1,fy1,fx2,fy2=r["coordinates"]
            coordlist=[r["coordinates"] for r in rlist]
            for cd in coordlist:
                x1,y1,x2,y2 = cd 
                fx1=min(fx1,x1)
                fy1=min(fy1,y1)
                fx2=max(fx2,x2)
                fy2=max(fy2,y2)
            regcopy[idx]["coordinates"]=[fx1,fy1,fx2,fy2]
        if c=="body":
            facecomp=["face","orbital","nose","ears","whiskers","cheek"]
            rlist=[x for x in regions if x["class"] in facecomp]
            fx1,fy1,fx2,fy2=r["coordinates"]
            coordlist=[r["coordinates"] for r in rlist]
            for cd in coordlist:
                x1,y1,x2,y2 = cd 
                fx1=min(fx1,x1)
                fy1=min(fy1,y1)
                fx2=max(fx2,x2)
                fy2=max(fy2,y2)
            regcopy[idx]["coordinates"]=[fx1,fy1,fx2,fy2]
    return regcopy


