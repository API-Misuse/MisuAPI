import subprocess
import logging
import re

import sys, os

import general_util
cur_file_dir = os.path.abspath(__file__).rsplit("/", 1)[0]
sys.path.append(cur_file_dir)

import config
JAVA_ARGS = config.JAVA_ARGS

cur_file_abspath, cur_dir_path, cur_file_name = general_util.get_cur_path(__file__)
logger_cmd = general_util.init_file_logger(cur_file_name, cur_dir_path)

def run_cmd_with_output(cmd, logger = None):
    """
    run cmd and print output.
    refererences : 
    1) https://stackoverflow.com/questions/40222793/python-subprocess-check-output-stderr-usage
    2) https://www.askpython.com/python-modules/python-system-command
    """

    if not logger:
        logger = logger_cmd

    if logger:
        logger.info(f"cmd: {cmd}")

    p = subprocess.run(cmd, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.stdout.decode('utf-8')

    error = p.stderr.decode('utf-8')
    if len(error) > 0 and error.strip() != "Picked up JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF8":
        logger.error(f"output error: {error}")

    return output

def run_cmd_without_output(cmd, logger = None):
    if logger:
        logger.info(f"cmd: {cmd}")

    res = subprocess.call(cmd, shell = True)