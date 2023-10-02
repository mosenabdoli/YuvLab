import numpy as np
import cv2
from pathlib import Path
import math
import os
import shutil

from plotter import *
from utils import *

class VideoYUV:
    def __init__(self, in_filename, size, label=""):
        if not os.path.exists('output'):
            os.makedirs('output')
        if os.path.exists(os.path.join('output', label)):
            shutil.rmtree(os.path.join('output', label))
        os.mkdir(os.path.join('output', label))
        out_filename = in_filename.replace('\\','/')
        idx = out_filename.rfind('/')
        out_filename = out_filename[idx + 1: -4] + '_' + label + ".yuv"
        self.out_filename = os.path.join('output', label, out_filename)
        if os.path.exists(self.out_filename):
            os.remove(self.out_filename)
            file = Path(self.out_filename)
            file.touch()
        self.height, self.width = size
        self.frame_len = int(self.width * self.height * 3 / 2)
        self.luma_len = int(self.width * self.height)
        self.chroma_len = int(self.width * self.height / 4)
        self.in_file = open(in_filename, 'rb')
        self.luma_shape = (self.height, self.width)
        self.chroma_shape = (int(self.height / 2), int(self.width / 2))

    def read_raw(self):
        try:
            raw = self.in_file.read(self.frame_len)
            yuv = np.frombuffer(raw, dtype=np.uint8)
            y = yuv[0 : self.luma_len]
            y = y.reshape(self.luma_shape)
            u = yuv[self.luma_len : self.luma_len + self.chroma_len]
            u = u.reshape(self.chroma_shape)
            v = yuv[self.luma_len + self.chroma_len : self.luma_len + 2 * self.chroma_len]
            v = v.reshape(self.chroma_shape)
        except Exception as e:
            print("error")
            return False, None, None, None
        return True, y, u, v

    def read(self):
        ret, y, u, v = self.read_raw()
        if not ret:
            return ret, y, u, v
        return ret, y, u, v

    def write(self, yuv, path, right):
        if path:
            self.write_raw(yuv, path, right)
        else:
            self.write_raw(yuv, self.out_filename, right)
        return

    def write_raw(self, yuv, path, right):
        self.out_file = open(path, right)
        try:
            self.out_file.write(yuv)
        except Exception as e:
            print(e)
            return False, None

    def play(self):
        while 1:
            ret, framey, frameu, framev = self.read()
            if ret:
                cv2.imshow("frame", frameu)
                cv2.waitKey(30)
            else:
                break
            if cv2.getWindowProperty("frame", cv2.WND_PROP_VISIBLE) < 1:
                break
        cv2.destroyAllWindows()

    def extract_frame(self, frame_idx):
        cur_idx = 0
        self.in_file.seek(frame_idx * (self.luma_len + 2 * self.chroma_len))
        ret, framey, frameu, framev = self.read() # dump or seek instead
        if not ret:
            print(f"Error occured at frame {cur_idx}")
            exit(0)
        self.in_file.seek(0)
        return framey, frameu, framev

    def frame_crop(self, fully, fullu, fullv, x, y, w, h):
        cropy = fully[y:y+h,x:x+w]
        xc = x // 2; yc = y // 2; wc = w // 2; hc = h // 2
        cropu = fullu[yc:yc+hc,xc:xc+wc]
        cropv = fullv[yc:yc+hc,xc:xc+wc]
        cropy = cropy.copy(order='C')
        cropu = cropu.copy(order='C')
        cropv = cropv.copy(order='C')
        return cropy, cropu, cropv

    def resample(self, in_signal, factor):
        in_dim = in_signal.shape
        out_dim = (int(in_dim[1] * factor), int(in_dim[0] * factor))
        out_signal = cv2.resize(in_signal, out_dim, interpolation = cv2.INTER_AREA)
        return out_signal

    def writeRgb(self, y, u, v, filename=''):
        yvu = cv2.merge((y, v, u))
        bgr = cv2.cvtColor(yvu, cv2.COLOR_YCrCb2BGR)
        cv2.imwrite(self.out_filename[0:-4] + '_' + filename + '.png', bgr)

    def compare(self, args):
        print(f"Comparing frame:{args.ref_frame} of {args.ref} with frame:{args.test_frame} of {args.test}")
        size = (args.height, args.width)
        cap_ref = VideoYUV(args.ref, size)
        frame_refy, _, _ = cap_ref.extract_frame(args.ref_frame)
        cap_test = VideoYUV(args.test, size)
        frame_testy, _, _ = cap_test.extract_frame(args.test_frame)
        diff = frame_refy.astype(int) - frame_testy.astype(int)
        diff = abs(diff)
        max_val = diff.max()
        idx = diff.argmax()
        warp = True
        i = 1
        if warp:
            par = 1.5
            warped = diff / max_val
            warped = 2 * warped - (np.power(warped, par)) * max_val
            warped = warped.astype(np.uint8)
            heatmap2d(warped, i)
            i = i + 1
        print(f"Max distortion is {max_val} which happens at {math.floor(idx / args.width)},{idx % args.width}")
        diff = diff.astype(np.uint8)
        heatmap2d(diff, i)
        i = i + 1
        hist(diff, i)
        plt.show()
    
    def show(self, args):
        frame = self.extract_frame(args.ref_frame)
        cv2.imshow("frame", frame)
        cv2.waitKey(10000)

    def crop(self, args, params):
        x = params.get('x')
        y = params.get('y')
        crop_wdt = params.get('width')
        crop_hgt = params.get('height')
        self.out_filename = change_outfilename_crop(self.out_filename, crop_wdt, crop_hgt)

        cur_frame = params.get('f_start')
        permission = 'wb'
        while cur_frame <= params.get('f_end'):
            framey, frameu, framev = self.extract_frame(cur_frame)
            cropy, cropu, cropv = self.frame_crop(framey, frameu, framev, x, y, crop_wdt, crop_hgt)
            self.write(cropy, False, permission)
            if permission == 'wb':
                permission = 'ab'
            ucropu = self.resample(cropu, 2)
            ucropv = self.resample(cropv, 2)
            self.write(cropu, False, 'ab')
            self.write(cropv, False, 'ab')
            cur_frame += 1

        self.writeRgb(cropy, ucropu, ucropv)
    
    def resize(self, args):
        framey, frameu, framev = self.extract_frame(args.ref_frame)
        uy = self.resample(framey, args.resize_factor)
        uu = self.resample(frameu, args.resize_factor)
        uv = self.resample(framev, args.resize_factor)
        self.write(uy, False, 'wb')
        self.write(uu, False, 'ab')
        self.write(uv, False, 'ab')
    
    def convert_png(self, params):
        cur_frame = params.get('f_start')
        while cur_frame <= params.get('f_end'):
            framey, frameu, framev = self.extract_frame(cur_frame)
            uframeu = self.resample(frameu, 2)
            uframev = self.resample(framev, 2)
            cur_frame += 1
            filename = 'converted-' + str(cur_frame)
            self.writeRgb(framey, uframeu, uframev, filename)