import os.path

import tq_img_utils as imutil

from test import join_base_dir as join_parent_base_dir


def test():
    img_path = r'E:\Workspace\Pycharm\Datasets\data\Dataset-DOWL2\DOWL2\zh\cctv\2k\1.png'
    bound = imutil.BoundingBox.get_from_two_points_format((840, 742, 901, 774))
    img = imutil.im_read(img_path)
    imutil.im_show('img', imutil.im_crop(img, bound))


def join_base_dir(path):
    path = join_parent_base_dir(os.path.join('img_operation', path))
    path = os.path.abspath(path)
    print(path)
    return path


def test_img_gray_binary_denoise():
    image = imutil.im_read(join_base_dir(r'1.jpg'))
    # 灰度化
    gray_image = imutil.average_grayscale(image)
    # 二值化
    binary_image = imutil.otsu_thresholding(gray_image)
    # 去噪
    denoise_image = imutil.denoise(binary_image)
    imutil.im_show('gray_image', gray_image)
    imutil.im_show('binary_image', binary_image)
    imutil.im_show('denoise_image', denoise_image)


def test_img_denoise():
    image = imutil.im_read(join_base_dir(r'opencv-noise.png'))
    imutil.im_show('image', image)
    denoise_image = imutil.denoise(image)
    imutil.im_show('denoise_image', denoise_image)
    denoise_image = imutil.denoise(image)
    imutil.im_show('denoise_image', denoise_image)
    denoise_image = imutil.denoise(image)
    imutil.im_show('denoise_image', denoise_image)


def test_img_draw_rectangle():
    image = imutil.im_read(join_base_dir(r'1.jpg'))
    imutil.im_show('image_draw', imutil.im_draw_rectangle(image, (0, 0, 300, 300)))
    imutil.im_show('image', image)
