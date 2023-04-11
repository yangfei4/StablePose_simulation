# StablePose_simulation
This repo aims to collect stable pose candidates for a given CAD models.

*NOTE:* Mass centers of objects have great impact on this experiment. In `Blender_proc2`, the definition of mass center is same as origin point of `.obj` file.
However, the origin point of `.obj` file is usually set to the center of the geometry by default, which is not mathching with real mass center. 
So, please make sure you have checked/updated the mass center of your `.obj` files before running the experiment. You may get the correct mass center information from original `.STP` files or other ways.


## Environment :atom:

*The following instructions assume that you have [anaconda][conda] installed and configured*

```
conda env create -f environment.yml
conda activate blender_proc
blenderproc pip install tqdm
```

## Check .mtl file
Make sure `tagboard_21x21x1cm.mtl` is in the same folder as `apriltag_board.png`, and the mtl file ends with `map_Kd apriltag_board.png`

## Run Commands :rocket:	
Assume you have put all cad models(.obj) under PATH/TO/CAD/MODELS. Then run:

```
bash scripts/pose_exp PATH/TO/CAD/MODELS PATH/TO/OUTPUT/DIR
```
E.g.:  `bash scripts/pose_exp ./CAD_model/models ./pose_exp`

## Results processing :floppy_disk:
Please follow the guidline in [save_pose.ipynb](https://urldefense.com/v3/__https://github.com/yangfei4/StablePose_simulation/blob/main/save_pose.ipynb__;!!DZ3fjg!-o-pKfulG6fhaTC2n8gX67C3nUFhSSwKGefaxhrYf74ze2Fsd0hnjrn-daN_jPA3OSyHLGbPpfjrknHlBKZ8SGlDibOc$ ).

## Render simulation process :film_projector:	
Before your simulation, twists the following lines in `simulation_demo.py`. The settings below will only generate one image. To produce 20 images, we need to make sure the memory is large enough to handle the rendering of 20 images of more than 12MB size.(8Gb DDR3 is not enough for such a job)
```python
# This will make the renderer render the first frame of the simulation
bproc.utility.set_keyframe_render_interval(frame_start=1, frame_end=2)

###############################################################
# render the whole pipeline and save them as PNGs
###############################################################
bproc.renderer.set_max_amount_of_samples(1)
bproc.renderer.set_noise_threshold(1)
bproc.renderer.set_cpu_threads(0)
```
Run the following script:
```
bash scripts/render_sim PATH/TO/CAD/MODELS PATH/TO/OUTPUT/DIR
```
E.g.:  `bash scripts/render_sim ./CAD_model/models ./pose_exp`
After running above command, a set of rendered images will be save in your output dictionary.
In sample script, we rendered first 20 frames of the simulation process as 20 .png images.

## Generate video from rendered images  :vhs:	
```
python generate_video.py PATH/TO/IMAGES
```
E.g.:  `python generate_video.py ./pose_exp/images`

![](./simulation_demo.gif)

[conda]: https://urldefense.com/v3/__https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html__;!!DZ3fjg!-o-pKfulG6fhaTC2n8gX67C3nUFhSSwKGefaxhrYf74ze2Fsd0hnjrn-daN_jPA3OSyHLGbPpfjrknHlBKZ8SCrVLMxb$ 
