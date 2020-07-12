

class Accessor:

    def __init__(self, cls):
        self.cls = cls


    def __get__(self, instance, owner):
        # instance.self
        # where self is CLASS attribute of owner
        # and instance is instance of owner class

        return self.cls(instance)

    def __set__(self, instance, value):
        # instance.self = value
        # where self is CLASS attribute
        return self.cls(instance).__set__(instance, value)

    def __delete__(self, instance):
        # del instance.self
        # where self is CLASS attribute
        return self.cls(instance).__delete__(instance)


def register_accessor(cls_parent, name):
    # Inspiration: https://github.com/pandas-dev/pandas/blob/c21be0562a33d149b62735fc82aff80e4d5942f5/pandas/core/accessor.py#L197
    def wrapper(cls):
        setattr(cls_parent, name, Accessor(cls))
        return cls
    return wrapper