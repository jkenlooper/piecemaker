from random import uniform, choice

COIN = (True, False)


def Property(func):
    """ http://adam.gomaa.us/blog/the-python-property-builtin/ """
    return property(**func())


def retuple(p):
    """ convert point str back to tuple if necessary """
    if isinstance(p, tuple):
        return p
    elif isinstance(p, str):
        return tuple(p.split(","))


class InterlockingCurvePoints:
    @staticmethod
    def get_curve_points(width, height):
        _anchor_left = (width * uniform(0.34, 0.43), height * uniform(-0.02, 0.22))

        _anchor_center = (
            (width * 0.50) - _anchor_left[0],
            (height * uniform(0.24, 0.34)) - _anchor_left[1],
        )
        _anchor_right = (
            width * uniform(0.57, 0.66) - (_anchor_left[0] + _anchor_center[0]),
            height * uniform(-0.02, 0.22) - (_anchor_left[1] + _anchor_center[1]),
        )
        _relative_stop = (
            width - (_anchor_left[0] + _anchor_center[0] + _anchor_right[0]),
            (height * 0.0) - (_anchor_left[1] + _anchor_center[1] + _anchor_right[1]),
        )

        # relative to anchor_left
        _control_start_a = (
            width * uniform(0.05, 0.29),
            height * 0.0,
        )
        _control_start_b = (
            (width * 0.07) + _anchor_left[0],
            (height * -0.05),
        )

        _control_left_a = (
            (width * -0.06),
            uniform(0.21, 1.01) * _anchor_center[1],
        )
        _control_left_b = (0, _anchor_center[1])

        # relative to anchor_right
        _control_center_a = (_anchor_right[0], 0)
        _control_center_b = (
            (width * 0.06) + _anchor_right[0],
            uniform(0.21, 1.01) * _anchor_right[1],
        )

        _control_right_a = (
            (width * -0.06),
            (height * -0.13),
        )
        _control_right_b = (width * 0.21, height * -0.08)
        return (
            _control_start_a,
            _control_start_b,
            _anchor_left,
            _control_left_a,
            _control_left_b,
            _anchor_center,
            _control_center_a,
            _control_center_b,
            _anchor_right,
            _control_right_a,
            _control_right_b,
            _relative_stop,
        )


class Path(object):
    def invert(self, t):
        return (t[0], t[1] * -1)

    def point(self, t):
        return ",".join([str(x) for x in t])

    def __init__(self, width=155.0, height=155.0, out=None):
        if out is None:
            self.out = choice(COIN)

        self.width = width  # total width of the path
        self.height = height  # total height of the path

        (
            self._control_start_a,
            self._control_start_b,
            self._anchor_left,
            self._control_left_a,
            self._control_left_b,
            self._anchor_center,
            self._control_center_a,
            self._control_center_b,
            self._anchor_right,
            self._control_right_a,
            self._control_right_b,
            self._relative_stop,
        ) = InterlockingCurvePoints.get_curve_points(width, height)

    @Property
    def control_start_a():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_start_a))
            return self.point(self._control_start_a)

        def fset(self, p):
            self._control_start_a = retuple(p)

        return locals()

    @Property
    def control_start_b():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_start_b))
            return self.point(self._control_start_b)

        def fset(self, p):
            self._control_start_b = retuple(p)

        return locals()

    @Property
    def control_left_a():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_left_a))
            return self.point(self._control_left_a)

        def fset(self, p):
            self._control_left_a = retuple(p)

        return locals()

    @Property
    def control_left_b():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_left_b))
            return self.point(self._control_left_b)

        def fset(self, p):
            self._control_left_b = retuple(p)

        return locals()

    @Property
    def control_center_a():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_center_a))
            return self.point(self._control_center_a)

        def fset(self, p):
            self._control_center_a = retuple(p)

        return locals()

    @Property
    def control_center_b():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_center_b))
            return self.point(self._control_center_b)

        def fset(self, p):
            self._control_center_b = retuple(p)

        return locals()

    @Property
    def control_right_a():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_right_a))
            return self.point(self._control_right_a)

        def fset(self, p):
            self._control_right_a = retuple(p)

        return locals()

    @Property
    def control_right_b():
        doc = "control point in path"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._control_right_b))
            return self.point(self._control_right_b)

        def fset(self, p):
            self._control_right_b = retuple(p)

        return locals()

    @Property
    def anchor_left():
        doc = "left anchor point in tongue"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._anchor_left))
            return self.point(self._anchor_left)

        def fset(self, p):
            self._anchor_left = retuple(p)

        return locals()

    @Property
    def anchor_center():
        doc = "center anchor point in tongue"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._anchor_center))
            return self.point(self._anchor_center)

        def fset(self, p):
            self._anchor_center = retuple(p)

        return locals()

    @Property
    def anchor_right():
        doc = "right anchor point in tongue"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._anchor_right))
            return self.point(self._anchor_right)

        def fset(self, p):
            self._anchor_right = retuple(p)

        return locals()

    @Property
    def relative_stop():
        doc = "last anchor point in path relative to previous anchor"

        def fget(self):
            if not self.out:
                return self.point(self.invert(self._relative_stop))
            return self.point(self._relative_stop)

        def fset(self, p):
            self._relative_stop = retuple(p)

        return locals()

    def render(self):
        " Create all the 'curveto' points "
        return f"""
c {self.control_start_a} {self.control_start_b} {self.anchor_left}
c {self.control_left_a} {self.control_left_b} {self.anchor_center}
c {self.control_center_a} {self.control_center_b} {self.anchor_right}
c {self.control_right_a} {self.control_right_b} {self.relative_stop}
        """.strip()


class VerticalPath(Path):
    " top to bottom "

    def point(self, t):
        t = (t[1], t[0])
        return ",".join([str(x) for x in t])


class HorizontalPath(Path):
    " left to right "

    def point(self, t):
        t = (t[0], t[1] * -1)
        return ",".join([str(x) for x in t])
