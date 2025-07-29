import json
from pathlib import Path
import PIL
import PIL.Image
import PIL.ImageTk
import subprocess
import threading 

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.messagebox 

import painfacelib.common.video as vid
import painfacelib.ml.estimate as e 

class LabelArray(tk.Frame):
    def __init__(self, master, labels_dict,  *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        
        i=0
        for k, v in labels_dict.items():
            lbl_key = tk.Label(master=self, text=k)
            lbl_val = tk.Label(master=self, text=v)
            lbl_key.grid(row=i, column=0)
            lbl_val.grid(row=i, column=1)
            i+=1

class ImageViewer(tk.Frame):
    def __init__(self, master, image_dir,  *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.image_dir = Path(image_dir)
        self.files = list(self.image_dir.glob('*.jpeg'))
        self.files = sorted(self.files, key=lambda x: x.name)


        self.lbl_image = tk.Label(master=self )
        self.lbl_image.grid(row=0,column=0,columnspan=2, pady=5, padx=20)
        self.current_index =  -1
        
        self.btn_prev = tk.Button(master=self,text=r"<", command=self.previous)
        self.btn_prev.grid(row=2, column=0, sticky='w')

        self.sv_count = tk.StringVar()
        self.sv_count.set(f"{self.current_index+1}/{len(self.files)}")
        self.lbl_counts = tk.Label(master=self, textvariable=self.sv_count)
        self.lbl_counts.grid(row=1,columnspan=2)

        self.btn_next = tk.Button(master=self,text=r">", command=self.next)
        self.btn_next.grid(row=2, column=1, sticky='e')
        
        self.next()

    def next(self):
        if self.current_index+1 < len(self.files):
            self.current_index+=1
            image = PIL.Image.open(self.files[self.current_index])
            image_tk = PIL.ImageTk.PhotoImage(image)
            self.lbl_image.config(image = image_tk)
            self.lbl_image.photo = image_tk
            self.sv_count.set(f"{self.current_index+1}/{len(self.files)}")
        else:
            pass

    def previous(self):
        if self.current_index > 0:
            self.current_index-=1
            image = PIL.Image.open(self.files[self.current_index])
            image_tk = PIL.ImageTk.PhotoImage(image)
            self.lbl_image.config(image = image_tk)
            self.lbl_image.photo = image_tk
            self.sv_count.set(f"{self.current_index+1}/{len(self.files)}")
        else:
            pass


class VideoLoading(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.sv_videofilename = tk.StringVar()
        self.videofilename = None
        self.video = None
        self.sv_videofilename.set("<Video Filename>")
        self.entry_video_filename = tk.Entry(master=self, textvariable=self.sv_videofilename)
        self.entry_video_filename.grid(row=0, column=1)
        
        
        self.button1 = tk.Button(master=self, text="Browse Files", width=15)
        self.button1.bind("<ButtonRelease-1>", self.buttonHandler)
        self.button1.grid(row=0,column=0)
         

        self.sv_video_info = tk.StringVar()
        self.lbl_video_info = tk.Label(master=self, textvariable = self.sv_video_info)
        self.btn_output_dir = tk.Button(master=self, text="Output Directory", width=15)
        self.btn_output_dir.bind('<ButtonRelease-1>', self.outputDirHandler)
        
        self.sv_output_dir = tk.StringVar()
        self.entry_output_dir = tk.Entry(master=self, textvariable=self.sv_output_dir)
        
        self.btn_output_dir.grid(row=1, column=0)
        self.entry_output_dir.grid(row=1, column=1)

        self.lbl_interval = tk.Label(master=self, text="Evaluation Freq")

        self.sv_interval = tk.StringVar()
        self.sv_interval.set('1 Frame per 30s')
        self.cmb_interval = ttk.Combobox(master=self, textvariable=self.sv_interval, width=15)
        self.cmb_interval['state']='readonly'
        self.cmb_interval['values'] = ('1 Frame per 1s','1 Frame per 3s','1 Frame per 10s','1 Frame per 30s')
        #self.cmb_interval.bind('<<ComboboxSelected>>', option_changed) 

        self.btn_evaluate = tk.Button(master=self, text="Evaluate Video", width=15, height=2)
        self.btn_evaluate.bind('<ButtonRelease-1>', self.processVideo)
       
        self.pb_process = ttk.Progressbar(master=self, orient="horizontal", mode="indeterminate")
        
        self.image_viewer = None

    def buttonHandler(self,event=None):
        fn = tk.filedialog.askopenfile(mode='r',
                                       title='Select a File',
                                       filetypes=[('Mpeg4 files', '*.mp4')]
                                       )
        if fn:
            self.sv_videofilename.set(Path(fn.name).name)
            self.videofilename = fn.name
            self.video = vid.VideoProcessor(self.videofilename)
            info = {
                'fps': self.video.fps,
                'number_of_frames': self.video.numberOfFrames,
                'duration(s)': int(self.video.numberOfFrames / self.video.fps)
            }
            self.sv_video_info.set(json.dumps(info,indent=4))
            #self.lbl_video_info.grid(row=5,column=0, columnspan=5)


            self.lbl_interval.grid(row=2, column=0)
            self.cmb_interval.grid(row=2, column=1)
            self.btn_evaluate.grid(row=3, columnspan=2)

            if self.image_viewer is not None:
                self.image_viewer.grid_forget()

    def outputDirHandler(self, event=None):
        fn = tk.filedialog.askdirectory(title='Select a Directory')
        if fn:
            self.sv_output_dir.set(fn)
            if Path(fn).joinpath('visualization').exists():
                self.add_image_viewer()

    def processVideo(self, event=None):
        th1 = threading.Thread(target=self._thread_process, args=())
        
        th1.start()
    
    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state='normal')
            except:
                pass

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state='disable')
            except:
                pass
    
    def _compute_frequency(self, sv_freq):
        fq = sv_freq.get()
        fq = float(fq.split()[-1].replace('s',''))
        interval = fq * self.video.fps
        return int(interval)

    def add_image_viewer(self):
        viz_dir = Path(self.sv_output_dir.get()).joinpath('visualization').__str__()
        self.image_viewer = ImageViewer(master=self, image_dir = viz_dir )
        self.image_viewer.grid(row=5, columnspan=2)


    def _thread_process(self):

        self.disable()
        self.pb_process.grid(row=4,column=0, columnspan=100)
        self.pb_process.start(50)
        config_dir = Path.home().joinpath('.painface')
        subject_type = 'c57bl/6'
        interval = 1000
        fau_model_dir = config_dir.joinpath('models').joinpath(subject_type.replace('/','')).joinpath('fau').joinpath('default')
        mgs_model_dir = config_dir.joinpath('models').joinpath(subject_type.replace('/','')).joinpath('pain-mgs').joinpath('default')
        payload = {
            'type': 'datasetdir',
            'fau_model_dir': fau_model_dir,
            'mgs_model_dir': mgs_model_dir,
            'output_dir': self.sv_output_dir.get(),
            'data_path': self.videofilename,
            'subject_type': subject_type,
            'study_type': 'pain-mgs',
            'interval': self._compute_frequency(self.sv_interval),
            'gpu': 0,
            'visualize': True,
            'dev': False
        }
        res = e.estimate_video(payload)
        tk.messagebox.showinfo(message="Evaluation Finished")
        self.pb_process.grid_forget()
        if res:
            self.add_image_viewer()
        self.enable()


        


