# -*- coding: utf-8 -*-

import optuna
import subprocess
import tempfile
import sys
from config import Config, Type, Scale, Param
import argparse


class Evaluator:

    def __init__(self, config: Config):
        self.config = config

    def get_filepath(self, root_path, idx):
        return "{}/1/{}/stderr".format(root_path, idx)

    def get_score(self, root_path, idx):
        with open(self.get_filepath(root_path, idx), 'r') as fin:
            return float(fin.readlines()[-1].strip())

    def collect_result(self, root_path):
        result = []
        for i in range(self.config.dataset_size):
            result.append(self.get_score(root_path, i))
        return result

    def __suggest(self, trial: optuna.Trial, param: Param):
        if param.type == Type.FLOAT:
            if param.scale == Scale.LOG:
                return trial.suggest_loguniform(
                    param.name, param.range_from, param.range_to)
            else:
                return trial.suggest_uniform(
                    param.name, param.range_from, param.range_to)
        elif param.type == Type.STRING:
            return param.value
        elif param.type == Type.DATASET:
            input_arg_list = ["<"] if param.is_redirect else []
            input_arg_list.append(param.template)
            dataset_range_arg_list = [":::"] + \
                list(map(str, range(self.config.dataset_size)))
            return input_arg_list + dataset_range_arg_list
        else:
            return trial.suggest_int(
                param.name, param.range_from, param.range_to)

    def __evaluate(self, trial: optuna.Trial):
        params = []
        dataset_param = []
        for param in self.config.param_list:
            if param.type == Type.DATASET:
                dataset_param = (self.__suggest(trial, param))
            else:
                params.append(self.__suggest(trial, param))

        tmpdir = tempfile.TemporaryDirectory()
        # do experiment
        parallel_arg_list = ['parallel', '--progress',
                             '-j11', '--silent', '--result', tmpdir.name]
        exec_arg_list = [self.config.exec_path] + \
            list(map(str, params)) + dataset_param

        subprocess.run(parallel_arg_list + exec_arg_list,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        result = self.collect_result(tmpdir.name)
        tmpdir.cleanup()

        return sum(result) / len(result)

    def doit(self):
        study = optuna.create_study(direction='minimize')
        study.optimize(self.__evaluate, n_trials=self.config.number_of_iteration,
                       n_jobs=self.config.parallel_job_size)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_path", help="configuration path for parameter tuning")
    args = parser.parse_args()

    config = Config(args.config_path)

    evaluator = Evaluator(config)
    evaluator.doit()
