import cv2
import os
from multiprocessing import Pool
import numpy as np
import argparse

def convert_to_binary(image):
	result = np.zeros_like(image)
	result[image > 0] = 1
	return result.astype(np.uint8)

def load_image(path):
	im = cv2.imread(path, 0)
	return im

def collect_image_names(path):
	files = os.listdir(path)
	files = list(filter(lambda x: x.endswith(".png"), files))

	return files

def process_image(params):
	base_structuring_elements = [
		np.array([
			[1, 1, 1],
			[0, 1, 0],
			[-1, -1, -1]
		]),
		np.array([
			[-1, 0, 0],
			[-1, 1, -1],
			[-1, -1, -1]
		])
	]
    
	structuring_elements = []
	for elem in base_structuring_elements:
		for i in range(4):
			structuring_elements.append(np.rot90(elem, k=i))

	image_file, args = params
	im = load_image(os.path.join(args.input, image_file))

	diag = np.sqrt(np.sum(np.asarray(im.shape[:2]) ** 2))
	num_iterations = int((args.percentage / 100) * diag)

	bin_im = convert_to_binary(im)
	original_bin_im = convert_to_binary(im)

	for _ in range(num_iterations):
		dst = np.zeros_like(im)
		for elem in structuring_elements:
			dst = np.logical_or(dst, cv2.morphologyEx(bin_im, cv2.MORPH_HITMISS, elem))
		bin_im[dst > 0] = 0

	for _ in range(num_iterations):
		dst = np.zeros_like(im)
		for elem in structuring_elements:
			dst = np.logical_or(dst, cv2.morphologyEx(bin_im, cv2.MORPH_HITMISS, elem))
		dst = cv2.morphologyEx(dst.astype(np.uint8), cv2.MORPH_DILATE, np.ones((3,3)))
		dst = np.logical_and(dst, original_bin_im).astype(np.uint8)
		bin_im[dst > 0] = 1

	bin_im[bin_im > 0] = 255

	cv2.imwrite(os.path.join(args.output, image_file), bin_im)

def main(args):
	image_files = collect_image_names(args.input)
	os.makedirs(args.output, exist_ok=True)

	thread_args = zip(image_files, [args] * len(image_files))

	p = Pool(args.num_threads)

	p.map(process_image, thread_args)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("-i", "--input", type=str, help="Folder containing images to prune.")
	parser.add_argument("-o", "--output", type=str, help="Destination folder for pruned images.")
	parser.add_argument("-p", "--percentage", type=int, help="Percentage of image length")
	parser.add_argument("--num_threads", type=int, help="Number of processing threads")

	args = parser.parse_args()

	main(args)
