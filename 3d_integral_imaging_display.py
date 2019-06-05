# -*- coding: utf-8 -*-
from pylab import *

from os import listdir
import json
from PIL import Image
import numpy


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
        resized_img = img.resize((480, 320), Image.ANTIALIAS)
        array_image = numpy.array(resized_img, dtype='int64')
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
    for ii in range(xsize):
        for jj in range(ysize):
            all_images_added_for_idx = all_images_added
            l_index = 0 - starting_y
            k_index = 0 - starting_x
            r_value = g_value = b_value = 0
            for image in ei:
                i_index = int(ii - k_index * (xsize * ei_xshift * ei_focal) / (sensor_xsize * z_0))
                j_index = int(jj - l_index * (ysize * ei_yshift * ei_focal) / (sensor_ysize * z_0))
                k_index += 1
                # when k_index is n_x it means next iteration is the first image on the next y row
                if k_index == n_x - starting_x - 1:
                    k_index = 0 - starting_x
                    l_index += 1
                # if the pixel is out of range, we don't take on count that image to reconstruct this pixel
                if (i_index < 0 or i_index >= xsize) or (j_index < 0 or j_index >= ysize):
                    all_images_added_for_idx -= 1
                else:
                    r_value += image[i_index, j_index, 0]
                    g_value += image[i_index, j_index, 1]
                    b_value += image[i_index, j_index, 2]

        # when every image has been iterated, we make the mean of the value of the pixel depending on how many images have been taken on count
            reconstructed_channel[ii, jj, 0] = r_value / all_images_added_for_idx
            reconstructed_channel[ii, jj, 1] = g_value / all_images_added_for_idx
            reconstructed_channel[ii, jj, 2] = b_value / all_images_added_for_idx
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
for x_images in range(n_x):
    for y_images in range(n_y):
        reconstruct_image(elementary_images, reconstruct_params, starting_x=x_images, starting_y=y_images)
# reconstruct_image(elementary_images, reconstruct_params, starting_x=0, starting_y=4)