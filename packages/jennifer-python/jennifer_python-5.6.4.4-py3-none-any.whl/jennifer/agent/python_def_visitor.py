# -*- coding: utf-8 -*-
import os
import ast

try:
    from functools import lru_cache
except ImportError:
    def lru_cache():
        def decorating_function(func):
            def func_wrapper(arg):
                return func(arg)
            return func_wrapper
        return decorating_function


class PythonDefVisitor:
    def __init__(self):
        self.defs = {}
        self.current_file = ''

    def visit_class_def(self, node):
        self.defs[self.current_file].append(node.name)
        for def_node in node.body:
            if hasattr(def_node, 'name'):
                self.defs[self.current_file].append(node.name + "." + def_node.name)

    def visit_function_def(self, node):
        self.defs[self.current_file].append(node.name)

    def visit_async_function_def(self, node):
        self.defs[self.current_file].append(node.name)

    @lru_cache()
    def list_defs(self, dir_path):
        self.defs = {}
        node_iter = ast.NodeVisitor()

        node_iter.visit_ClassDef = self.visit_class_def
        node_iter.visit_FunctionDef = self.visit_function_def
        node_iter.visit_AsyncFunctionDef = self.visit_async_function_def

        for root, dirnames, filenames in os.walk(dir_path):
            for file_name in filenames:
                if not file_name.endswith(".py"):
                    continue

                file_path = os.path.join(root, file_name)
                with open(file_path) as f:
                    self.current_file = file_path
                    self.defs[self.current_file] = []
                    node_iter.visit(ast.parse(f.read()))

        return self.defs

    def find_def(self, def_name):
        list_files = []

        for file, defs in self.defs.items():
            if '*' in def_name:
                for d in defs:
                    if d.startswith(def_name[:-1]):
                        list_files.append(file)
            else:
                if def_name in defs:
                    list_files.append(file)

        return ', '.join(list_files)
