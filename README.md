# Introducing computational strategies to improve edge creation from predicted object boundaries

This repository contains the code and evaluation results for the paper: ...
If you adapt, remix, transform, or build upon the material, please cite the published paper.

## Evaluation results from the paper

All evaluations that were referenced in the paper are available as raw ```.csv``` and ```.txt``` files in ```paper_evaluations/ ```.

## Running an evaluation on custom data

The following example steps outline how an edge creation problem can be evaluated using our proposed pipeline:
1. Requirements
...

2. Put the non post-processed boundary predictions and the ground truth edges into seperate folders. The ground truth data can be in the form of images or ```.mat``` files following the [BSDS 500](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html) structure. Boundary predictions should be images. For both the predictions and the ground truth a 0 indicates background; otherwise the pixel contributes to a boundary or edge.
```
.
├── my_method
|   ├── predictions
|       ├── train
|       ├── val
|       ├── test
|   ├── ground_truth
|       ├── train
|       ├── val
|       ├── test
```
3. Find the best parameters for alpha, beta and gamma by evaluating the validation set. This is achieved by first running ```post_processing_gwps.py```, ```post_processing_2d.py``` and ```post_processing_3d.py``` on the validation set predictions for different threshold values ```-t``` (corresponds to alpha). 
```gwps```, ```2d```, ```3d``` in filenames correspond to beta.
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

4. Prune the post-processed images by running ```prune.py``` for different values for ```-p``` (corresponds to gamma).
``` 
python prune.py -i parameter_search/gwps/val/t_0 -o parameter_search/gwps_pruned/val/t_0 -p 0
...
python prune.py -i parameter_search/gwps/val/t_0 -o parameter_search/gwps_pruned/val/t_0 -p 100
``` 
This needs to be repeated for all values of ```-t``` chosen in the previous step by appending ```/t_{value}``` to the output paths that become the input paths for this step.

5. Run the evaluation script on each post-processing method to determine the best parameter combination.
```
python evaluate.py -i parameter_search/gwps_pruned/val -o parameter_search/gwps_eval/val -gt my_method/ground_truth/val
python evaluate.py -i parameter_search/2d_pruned/val -o parameter_search/2d_eval/val -gt my_method/ground_truth/val
python evaluate.py -i parameter_search/3d_pruned/val -o parameter_search/3d_eval/val -gt my_method/ground_truth/val
```

6. The raw ```.csv``` evaluation files need to be processed further to determine the final metrics by running ```aggregate_evaluations.py``` and ```evaluate_aggregations.py``` on each method.
```
python aggregate_evaluations.py -i parameter_search/gwps_eval/val -o parameter_search/gwps_aggregated/val
python evaluate_aggregations.py -i parameter_search/gwps_aggregated/val -o parameter_search/gwps_results/val

python aggregate_evaluations.py -i parameter_search/2d_eval/val -o parameter_search/2d_aggregated/val
python evaluate_aggregations.py -i parameter_search/2d_aggregated/val -o parameter_search/2d_results/val

python aggregate_evaluations.py -i parameter_search/3d_eval/val -o parameter_search/3d_aggregated/val
python evaluate_aggregations.py -i parameter_search/3d_aggregated/val -o parameter_search/3d_results/val
```

7. Find the final results for the evaluation metrics for each method in:
```
parameter_search/gwps_results/val/overview.csv
parameter_search/2d_results/val/overview.csv
parameter_search/3d_results/val/overview.csv
```
These csv have the following columns: alpha,gamma,SDE. Compare the best SDE value from each of the ```overview.csv``` files to determine the best method (beta parameter). In the aggregated folder (see step 6) of the best method find the file ```t_{value}__p_{value}``` for detailed results regarding IoU-Box, mean, median and std. deviation.

8. Start again from step 2 and use the best parameters for alpha, beta and gamma on the test set.
