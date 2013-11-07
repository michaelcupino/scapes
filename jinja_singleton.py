# class inherits from type to create a metaclass
class _Singleton(type):

    """A Singleton Metaclass
    Typical usage:
    class Test():
        __metaclass__ = _Singleton
        x = 1"""

    # keep track of instances by class
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# requires jinja2
class J2EnviornmentSingleton(jinja2.Enviornment):
    """A singleton of jinja2.Enviornment"""
    __metaclass__ = _Singleton

