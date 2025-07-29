
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog

import painfacelib.common as common
from painfacelib.ui.glib.videoloading import VideoLoading


class Application():
    def __init__(self, *args,**kwargs):
        self.root = tk.Tk()
        self.root.title('Painface')
        self.root.geometry('+200+200')

        self.frm_video_loading = VideoLoading(master=self.root, width=400)
        self.frm_video_loading.grid(row=0,column=0,padx=20, pady=20 )
        
        self.root.bind("<Key>", self.key_handler)

    def run(self,*args, **kwargs):
        self.root.mainloop()

    def key_handler(self,event=None):
        # print(event)
        # print(event.char, event.keysym, event.keycode)
        if event.keysym == 'Right':
            if self.frm_video_loading.image_viewer is not None:
                self.frm_video_loading.image_viewer.next()
        if event.keysym == 'Left':
            if self.frm_video_loading.image_viewer is not None:
                self.frm_video_loading.image_viewer.previous()

if __name__=='__main__':
    app = Application()
    app.run()
