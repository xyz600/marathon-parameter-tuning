import os
import yaml
from enum import Enum
from typing import List


class Scale(Enum):
    LINEAR = 0,
    LOG = 1

    def construct(scale_str: str):
        if scale_str == "log":
            return Scale.LOG
        elif scale_str == "linear":
            return Scale.LINEAR
        else:
            raise ValueError("inappropreate scale parameter")


class Type(Enum):
    FLOAT = 0,
    INT = 1

    def construct(type_str: str):
        if type_str == "float":
            return Type.FLOAT
        elif type_str == "int":
            return Type.INT
        else:
            raise ValueError("inappropreate type parameter")


class Param:
    def __init__(self):
        self.name: str = ""
        self.type: Type = Type.FLOAT
        self.range_from: float = 0.0
        self.range_to: float = 1.0
        self.scale: Scale = Scale.LINEAR


class Config:

    def _validate(self):

        for param in self.param_list:

            assert(param.range_from < param.range_to)
            if param.scale == Scale.LOG:
                assert(0 < param.range_from)
                assert(0 < param.range_to)

        assert(os.path.exists(self.dataset_template.format(0)))
        assert(os.path.exists(self.dataset_template.format(self.dataset_size - 1)))

    def __init__(self, yaml_filepath: str):
        with open(yaml_filepath) as fin:
            obj = yaml.safe_load(fin)

            self.param_list: List[Param] = []

            for param_yml in obj["param_list"]:
                param = Param()
                param.name = param_yml["name"]
                param.type = Type.construct(param_yml["type"])
                if param.type == Type.FLOAT:
                    param.range_from = float(param_yml["range_from"])
                    param.range_to = float(param_yml["range_to"])
                else:
                    param.range_from = int(param_yml["range_from"])
                    param.range_to = int(param_yml["range_to"])
                param.scale = Scale.construct(param_yml["scale"])
                self.param_list.append(param)

            self.dataset_template = obj["dataset_template"]
            self.number_of_iteration = int(obj["number_of_iteration"])
            self.dataset_size = int(obj["dataset_size"])
            self.exec_path = obj["exec_path"]
            self.parallel_job_size = obj["parallel_job_size"]

        self._validate()
