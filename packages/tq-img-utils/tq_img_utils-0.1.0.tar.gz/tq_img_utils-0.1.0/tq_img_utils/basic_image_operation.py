import os

from typing import Union, Optional, Tuple
from enum import Enum

import cv2 as cv
from PIL import Image as PIL_Image

from .bounding_box import BoundingBox
from .utils import np


class ImgReadFlags(Enum):
    COLOR = cv.IMREAD_COLOR  # 1
    GRAYSCALE = cv.IMREAD_GRAYSCALE  # 0
    UNCHANGED = cv.IMREAD_UNCHANGED  # -1
    ANY_COLOR_N_DEPTH = cv.IMREAD_ANYCOLOR | cv.IMREAD_ANYDEPTH  # 6

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, ImgReadFlags):
            return self is other
        return False


class ImgColorspaceConvertFlags(Enum):
    BGR2RGB = cv.COLOR_BGR2RGB  # 4
    RGB2BGR = cv.COLOR_RGB2BGR  # 4
    BGR2GRAY = cv.COLOR_BGR2GRAY  # 6
    GRAY2BGR = cv.COLOR_GRAY2BGR  # 8
    BGR2HSV = cv.COLOR_BGR2HSV  # 40
    HSV2BGR = cv.COLOR_HSV2BGR  # 54

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, ImgColorspaceConvertFlags):
            return self is other
        return False


class FontFace(Enum):
    HERSHEY_SIMPLEX = cv.FONT_HERSHEY_SIMPLEX  # 0
    HERSHEY_PLAIN = cv.FONT_HERSHEY_PLAIN  # 1
    HERSHEY_COMPLEX = cv.FONT_HERSHEY_COMPLEX  # 3

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, FontFace):
            return self is other
        return False


# TODO 后续对于基础图像操作，需要同时支持 PIL 和 OpenCV
"""
大致思路是，通过传入图像的类型进行判定，是opencv操作还是 PIL 操作。Union[Image, ndarray]
"""


def im_read(img_file, flags=ImgReadFlags.COLOR, return_pil: bool = False) -> Union[PIL_Image.Image, np.ndarray]:
    """
    按照指定的颜色形式读取对应路径的图像文件
    :param img_file: 读取图像的路径，如果文件不存在则会抛出FileNotFoundError
    :param flags: 读取形式，详见ImgReadFlags；如果输入错误的读取形式，会抛出ValueError
    :param return_pil: 是否返回 PIL.Image.Image 对象。默认为 False，返回 opencv 图像（ndarray）。
    """
    if flags not in ImgReadFlags:
        raise ValueError(f'Non-exists flags: {flags}')
    if not os.path.isfile(img_file):
        raise FileNotFoundError(f'{img_file} does not exist')
    if return_pil:
        return PIL_Image.open(img_file)
    return cv.imread(img_file, flags.value)


def im_read_resized(image_file, flags=ImgReadFlags.COLOR, dim: Tuple[int, int] = None,
                    rate: Tuple[float, float] = None, return_pil: bool = False) -> Union[PIL_Image.Image, np.ndarray]:
    """
    按照指定的颜色形式读取对应路径的图像文件。
    同时可以对读取的图像进行放缩，优先使用宽高进行缩放，若宽高为None则使用缩放比例，若均为None则会抛出ValueError
    :param image_file: 读取图像的路径，如果文件不存在则会抛出FileNotFoundError
    :param flags: 读取形式，详见ImgReadFlags；如果输入错误的读取形式，会抛出ValueError
    :param dim: 放缩的宽与高tuple(width, height), width与height可以为None, e.g.(None,None) or (None, 111)
    :param rate: 宽与高的缩放比例tuple(width_rate, height_rate), width_rate与height_rate不可为None
    :param return_pil: 是否返回 PIL.Image.Image 对象。默认为 False，返回 opencv 图像（ndarray）。
    """
    cv_image = im_read(image_file, flags, return_pil)
    cv_image = im_resize(cv_image, dim, rate)
    return cv_image


def im_write(img_file: str, img: Union[np.ndarray, PIL_Image.Image], dpi: Optional[Tuple[int, int]] = None):
    """
    将图像写入对应的文件路径中
    :param img_file: 存储图像的文件路径，如果文件的文件目录不存在则会抛出FileNotFoundError
    :param img: 需要存储的图像对象
    :param dpi: 设置图像的dpi信息(horizontal_dpi, vertical_dpi)。仅当img为PIL.Image对象时生效。
    """
    dir_name = os.path.dirname(img_file)
    if not os.path.exists(dir_name):
        raise FileNotFoundError(f'{dir_name} does not exist')
    if isinstance(img, PIL_Image.Image):  # 注意 img 可能为 Image 的子类，因此使用 isinstance
        img.save(img_file, dpi=dpi)
    else:
        cv.imwrite(img_file, img)


def im_cvt_color(img, flags=ImgColorspaceConvertFlags.BGR2RGB):
    """
    根据传入的图像按照指定的转换方式，转换为对应的颜色空间，并返回新的图像
    :param img: 需要转换的图像
    :param flags: 转换方式，详见ImgColorspaceConvertFlags；如果输入错误的转换方式，会抛出ValueError
    """
    if flags not in ImgColorspaceConvertFlags:
        raise ValueError(f'Non-exists flags: {flags}')
    return cv.cvtColor(img, flags.value)


def average_grayscale(image):
    """
    使用平均值法进行灰度化，返回新的图像
    :param image: BGR image
    """
    return im_cvt_color(image, ImgColorspaceConvertFlags.BGR2GRAY)


def im_show(name: str, img: Union[np.ndarray, PIL_Image.Image, str]):
    """
    窗口展示图像并等待
    :param name: 展示窗名称
    :param img: 展示图像. 可以是 image filepath，opencv image object(numpy.ndarray), PIL.Image.
        如果是 image filepath, 则默认根据彩色颜色空间读取。
    """
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    if isinstance(img, PIL_Image.Image):  # 注意 img 可能为 Image 的子类，因此使用 isinstance
        img = im_to_ndarray(img)
    elif isinstance(img, str):
        if not os.path.isfile(img):
            raise FileNotFoundError(f'{img} does not exist')
        img = im_read(img)
    cv.imshow(name, img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def im_resize(image: np.ndarray, dim: Tuple[int, int] = None, rate: Tuple[float, float] = None) -> np.ndarray:
    """
    根据宽高或缩放比例选择适合的插值方法，以此根据传入的图像，对其进行尺度放缩，并返回新的图像；
    优先使用宽高进行缩放，若宽高为None则使用缩放比例，若均为None则会抛出ValueError
    :param image: 图像
    :param dim: 放缩的宽与高tuple(width, height), width与height可以为None, e.g.(None,None) or (None, 111)
    :param rate: 宽与高的缩放比例tuple(width_rate, height_rate), width_rate与height_rate不可为None
    """

    def im_resize_width_and_height(img: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        根据宽高进行适合的插值方法进行尺度放缩
        :param img: 图像
        :param width: 放缩的宽
        :param height: 放缩的高
        """
        o_height, o_width = img.shape[:2]  # 获取图像的高和宽

        # 如果变形后的长宽与原来相同，直接不缩放返回image
        if o_height == height and o_width == width:
            return img

        # 如果长宽仅有一个为None，那默认根据另一方的比例进行缩放
        if width is None:
            r = height / float(o_height)
            width = int(o_width * r)
        elif height is None:
            r = width / float(o_width)
            height = int(o_height * r)

        # 根据宽高放大情况，选择最优的插值算法
        max_ratio = max(width / o_width, height / o_height)
        if max_ratio <= 3.0:  # 小于等于 3 倍
            magnify_interpolation = cv.INTER_LINEAR
        elif max_ratio <= 4.0:  # 小于等于 4 倍
            magnify_interpolation = cv.INTER_CUBIC
        else:  # 大于 4 倍
            magnify_interpolation = cv.INTER_LANCZOS4
        # 根据宽高是放还是缩，进行变形
        if o_width <= width and o_height <= height:  # 放大
            resized = cv.resize(img, (width, height), interpolation=magnify_interpolation)
        elif o_width >= width and o_height >= height:  # 缩小
            resized = cv.resize(img, (width, height), interpolation=cv.INTER_AREA)
        elif o_width > width and o_height < height:  # 高先放大，宽再缩小
            temp = cv.resize(img, (o_width, height), interpolation=magnify_interpolation)
            resized = cv.resize(temp, (width, height), interpolation=cv.INTER_AREA)
        else:  # 宽先放大，高再缩小
            temp = cv.resize(img, (width, o_height), interpolation=magnify_interpolation)
            resized = cv.resize(temp, (width, height), interpolation=cv.INTER_AREA)
        return resized

    def im_resize_rate(img: np.ndarray, r: Tuple[float, float]) -> np.ndarray:
        """
        根据比例进行适合的插值方法进行尺度放缩
        :param img: 图像
        :param r: 宽与高的缩放比例tuple(width_rate, height_rate)
        """
        o_height, o_width = img.shape[:2]  # 获取图像的高和宽
        return im_resize_width_and_height(img, int(o_width * r[0]), int(o_height * r[1]))

    if dim is not None:
        return im_resize_width_and_height(image, dim[0], dim[1])
    elif rate is not None:
        return im_resize_rate(image, rate)
    else:
        raise ValueError('dim or rate is required')


def im_crop(img, rect: Union[Tuple[int, int, int, int], BoundingBox]) -> np.ndarray:
    """
    根据给定的图像，裁剪给定的范围(rect)，并返回新的图像(并不修改原图像).
    :param img: 需要裁剪的图像
    :param rect: crop rectangle. tuple of int, format: (x,y,offset_x,offset_y); or BoundingBox.
    """
    if isinstance(rect, BoundingBox):
        x, x_max, y, y_max = rect.format_min_max()
    else:
        x, y, offset_x, offset_y = rect
        x_max, y_max = x + offset_x, y + offset_y
    height, width = img.shape[0], img.shape[1]
    if 0 <= x < x_max <= width and 0 <= y < y_max <= height:
        return img[y:y_max, x:x_max]
    else:
        raise ValueError(
            f'wrong bounding box: x:{x}, y:{y}, x_max:{x_max}, y_max:{y_max}, image_width:{width}, image_height:{height}')


def im_draw_contours(image, contours, contourIdx, color: Tuple[int, int, int], thickness):
    """
    根据传入的图像，在其上画出给定的轮廓，返回修改后的图像
    :param image: 传入的图像
    :param contours: 轮廓列表，元素为Numpy数组，表示轮廓点的坐标
    :param contourIdx: 绘制对应索引的轮廓，-1表示所有，正整数表示对应轮廓
    :param color: 轮廓的颜色，tuple(B,G,R)
    :param thickness: 轮廓线的厚度
    """
    return cv.drawContours(image, contours, contourIdx, color, thickness)


def im_draw_rectangle(image, rectangle: Union[Tuple[int, int, int, int], BoundingBox],
                      color: Tuple[int, int, int] = (0, 0, 255),
                      thickness=4):
    """
    根据传入的图像，在其上画给定的矩形，返回修改后的图像
    :param image: 绘画的图像
    :param rectangle: 矩形参数，(x,y,width,height) or BoundingBox
    :param color: 矩形边框颜色tuple(B,G,R)
    :param thickness: 矩形边框粗度
    """
    if isinstance(rectangle, BoundingBox):
        return cv.rectangle(image, (rectangle.left(), rectangle.top()), (rectangle.right(), rectangle.bottom()), color,
                            thickness)
    else:
        x, y, w, h = rectangle
        return cv.rectangle(image, (x, y), (x + w, y + h), color, thickness)


def im_draw_circle(image, position: Tuple[int, int], radius=1, color: Tuple[int, int, int] = (0, 255, 0), thickness=10):
    """
    根据给定的图像，在指定的位置上绘画指定要求的圆，返回修改后的图像
    :param image: Image to draw circle on
    :param position: 圆圈圆心坐标，(x:int, y:int)
    :param radius: 圆圈半径
    :param color: 圆圈颜色tuple(B,G,R)
    :param thickness: 圆圈线粗度
    """
    return cv.circle(image, position, radius, color, thickness)


def otsu_thresholding(image):
    """
    应用Otsu最大类间方差法进行二值化，将灰度图像进行二值化，得到新的二值化图像
    :param image: 需要是灰度图像
    """
    _, thresholded = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return thresholded


def denoise(image, kernel_size=3):
    """
    使用中值滤波进行去噪，并返回新的图像
    :param image: 需要图像
    :param kernel_size: 指定了中值滤波的内核大小，具体来说，它表示滤波器窗口的尺寸
    """
    # 中值滤波 常用来去除椒盐噪声 相当于将9个值进行排序，取中值作为当前值
    return cv.medianBlur(image, kernel_size)


def im_bounding_rectangle(contour):
    """
    根据给定的边框图像，绑定对应的矩形边框，并返回对应边框信息(x,y,w,h)
    """
    return cv.boundingRect(contour)


def im_draw_text(image, text, position: Tuple[int, int], fontFace=FontFace.HERSHEY_PLAIN, fontScale=1,
                 color: Tuple[int, int, int] = (0, 0, 255),
                 thickness=1):
    """
    在给定的图像上绘画指定属性与内容的文本，返回修改后的图像
    :param image: 添加的图像
    :param text: 添加的文本
    :param position: 文本左下坐标在图中的位置,(x:int,y:int)
    :param fontFace: 字体样式, 详见FONT_FACE
    :param fontScale: 字体大小
    :param color: 文本颜色tuple(B,G,R)
    :param thickness: 字体粗细
    """
    return cv.putText(image, text, position, fontFace.value, fontScale, color, thickness)


def box_points(center: Tuple[float, float], point: Tuple[float, float], rotation: float):
    """
    根据矩形的中心点、宽高和旋转角度，计算得到矩阵四个顶点的坐标
    :param center: 矩形的中心坐标(x,y)
    :param point: 矩形的宽高(width,height)
    :param rotation: 矩形旋转的角度
    """
    return cv.boxPoints((center, point, rotation))


def im_to_PIL(img: np.ndarray):
    """
    将 opencv 的图像(Numpy 数组, ndarray)转换为 PIL 图像（Image 对象）
    :param img: opencv 的图像(Numpy 数组)
    :return: PIL 图像(Image 对象)
    """
    return PIL_Image.fromarray(im_cvt_color(img, ImgColorspaceConvertFlags.BGR2RGB))


def im_to_ndarray(img: PIL_Image.Image):
    """
    将 PIL 图像（Image 对象）转换为 opencv 的图像(Numpy 数组, ndarray)
    :param img: opencv 的图像(Numpy 数组)
    :return: opencv 的图像(Numpy 数组, ndarray)
    """
    return im_cvt_color(np.asarray(img), ImgColorspaceConvertFlags.RGB2BGR)
