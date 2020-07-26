import cv2
import numpy as np
import os
import argparse
from scipy.io import loadmat
from scipy import ndimage
from skimage import morphology, measure
import pandas 
import glob
import ntpath

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def sde(ground_truth_frame, entry_frame):
	# skeleton_ground_truth = (ground_truth_frame == 255) * 1
	# skeleton_entry = (entry_frame == 255) * 1
	assert(ground_truth_frame.max() <= 1), f"Maximum is {ground_truth_frame.max()}"
	assert(entry_frame.max() <= 1), f"Maximum is {entry_frame.max()}"

	if np.sum(entry_frame) == 0 and np.sum(ground_truth_frame) > 0:
		h, w = entry_frame.shape[:2] 
		entry_frame[h // 2, w // 2] = 1

	if np.sum(ground_truth_frame) == 0 and np.sum(entry_frame) > 0:
		h, w = ground_truth_frame.shape[:2] 
		ground_truth_frame[h // 2, w // 2] = 1

	contour_ground_truth = ground_truth_frame == 1
	contour_entry = entry_frame == 1 

	#generate sdf from contours
	ground_truth_distance_transform = ndimage.distance_transform_edt(np.logical_not(ground_truth_frame))
	entry_frame_distance_transform = ndimage.distance_transform_edt(np.logical_not(entry_frame))
	#sum the sdf indexed by the contour for each and take average

	if np.sum(contour_entry) > 0:
		precision = np.sum( entry_frame_distance_transform[contour_ground_truth] ) / np.sum(entry_frame)
	else:
		precision = None

	if np.sum(contour_ground_truth) > 0:
		recall = np.sum( ground_truth_distance_transform[contour_entry] ) / np.sum(ground_truth_frame)
	else:
		recall = None

	score = None
	if precision is None and recall is None:
		score = 0
	elif precision is None:
		score = 3.0*recall/2
	elif recall is None:
		score = 3.0*precision/2
	else:
		score = (precision + recall)/2
	return (precision, recall, score)

def set_bounding_boxes_to_one(image):
	result = np.zeros(image.shape, dtype=np.uint8)
	image_labeled = measure.label(image, background=0)

	values = np.unique(image_labeled)
	for val in values[1:]:	# Skip background 
		pixels_of_label = (image_labeled == val) * 1
		slice_x, slice_y = ndimage.find_objects(pixels_of_label)[0]
		result[slice_x, slice_y] = 1	# Set bounding box area to 1 in result image

	return result

def iou_bounding_box(gt, pred):
	bb_gt = set_bounding_boxes_to_one(gt)
	bb_pred = set_bounding_boxes_to_one(pred)

	return iou_with_offset(bb_gt, bb_pred, offset=0)

def iou_with_offset(gt, pred, offset=0):
	dilated_gt = gt
	if offset > 0:
		# Dilate to add symmetric border around skeletonized gt
		selem = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
		for _ in range(0, offset):
			dilated_gt = morphology.binary_dilation(dilated_gt, selem=selem)

	true_positive_count = np.sum ( (dilated_gt == 1) & (pred == 1) )
	false_positive_count = np.sum ( (dilated_gt != 1) & (pred == 1) )
	false_negative_count = np.sum ( (gt == 1) & (pred != 1) )

	intersection = true_positive_count
	union = true_positive_count + false_negative_count + false_positive_count

	if intersection == 0 and union == 0:
		return 1
	if union == 0:
		return 0

	return intersection / union

def main(args):
	os.makedirs(args.output, exist_ok=True)

	ground_truth_images = glob.glob(os.path.join(args.ground_truth, "*.png"))
	ground_truth_lookup = dict()
	print("Loading ground truth...")
	for i, image in enumerate(ground_truth_images):
		print(f"\r{i + 1}/{len(ground_truth_images)}", end="")
		im = cv2.imread(image, 0)
		
		im[im > 0] = 1
		
		ground_truth_lookup[path_leaf(image).split(".")[0]] = [im]
	print("")

	ts = [x for x in range(0, 255) if x % 10 == 0]
	ps = [x for x in range(11)] + [x for x in range(20, 101) if x % 10 == 0]

	total = len(ts) * len(ps)
	count = 0
	print("Evaluating...")
	for t in ts:
		for p in ps:
			print(f"\r{count + 1}/{total}", end="")
			count += 1
			csv_name = f"t_{t}__p_{p}.csv"

			if os.path.exists(os.path.join(args.output, csv_name)):
				print(f"Skipping t={t}, p={p}")
				continue

			cols = ["name"]
			for x in range(args.num_subjects):
				cols.append(f"precision_{x}")
				cols.append(f"recall_{x}")
				cols.append(f"sde_{x}")
				cols.append(f"bbiou_{x}")
				for y in [0, 5, 10, 15, 20]:
					cols.append(f"iou_{y}_{x}")

			df = pandas.DataFrame(columns=cols)

			path_to_images = os.path.join(args.input, f"t_{t}", f"p_{p}")
			image_names = os.listdir(path_to_images)
			image_names = list(filter(lambda x: x.endswith(".png"), image_names))

			for image in image_names:
				predicted_image = cv2.imread(os.path.join(path_to_images, image), 0)
				predicted_image[predicted_image > 0] = 1

				if not image.split(".")[0] in ground_truth_lookup:
					name = image.split(".")[0]
					print(f"WARNING: Ground truth for image {name} does not exist!")
					continue

				gt_images = ground_truth_lookup[image.split(".")[0]]
				new_row = {
						"name": image
				}
				for subject in range(len(gt_images)):
					gt_image = gt_images[subject]
					gt_image[gt_image > 0] = 1
					precision, recall, sde_value = sde(gt_image, predicted_image)
					bbiou = iou_bounding_box(gt_image, predicted_image)
									
					new_row[f"precision_{subject}"] = precision
					new_row[f"recall_{subject}"] = recall
					new_row[f"sde_{subject}"] = sde_value
					new_row[f"bbiou_{subject}"] = bbiou

					for iou in [0, 5, 10, 15, 20]:
						offset_iou = iou_with_offset(gt_image, predicted_image, iou)
						new_row[f"iou_{iou}_{subject}"] = offset_iou
				
				df = df.append(new_row, ignore_index=True)
			df = df.set_index("name")
			df.to_csv(os.path.join(args.output, csv_name))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("-i", "--input", type=str, help="Top level folder of pruned images.")
	parser.add_argument("-gt", "--ground_truth", type=str, help="Folder containing ground truth edge images.")
	parser.add_argument("-o", "--output", type=str, help="Destination folder for evaluation csv files.")

	parser.add_argument("-n", "--num_subjects", type=int, help="Number of subjects that evaluated the ground truth data.")

	args = parser.parse_args()

	main(args)
