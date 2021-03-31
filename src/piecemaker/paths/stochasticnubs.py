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


class Path(object):
    anchor_extremes = ["anchor_left-right-down", "none"]

    def invert(self, t):
        return (t[0], t[1] * -1)

    def point(self, t):
        return ",".join([str(x) for x in t])

    def __init__(self, width=155.0, height=155.0, out=None):
        if out is None:
            self.out = choice(COIN)
        # self.out = True

        anchor_extreme = choice(self.anchor_extremes)
        # anchor_extreme = self.anchor_extremes[0]

        self.width = width  # total width of the path
        self.height = height  # total height of the path
        if anchor_extreme == "anchor_left-right-down":
            self._anchor_left = (
                width * uniform(0.25, 0.50),
                height * uniform(0.0, 0.15),
            )
        else:
            self._anchor_left = (width * 0.25, height * 0)
        self._anchor_center = (
            (width * 0.5) - self._anchor_left[0],
            (height * 0.30) - self._anchor_left[1],
        )
        self._anchor_right = (
            (width * 0.75) - (self._anchor_left[0] + self._anchor_center[0]),
            (height * 0) - (self._anchor_left[1] + self._anchor_center[1]),
        )
        if anchor_extreme == "anchor_left-right-down":
            self._relative_stop = (
                width
                - (
                    self._anchor_left[0]
                    + self._anchor_center[0]
                    + self._anchor_right[0]
                ),
                (height * 0.0)
                - (
                    self._anchor_left[1]
                    + self._anchor_center[1]
                    + self._anchor_right[1]
                ),
            )
        else:
            self._relative_stop = (
                width
                - (
                    self._anchor_left[0]
                    + self._anchor_center[0]
                    + self._anchor_right[0]
                ),
                (self._anchor_left[1] + self._anchor_center[1] + self._anchor_right[1])
                * -1,
            )

        if anchor_extreme == "anchor_left-right-down":
            self._control_start_a = (width * 0.30, height * 0.2)
        else:
            self._control_start_a = (0.25 * width, 0)

        if anchor_extreme == "anchor_left-right-down":
            self._control_start_b = (
                width * 0.0,
                height * 0.3,
            )
        else:
            self._control_start_b = (0.25 * width, 0)

        if anchor_extreme == "anchor_left-right-down":
            self._control_left_a = (0, 0)
        else:
            self._control_left_a = (
                (width * 0.25) - (self._anchor_left[0]),
                (height * 0.15) - (self._anchor_left[1]),
            )

        self._control_left_b = (
            # (width * uniform(0.25, 0.50)) - (self._anchor_left[0]),
            # (height * uniform(0.20, 0.40)) - (self._anchor_left[1])
            (width * 0.25) - (self._anchor_left[0]),
            (height * 0.30) - (self._anchor_left[1]),
        )

        self._control_center_a = (
            (width * 0.75) - (self._anchor_left[0] + self._anchor_center[0]),
            (height * 0.30) - (self._anchor_left[1] + self._anchor_center[1]),
        )
        self._control_center_b = (
            (width * 0.35) - (self._anchor_left[0] + self._anchor_center[0]),
            (height * 0.0) - (self._anchor_left[1] + self._anchor_center[1]),
        )

        self._control_right_a = (
            (width * uniform(0.80, 0.82))
            - (self._anchor_left[0] + self._anchor_center[0] + self._anchor_right[0]),
            (height * uniform(0.10, -0.15))
            - (self._anchor_left[1] + self._anchor_center[1] + self._anchor_right[1]),
        )
        self._control_right_b = (
            (width * uniform(0.85, 1.0))
            - (self._anchor_left[0] + self._anchor_center[0] + self._anchor_right[0]),
            (height * uniform(-0.15, 0.15))
            - (self._anchor_left[1] + self._anchor_center[1] + self._anchor_right[1]),
        )

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
