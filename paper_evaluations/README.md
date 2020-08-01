# Evaluation files from the paper

Each method contains seperate ```.zip``` files for each configuration of the beta parameter. Included are results from the parameter optimization on the validation as well as the evaluation on the test set using the best parameter combination.

## Data sets

- [Kidney Boundaries](https://endovissub2017-kidneyboundarydetection.grand-challenge.org/)
- [NYU Depth V2](https://cs.nyu.edu/~silberman/datasets/nyu_depth_v2.html)
- [BSDS 500](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html)

## Naming consistency 

If you are following the custom data evaluation steps the corresponding folder names of step 5 and 6 are:

| Evaluation folder name | Folder name in custom data guide | Step |
|:----------------------:|:--------------------------------:|:----:|
|        adjusted        |     {method}_eval/{val/test}     |   5  |
|       aggregated       |  {method}_aggregated/{val/test}  |   6  |
|         results        |    {method}_results/{val/test}   |   6  |
