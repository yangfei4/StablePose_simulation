###########################################
# This script is for visualizing simulation
###########################################

import blenderproc as bproc
import argparse
import numpy as np
import bpy
import time

from pathlib import Path
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('cad_models', default="./CAD_model/models",help="Path to the object file containing USB type-c components.")
parser.add_argument('tag_board', default="./CAD_model/tagboard_21x21x1cm.obj",help="Path to the object file containing the tagboard.")
parser.add_argument('output_dir', nargs='?', default="./pose_exp/", help="Path to where the final files will be saved ")
args = parser.parse_args()
bproc.init()

def pipeline_init():
    ###############################################################
    # Set the camera pose same as world frame, located in origin
    ###############################################################
    cam_k = np.array([[21627.734375, 0, 2353.100109], 
                      [0, 21643.369141, 1917.666411],
                      [0, 0, 1]])
    W, H = int(5472), int(3648)
    bproc.camera.set_resolution(W, H)
    bproc.camera.set_intrinsics_from_K_matrix(cam_k, W, H)
    
    cam_pose = np.array([[1, 0, 0,  0],
                        [0, 1, 0,  0],
                        [0, 0, 1,  2],
                        [0, 0, 0,  1]])

    bproc.camera.add_camera_pose(cam_pose)
    cam_R = cam_pose[0:3, 0:3]

    ###############################################################
    # Define a point light
    ###############################################################
    light = bproc.types.Light()
    light.set_type("POINT")
    light.set_location([0, 0, 2])
    light.set_energy(50)



###############################################################
# Load usb objects
###############################################################
# Define a function that samples the pose of a given usb object
def sample_pose(obj: bproc.types.MeshObject):
    # Sample the location above the tagboard
    obj.set_scale([1, 1, 1])
    obj.set_location(np.random.uniform([-0.08, -0.08, 0.05], [0.08, 0.08, 0.06]))
    obj.set_rotation_euler(bproc.sampler.uniformSO3())


if __name__== "__main__":
    ## Save final pose for three parts seperately, 
    ## which means every round only simulates with one type part
    parts = ['mainshell', 'topshell', 'insert_mold']

    part_num = 10
    iter = 1

    ###############################################################
    # Load tag_board which is going to catch the usb objects
    ###############################################################
    tag_board = bproc.loader.load_obj(args.tag_board)[0]
    tag_board.set_cp("category_id", 0)
    # tag_board.set_scale([2, 0.3, 2])
    tag_board.set_scale([1.6, 0.3, 1.6])
    tag_board.set_location(np.array([0, 0, -0.1]))
    tag_board.set_rotation_euler(np.array([-np.pi/2, np.pi, 0]))
    # Make the tagboard object passively participate in the physics simulation
    tag_board.enable_rigidbody(active=False, collision_shape="CONVEX_HULL", mass=1)

    obj_queue = []
    for obj in Path(args.cad_models).rglob('*.obj'):
    # for obj in Path("./CAD_model/UT1113").rglob('*.obj'):
        if 'background' in obj.name:
            continue

        catogory = obj.name[:-4]

        ## mainshell or topshell or insert_mol
        ## each scene contains 10 parts
        pipeline_init()
    
        for _ in range(part_num):
            idx = parts.index(catogory)
            part = bproc.loader.load_obj(str(obj)).pop()
            part.set_name(parts[idx])
            part.set_cp("category_id", idx+1)
            obj_queue.append(part)

    # Sample the poses of all usb objects, while making sure that no objects collide with each other.
    bproc.object.sample_poses(
        obj_queue,
        sample_pose_func=sample_pose
    )

    ###############################################################
    # Physical simulation settings
    ###############################################################
    # This defalt collision shape is Convex_Hull. 
    # It turns out the experiment results with convex_hull are same as reuslts with decomposed obj.
    for part in obj_queue:
        part.enable_rigidbody(active=True, collision_shape="CONVEX_HULL", mass=0.1)

    # Simulation time
    bproc.object.simulate_physics(
    min_simulation_time=1,
    max_simulation_time=10,
    check_object_interval=1
    )

    # This will make the renderer render the first 20 frames of the simulation
    bproc.utility.set_keyframe_render_interval(frame_start=0, frame_end=20)

    ###############################################################
    # render the whole pipeline and save them as PNGs
    ###############################################################
    bproc.renderer.set_max_amount_of_samples(50)
    bproc.renderer.set_noise_threshold(1)
    bproc.renderer.set_cpu_threads(0)
    # activate normal rendering
    bproc.renderer.enable_normals_output()
    bproc.renderer.enable_segmentation_output(map_by=["instance", "class", "name"])
    data = bproc.renderer.render()

    # Write data to coco file
    # bproc.writer.write_coco_annotations(os.path.join(args.output_dir, 'coco_data'),
    bproc.writer.write_coco_annotations(f"{args.output_dir}",
                            # instance_segmaps=seg_data["instance_segmaps"],
                            # instance_attribute_maps=seg_data["instance_attribute_maps"],
                            instance_segmaps=data["instance_segmaps"],
                            instance_attribute_maps=data["instance_attribute_maps"],
                            colors=data["colors"],
                            mask_encoding_format='polygon',
                            color_file_format="PNG", 
                            append_to_existing_output=True)