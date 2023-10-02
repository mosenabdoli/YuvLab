import shutil
import argparse
import json
import sys

from plotter import *
from VideoYUV import *
from utils import *

parser = argparse.ArgumentParser(description="Read and compare YUV signals")
parser.add_argument('--mode', type=str, metavar='', help='Modes: compare, play')
parser.add_argument('--ref', type=str, metavar='', help='Address of the reference YUV file')
parser.add_argument('--test', type=str, metavar='', help='Address of the test YUV file')
parser.add_argument('--label', type=str, default='', metavar='', help='A label describing the operation')
parser.add_argument('--ref_frame', type=int, default=0, metavar='', help='Frame index from the reference YUV file')
parser.add_argument('--test_frame', type=int, default=1, metavar='', help='Frame index from the test YUV file')
parser.add_argument('-W', '--width', type=int, metavar='', help='Width of YUV file in pixels')
parser.add_argument('-H', '--height', type=int, metavar='', help='Height of YUV file in pixels')
parser.add_argument('--resize_factor', type=float, default=1.0, metavar='', help='Height of YUV file in pixels')

def main():
    # Parameters
    with open('params.json') as config_file:
        params = json.load(config_file)
    args = parser.parse_args()
    overwrite_params(params, args)

    # YUV object
    size = (args.height, args.width)
    cap = VideoYUV(args.ref, size, args.label)
    
    # Function
    print(f'Function: {args.mode}')

    if args.mode == 'compare':
        cap.compare(args)
    elif args.mode == 'play':
        cap.play()
    elif args.mode == 'show':        
        cap.show(args)
    elif args.mode == 'crop':
        cap.crop(args, params)
    elif args.mode == 'resize':
        cap.resize(args)
    elif args.mode == 'convert-png':
        cap.convert_png(params)
    else:
        print(f'mode {args.mode} not supported!\nEXITING...')
        exit(0)

if __name__ == "__main__":
    main()
