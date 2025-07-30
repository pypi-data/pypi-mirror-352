

class ClassInfo:
    def __init__(self, name, node_type, super_class_name):
        self.name = name
        self.node_type = node_type
        self.super_class_name = super_class_name

    def to_json(self):
        ret = self.__dict__
        return ret
