import cv2
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('image_path', default="./pose_exp/images",help="Path to the object file containing USB type-c components.")
args = parser.parse_args()

img_array = []
path_list = glob.glob(f'{args.image_path}/*.png')
path_list.sort()

for filename in path_list:
    img = cv2.imread(filename)
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)

out = cv2.VideoWriter('sim_demo.avi',cv2.VideoWriter_fourcc(*'DIVX'), 5, size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()