import shutil
import os
import io
import logging
import logging.handlers
import time
import re
import sys

import yaml_util

# get path of current py file and directory
cur_file  = os.path.abspath(__file__)
cur_dir = cur_file.rsplit("/", 1)[0] 

sys.path.append(cur_dir)

JAVA_ARGS = "-Xmx4g -Xms1g"

NOT_IN_GITEE = ["Artificial-Intelligence-Deep-Learning-Machine-Learning-Tutorials", "deepnlp"]

# refer to: 
# 1) An empirical study on TensorFlow program bugs
# 2) Taxonomy of real faults in deep learning systems
# 1) bug, fix, wrong, error, nan, inf, issue, fault, fail, crash
# 2) ("fix" or "solve") and ("bug" or "issue" or "problem" or "defect" or "error").
KEYWORDS = [
    'bug', 'defect', 'issue', 'problem', 'error', 'fault', 'fail', 'wrong', 'nan', 'inf', 'crash',
    'fix', 'solve', 'repair'
]

def get_top_200_repos(dataset_yaml_file, logger = None):
    repo_dict_ori = utils_yaml.read_yaml(dataset_yaml_file)
    not_in_gitee_cnt = 0
    repo_dict = {}

    repo_cnt = 0
    for index, info_dict in repo_dict_ori.items():
        repo_name = info_dict["repo.name"]
        if repo_name in NOT_IN_GITEE:
            not_in_gitee_cnt += 1
            if logger:
                logger.warn(f"No.{index} repo: {info_dict['repo.name']} is not in gitee.")
            continue
        repo_dict[index] = info_dict
        repo_cnt += 1
        if repo_cnt == 200:
            break

    if not_in_gitee_cnt != len(NOT_IN_GITEE):
        raiseExp(f"not_in_gitee_cnt {not_in_gitee_cnt} != len(NOT_IN_GITEE) {len(NOT_IN_GITEE)}")

    return repo_dict

def rm_file(a_file):
    if os.path.exists(a_file):
        os.remove(a_file)

def mk_dir_from_file_path(file_path):
    # assert os.path.isfile(file_path), f"{file_path} is not a file"
    dir_path = file_path.rsplit("/", 1)[0] 
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def mk_dir_from_dir_path(dir_path):
    # assert os.path.isdir(dir_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def init_logger(cur_file_name, cur_dir_path):
    logger = logging.getLogger(cur_file_name)

    if (logger.hasHandlers()):
        logger.handlers.clear()
    
    logger.setLevel(logging.DEBUG)

    # set two handlers
    log_file = "[log]-{}.log".format(cur_file_name)
    log_file_abs = os.path.join(cur_dir_path, log_file)
    # 1) first type
    fileHandler = logging.FileHandler(log_file_abs, mode = 'w')
    fileHandler.setLevel(logging.DEBUG)

    # 2) second type
    rotate_file_handler = logging.handlers.RotatingFileHandler(log_file_abs, mode='w', maxBytes=5*1024*1024,  
                                 backupCount=100, encoding=None, delay=0)
    rotate_file_handler.setLevel(logging.DEBUG)
    
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    
    # a good and standard one
    # formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s [%(filename)s:%(lineno)d]', datefmt='%Y-%m-%d %H:%M:%S')
    # a simple one
    formatter = logging.Formatter('[%(message)s]')
    
    consoleHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    rotate_file_handler.setFormatter(formatter)

    # logger.addHandler(fileHandler)
    logger.addHandler(rotate_file_handler)
    logger.addHandler(consoleHandler)
    
    return logger

def init_file_logger(cur_file_name, cur_dir_path):
    logger = logging.getLogger(cur_file_name)
    logger.setLevel(logging.DEBUG)

    # set two handlers
    log_file = "[log]-{}.log".format(cur_file_name)
    # rm_file(log_file)
    fileHandler = logging.FileHandler(os.path.join(cur_dir_path, log_file), mode = 'w')
    fileHandler.setLevel(logging.DEBUG)

    # set formatter
    # formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter('')
    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    
    return logger

def printInfo(msg, logger = None):
    string = f"{msg}"
    print(string)
    if logger is not None:
        logger.info(string)

def read_file(path):
    if not os.path.exists(path):
        raise Exception("{} does not exists.".format(path))
        return []
    """
    read lines from file
    """
    stripped_lines = []
    with io.open(path, encoding = 'utf-8', mode = 'r') as f:
            lines = f.readlines()
            for line in lines:
                stripped_lines.append(line.strip())
    return stripped_lines

def read_file_no_strip(path):
    if not os.path.exists(path):
        raise Exception("{} does not exists.".format(path))
        return []
    """
    read lines from file
    """
    stripped_lines = []
    with io.open(path, encoding = 'utf-8', mode = 'r') as f:
            lines = f.readlines()
            for line in lines:
                stripped_lines.append(line)
    return stripped_lines

def read_file_to_str(path):
    string = ""
    with io.open(path, encoding = 'utf-8', mode = 'r') as f:
        string = f.read()
    return string

def raiseExp(msg):
    raise Exception(f"Exception: {msg}")

def write_str_to_file(file_path, line, append = True):
    mk_dir_from_file_path(file_path)

    if append:
        with open(file_path,'a+') as f:
            f.write(line)
    else:
        with open(file_path,'w') as f:
            f.write(line)

def write_line_to_file(file_path, line, line_break = True, append = True):
    mk_dir_from_file_path(file_path)

    if line_break:
        line = line + "\n"

    if append:
        with open(file_path,'a+') as f:
            f.write(line)
    else:
        with open(file_path,'w') as f:
            f.write(line)

def write_list_to_file(file_path, lines_list, append = True, line_break = True):
    mk_dir_from_file_path(file_path)
    
    if append:
        with open(file_path,'a+') as f:
            for line in lines_list:
                if line_break:
                    line = line + "\n"
                f.write(line)
    else:
        with open(file_path,'w') as f:
            for line in lines_list:
                if line_break:
                    line = line + "\n"
                f.write(line)

def write_dict_to_file(file_path, lines_dict, append = True, line_break = True):
    mk_dir_from_file_path(file_path)
    
    mode = "w"
    if append:
        mode = "a+"
    with open(file_path,mode) as f:
        for key, value in lines_dict.items():
            line = f"{key}  {value}"
            if line_break:
                line = line + "\n"
            f.write(line)

def list_all_files(dir_path, file_type = ""): #file_type -> postfix  e.g., .yml
    files_list = []
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isdir(file_path):
            print("file_path: {} is dir".format(file_path))
        
        if os.path.isfile(file_path):
            if file_type == "":
                files_list.append(file_path)
            else:
                if file_path[-len(file_type) : ] == file_type:
                    files_list.append(file_path)
    return files_list

def remove_all_content_in_dir(dir_path, logger = None):
    printInfo(f"remove all content in {dir_path}", logger)

    if len(dir_path) < 10:
        raiseExp("[Warning] len(dir_path) < 10.")

    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

def get_dirpath_from_file_abspath(file_abspath):
    return file_abspath.rsplit("/", 1)[0] 

def get_filename_from_file_abspath(file_abspath):
    return file_abspath.rsplit("/", 1)[1] 

def get_cur_path(file_attr):
    """
    example: 
    cur_file_abspath, cur_dir_path, cur_file_name = utils.get_cur_path(__file__)
    """
    cur_file_abspath  = os.path.abspath(file_attr)
    cur_dir_path = cur_file_abspath.rsplit("/", 1)[0] 
    cur_file_name = cur_file_abspath.rsplit("/", 1)[1] [:- len(".py")]
    return cur_file_abspath, cur_dir_path, cur_file_name

def sleep(sleep_time_in_seconds, logger = None):
    if logger is not None:
        logger.info("Sleep Start : %s" % time.ctime())
    time.sleep(sleep_time_in_seconds)
    if logger is not None:
        logger.info("Sleep End : %s" % time.ctime())

def contain_keywords(message, keywords, logger = None):
    contained_keywords = []
    for keyword in keywords:
        # logger.debug(f"check keyword: {keyword}, \nmessage:{message}, {type(message)}")
        # if isinstance(message, bytes):
        #     logger.warn("the commit message type is bytes rather than string. message: {message}")
        #     message = message.decode('utf-8')
        result = re.search(keyword, message, re.I)
        if result is not None:
            # anti-pattern 
            if "Merge pull request" in message:
                if logger:
                    logger.warn(f"Merge pull request is found.")
                continue

            contained_keywords.append(keyword)
            span = result.span()
            if logger:
                logger.info(f"current commit message contain keyword: {keyword}. Corresponding match string is: {message[span[0]:]}")
    return contained_keywords

def contain_complete_keywords(message_word_list, keywords):
    contained_keywords = []
    contained_keywords_complete = []
    for word in message_word_list:
        if word != word.strip():
            raiseExp("word != word.strip().")
        for keyword in keywords:
            if keyword == word:
                contained_keywords_complete.append(word)
            elif keyword in word:
                contained_keywords.append(word)
    return contained_keywords, contained_keywords_complete

def isDevNull(file_name):
    name = "/dev/null"
    if file_name.strip() == name:
        return True
    return False

def get_all_dir_paths(folder):
    if not os.path.exists(folder):
        raiseExp(f"{folder} does not exist!")

    dir_paths = []
    for dir_name in os.listdir(folder):
        dir_path = os.path.join(folder, dir_name)
        if os.path.isdir(dir_path):
            dir_paths.append(dir_path)
    return dir_paths

def get_all_file_paths(dir_path, posfix):
    all_file_paths = []
    for name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, name)

        if os.path.isfile(file_path) and file_path.endswith(posfix):
            all_file_paths.append(file_path)
    return all_file_paths

def get_all_files_recursive(dir_path, postfix = ""):
    assert postfix != ""
    import glob
    file_paths = []
    pattern = f'{dir_path}/**/*{postfix}'
    file_paths = glob.glob(pattern, recursive=True)
    return file_paths
    
def add_to_list(node, node_list):
    if node not in node_list:
        node_list.append(node)

def add_to_dict(node_to_add, edges, node):
    if node not in edges.keys():
        edges[node] = [node_to_add]
    else:
        if node_to_add not in edges[node]:
            edges[node].append(node_to_add)
    
def get_subdir_paths(dir_path):
    subdir_paths = []
    for dir_name in os.listdir(dir_path):
        subdir_path = os.path.join(dir_path, dir_name)
        if os.path.isdir(subdir_path):
            subdir_paths.append(subdir_path)
    return subdir_paths

def init_clean_dir(dir):
    mk_dir_from_dir_path(dir)
    remove_all_content_in_dir(dir)

def get_dir_name(dir_path):
    if dir_path.endswith("/"):
        dir_path = dir_path[:-1]
    
    dir_path = dir_path.rsplit("/", 1)[-1]

    return dir_path

def get_real_repo_name(org_repo_name):
    dataset_yaml_path = "/mnt/2020-11-API-misuse/Repair_API_Misuse/api-misuse-repair/1_collect_dl_repos/repo_collection/dataset-v4/dataset.yml"
    dataset_dict = yaml_util.read_yaml(dataset_yaml_path)
    name_dict = {}
    for number, info_dict in dataset_dict.items():
        # repo.owner: EleutherAI
        # repo.name: gpt-neo
        org_repo_name_cur = info_dict['repo.owner'] + "_" + info_dict['repo.name']
        if org_repo_name == org_repo_name_cur:
            return info_dict['repo.name']
    raise Exception(f"{org_repo_name} cannot be matched!")

def get_real_repo_name_dict():
    dataset_yaml_path = "/mnt/2020-11-API-misuse/Repair_API_Misuse/api-misuse-repair/1_collect_dl_repos/repo_collection/dataset-v4/dataset.yml"
    dataset_dict = yaml_util.read_yaml(dataset_yaml_path)
    name_dict = {}
    for number, info_dict in dataset_dict.items():
        # repo.owner: EleutherAI
        # repo.name: gpt-neo
        org_repo_name_cur = info_dict['repo.owner'] + "_" + info_dict['repo.name']
        if 'fork_repo_name' in info_dict.keys():
            name_dict[org_repo_name_cur] = info_dict['fork_repo_name']
    return name_dict

