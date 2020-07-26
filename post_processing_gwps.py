import cv2
import numpy as np
import os
import argparse

from skimage.morphology import skeletonize
from multiprocessing import Pool

def connectivity_number_8(mat):
    POS = [(1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2)]
    
    op = np.copy(mat)
    op[op > 0] = 1
    
    result = 0
    for k in [0, 2, 4, 6]:
        elem_k = op[POS[k]]
        elem_k_1 = op[POS[(k + 1) % 8]]
        elem_k_2 = op[POS[(k + 2) % 8]]
        
        x_k = 1 - elem_k
        x_k_1 = 1 - elem_k_1
        x_k_2 = 1 - elem_k_2
        
        result += x_k - (x_k * x_k_1 * x_k_2)
    
    return result   

def load_image(path, threshold):
    im = cv2.imread(path, 0)
    im[im < threshold] = 0

    return im

def connected_components(mat):
    ret, labels = cv2.connectedComponents(mat.astype(np.uint8))
    component = np.zeros_like(mat)
    
    comp_labels = set(labels[labels > 0])
    # print(len(comp_labels))

    for label in comp_labels:
        component[:] = 0
        if len(mat[labels == label]) > 50:
            component[labels == label] = mat[labels == label]
            yield component

def iteratively_remove(mat):
    result = np.copy(mat)
    unique_values = list(set(mat[mat > 0]))
    sorted(unique_values)

    for value in unique_values:
        indices_to_check = [tuple(x) for x in list(np.argwhere(result == value))]
        
        nb_mat = np.copy(result)
        indices_list = np.array(indices_to_check)
        nb_mat[indices_list[:, 0], indices_list[:, 1]] = 0

        for index in indices_to_check:
            nb_mat[index] = 1
            
            nb_pixels = get_neighbourhood(nb_mat, index)

            if np.sum(nb_pixels) > 1 and connectivity_number_8(nb_pixels) == 1:
                result[index] = 0

    return result

def get_neighbourhood(mat, index):
    DIRS = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, 1), (1, -1), (-1, -1), (1, 1)]
    max_y, max_x = mat.shape
    result = np.zeros((3,3))
    
    for dir in DIRS:
        nb_index = (index[0] + dir[0], index[1] + dir[1])
        if not exists(nb_index, max_y, max_x):
            continue
        if mat[nb_index] > 0:
            result[(1 + dir[0], 1 + dir[1])] = 1
        
    return result

def exists(index, ny, nx):
    return (0 <= index[0] < ny) and (0 <= index[1] < nx)

def has_inf(mat):
    return np.isinf(mat).any()

def calc_gwdt(mat):
    DIRS = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    #DIRS = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    result = np.zeros_like(mat)
    result[mat > 0] = np.inf
    
    max_y, max_x = result.shape
    neighbours = np.zeros(len(DIRS))
    
    candidate_indices = np.argwhere(np.isinf(result))
    
    while len(candidate_indices):
        round_result = np.copy(result)

        next_round_candidates = []
        for index in candidate_indices:   
            index = tuple(index)
            if round_result[index] != np.inf:
                continue
            
            new_indices = []
            for i, dir in enumerate(DIRS):
                nb = (index[0] + dir[0], index[1] + dir[1])
                if not exists(nb, max_y, max_x):
                    neighbours[i] = np.inf
                    continue
                
                if result[nb] == np.inf:
                    new_indices.append(nb)
                neighbours[i] = result[nb]
                
            nb_min_arg = np.argmin(neighbours)
            if neighbours[nb_min_arg] == np.inf:
                continue
                
            next_round_candidates.extend(new_indices)
            
            target_dir = DIRS[nb_min_arg]
            nb_index = (index[0] + target_dir[0], index[1] + target_dir[1])
            round_result[index] = mat[index] + result[nb_index]
            
        candidate_indices = next_round_candidates

        result = round_result
    return result

def collect_image_names(path):
    files = os.listdir(path)
    files = list(filter(lambda x: x.endswith(".png"), files))

    return files

def process_image(params):    
    image_file, args = params

    im = load_image(os.path.join(args.input, image_file), args.threshold)
    im_result = np.zeros_like(im)
    
    for connected_component in connected_components(im):
        gwdt = calc_gwdt(im.astype(np.float)).astype(np.int)
        edge = iteratively_remove(gwdt)
        im_result[edge > 0] = 255

    cv2.imwrite(os.path.join(args.output, image_file), im_result)

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
