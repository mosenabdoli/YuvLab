import cv2
from pathlib import Path
import os
import shutil
from VideoYUV import *


path = 'C:\\Users\\mabdoli\\Ubuntu\\Code\\AIVC\\raw_videos'
patch_size = 64


def main():
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.makedirs('output')
    files = os.listdir(path)

    for file in files:
        if not file.endswith('yuv'):
            continue

        name, num_frame, width, height = getSeqInfo(file)
        size = (height, width)
        filepath = os.path.join(path, file)
        cap = VideoYUV(filepath, size)

        for frame in range(num_frame):
            y = 0
            framey, frameu, framev = cap.extract_frame(frame)
            while y + patch_size <= height:
                x = 0
                while x + patch_size <= width:
                    cropy, cropu, cropv = cap.crop(framey, frameu, framev, x, y, patch_size, patch_size)
                    outfile = name + '_' + str(frame) + '_' + str(y) + ',' + str(x) + '.yuv'
                    outpath = os.path.join('output', outfile)
                    cap.write(cropy, outpath, 'wb')
                    ucropu = cap.upsample(cropu, 2)
                    ucropv = cap.upsample(cropv, 2)
                    cap.write(ucropu, outpath, 'ab')
                    cap.write(ucropv, outpath, 'ab')
                    x = x + patch_size
                y = y + patch_size
        print(f"{name}: Frame {frame} finished")



def getSeqInfo(file):
    idx = file.find('_')
    name = file[0:idx]
    print(name)
    resolution = file[idx + 1:]
    idx = resolution.find('_')
    resolution = resolution[0:idx]
    idx = resolution.find('x')
    width = int(resolution[0:idx])
    height = resolution[idx + 1:]
    height = int(height.replace('p', ''))
    size = os.path.getsize(os.path.join(path, file))
    size = size / (1.5 * width * height)
    if int(size) != size:
        print(f'Possibly wrong num frames: {size}')
    else:
        num_frame = int(size)
        if num_frame % 10 == 1:
            num_frame = num_frame - 1 # copy-right frame
    return name, num_frame, width, height

if __name__ == '__main__':
    main()
