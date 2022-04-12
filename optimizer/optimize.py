# -*- coding: utf-8 -*-

import shutil
import optuna
import subprocess
import tempfile
import sys
from config import Config, Type, Scale, Param
import argparse


class Evaluator:

    def __init__(self, config: Config):
        self.config = config

    def get_score(self, root_path, filename, idx):
        name = filename.format(idx)
        filepath = "{}/1/{}/stderr".format(root_path, name)

        with open(filepath, 'r') as fin:
            return float(fin.readlines()[-1].strip())

    def collect_result(self, root_path, filename):
        return list(map(
            lambda i: self.get_score(root_path, filename, i),
            range(self.config.dataset_size)))

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
            input_arg_list.append(param.data_dir / "{}")
            dataset_range_arg_list = [
                ":::"] + list(map(lambda num: param.filename.format(num), range(self.config.dataset_size)))
            return input_arg_list + dataset_range_arg_list
        else:
            return trial.suggest_int(
                param.name, param.range_from, param.range_to)

    def __evaluate(self, trial: optuna.Trial):
        params = []
        dataset_param = []
        filename = ""
        for param in self.config.param_list:
            if param.type == Type.DATASET:
                dataset_param = (self.__suggest(trial, param))
                filename = param.filename
            else:
                params.append(self.__suggest(trial, param))

        with tempfile.TemporaryDirectory() as tmpdir:

            # do experiment
            parallel_arg_list = ['parallel', '--progress',
                                 '-j11', '--silent', '--result', tmpdir]
            exec_arg_list = [self.config.exec_path] + \
                list(map(str, params)) + dataset_param

            subprocess.run(parallel_arg_list + exec_arg_list,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            result = self.collect_result(tmpdir, filename)

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
