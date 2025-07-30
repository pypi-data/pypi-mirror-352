from dataclasses import dataclass
import sys
from .utils import tq_json

from typing import Union, Tuple, List, Optional, Any, Dict


@dataclass
class BoundingBox:
    """
    Width-Height format of bounding box.
    The area of the bounding box should be positive(left>right and top>bottom).
    """
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x: int, y: int, width: int, height: int,
                 constraint: Tuple[int, int] = None, constrain_warning: bool = False,
                 is_lowest_value_zero: bool = True):
        """
        :param x: x coordinate
        :param y: y coordinate
        :param width: width of the bounding box
        :param height: height of the bounding box
        :param constraint: the constraint of the bounding box, tuple(width, height). it will automatically constrain the bounding. btw, x, y are greater than 0 in default
        :param constrain_warning: if True, it will raise ValueError while bounding is out of the constraint(if constraint is given); oppositely, it won't.
        :param is_lowest_value_zero: whether the bounding box's lowest value are zero, or not. If True, the lowest value of bounding box will be constrained to zero.
            if constraint is not None and is_lowest_value_zero is False, it will not release the constraint that lowest value should be zero.
            So, if is_lowest_value_zero is False, you shouldn't set the constraint.
        :raises ValueError: raise ValueError, if the area of the bounding box is not positive, or if bounding is out of the constraint while auto_constraining is True.
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"The area of the bounding must be positive(w:{width}, h:{height}).")
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if constraint is not None:  # constraint 自动包含最低值为 0 的限制
            if constrain_warning and self.is_out_of_constraint(constraint):
                raise ValueError(f"The bounding{x, y, width, height} is out of constraint{constraint}.")
            self.constrain(constraint)
            if self.width <= 0 or self.height <= 0:
                raise ValueError(
                    f"After constraining, the area of the bounding isn't positive(w:{self.width}, h:{self.height}).")
        elif is_lowest_value_zero:  # constraint 不存在，再使用 is_lowest_value_zero 判断
            self.x = 0 if self.x < 0 else self.x
            self.y = 0 if self.y < 0 else self.y

    def is_out_of_constraint(self, constraint: Tuple[int, int]):
        left = self.x < 0 or self.x > constraint[0]
        top = self.y < 0 or self.y > constraint[1]
        right = self.right() < 0 or self.right() > constraint[0]
        bottom = self.bottom() < 0 or self.bottom() > constraint[1]
        return left or top or right or bottom

    def constrain(self, constraint: Tuple[int, int]):
        """
        :param constraint: the constraint of the bounding box, tuple(width, height). and x, y must greater than 0 in default
        """
        width_threshold, height_threshold = constraint
        # 得用两点的方式
        left, top, right, bottom = self.left(), self.top(), self.right(), self.bottom()
        # 先确定 x, y
        self.x = max(0, min(left, width_threshold))
        self.y = max(0, min(top, height_threshold))
        # 后确定 width, height
        self.width = max(0, min(right, width_threshold)) - self.x
        self.height = max(0, min(bottom, height_threshold)) - self.y

    def top(self):
        return self.y

    def bottom(self):
        return self.y + self.height

    def left(self):
        return self.x

    def right(self):
        return self.x + self.width

    def area(self):
        """ get the area of the bounding """
        return self.width * self.height

    @staticmethod
    def get_from_min_max_format(region: Tuple[int, int, int, int], constraint: Tuple[int, int] = None,
                                constrain_warning: bool = False) -> 'BoundingBox':
        """
        get bounding box from min_max_format.
        :param region: Min-Max format: (x_min, x_max, y_min, y_max)
        :param constraint: the constraint of the bounding box, tuple(width, height). it will automatically constrain the bounding. btw, x, y must greater than 0 in default
        :param constrain_warning: if True, it will raise ValueError while bounding is out of the constraint(if constraint is given); oppositely, it won't.
        """
        x_min, x_max, y_min, y_max = region
        return BoundingBox(x_min, y_min, x_max - x_min, y_max - y_min, constraint, constrain_warning)

    @staticmethod
    def get_from_two_points_format(region: Tuple[int, int, int, int],
                                   constraint: Tuple[int, int] = None,
                                   constrain_warning: bool = False) -> 'BoundingBox':
        """
        get bounding box from two_points_format.
        :param region: Two-Points format: (x_min, y_min, x_max, y_max)
        :param constraint: the constraint of the bounding box, tuple(width, height). it will automatically constrain the bounding. btw, x, y must greater than 0 in default
        :param constrain_warning: if True, it will raise ValueError while bounding is out of the constraint(if constraint is given); oppositely, it won't.
        """
        x_min, y_min, x_max, y_max = region
        return BoundingBox.get_from_min_max_format((x_min, x_max, y_min, y_max), constraint, constrain_warning)

    @staticmethod
    def get_from_vertexes_format(vertex: List[List[Union[float, int]]],
                                 constraint: Tuple[int, int] = None,
                                 constrain_warning: bool = False) -> 'BoundingBox':
        """
        通过四个角点获取 bounding_box。如果是自由的四个角点，则获取最大矩形的 bounding_box.
        :param vertex: list of vertex coordinates: [left-top, right-top, right-bottom, left-bottom]; vertex coordinates: [x, y].
        :param constraint: the constraint of the bounding box, tuple(width, height). it will automatically constrain the bounding. btw, x, y must greater than 0 in default
        :param constrain_warning: if True, it will raise ValueError while bounding is out of the constraint(if constraint is given); oppositely, it won't.
        :return: the maximum rectangle of bounding box. (x:int, y:int, width:int, height:int).
        """
        lt, rt, rb, lb = vertex
        x_min = int(min(lt[0], rt[0], rb[0], lb[0], sys.maxsize))  # 求最小值，用系统处理最大值限制结果。因为文本框的处理设计计算机本身能力，需要进行限制
        x_max = int(max(lt[0], rt[0], rb[0], lb[0], 0))  # 求最大值，用 0 限制结果最小值
        y_min = int(min(lt[1], rt[1], rb[1], lb[1], sys.maxsize))
        y_max = int(max(lt[1], rt[1], rb[1], lb[1], 0))
        return BoundingBox(x_min, y_min, x_max - x_min, y_max - y_min, constraint, constrain_warning)

    def format_width_height(self):
        """ get Width-Height format: (x, y, width, height) """
        return self.x, self.y, self.width, self.height

    def format_min_max(self):
        """ get Min-Max format: (x_min, x_max, y_min, y_max) """
        return self.x, self.right(), self.y, self.bottom()

    def format_two_points(self):
        """ get Two-Points format: (x_min, y_min, x_max, y_max) """
        return self.x, self.y, self.right(), self.bottom()

    @staticmethod
    def get_property_names() -> Tuple[str, str, str, str]:
        return 'x', 'y', 'width', 'height'

    @staticmethod
    def from_dict(obj: dict) -> 'BoundingBox':
        return BoundingBox(obj['x'], obj['y'], obj['width'], obj['height'])

    @staticmethod
    def to_dict(bbox: 'BoundingBox') -> Dict[str, Any]:
        """ convert bounding box to dict """
        return {'x': bbox.x, 'y': bbox.y, 'width': bbox.width, 'height': bbox.height}

    def to_json(self) -> str:
        """ convert bounding box to json string """
        return tq_json.dumps_json(self)

    @staticmethod
    def from_json(json_str: str) -> 'BoundingBox':
        """ convert json string to bounding box """
        return tq_json.loads_json(json_str)

    def copy(self) -> 'BoundingBox':
        return BoundingBox(self.x, self.y, self.width, self.height)

    def get_extend_bounds(self, margin: int, constraint: Tuple[int, int] = None) -> 'BoundingBox':
        """
        extend bounding(add margin), return new bounding box. x, y aren't greater than 0 in default, so it's better to use constraint.
        :param margin: extend margin value
        :param constraint: the constraint of the bounding box, tuple(width, height). and x, y are greater than 0 in default
            if constraint is not None, it will extend bounds first, then constrain the extended bounds.
        :return: the extended bounding box
        """
        return BoundingBox(self.x - margin, self.y - margin, self.width + 2 * margin, self.height + 2 * margin,
                           constraint, is_lowest_value_zero=False)

    def get_shrink_bounds(self, padding: int, constraint: Tuple[int, int] = None) -> 'BoundingBox':
        """
        shrink bounding box(delete padding), return new bounding. x, y aren't greater than 0 in default, so it's better to use constraint.
        :param padding: padding value to shrink bounding
        :param constraint: the constraint of the bounding box, tuple(width, height). and x, y are greater than 0 in default
            if constraint is not None, it will extend bounds first, then shrink the extended bounds.
        :return: the new shrinking bounding box
        """
        return BoundingBox(self.x + padding, self.y + padding, self.width - 2 * padding, self.height - 2 * padding,
                           constraint, is_lowest_value_zero=False)

    def intersection(self, e: 'BoundingBox') -> Optional['BoundingBox']:
        """ get the intersection of these two bounding box """
        left_max = max(self.x, e.x)
        top_max = max(self.y, e.y)
        right_min = min(self.right(), e.right())
        bottom_min = min(self.bottom(), e.bottom())
        if top_max >= bottom_min or left_max >= right_min:
            return None
        return self.get_from_min_max_format((left_max, right_min, top_max, bottom_min))

    def width_intersection(self, e: 'BoundingBox') -> float:
        """ get the width intersection of these two bounding box(return 0 if they do not intersect) """
        left_max = max(self.left(), e.left())
        right_min = min(self.right(), e.right())
        width_intersection = right_min - left_max
        return width_intersection if width_intersection >= 0 else 0

    def height_intersection(self, e: 'BoundingBox') -> float:
        """ get the height intersection of these two bounding box(return 0 if they do not intersect) """
        top_max = max(self.top(), e.top())
        bottom_min = min(self.bottom(), e.bottom())
        height_intersection = bottom_min - top_max
        return height_intersection if height_intersection >= 0 else 0

    def union(self, e: 'BoundingBox') -> 'BoundingBox':
        """
        get the union of these two bounding(a new bounding box).
        union bounding format: (left_min, right_max, top_min, bottom_max).
        return the rectangle bounding, not the traditional union of two bounding boxes
        """
        left_min = min(self.x, e.x)
        top_min = min(self.y, self.y)
        right_max = max(self.right(), e.right())
        bottom_max = max(self.bottom(), e.bottom())
        return self.get_from_min_max_format((left_min, right_max, top_min, bottom_max))

    def inside(self, e: 'BoundingBox') -> bool:
        """ True if this bounding box is inside the given bounding box(including equality). """
        if self.left() >= e.left() and self.right() <= e.right() and self.top() >= e.top() and self.bottom() <= e.bottom():
            return True
        else:
            return False

    def contains(self, e: 'BoundingBox') -> bool:
        """ True if this bounding box contains the given bounding box(including equality). """
        if self.left() <= e.left() and self.right() >= e.right() and self.top() <= e.top() and self.bottom() >= e.bottom():
            return True
        else:
            return False

    def iou(self, e: 'BoundingBox') -> float:
        """
        calculate the IoU of the area of two bounding
        IoU, Intersection over Union：(|A∩B| / |A∪B|).
        """
        intersection = self.intersection(e)  # 获取交集.
        if intersection is None:
            return 0
        else:
            intersection_area = intersection.area()
            union_area = self.area() + e.area() - intersection_area  # 因为并集的处理方法，无法正确表示并集的面积，所以不适用对应方法获取并集
            return intersection_area / union_area

    def height_iou(self, e: Union['BoundingBox', Tuple[Union[float, int], Union[float, int]]]) -> float:
        """
        calculate the IoU of the height of two bounding
        IoU, Intersection over Union：(|A∩B| / |A∪B|).

        :param e: the bounding box or a tuple(top, bottom)
        """
        if isinstance(e, tuple):
            e_top, e_bottom = e
        else:
            e_top, e_bottom = float(e.top()), float(e.bottom())
        height_intersection = min(float(self.bottom()), e_bottom) - max(float(self.y), e_top)  # 高度交集: 最小底边-最大顶边
        height_union = max(float(self.bottom()), e_bottom) - min(float(self.y), e_top)  # 高度并集: 最大底边-最小顶边
        if height_intersection <= 0:  # 没有高度交集，返回 0
            return 0
        return height_intersection / height_union

    def target_cover(self, target: 'BoundingBox') -> float:
        """ 文本框在目标文本框(target)的区域覆盖率：(|A∩B| / |B|). """
        intersection = self.intersection(target)  # 获取交集
        if intersection is None:
            return 0
        else:
            target_area = target.area()
            intersection_area = intersection.area()
            return intersection_area / target_area


# 设置 BoundingBox 的 JSON encode & decode function
tq_json.TqJSONEncoder.set_class_serialize_function(BoundingBox, BoundingBox.to_dict)
tq_json.TqJSONDecoder.set_class_objectify_function(BoundingBox.get_property_names(), BoundingBox.from_dict)
