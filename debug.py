import pprint, traceback, inspect

pp = pprint.PrettyPrinter(indent=4)

class Debug:

    DEBUG = True
    IS_DEBUG = __debug__ # If debug checks should be made
    PRINT_DTORS = True
    LOG_FUNCTION = None

    def __init__(self, *args):
        if args:
            Debug.print(*args, ctor=True)

    def setDebug(self, on):
        self.DEBUG = on
    
    def say(self, *s, **kwargs):
        if not self.DEBUG:
            return
        stack = inspect.stack()
        frame = stack[1][0]
        lineno = stack[1][2]
        the_class = frame.f_locals["self"].__class__
        the_method = frame.f_code.co_name
        # the_lineno = frame.f_code.co_firstlineno
        if kwargs.get('time', False):
            s = s + (time.time(),)
        s = Debug.cleanArgs(*s)
        args = (('%s.%s:%i' % (the_class.__name__, the_method, lineno)).ljust(35),) + s
        if Debug.LOG_FUNCTION:
            Debug.LOG_FUNCTION(*args)
        else:
            print(*args)

    here = say

    def todo(self, *s):
        if not self.DEBUG:
            return
        stack = inspect.stack()
        frame = stack[1][0]
        lineno = stack[1][2]
        the_class = frame.f_locals["self"].__class__
        the_method = frame.f_code.co_name
        # the_lineno = frame.f_code.co_firstlineno
        s = Debug.cleanArgs(*s)
        args = (('%s.%s:%i TODO:' % (the_class.__name__, the_method, lineno)).ljust(35),) + s
        if Debug.LOG_FUNCTION:
            Debug.LOG_FUNCTION(*args)
        else:
            print(*args)

    @staticmethod
    def repr(x):
        """ Return a clean representation of an object. """
        if type(x) == str:
            return x
        if type(x) == type:
            return x
        else:
            return x.__repr__().replace('PyQt5.QtCore.', '').replace('PyQt5.QtGui.', '')

    @staticmethod
    def cleanArgs(*args):
        """ Return a cleaned up string from a list of args. """
        global pp
        ret = ()
        for index, i in enumerate(args):
            if isinstance(i, dict) or isinstance(i, list):
                if index == 0:
                    ret += ('\n' + pp.pformat(i) + '\n',)
                else:
                    ret += (pp.pformat(i),)
            else:
                ret += (Debug.repr(i),)
        return ret
    
    @staticmethod
    def pretty(x, exclude=[], noNone=True):
        if not isinstance(exclude, list):
            exclude = [exclude]
        s = ''
        if isinstance(x, dict):
            parts = []
            for k, v in x.items():
                if k not in exclude and (noNone and v is not None):
                    parts.append('%s: %s' % (k, Debug.repr(v)))
            s += ', '.join(parts)
        return s

    @staticmethod
    def print(*s, ctor=False):
        if not Debug.DEBUG:
            return
        stack = inspect.stack()
        if ctor:
            frame = stack[2][0]
            lineno = stack[2][2]
        else:
            frame = stack[1][0]
            lineno = stack[1][2]
        the_method = frame.f_code.co_name
        # the_lineno = frame.f_code.co_firstlineno
        s = Debug.cleanArgs(*s)
        args = (('%s.%s:%i' % (__name__, the_method, lineno)).ljust(35),) + s
        print(*args)

    def stack(self):
        if not self.DEBUG:
            return
        traceback.print_stack()
        print()

    @staticmethod
    def showPoint(path, point, name, coords=False):
        OFFSET = 2.0
        def S(p):
            return '(%.1f, %.1f)' % (point.x(), point.y())
        dot = QRectF(0, 0, OFFSET, OFFSET)
        dot.moveCenter(point)
        path.addRoundedRect(dot, OFFSET / 2, OFFSET / 2)
        if coords is True:
            s = name + ': ' + S(point)
        else:
            s = name
        path.addText(point + QPointF(OFFSET, OFFSET), QFont('Helvetica', 6, 0), s)
