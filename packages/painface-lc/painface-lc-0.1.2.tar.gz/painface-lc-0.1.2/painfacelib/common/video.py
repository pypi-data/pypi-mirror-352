import cv2
import os
from pathlib import Path
import json
from . import utils
import painfacelib.common as common

logger=common.logger.write 
color= common.Color

class VideoProcessor():
    def __init__(self,videoFilename):
        self.filename=None
        self.cap=None
        self.currentFrame=None
        self.numberOfFrames=0
        self.fps=0
        self.duration=0
        self.openVideoFile(videoFilename)
        self.cap_position=0
        self.application_data = utils.load_application_data()

    def openVideoFile(self,filename):
        filename = str(filename)
        if os.path.exists(filename):
            self.filename=filename
            self.cap=cv2.VideoCapture(self.filename)
            (ret,frame) = self.cap.read()
            if ret :
                self.currentFrame=frame
                self.numberOfFrames= int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.duration = int(self.numberOfFrames/self.fps)
                self.cap_position =int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                
                print(f"Filename : {filename}")
                print("Number of Frames : {0} , FPS : {1} , Duration {2}:{3} Current Pos : {4}".format(self.numberOfFrames,self.fps,\
                                                                    int(self.duration/60),self.duration % 60,self.cap_position))
            else:
                print("Error in reading frame : VideoProcessor.getCurrentFrame")
        else:
            self.newVideo(filename)


    def getCurrentFrame(self):  ### BGR image 
        return self.currentFrame 
        #return cv2.cvtColor(self.currentFrame, cv2.COLOR_BGR2RGB)
   
    def getFrameByStep(self,step=1):
        current_position=int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.cap.set(1,current_position+step-1)
        (ret,frame)=self.cap.read()
        if ret:
            self.currentFrame=frame
            self.cap_position =int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            return self.getCurrentFrame()
        else:
            return None

    def getFrameByIndex(self,idx):
        if idx < self.numberOfFrames and idx >= 0 :
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
            (ret,frame)=self.cap.read()
            if ret:
                self.currentFrame=frame
                self.cap_position=int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                return self.getCurrentFrame()
            else:
                return None

    def _generateMeta(self,idx, subject_type, study_type):
        doc = utils.data_template('evaluation')
        doc = utils.add_timestamp(doc)
        doc = utils.add_uuid(doc)
        filename = Path(self.filename).name

        score={}
        score[study_type]={}
        score['prediction-info']={}
        score['prediction-info'][study_type]={}
        score['prediction-info'][study_type]['confidence']={}
        for v in self.application_data['subject_templates'][subject_type][study_type]['scores']:
            score[study_type][v['class']]=v['value'][0]
            score['prediction-info'][study_type]['confidence'][v['class']]=None

        doc['score']=score
        doc['image_source']='local_video'
        doc['image_path']= "%s/%08d" % (filename,idx)
        doc['reference']['video_filename'] = filename
        doc['reference']['fps'] = self.fps
        doc['reference']['frame_index'] = idx
        doc['reference']['video_storage']='system'
        doc['reference']['number_of_frames']=self.numberOfFrames
        doc['reference']['subject_type'] = subject_type 
        doc['updated_by'] = 'system'
        doc['inserted_by'] = 'system'

        return doc
    def generateSample(self,idx, output_dir, subject_type ,study_type,output_base=None):
        if idx < self.numberOfFrames and idx >= 0 :
            self.cap.set(1,idx)
            (ret,frame)=self.cap.read()
            doc = self._generateMeta(idx, subject_type,study_type)
            if output_base is None:
                output_base = "{}_{:08d}".format(Path(self.filename).stem,idx)
            img_fn = "{}.jpeg".format(output_base)
            meta_fn = "{}.json".format(output_base)
            out_filename_img = Path(output_dir).joinpath(img_fn)
            out_filename_meta = Path(output_dir).joinpath(meta_fn)
            if ret:
                self.currentFrame=frame
                self.cap_position=int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                frame = self.getCurrentFrame()
                json.dump(doc,open(out_filename_meta,'w'),indent=4)
                cv2.imwrite(str(out_filename_img),frame,[int(cv2.IMWRITE_JPEG_QUALITY), 80])
                return (doc, frame)
            else:
                return None
        else:
            raise Exception("Out of range")

    def generateSampleFromGT(self,score, output_dir ,study_type,output_base=None):
        idx = score['reference']['frame_index']
        if idx < self.numberOfFrames and idx >= 0 :
            doc = score
            doc['score'][study_type+'-gt'] = doc['score'][study_type]
            del doc['score'][study_type]
            doc['score']['prediction-info']={}
            doc['score']['prediction-info'][study_type]={}
            doc['score']['prediction-info'][study_type]['confidence']={}
            self.cap.set(1,idx)
            (ret,frame)=self.cap.read()
            if output_base is None:
                output_base = "{}_{:08d}".format(Path(self.filename).stem,idx)
            img_fn = "{}.jpeg".format(output_base)
            meta_fn = "{}.json".format(output_base)
            out_filename_img = Path(output_dir).joinpath(img_fn)
            out_filename_meta = Path(output_dir).joinpath(meta_fn)
            if ret:
                self.currentFrame=frame
                self.cap_position=int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                frame = self.getCurrentFrame()
                json.dump(doc,open(out_filename_meta,'w'),indent=4)
                cv2.imwrite(str(out_filename_img),frame,[int(cv2.IMWRITE_JPEG_QUALITY), 80])
                return (doc, frame)
            else:
                return None
        else:
            raise Exception("Out of range")

    def generateDataset(self, output_dir, subject_type, study_type, interval, output_base=None):
        logger("Generating ..",color.PROCESS)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True,exist_ok=True)
        video = self
        n_frames = video.numberOfFrames
        rng = list(range(0,n_frames, interval))
        total = len(rng)
        for i, idx in enumerate(rng) :
            res = video.generateSample(idx,output_dir, subject_type, study_type)
            print("\r[{}/{}] are being generated".format(i+1,total),end="\r")
        print()
        logger("Dataset is generated at {}".format(output_dir.__str__()), color.OK)

    def newVideo(self,outfilename="./output.mp4",frames=[], size=(640,400),fps=30):
        vwriter=cv2.VideoWriter(outfilename,cv2.VideoWriter_fourcc(*'mp4v'),fps,size)
        for idx,f in enumerate(frames):
            resized=cv2.resize(F,size)
            vwriter.write(resized)
            print("\rProgressing %d / %d" %( idx , len(frames)),end="\r")
        vwriter.release()
        self.openVideoFile(outfilename)

    def cropVideo(self,bbox,outfilename='./output.mp4',output_size=None,grayscale=True): #bbox = [c1,y1,x2,y2]
        
        
        m_bbox=bbox
        x1,y1,x2,y2 = m_bbox
        cnt=0
        self.cap.set(1,0)
        ret,frame = self.cap.read()
        fps = self.fps
        h,w,c = frame.shape 

        if output_size is None:
            output_size = (w,h)

        if(grayscale):
            vwriter=cv2.VideoWriter(str(outfilename),cv2.VideoWriter_fourcc(*'mp4v'),fps,output_size, 0) ## 0 for grayscale
        else:
            vwriter=cv2.VideoWriter(str(outfilename),cv2.VideoWriter_fourcc(*'mp4v'),fps,output_size)

        is_end= False

        while not is_end:
            cnt+=1
            ret,frame = self.cap.read()
            
            if ret:
                if grayscale:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cropped = frame[y1:y2,x1:x2]
                resized=cv2.resize(cropped,output_size)
                vwriter.write(resized)
            else:
                is_end = True
            print("\rProgressing %d / %d" %(cnt,self.numberOfFrames),end="\r")


    def extractVideo(self,begin_index,last_index,outfilename="./output.mp4",size=None):
        
        if begin_index is None: begin_index=0
        self.cap.set(1,begin_index)

        ret, frame = self.cap.read()
        h ,w , _ = frame.shape

        if size is None: size = (w,h)

        vwriter=cv2.VideoWriter(outfilename,cv2.VideoWriter_fourcc(*'mp4v'),self.fps,size)

        if last_index is None:
            is_end = False
            cnt=0
            while not is_end:
                cnt+=1
                ret,frame = self.cap.read()
                
                if ret:

                    resized=cv2.resize(frame,size)
                    vwriter.write(resized)
                else:
                    is_end = True
                print("\rProgressing %d / %d" %(cnt,self.numberOfFrames),end="\r")
        else:
            for idx in range(begin_index,last_index):
                ret,frame = self.cap.read()
                if ret:
                    resized=cv2.resize(frame,size)
                    vwriter.write(resized)
                print("\rProgressing %d / %d" %(idx-begin_index+1,last_index-begin_index),end="\r")
        vwriter.release()
        
    def extractVideoFrames(self,begin_index,last_index,size=None):
        
        

        if begin_index is None: begin_index=0
        self.cap.set(1,begin_index)

        ret, frame = self.cap.read()
        h ,w , _ = frame.shape

        if size is None: size = (w,h)

        frames=[]

        if last_index is None:
            is_end = False
            cnt=0
            while not is_end:
                cnt+=1
                ret,frame = self.cap.read()
                
                if ret:
                    
                    resized=cv2.resize(frame,size)
                    frames.append(resized)

                else:
                    is_end = True

        else:
            for idx in range(begin_index,last_index):
                ret,frame = self.cap.read()
                if ret:
                    resized=cv2.resize(frame,size)
                    frames.append(resized)
        return frames 
        
        
    def __iter__(self):
        return self

    def __next__(self):
        (ret,frame)=self.cap.read()
        if ret:
            yield frame 
        else:
            raise StopIteration

    def items(self):
        self.cap.set(1,0)
        self.cap_position=0
        for i in range(self.numberOfFrames):
            (ret,frame)=self.cap.read()
            if ret:
                self.cap_position =int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                yield frame 
            else:
                raise StopIteration

        self.cap.set(1,0)
        self.cap_position =int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))






