# Introducing computational strategies to improve edge creation from predicted object boundaries

This repository contains the code and evaluation results for the paper: ...
If you adapt, remix, transform, or build upon the material, please cite the published paper.

## Evaluation results from the paper

All evaluations that were referenced in the paper are available as raw ```.csv``` and ```.txt``` files in ```paper_evaluations/ ```.

## Running an evaluation on custom data

The following example steps outline how an edge creation problem can be evaluated using our proposed pipeline:
1. Requirements
- Python 3
  - OpenCV
  - scipy
  - scikit-image
  - Pandas

2. Put the non post-processed boundary predictions and the ground truth edges into seperate folders. The ground truth data can be in the form of images or ```.mat``` files following the [BSDS 500](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html) structure. Boundary predictions should be images. For both the predictions and the ground truth a 0 indicates background; otherwise the pixel contributes to a boundary or edge.
```
.
├── my_method
    ├── predictions
    |   ├── train
    |   ├── val
    |   └── test
    └── ground_truth
        ├── train
        ├── val
        └── test
```
3. Find the best parameters for alpha, beta and gamma by evaluating the validation set. This is achieved by first running ```post_processing_gwps.py```, ```post_processing_2d.py``` and ```post_processing_3d.py``` on the validation set predictions for different threshold values ```-t``` (corresponds to parameter alpha). 
```gwps```, ```2d```, ```3d``` in filenames correspond to parameter beta.
```
python post_processing_gwps.py -i my_method/predictions/val -o parameter_search/gwps/val -t 0
...
python post_processing_gwps.py -i my_method/predictions/val -o parameter_search/gwps/val -t 250

python post_processing_2d.py -i my_method/predictions/val -o parameter_search/2d/val -t 0
...
python post_processing_2d.py -i my_method/predictions/val -o parameter_search/2d/val -t 250

python post_processing_3d.py -i my_method/predictions/val -o parameter_search/3d/val -t 0
...
python post_processing_3d.py -i my_method/predictions/val -o parameter_search/3d/val -t 250
``` 

4. Prune the post-processed images by running ```prune.py``` for different values for ```-p``` (corresponds to parameter gamma).
``` 
python prune.py -i parameter_search/gwps/val/t_0 -o parameter_search/gwps_pruned/val/t_0 -p 0
...
python prune.py -i parameter_search/gwps/val/t_0 -o parameter_search/gwps_pruned/val/t_0 -p 100
``` 
This needs to be repeated for all values of ```-t``` chosen in the previous step by appending ```/t_{value}``` to the output paths that become the input paths for this step.

5. Run the evaluation script on each post-processing method to determine the best parameter combination. Use the parameter ```-n``` to set the number of subjects that evaluated the ground truth data (Default = 1; use 1 for ground truth image data; only use values > 1 for BSDS 500 like ```.mat``` ground truth files)
```
python evaluate.py -i parameter_search/gwps_pruned/val -o parameter_search/gwps_eval/val -gt my_method/ground_truth/val
python evaluate.py -i parameter_search/2d_pruned/val -o parameter_search/2d_eval/val -gt my_method/ground_truth/val
python evaluate.py -i parameter_search/3d_pruned/val -o parameter_search/3d_eval/val -gt my_method/ground_truth/val
```

6. The raw ```.csv``` evaluation files need to be processed further to determine the final metrics by running ```aggregate_evaluations.py``` and ```evaluate_aggregations.py``` on each method. Use parameter ```-n``` to set the number of subjects that evaluated the ground truth data (for details see step 5).
```
python aggregate_evaluations.py -i parameter_search/gwps_eval/val -o parameter_search/gwps_aggregated/val
python evaluate_aggregations.py -i parameter_search/gwps_aggregated/val -o parameter_search/gwps_results/val --name GWPS

python aggregate_evaluations.py -i parameter_search/2d_eval/val -o parameter_search/2d_aggregated/val
python evaluate_aggregations.py -i parameter_search/2d_aggregated/val -o parameter_search/2d_results/val --name 2D

python aggregate_evaluations.py -i parameter_search/3d_eval/val -o parameter_search/3d_aggregated/val
python evaluate_aggregations.py -i parameter_search/3d_aggregated/val -o parameter_search/3d_results/val --name 3D
```

7. Find the final results for the evaluation metrics for each method in:
```
parameter_search/gwps_results/val/overview.csv
parameter_search/2d_results/val/overview.csv
parameter_search/3d_results/val/overview.csv
```
These csv files have the following columns: alpha,gamma,SDE. Compare the best SDE value from each of the ```overview.csv``` files to determine the best method (parameter beta). In the ```{method}_aggregated``` folder (see step 6) of the best method find the ```t_{value}__p_{value}.txt``` file for detailed results regarding IoU-Box, mean, median and std. deviation.

8. Start again from step 2 and use the best parameters for alpha, beta and gamma on the test set.

### Custom parameter search granularity

Currently all scripts are build to process the parameter search granularity as described in the paper. To use a custom granularity find the following lines and change the parameter values for the variable ```ts``` (corresponds to thresholding, i.e. alpha) and ```ps``` (corresponds to pruning, i.e. gamma).

In ```evaluate.py``` at line 114 and 115:
```
ts = [x for x in range(0, 255) if x % 10 == 0]
ps = [x for x in range(11)] + [x for x in range(20, 101) if x % 10 == 0]
```
In ```aggregate_evaluations.py``` at line 11 and 12.

In ```evaluate_aggregations.py``` at line 13 and 14.

# License

This work is available under an Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). This is a human-readable summary of (and not a substitute for) the license. Disclaimer. You are free to:
```
Share — copy and redistribute the material in any medium or format
Adapt — remix, transform, and build upon the material

The licensor cannot revoke these freedoms as long as you follow the license terms.
```
Under the following terms:
```
Attribution — You must give appropriate credit, provide a link to the
license, and indicate if changes were made. You may do so in any reasonable
manner, but not in any way that suggests the licensor endorses you or your use.

NonCommercial — You may not use the material for commercial purposes.

ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
```
Notices:
```
You do not have to comply with the license for elements of the material in the public domain or where your use is permitted by an applicable exception or limitation.
No warranties are given. The license may not give you all of the permissions necessary for your intended use. For example, other rights such as publicity, privacy, or moral rights may limit how you use the material.
```
