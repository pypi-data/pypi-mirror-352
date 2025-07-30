from .profile_data import PiData


class PiMethod(PiData):
    def __init__(self, o, name_hash):
        PiData.__init__(self, o)
        self.type = PiData.TYPE_METHOD
        self.key = name_hash
        self.start_cpu = o.get_method_thread_cpu_time(o.start_cpu_time)
        self.end_time = 0
        self.end_cpu = 0
        self.elapsed_time = 0
        self.error_hash = 0

    def get_type(self):
        return self.type

    def print_description(self):
        print(' ' * (self.parent_index + 4), 'Method', "index:", self.index, "pidx:", self.parent_index,
              "key:", self.key, "start_time:", self.start_time, "start_cpu:", self.start_cpu, "end_time:",
              self.end_time, "end_cpu:", self.end_cpu, "error_hash:", self.error_hash)


class PiMethodParameter(PiData):
    def __init__(self, o, method_name_hash, method_param_text):
        PiData.__init__(self, o)
        self.type = PiData.TYPE_METHOD_PARAM
        self.key = method_name_hash
        self.start_time = o.get_current_point_time()
        self.param = method_param_text

    def get_type(self):
        return self.type

    def print_description(self):
        print(' ' * (self.parent_index + 4), 'MethodParameter', "index:", self.index, "pidx:", self.parent_index,
              "key:", self.key, "start_time:", self.start_time, "param:", self.param)


class PiMethodReturn(PiData):
    def __init__(self, o, method_name_hash, method_ret_text):
        PiData.__init__(self, o)
        self.type = PiData.TYPE_METHOD_RETURN
        self.key = method_name_hash
        self.start_time = o.get_current_point_time()
        self.ret = method_ret_text

    def get_type(self):
        return self.type

    def print_description(self):
        print(' ' * (self.parent_index + 4), 'MethodParameter', "index:", self.index, "pidx:", self.parent_index,
              "key:", self.key, "start_time:", self.start_time, "ret:", self.ret)
