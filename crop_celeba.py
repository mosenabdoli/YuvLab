import numpy as np
import cv2
from pathlib import Path
import os
import shutil

path = 'E:\Sources\Face\data\celeba\images'
src_width = 1024
src_height = 1024
crp_width = 64
crp_height = 64
num_row = src_height // crp_height
num_col = src_width // crp_width

def main():
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.makedirs('output')
    files = os.listdir(path)
    num_files = len(files)
    # file = files[0]
    # img = cv2.imread(os.path.join(path, file))
    # crop_img = img[0:64, 0:64]
    # outpath = os.path.join('output', '00_' + file)
    # cv2.imwrite(outpath, crop_img)
    counter = 0
    for file in files:
        print(f"Processing {counter} of {len(files)}")
        counter = counter + 1
        for row in range(num_row):
            for col in range(num_col):
                if row == 0 or col == 0:
                    continue
                startx = col * crp_width
                endx = startx + crp_width
                starty = row * crp_height
                endy = starty + crp_height
                img = cv2.imread(os.path.join(path, file))
                crop_img = img[starty:endy, startx:endx]
                outpath = os.path.join('output', str(col) + "," + str(row) + '_' + file)
                cv2.imwrite(outpath, crop_img)
    # cv2.imshow("cropped", crop_img)
    # cv2.waitKey(0)
    # for file in files:
    #     print(file)

    return 0

if __name__ == '__main__':
    main()