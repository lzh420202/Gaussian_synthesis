# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import subprocess

import torch


def parse_args():
    """Parse parameters."""
    parser = argparse.ArgumentParser(
        description='Process a checkpoint to be published')
    parser.add_argument('in_file', help='input checkpoint filename')
    parser.add_argument('out_file', help='output checkpoint filename')
    args = parser.parse_args()
    return args


def process_checkpoint(in_file, out_file):
    """Only inference related parameters are retained.

    Args:
        in_file (str): Filename of input checkpoint.
        out_file (str): Filename of output checkpoint.
    """
    checkpoint = torch.load(in_file, map_location='cpu')
    # remove optimizer for smaller file size
    if 'optimizer' in checkpoint:
        del checkpoint['optimizer']
    # if it is necessary to remove some sensitive data in checkpoint['meta'],
    # add the code here.
    if torch.__version__ >= '1.6':
        torch.save(checkpoint, out_file, _use_new_zipfile_serialization=False)
    else:
        torch.save(checkpoint, out_file)
    sha = subprocess.check_output(['sha256sum', out_file]).decode()
    if out_file.endswith('.pth'):
        out_file_name = out_file[:-4]
    else:
        out_file_name = out_file
    final_file = out_file_name + f'-{sha[:8]}.pth'
    subprocess.Popen(['mv', out_file, final_file])
    return final_file


def main():
    """Main function of publish model."""
    args = parse_args()
    final_file = process_checkpoint(args.in_file, args.out_file)
    print(f'\n{final_file}\n')


if __name__ == '__main__':
    main()
