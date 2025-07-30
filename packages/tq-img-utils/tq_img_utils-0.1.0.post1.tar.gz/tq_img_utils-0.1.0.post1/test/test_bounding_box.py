from tq_img_utils import BoundingBox


class TestInitBound:
    @staticmethod
    def test_area():  # pass
        """ not (width <= 0 or height <= 0) """
        print()
        try:
            BoundingBox(1, 1, 1, 3)
            BoundingBox(1, 1, -1, 3)
        except ValueError as e:
            print(e)  # The area of the bounding must be positive(w:-1, h:3).

    @staticmethod
    def test_lowest_value_zero():
        # 自动约束最小值为 0
        b = BoundingBox(-1, -1, 2, 2)
        assert b == BoundingBox(x=0, y=0, width=2, height=2)
        # 取消最小值为 0 的约束
        b = BoundingBox(-1, -1, 2, 2, is_lowest_value_zero=False)
        assert b.format_width_height() == (-1, -1, 2, 2)

    @staticmethod
    def test_constrain():  # pass
        print()
        constraint = (2, 2)  # 坐标系约束范围
        b = BoundingBox(-1, 0, 2, 2, constraint)
        assert b == BoundingBox(x=0, y=0, width=1, height=2)  # 因为横坐标 -1~0 被裁剪了，所以 width-1
        b = BoundingBox(1, 1, 3, 3, constraint)
        assert b == BoundingBox(x=1, y=1, width=1, height=1)

        try:  # constrain 之后，仍然 area 不为正 (区域都不在 constraint 中)
            BoundingBox(3, 3, 3, 3, constraint)
        except ValueError as e:
            print(e)  # After constraining, the area of the bounding isn't positive(w:0, h:0).

    @staticmethod
    def test_constrain_warn():  # pass
        print()
        constraint = (2, 2)  # 坐标系约束范围
        try:  # 部分区域在 constraint 中
            BoundingBox(1, 1, 3, 3, constraint, True)
        except ValueError as e:
            print(e)  # The bounding(1, 1, 3, 3) is out of constraint(2, 2).

    @staticmethod
    def test_get_from_other_formats():  # pass
        b = BoundingBox(1, 2, 2, 3)
        assert b == BoundingBox.get_from_min_max_format((1, 3, 2, 5))  # (x_min, x_max, y_min, y_max)
        assert b == BoundingBox.get_from_two_points_format((1, 2, 3, 5))  # (x_min, y_min, x_max, y_max)
        # list of vertex coordinates: [left-top, right-top, right-bottom, left-bottom]; vertex coordinates: [x, y].
        assert b == BoundingBox.get_from_vertexes_format([[1, 2], [3, 2], [1, 5], [3, 5]])


"""
后续都是测试 BoundingBox 对象的具体方法
"""


def test_is_out_of_constraint():  # pass
    constraint = (2, 2)  # 坐标系约束范围
    b = BoundingBox(0, 0, 2, 2)
    assert b.is_out_of_constraint(constraint) is False

    b = BoundingBox(1, 1, 3, 3)
    assert b.is_out_of_constraint(constraint) is True


def test_constrain():  # pass
    constraint = (2, 2)  # 坐标系约束范围

    b = BoundingBox(0, 0, 2, 2)
    b.constrain(constraint)
    assert b == BoundingBox(0, 0, 2, 2)  # BoundingBox 是 ValueObject，所以可以直接比较

    b = BoundingBox(-1, -1, 3, 3)
    b.constrain(constraint)
    assert b != BoundingBox(-1, -1, 3, 3)
    assert b == BoundingBox(0, 0, 2, 2)


def test_get_properties():
    """ 测试一些获取属性的函数, pass """
    b = BoundingBox(11, 12, 2, 2)
    assert b.top() == 12  # y
    assert b.bottom() == 14  # y+height
    assert b.left() == 11  # x
    assert b.right() == 13  # x+width
    assert b.area() == 4  # width * height


def test_get_formats():  # pass
    b = BoundingBox(11, 12, 2, 2)
    assert b.format_width_height() == (11, 12, 2, 2)
    assert b.format_min_max() == (11, 13, 12, 14)
    assert b.format_two_points() == (11, 12, 13, 14)


def test_dict():  # pass
    b = BoundingBox(11, 12, 2, 2)
    b_dict = {"x": 11, "y": 12, "width": 2, "height": 2}
    assert BoundingBox.to_dict(b) == b_dict
    assert BoundingBox.from_dict(b_dict) == b


def test_json():  # pass
    b = BoundingBox(11, 12, 2, 2)
    b_json = '{"x": 11, "y": 12, "width": 2, "height": 2}'
    s = b.to_json().replace('\n', '').replace(' ', '')
    assert s == b_json.replace(' ', '')
    assert BoundingBox.from_json(b_json) == b


def test_copy():  # pass
    b = BoundingBox(11, 12, 2, 2)
    b1 = b.copy()
    # 等价 但 不相同(不是同一个对象实例)
    assert b == b1
    assert b is not b1


def test_get_extend_bounds():  # pass
    constraint = (11, 11)  # 坐标系约束范围
    bbox = BoundingBox(0, 0, 10, 10)
    # 四边都向外扩展 2，且是忽略约束的（可小于 0）
    assert bbox.get_extend_bounds(2) == BoundingBox(x=-2, y=-2, width=14, height=14, is_lowest_value_zero=False)
    # 也可通过负数进行缩小
    assert bbox.get_extend_bounds(-2) == BoundingBox(x=2, y=2, width=6, height=6)
    # constraint 设置，则先扩大，再约束
    assert bbox.get_extend_bounds(2, constraint) == BoundingBox(x=0, y=0, width=11, height=11)


def test_bbox_shrink():  # pass
    constraint = (4, 4)  # 坐标系约束范围
    bbox = BoundingBox(0, 0, 10, 10)
    # 四边都向内缩小 2
    assert bbox.get_shrink_bounds(2) == BoundingBox(x=2, y=2, width=6, height=6)
    # 也可通过负数进行扩大，且是忽略约束的（可小于 0）
    assert bbox.get_shrink_bounds(-2) == BoundingBox(x=-2, y=-2, width=14, height=14, is_lowest_value_zero=False)
    # constraint 设置，则先缩小，再约束
    assert bbox.get_shrink_bounds(2, constraint) == BoundingBox(x=2, y=2, width=2, height=2)


def test_intersection():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.intersection(c) == BoundingBox(0, 0, 5, 5)
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.intersection(c) == BoundingBox(0, 0, 10, 10)
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.intersection(c) == BoundingBox(5, 5, 5, 5)
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.intersection(c) is None
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.intersection(c) is None


def test_width_intersection():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.width_intersection(c) == 5
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.width_intersection(c) == 10
    # 部分相交
    c = BoundingBox(5, 0, 10, 10)
    assert b.width_intersection(c) == 5
    # 不相交(相切)
    c = BoundingBox(10, 0, 10, 10)
    assert b.width_intersection(c) == 0
    # 不相交(完全分离)
    c = BoundingBox(12, 0, 10, 10)
    assert b.width_intersection(c) == 0


def test_height_intersection():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.height_intersection(c) == 5
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.height_intersection(c) == 10
    # 部分相交
    c = BoundingBox(0, 5, 10, 10)
    assert b.height_intersection(c) == 5
    # 不相交(相切)
    c = BoundingBox(0, 10, 10, 10)
    assert b.height_intersection(c) == 0
    # 不相交(完全分离)
    c = BoundingBox(0, 12, 10, 10)
    assert b.height_intersection(c) == 0


def test_union():  # pass
    # 不是传统意义上的 union，只能根据边界，确当 union（矩形）
    b = BoundingBox(0, 0, 10, 10)
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.union(c) == BoundingBox(0, 0, 10, 10)
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.union(c) == BoundingBox(0, 0, 10, 10)
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.union(c) == BoundingBox(0, 0, 15, 15)
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.union(c) == BoundingBox(0, 0, 20, 20)
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.union(c) == BoundingBox(0, 0, 22, 22)


def test_inside():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # b inside c
    c = BoundingBox(0, 0, 15, 15)
    assert b.inside(c) is True
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.inside(c) is False
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.inside(c) is True
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.inside(c) is False
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.inside(c) is False
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.inside(c) is False


def test_contains():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # b inside c
    c = BoundingBox(0, 0, 15, 15)
    assert b.contains(c) is False
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.contains(c) is True
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.contains(c) is True
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.contains(c) is False
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.contains(c) is False
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.contains(c) is False


def test_iou():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # b inside c
    c = BoundingBox(0, 0, 15, 15)
    assert b.iou(c) == (10 * 10) / (15 * 15)
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.iou(c) == (10 * 10) / (10 * 10)
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.iou(c) == (5 * 5) / (10 * 10 + 10 * 10 - 5 * 5)
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.iou(c) == 0
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.iou(c) == 0


def test_height_iou():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # b inside c
    c = BoundingBox(0, 0, 15, 15)
    assert b.height_iou(c) == 10 / 15
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.height_iou(c) == 10 / 10
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.height_iou(c) == 5 / (10 + 10 - 5)
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.height_iou(c) == 0
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.height_iou(c) == 0


def test_height_iou1():
    def height_iou(top1, bottom1, top2, bottom2):  # 测试旧代码的 height_iou
        # 高度交叉　　最小底边-最大顶边
        height_intersection = min(bottom1, bottom2) - max(top1, top2)
        # 高度联合　最大底边-最小顶边
        height_union = max(bottom1, bottom2) - min(top1, top2)
        if height_union == 0:
            return height_intersection * 10
        return height_intersection / height_union

    b = (0, 10)  # (top, bottom)
    # b inside c
    c = (0, 15)
    assert height_iou(*b, *c) == 10 / 15
    # 相等
    c = (0, 10)
    assert height_iou(*b, *c) == 10 / 10
    # 部分相交
    c = (5, 15)
    assert height_iou(*b, *c) == 5 / (10 + 10 - 5)
    # 不相交(相切)
    c = (10, 20)
    assert height_iou(*b, *c) == 0
    # 不相交(完全分离)
    c = (12, 22)
    assert height_iou(*b, *c) == 0  # 这里会和 BoundingBox 的逻辑有区别，它不会限制交集为空的输出（负数）


def test_target_cover():  # pass
    b = BoundingBox(0, 0, 10, 10)
    # b inside c
    c = BoundingBox(0, 0, 15, 15)
    assert b.target_cover(c) == (10 * 10) / (15 * 15)
    # c inside b
    c = BoundingBox(0, 0, 5, 5)
    assert b.target_cover(c) == (5 * 5) / (5 * 5)
    # 相等
    c = BoundingBox(0, 0, 10, 10)
    assert b.target_cover(c) == (10 * 10) / (10 * 10)
    # 部分相交
    c = BoundingBox(5, 5, 10, 10)
    assert b.target_cover(c) == (5 * 5) / (10 * 10)
    # 不相交(相切)
    c = BoundingBox(10, 10, 10, 10)
    assert b.target_cover(c) == 0
    # 不相交(完全分离)
    c = BoundingBox(12, 12, 10, 10)
    assert b.target_cover(c) == 0
