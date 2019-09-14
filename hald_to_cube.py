from __future__ import print_function, division

import math
import sys
import argparse
import os

from PIL import Image


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="Path to input file or input directory. "
                                      "If directory, all files are converted recursively.")
    parser.add_argument('output', help="Path to output file or directory, depending on whether input "
                                       "is file or directory. If input is file and output is directory, output file"
                                       " is named like input and placed in the output directory.")
    parser.add_argument('--overwrite', help="overwrite existing output file(s)", action="store_true")
    
    args = parser.parse_args()

    input = args.input
    output = args.output
    overwrite = args.overwrite
    
    if os.path.isdir(input):
        if os.path.isdir(output) or not os.path.exists(output):
            convert_directory(input, output, overwrite)
        else:
            raise ValueError("If input is directory, output must be directory, too.")
    elif os.path.isfile(input):
        convert_file(input, output, overwrite)
    else:
        raise ValueError("annot open input")

def convert_directory(input, output, overwrite):
    for dir_input, dirs, files in os.walk(input):
        # get path relative to input directory
        if dir_input != input:
            dir_input_relative = os.path.relpath(dir_input, input)
            
            print(dir_input_relative)
    
            # construct the path in the output directory
            dir_output = os.path.join(output, dir_input_relative)

        else:
            dir_output = output

        # if directory does not exist, create it
        if not os.path.exists(dir_output):
            os.mkdir(dir_output)

        # convert all files
        for file in files:
            filepath = os.path.join(dir_input, file)
            convert_file(filepath, dir_output, overwrite)

def convert_file(input, output, overwrite):
    try:
        in_ = Image.open(input)
    except:
        return
    
    if os.path.isdir(output):
        filename = os.path.basename(input)
        filename_no_extension = os.path.splitext(filename)[0]
        file_output = os.path.join(output, '{}.cube'.format(filename_no_extension))
    else:
        file_output = output

    if os.path.exists(file_output):
        if overwrite:
            os.remove(file_output)
        else:
            raise ValueError("Output file exists")

    w, h = in_.size
    if w != h:
        print('HALD input is not square.', file=sys.stderr)
        return
        
    steps = int(round(math.pow(w, 1/3)))
    if steps**3 != w:
        print('HALD input size is invalid: %d is not a cube.' % w, file=sys.stderr)

    print('%d steps -> %d values' % (steps, steps**6), file=sys.stderr)

    out = open(file_output, 'w')
    out.write('LUT_3D_SIZE %d\n' % (steps ** 2))
    out.write('DOMAIN_MIN 0.0 0.0 0.0\n')
    out.write('DOMAIN_MAX 1.0 1.0 1.0\n')

    for pixel in in_.getdata():
        r, g, b = pixel[:3]
        out.write('%f %f %f\n' % (r / 255.0, g / 255.0, b / 255.0))


if __name__ == '__main__':
    main()
