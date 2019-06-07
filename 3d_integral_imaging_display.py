# -*- coding: utf-8 -*-
from pylab import *

from os import listdir
import json
from PIL import Image
from numpy import *

def load_images(path):
    """
    Returns a list with every image in a folder
    :param path: path to the image's folder
    :return:
    """
    images_list = listdir(path)
    loaded_images = []
    for image in sorted(images_list):
        img = Image.open(path + '/' + image)
        resized_img = img.resize((1080, 720), Image.ANTIALIAS)
        # array_image = numpy.array(resized_img, dtype='int64')
        array_image = array(resized_img, dtype='uint8')
        loaded_images.append(array_image)

    return loaded_images


def read_json_parameters(path):
    """
    Returns the parameters to the image reconstruction loaded from a Json file
    :param path: path to the Json file with the
    :return: ei_path: path to the folder containing the integral images
             ei_shift: the distance between each taken picture
             ei_focal: the focal distance of the lens used to take the pictures
             sensor_ysize: y size of the sensor
             sensor_xsize: x size of the sensor
             n_x: number of pictures taken on the x axis
             n_y: number of pictures taken on the y axis
             z_0: distance to the focal plane chose
    """
    params_json = open(path, 'r')
    params = json.loads(params_json.read())
    ei_path = params['eiPath']
    reconstruct_params = params['reconstructParams']
    return ei_path, reconstruct_params


def get_rgb_channels(img):
    """
    Returns the R G and B channels of an image and adds them to the channel's
    :param img:
    :return:
    """
    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]
    return R, G, B


def reconstruct_image(ei, params, starting_x=0, starting_y=0):
    """
    Reconstructs a channel given the list of that same channel in every EI
    :param ei:
    :param params:
    :param starting_y:
    :param starting_x:
    :return:
    """
    # We first load all the reconstruction needed params

    ei_xshift = float(params['eiXShift'])
    ei_yshift = float(params['eiYShift'])
    ei_focal = float(params['eiFocal'])
    sensor_xsize = float(params['sensor_xSize'])
    sensor_ysize = float(params['sensor_ySize'])
    n_x = int(params['nX'])
    n_y = int(params['nY'])
    z_0 = float(params['z0'])
    xsize = params['xSize']
    ysize = params['ySize']
    # We then create the X Y shaped array that will include the final info of the reconstructed channel
    all_images_added = len(ei)
    reconstructed_channel = zeros((xsize, ysize, 3), dtype='uint8')
    k = 0 - starting_x
    l = 0 - starting_y
    for image in ei:
        xroll = int(round(-k * (ei_focal * xsize * ei_xshift)/(z_0 * sensor_xsize)))
        rolled_image = roll(image, xroll, axis=1)
        yroll = int(round(-l * (ei_focal * ysize * ei_yshift)/(z_0 * sensor_ysize)))
        full_rolled_image = roll(rolled_image, yroll, axis=0)
        reconstructed_channel += full_rolled_image/ all_images_added
        k += 1
        if k == n_x - starting_x:
            k = 0 - starting_x
            l += 1

    imsave('images_generated_for_view/%i_%i_%f.jpg' % (starting_x, starting_y, z_0), reconstructed_channel)

    return


params_path = sys.argv[1]
ei_path, reconstruct_params = read_json_parameters(params_path)
elementary_images = load_images(ei_path)

xsize = elementary_images[0].shape[0]
ysize = elementary_images[0].shape[1]
reconstruct_params.update({
    'xSize': xsize,
    'ySize': ysize
})

n_x = int(reconstruct_params['nX'])
n_y = int(reconstruct_params['nY'])
# for x_images in range(n_x):
#     for y_images in range(n_y):
#         reconstruct_image(elementary_images, reconstruct_params, starting_x=x_images, starting_y=y_images)
for wow in range(100):
    reconstruct_params['z0'] += 50
    reconstruct_image(elementary_images, reconstruct_params)
# reconstruct_image(elementary_images, reconstruct_params, starting_x=0, starting_y=4)