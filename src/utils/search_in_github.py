#tf.summary.scalar

"""
this is to search code gloablly in github for collecting api usages.
"""
# ============================================ import
import os
import collections
import sys

# to import utils
cur_dir = os.path.abspath(__file__).rsplit("/", 1)[0]

sys.path.append(cur_dir)
import utils, utils_yaml, utils_github, utils_cmd

# ============================================ init
cur_file_abspath, cur_dir_path, cur_file_name = utils.get_cur_path(__file__)

logger = utils.init_logger(cur_file_name, cur_dir_path)

api_tokens = [
    "2307831934e084912e55c5bc43c01807dedda02b" # deeplearningrepos@126.com
]

# files_dir = os.path.join(cur_dir, "downloaded_files")
# utils.mk_dir_from_dir_path(files_dir)
# utils.remove_all_content_in_dir(files_dir)            

# MAX_REPO_LIMIT = 500
# MAX_REAL_REPO_LIMIT = 200
REMAIN_RATE_LIMIT = 15

def search_code():
    keyword = "tf.summary.scalar"
    keyword2 = "tf.control_dependencies"
    # https://api.github.com/search/code?q="tf.summary.scalar" "tf.control_dependencies" in:file extension:py cats pushed:<2017-10-18
    # https://api.github.com/search/code?q=tf.summary.scalar+tf.control_dependencies+in:file+extension:py+pushed:<2017-10-18
    # https://api.github.com/search/code?q=tf.summary.scalar+tf.control_dependencies+in:file+extension:py+pushed:<2017-10-18&access_token=2307831934e084912e55c5bc43c01807dedda02b
    # https://api.github.com/search/code?q=tf.summary.scalar+tf.control_dependencies+in:file+extension:py&access_token=2307831934e084912e55c5bc43c01807dedda02b
    # https://api.github.com/search/code?q=tf.summary.scalar+tf.control_dependencies+in:file+extension:py+repo:tensorflow/models+pushed:<2017-10-18&access_token=2307831934e084912e55c5bc43c01807dedda02b
    query = f'"{keyword}" "{keyword2}" in:file extension:py pushed:<2020-10-18 repo:tensorflow/models'
    g, results = utils_github.search_code(api_tokens, logger, query)
    for result in results:
        logger.debug(result.html_url)
        logger.debug(result)

def search_code_in_github(api, save_files_dir, max_real_repo_cnt):
    """
    https://api.github.com/search/code?q=pickle.load+in:file+extension:py+sort:best%20match&access_token=2307831934e084912e55c5bc43c01807dedda02b

    https://github.com/search?o=desc&q=pickle.load&s=indexed&type=Code
    """
    # max_real_repo_cnt = 0

    external_files_info_file = os.path.join(save_files_dir, "../external_files_info.yaml")
    keyword = api
    query = f'"{keyword}" in:file extension:py'
    g, code_results = utils_github.search_code(api_tokens, logger, query)
    
    external_file_dict = collections.OrderedDict({})
    # with open(external_files_info_file, "w") as write_f:
    actual_cnt = 0
    for i in range(code_results.totalCount):
        code_result = code_results[i]
        # update
        utils_github.update_remain_rate(g, logger, REMAIN_RATE_LIMIT)
        # logger.info(f"{code_result}")
        # download_url = code_result.download_url
        download_file_name = code_result.name
        content = code_result.decoded_content
        content = content.decode("utf-8")
        
        lines = content.split("\n")
        if len(lines) > 1500:
            logger.warn(f"{download_file_name} is too long ({len(lines)}). Not considered at present.")
            continue

        tmp_i = 1
        download_file_path = os.path.join(save_files_dir, download_file_name)
        while os.path.exists(download_file_path):
            logger.warn(f"{download_file_name} {code_result.path} already exists!")
            download_file_path = os.path.join(save_files_dir, f"{tmp_i}-" + download_file_name)
            tmp_i += 1

        # method 2) get decoded_content
        utils.write_str_to_file(download_file_path, content, False)

        # 
        file_dict = collections.OrderedDict({})
        file_dict['code_result.name'] = code_result.name
        file_dict['code_result.path'] = code_result.path
        file_dict['code_result.html_url'] = code_result.html_url
        file_dict['code_result.repository.full_name'] = code_result.repository.full_name
        file_dict['code_result.url'] = code_result.url
        external_file_dict[i] = file_dict

        actual_cnt += 1
        if actual_cnt == max_real_repo_cnt: # actual_cnt starts from 1
            break
    utils_yaml.write_to_yaml(external_files_info_file, external_file_dict)
    pass
    

