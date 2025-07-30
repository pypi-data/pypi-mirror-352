import time
from PIL import Image, ImageDraw, ImageTk
from importlib.resources import files
import threading
import cv2

class PhotoBoothApp:
    def __init__(self, url, root, canvas,
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
        self.root_zoom_callback_func = root_zoom_callback_func
        self.root_hide_callback_funct = root_hide_callback_func
        self.frame = None
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
        self.panel = None
        self.image_id = None
        self.canvas = canvas

        self.vs = None
        self.latest_frame = None
        self.tk_image = None
        self.camera_unavailable = False
        self.connecting = True

        self.img_loading = ImageTk.PhotoImage(
            Image.open(files('cm.imgs').joinpath('camera_is_connecting.png'))
        )

        self.img_unavailable = ImageTk.PhotoImage(
            Image.open(files('cm.imgs').joinpath('camera_is_not_available.png'))
        )

        threading.Thread(target=self.connect_camera, daemon=True).start()
        threading.Thread(target=self.get_image_loop, daemon=True).start()
        threading.Thread(target=self.videoLoop, daemon=True).start()

    def connect_camera(self):
        try:
            self.vs = cv2.VideoCapture(self.url)
            time.sleep(1)
            if not self.vs.isOpened():
                self.camera_unavailable = True
        except Exception as e:
            print(f"[{self.cam_type}] Ошибка подключения камеры: {e}")
            self.camera_unavailable = True
        finally:
            self.connecting = False

    def get_image_loop(self):
        while not self.stopEvent.is_set():
            if self.vs and self.vs.isOpened():
                ret, frame = self.vs.read()
                if ret:
                    try:
                        frame = cv2.resize(frame, (self.video_width, self.video_height))
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(image)
                        self.tk_image = ImageTk.PhotoImage(image)
                    except Exception as e:
                        print(f"[{self.cam_type}] Ошибка обработки кадра: {e}")
                        self.tk_image = None
            time.sleep(0.05)

    def videoLoop(self):
        while True:
            if not self.can_show:
                time.sleep(0.05)
                continue

            image = (self.tk_image if self.tk_image is not None else
                     self.img_unavailable if self.camera_unavailable else
                     self.img_loading)

            if not hasattr(self, 'image_id') or self.image_id is None:
                self.image_id = self.canvas.create_image(
                    self.place_x, self.place_y, image=image)
                self.canvas.tag_raise(self.image_id)
                self.canvas.tag_bind(self.image_id, '<Button-1>', self.img_callback)
            else:
                try:
                    self.canvas.itemconfig(self.image_id, image=image)
                    self.canvas.tag_raise(self.image_id)
                    self.canvas.coords(self.image_id, self.place_x, self.place_y)
                except Exception as e:
                    print(f"[videoLoop] Ошибка при обновлении изображения: {e}")
                    self.image_id = None

            time.sleep(0.05)

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
            if self.vs:
                self.vs.release()
        except:
            pass
        self.root.quit()

    def play_video(self):
        self.can_show = True

    def stop_video(self):
        self.can_show = False
        if hasattr(self, 'image_id') and self.image_id is not None:
            self.canvas.delete(self.image_id)
            self.image_id = None
            #self._last_image_shown = None


def start_video_stream(root, canvas, xpos, ypos, v_width, v_height,
                       cam_login, cam_pass, cam_ip, zoomed_x, zoomed_y,
                       zoomed_video_width, zoomed_video_height,
                       cam_type=None,
                       cam_port=554,
                       zoom_callback_func=None, hide_callback_func=None):
    url = f"rtsp://{cam_login}:{cam_pass}@{cam_ip}:{cam_port}/Streaming/Channels/102"

    inst = PhotoBoothApp(url, root=root, canvas=canvas, width=v_width,
                         height=v_height, pos_x=xpos, pos_y=ypos,
                         zoomed_x=zoomed_x,
                         zoomed_y=zoomed_y,
                         root_zoom_callback_func=zoom_callback_func,
                         root_hide_callback_func=hide_callback_func,
                         cam_type=cam_type,
                         zoomed_video_width=zoomed_video_width,
                         zoomed_video_height=zoomed_video_height)
    return inst

