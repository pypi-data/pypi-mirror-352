from __future__ import print_function
import time
from PIL import Image, ImageDraw, ImageTk
import threading
import cv2
import numpy as np


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


class PhotoBoothApp:
    def __init__(self, url, outputPath, root, canvas,
                 width=300, height=300,
                 pos_x=500, pos_y=500, zoomed_x=1000, zoomed_y=1000,
                 zoomed_video_width=1000, zoomed_video_height=700,
                 root_zoom_callback_func=None,
                 root_hide_callback_func=None,
                 cam_type=None):
        self.url = url
        self.can_show = False
        self.zoomed = False
        self.cam_type = cam_type
        self.zoomed_video_width = zoomed_video_width
        self.zoomed_video_height = zoomed_video_height
        self.outputPath = outputPath
        self.root_zoom_callback_func = root_zoom_callback_func
        self.root_hide_callback_funct = root_hide_callback_func
        self.frame = None
        self.latest_frame = None
        self.can_zoom = True
        self.thread = None
        self.stopEvent = threading.Event()
        self.zoomed_x = zoomed_x
        self.zoomed_y = zoomed_y

        self.root = root
        self.init_x, self.init_y = pos_x, pos_y
        self.place_x, self.place_y = pos_x, pos_y
        self.init_video_width, self.init_video_height = width, height
        self.video_width, self.video_height = width, height

        self.canvas = canvas
        self.image_id_1 = None
        self.image_id_2 = None
        self.tk_image_1 = None
        self.tk_image_2 = None
        self.last_used_id = 1

        self.img_loading = ImageTk.PhotoImage(Image.open("imgs/camera_is_connecting.png"))
        self.img_unavailable = ImageTk.PhotoImage(Image.open("imgs/camera_is_not_available.png"))
        self.camera_unavailable = False

        threading.Thread(target=self.read_frames_loop, daemon=True).start()
        threading.Thread(target=self.video_loop, daemon=True).start()

    def read_frames_loop(self):
        cap = cv2.VideoCapture(self.url)
        reconnect_interval = 5
        last_reconnect_attempt = 0
        unavailable_threshold = 10
        camera_down_start = None

        while not self.stopEvent.is_set():
            try:
                if not cap.isOpened():
                    now = time.time()
                    if camera_down_start is None:
                        camera_down_start = now
                    elif now - camera_down_start > unavailable_threshold:
                        self.camera_unavailable = True
                    if now - last_reconnect_attempt > reconnect_interval:
                        cap.release()
                        cap = cv2.VideoCapture(self.url)
                        last_reconnect_attempt = now
                    time.sleep(1)
                    continue
                else:
                    camera_down_start = None
                    self.camera_unavailable = False

                ret, frame = cap.read()
                if ret:
                    self.latest_frame = frame
                else:
                    time.sleep(0.1)

            except Exception as e:
                print(f"[{self.cam_type}] [read_frames_loop error]", e)
                time.sleep(1)

    def video_loop(self):
        while not self.stopEvent.is_set():
            try:
                if not self.can_show:
                    time.sleep(0.05)
                    continue

                frame = self.latest_frame
                if frame is None:
                    image = self.img_unavailable if self.camera_unavailable else self.img_loading
                    self._show_image(image, static=True)
                    time.sleep(0.05)
                    continue

                resized = cv2.resize(frame, (self.video_width, self.video_height))
                image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)
                tk_image = ImageTk.PhotoImage(pil_image)

                self._show_image(tk_image)

            except Exception as e:
                print(f"[{self.cam_type}] [video_loop error]", e)
            time.sleep(0.03)

    def _show_image(self, image, static=False):
        if self.last_used_id == 1:
            if self.image_id_2 is None:
                self.image_id_2 = self.canvas.create_image(self.place_x, self.place_y, image=image)
                self.canvas.tag_bind(self.image_id_2, '<Button-1>', self.img_callback)
            else:
                self.canvas.itemconfig(self.image_id_2, image=image)
                self.canvas.coords(self.image_id_2, self.place_x, self.place_y)
            self.canvas.tag_raise(self.image_id_2)
            self.last_used_id = 2
            if not static:
                self.tk_image_2 = image
        else:
            if self.image_id_1 is None:
                self.image_id_1 = self.canvas.create_image(self.place_x, self.place_y, image=image)
                self.canvas.tag_bind(self.image_id_1, '<Button-1>', self.img_callback)
            else:
                self.canvas.itemconfig(self.image_id_1, image=image)
                self.canvas.coords(self.image_id_1, self.place_x, self.place_y)
            self.canvas.tag_raise(self.image_id_1)
            self.last_used_id = 1
            if not static:
                self.tk_image_1 = image

    def hide_callback(self, root_calback=True):
        self.video_width = self.init_video_width
        self.video_height = self.init_video_height
        self.place_x = self.init_x
        self.place_y = self.init_y
        self.can_show = True
        if self.root_hide_callback_funct and root_calback:
            self.root_hide_callback_funct(self.cam_type)
            self.zoomed = False

    def set_new_params(self, x=None, y=None, width=None, height=None):
        if width:
            self.video_width = width
        if height:
            self.video_height = height
        if x:
            self.place_x = x
        if y:
            self.place_y = y

    def zoom_callback(self, root_calback=True):
        self.video_width = self.zoomed_video_width
        self.video_height = self.zoomed_video_height
        self.place_x = self.zoomed_x
        self.place_y = self.zoomed_y
        self.can_show = True
        if self.root_zoom_callback_func and root_calback:
            self.root_zoom_callback_func(self.cam_type)
        self.zoomed = True

    def img_callback(self, *args):
        if not self.can_zoom:
            return
        self.can_show = False
        if self.zoomed:
            self.hide_callback()
        else:
            self.zoom_callback()

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        try:
            self.root.quit()
        except:
            pass

    def stop_video(self):
        self.can_show = False

    def play_video(self):
        self.can_show = True


def start_video_stream(root, canvas, xpos, ypos, v_width, v_height,
                       cam_login, cam_pass, cam_ip, zoomed_x, zoomed_y,
                       zoomed_video_width, zoomed_video_height,
                       cam_type=None,
                       cam_port=554,
                       zoom_callback_func=None, hide_callback_func=None):
    url = f"rtsp://{cam_login}:{cam_pass}@{cam_ip}:{cam_port}/Streaming/Channels/102"

    inst = PhotoBoothApp(url, "output", root=root, canvas=canvas, width=v_width,
                         height=v_height, pos_x=xpos, pos_y=ypos,
                         zoomed_x=zoomed_x,
                         zoomed_y=zoomed_y,
                         root_zoom_callback_func=zoom_callback_func,
                         root_hide_callback_func=hide_callback_func,
                         cam_type=cam_type,
                         zoomed_video_width=zoomed_video_width,
                         zoomed_video_height=zoomed_video_height)
    return inst
