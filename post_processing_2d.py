import cv2
import numpy as np
import os
import argparse

from skimage import morphology
from multiprocessing import Pool

def load_image(path, threshold):
    im = cv2.imread(path, 0)
    im[im < threshold] = 0

    return im

def collect_image_names(path):
    files = os.listdir(path)
    files = list(filter(lambda x: x.endswith(".png"), files))

    return files

def process_image(params):    
    image_file, args = params

    im = load_image(os.path.join(args.input, image_file), args.threshold)
    
    im = morphology.skeletonize(im > 0)
    result = np.multiply(im, 255.0)

    cv2.imwrite(os.path.join(args.output, image_file), result)

def main(args):
    image_files = collect_image_names(args.input)

    if os.path.exists(args.output):
        already_processed_image_files = collect_image_names(args.output)
        for image in already_processed_image_files:
            image_files.remove(image)
    else:
        os.makedirs(args.output)

    if len(image_files) > 0:
        print(f"Processing {len(image_files)} files")
        thread_args = zip(image_files, [args] * len(image_files))

        p = Pool(args.num_threads)

        p.map(process_image, thread_args)
    else:
        print("Already processed all files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-i", "--input", type=str, help="Folder containing images to convert.")
    parser.add_argument("-o", "--output", type=str, help="Destination folder for postprocessed images.")
    parser.add_argument("-t", "--threshold", type=int, help="Filter threshold.")

    parser.add_argument("--num_threads", type=int, help="Number of preocessing threads.")
    
    args = parser.parse_args()

    main(args)
