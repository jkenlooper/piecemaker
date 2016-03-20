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
        return tuple(p.split(','))

class Path(object):
    def invert(self, t):
        return (t[0], t[1]*-1)
    def point(self, t):
        return ','.join([str(x) for x in t])
    tongue_length = 0.30 # 0.30 including shoulder
    def __init__(self, start=(0,0), width=155.0, out=None):
        if out == None:
            self.out = choice(COIN)
        #self.out = False
        #self.out = True
        self._middle = width/2
        left_shoulder = (uniform(0.27,0.47),uniform(0.06,0.18)) # 0.37, 0.08
        right_shoulder = (uniform(0.27,0.47),uniform(0.06,0.18)) # 0.37, 0.08
        self._start = retuple(start)
        self.width = width # total width of the path
        self._stop = (width,0)
        self._anchor_left = (
                width*left_shoulder[0],
                width*left_shoulder[1])
        self._anchor_center = (
                (width/2) - self._anchor_left[0]
                ,(width*self.tongue_length)-(left_shoulder[1]*width))
        self._anchor_right = (
                (self._anchor_left[0]+self._anchor_center[0]) - width*right_shoulder[0],
                ((self._anchor_left[1]+self._anchor_center[1]) - width*right_shoulder[1])*-1)
        self._relative_stop = (
                width-(self._anchor_left[0]+self._anchor_center[0]+self._anchor_right[0]),
                (self._anchor_left[1]+self._anchor_center[1]+self._anchor_right[1])*-1)
        self._relative_middle = (
                self._middle,
                (self._middle + width*0.05)*-1)
                #(self._middle + width*0.13)*-1)

        # relative to anchor_left
        self._control_start_a = (
                0.16*width,
                0)
        self._control_start_b = (
                (0.07*width)+self._anchor_left[0],
                (0.05*width)*-1)

        self._control_left_a = (
                (0.06*width)*-1,
                uniform(0.31,0.91)*self._anchor_center[1])
        self._control_left_b = (
                0,
                self._anchor_center[1])

        # relative to anchor_right
        self._control_center_a = (
                self._anchor_right[0],
                0)
        self._control_center_b = (
                0.06*width+self._anchor_right[0],
                uniform(0.31,0.91)*self._anchor_right[1])

        self._control_right_a = (
                (0.06*width)*-1,
                (0.13*width)*-1)
        self._control_right_b = (
                0.21*width,
                (0.08*width)*-1)

    @Property
    def start():
        doc = "first anchor point in path"
        def fget(self):
            return self.point(self._start)
        def fset(self, p):
            self._start = retuple(p)
        return locals()

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

    @Property
    def relative_middle():
        doc = "last anchor point in path relative to previous anchor"
        def fget(self):
            return self.point(self._relative_middle)
        def fset(self, p):
            self._relative_middle = retuple(p)
        return locals()

    @Property
    def stop():
        doc = "last anchor point in path"
        def fget(self):
            return self.point(self._stop)
        def fset(self, p):
            self._stop = retuple(p)
        return locals()

    def render(self):
        " Create all the 'curveto' points "
        if not self.out:
            m = list(self._relative_middle)
            m[1] = m[1]*-1
            self._relative_middle = tuple(m)

        return u'c %(control_start_a)s %(control_start_b)s %(anchor_left)s c %(control_left_a)s %(control_left_b)s %(anchor_center)s c %(control_center_a)s %(control_center_b)s %(anchor_right)s c %(control_right_a)s %(control_right_b)s %(relative_stop)s' % ({
            'start':self.start,
            'control_start_a':self.control_start_a,
            'control_start_b':self.control_start_b,
            'control_left_a':self.control_left_a,
            'control_left_b':self.control_left_b,
            'anchor_left':self.anchor_left,
            'control_center_a':self.control_center_a,
            'control_center_b':self.control_center_b,
            'anchor_center':self.anchor_center,
            'control_right_a':self.control_right_a,
            'control_right_b':self.control_right_b,
            'anchor_right':self.anchor_right,
            'relative_stop':self.relative_stop,
            'relative_middle':self.relative_middle,
            })

class VerticalPath(Path):
    " top to bottom "
    def point(self, t):
        t = (t[1], t[0])
        return ','.join([str(x) for x in t])

class HorizontalPath(Path):
    " left to right "
    def point(self, t):
        t = (t[0], t[1]*-1)
        return ','.join([str(x) for x in t])
