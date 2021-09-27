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
        else:
            return trial.suggest_uniformint(
                param.name, param.range_from, param.range_to)

    def __evaluate(self, trial: optuna.Trial):
        params = []
        for param in self.config.param_list:
            params.append(self.__suggest(trial, param))

        tmpdir = tempfile.TemporaryDirectory()
        # do experiment
        parallel_arg_list = ['parallel', '--progress',
                             '-j11', '--silent', '--result', tmpdir.name]
        exec_arg_list = [self.config.exec_path] + list(map(str, params))
        input_redirect_arg_list = ["<", self.config.dataset_template]
        dataset_range_arg_list = [":::"] + \
            list(map(str, range(self.config.dataset_size)))

        subprocess.run(parallel_arg_list + exec_arg_list +
                       input_redirect_arg_list +
                       dataset_range_arg_list,
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
