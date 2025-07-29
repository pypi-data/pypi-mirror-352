
# import miscellaneous modules
import cv2
import os
import io
import uuid
import numpy as np
import time
import traceback
import sys
import json
from pathlib import Path
from . import utils as u 
import math as m
from . import video as vp 
import painfacelib.common as common 

logger=common.logger.write 
color= common.Color

_color=['gray','purple','yellow','cyan','green','orange','brown','coral','darkblue','darkcyan','blueviolet','crimson','chocolate','cadeblue','pink','firebrick','darkgreen','darkviolet','darkorange','darkred','dimgray','darkturquoise']
_classes=['tbd','body','face','orbital','nose','ears','whiskers','cheek']

colormap={ ## rgb
    "body":(153, 51, 255),
    "face" : (255, 51, 0),
    "orbital":(0, 153, 204),
    "nose": (0, 153, 51),
    "ears":(255, 153, 0),
    "whiskers":(204, 51, 0),
    "cheek":(0,165,255)
}

def draw_caption(image, box, caption):
    b = np.array(box).astype(int)
    #cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    cv2.putText(image, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def draw_score(image,box,caption):
    b = np.array(box).astype(int)
    #cv2.putText(image, caption, (b[0]+10, b[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(image, caption, (b[0]+5, b[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def write_image(image,score_object,filename,scale=1.0,study_type='pain-mgs'):
    region=score_object['annotations']['regions']
    scores=score_object['score'][study_type]
    if study_type + '-gt' in score_object['score']: 
        scores_gt = score_object['score'][study_type+'-gt']
    else: 
        scores_gt = None
    ## resize image
    h,w,c=image.shape
    image=cv2.resize(image,(int(w*scale),int(h*scale)))
    for r in region:
        bbox = r['coordinates']
        x1 = int(bbox[0] * scale)
        y1 = int(bbox[1] * scale)
        x2 = int(bbox[2] * scale)
        y2 = int(bbox[3] * scale)
        label_name = r['class']
        # print(bbox, classification.shape)
        model_score = r['model_score']
        #caption = '{} {:.3f}'.format(label_name, model_score)
        caption = '{}'.format(label_name)
        # draw_caption(img, (x1, y1, x2, y2), label_name)
        # draw_caption(image, (x1, y1, x2, y2), caption)
        color=colormap[label_name]
        color=(color[2],color[1],color[0])
        cv2.rectangle(image, (x1, y1), (x2, y2), color=color, thickness=1)

        if label_name in scores:
            mgs_score=scores[label_name]
            if scores_gt is not None:
                mgs_score_gt=scores_gt[label_name]
            else:
                mgs_score_gt=None
            if mgs_score_gt == -1 :
                mgs_score_gt='X'
            #mgs_confidence=scores[label_name]['confidence']
            if mgs_score_gt is not None:
                score_caption="{}:{}".format(mgs_score, mgs_score_gt)
            else:
                score_caption="{}".format(mgs_score)
            draw_score(image, (x1,y1,x2,y2), score_caption)
    cv2.imwrite(str(filename),image, [int(cv2.IMWRITE_JPEG_QUALITY), 80])

def write_image_bb(image,score_object,filename,scale=1.0):
    region=score_object['annotations']['regions']
    ## resize image
    h,w,c=image.shape
    image=cv2.resize(image,(int(w*scale),int(h*scale)))
    for r in region:
        bbox = r['coordinates']
        x1 = int(bbox[0] * scale)
        y1 = int(bbox[1] * scale)
        x2 = int(bbox[2] * scale)
        y2 = int(bbox[3] * scale)
        label_name = r['class']
        # print(bbox, classification.shape)
        model_score = r['model_score']
        #caption = '{} {:.3f}'.format(label_name, model_score)
        caption = '{}'.format(label_name)
        # draw_caption(img, (x1, y1, x2, y2), label_name)
        draw_caption(image, (x1, y1, x2, y2), caption)
        color=colormap[label_name]
        color=(color[2],color[1],color[0])
        cv2.rectangle(image, (x1, y1), (x2, y2), color=color, thickness=1)
    cv2.imwrite(str(filename),image, [int(cv2.IMWRITE_JPEG_QUALITY), 80]) 

def visualize_images(videoProcessor,dataset_filename,scale=1.0,study_type='pain-mgs',backend=None):
    dataset_dir=Path(dataset_filename).parent
    dataset=json.load(open(dataset_filename,'r'))
    scores=dataset['scores']
    sn=len(scores)
    global_count=0
    global_total=0
    if backend is not None:
        global_count=backend.AsyncResult(backend.request.id).info.get('current',0)
        global_total=backend.AsyncResult(backend.request.id).info.get('total',0)
    for idx, s in enumerate(scores):
        image_cache=s['image_cache']
        image_path=dataset_dir.joinpath(image_cache)
        frame_index=s['reference']['frame_index']
        frame=videoProcessor.getFrameByIndex(frame_index)
        write_image(frame,s, str(image_path),scale=scale,study_type=study_type)
        print("\rImage [{:04d}/{:04d}] written.".format(idx+1,sn),end="\r")
        u.update_states(backend, state="GENERATING_IMAGES", meta={'current': global_count+idx+1 , 'total': global_total})

def visualize_images_from_dataset(video_dir,dataset_filename,scale=1.0,study_type='pain-mgs',backend=None):
    dataset_dir=Path(dataset_filename).parent
    dataset=json.load(open(dataset_filename,'r'))
    scores=dataset['scores']
    sn=len(scores)
    global_count=0
    global_total=0
    current_video_file=scores[0]['reference']['video_filename']
    videoProcessor=vp.VideoProcessor(Path(video_dir).joinpath(current_video_file).__str__())
    if backend is not None:
        global_count=backend.AsyncResult(backend.request.id).info.get('current',0)
        global_total=backend.AsyncResult(backend.request.id).info.get('total',0)
    for idx, s in enumerate(scores):
        if s['reference']['video_filename']!=current_video_file:
            current_video_file=s['reference']['video_filename']
            videoProcessor=vp.VideoProcessor(Path(video_dir).joinpath(current_video_file).__str__())
        image_cache=s['image_cache']
        image_path=dataset_dir.joinpath(image_cache)
        frame_index=s['reference']['frame_index']
        frame=videoProcessor.getFrameByIndex(frame_index)
        write_image(frame,s, str(image_path),scale=scale,study_type=study_type)
        print("\rImage [{:04d}/{:04d}] written.".format(idx+1,sn),end="\r")
        u.update_states(backend, state="GENERATING_IMAGES", meta={'current': global_count+idx+1 , 'total': global_total})

def visualize_dataset_directory(dataset_dir, output_dir, scale= 0.5, study_type ='pain-mgs'):

    logger("Loading datasets from :{}".format(dataset_dir),color.PROCESS)
    dataset_dir = Path(dataset_dir)
    output_dir = dataset_dir.joinpath('visualization')
    if output_dir is not None:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    samplelist = list(dataset_dir.glob('*.json'))
    samplepairs = []
    for samplefn in samplelist:
        doc = json.load(open(samplefn,'r'))
        sample_img_fn = samplefn.with_suffix('.jpeg')
        if sample_img_fn.exists():
            samplepairs.append([doc,samplefn,sample_img_fn])
    logger("Dataset Loaded",color.OK)
    n_samples=len(samplepairs)
    for idx, p in enumerate(samplepairs):
        doc, doc_path, image_path = p
        image = cv2.imread(str(image_path),cv2.IMREAD_UNCHANGED)
        output_fn = output_dir.joinpath(image_path.name)
        write_image(image, doc, str(output_fn), scale=scale, study_type=study_type)
    logger("Visualization written in {}".format(output_dir.__str__()), color.OK)


