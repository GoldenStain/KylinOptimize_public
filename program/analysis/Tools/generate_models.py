"""
The tool to generate the AI models.
Usage: python3 generate_models.py [-h] [-d] [-m] [-s] [-t]
"""
import argparse
import ast
import os
import sys
import subprocess

FILE_PATH = os.path.realpath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_PATH, '..', '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# from analysis.optimizer.workload_characterization import WorkloadCharacterization
from analysis.optimizer.app_characterization import AppCharacterization


def main(csv_path, model_path, feature_selection, search, model_type):
    """
    generate AI models
    :param csv_path: csv path
    :param model_path: model path
    :param feature_selection: select feature model, default value is False
    :param search: enable the grid search for model train, default value is False
    :return: None
    """
    try:
        processor = AppCharacterization(model_path, mode="train")
        processor.train(csv_path, feature_selection, search, model=model_type)
    except subprocess.CalledProcessError as e:
            print(f"Error executing perf command: {e.output}")
            print(f"Stderr: {e.stderr}")
            raise



if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description="generate AI models")
    ARG_PARSER.add_argument('-d', '--csv_path', metavar='DATA',
                            default=FILE_PATH + "/../analysis/dataset", help='input csv path')
    ARG_PARSER.add_argument('-m', '--model_path', metavar='MODEL',
                            default=FILE_PATH + "/../analysis/models", help='input model path')
    ARG_PARSER.add_argument('-s', '--select', metavar='SELECT',
                            type=ast.literal_eval, default=False,
                            help='whether feature models to be generate, True or False')
    ARG_PARSER.add_argument('-g', '--search', metavar='SEARCH',
                            default=False, help='wether enable the parameter space search')
    ARG_PARSER.add_argument('-t', '--model_type', metavar='TYPE',
                            choices=['rf', 'svm', 'xgb'],
                            default='rf', help='model type to train (default: rf)')
    ARGS = ARG_PARSER.parse_args()

    main(ARGS.csv_path, ARGS.model_path, ARGS.select, ARGS.search, ARGS.model_type)
