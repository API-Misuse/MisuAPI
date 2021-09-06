"""
process to filter bug fixing commmits

1) For each repo dir, check DONE file
2) For each commit dir, 
    1. get repo_dict
    2. check if python file exists in patch diff
    3. check if it is a merge
    4. check if it has api related code changes (GumTree output)
    5. save linked issue urls & messages (related bug report).
"""
import os
import collections

import config
from utils import yaml_util, github_util, general_util

api_tokens = config.API_TOKENS
cur_dir = os.path.abspath(__file__).rsplit("/", 1)[0]
cur_file_abspath, cur_dir_path, cur_file_name = general_util.get_cur_path(__file__)
logger = general_util.init_logger(cur_file_name, cur_dir_path)
parse_folder = os.path.join(cur_dir, "parsed_repos")

def filter_commits():
    repo_dirs = general_util.get_all_dir_paths(parse_folder)
    
    start = 0
    end = start + 40
    for repo_i in range(start, end):
        repo_dir_path = repo_dirs[repo_i]
        repo_done_file = os.path.join(repo_dir_path, "DONE")
        repo_filter_done_file = os.path.join(repo_dir_path, "REPO_DONE_FILTER")
        if not os.path.exists(repo_done_file):
            continue

        if os.path.exists(repo_filter_done_file):
            continue
        
        # full_name: Qidian213/deep_sort_yolov3
        repo_info_yaml = yaml_util.read_yaml(os.path.join(repo_dir_path, "repo_info.yaml"))
        repo_full_name = repo_info_yaml['full_name']

        logger.info(f"cur_repo: {repo_full_name} {repo_done_file}")

        commit_dirs = general_util.get_all_dir_paths(repo_dir_path)
        for commit_dir_path in commit_dirs:
            is_a_bug = True
            is_a_bug_file = os.path.join(commit_dir_path, "IS_A_BUG")
            filter_done_file = os.path.join(commit_dir_path, "DONE_FILTER")
            bug_info_file = os.path.join(commit_dir_path, "bug_info.yaml")

            if os.path.exists(filter_done_file):
                logger.info(f"{filter_done_file} is done. continue")
                continue
                # pass

            # get yaml file now
            yaml_file_path = os.path.join(commit_dir_path, "readme.yaml")
            repo_dict = yaml_util.read_yaml(yaml_file_path)

            sha = repo_dict['sha']

            # check py file
            patch_file_cnt = repo_dict['added_files'] + repo_dict['removed_files'] + repo_dict["modified_files"]
            has_py_patch = False
            for i in range(patch_file_cnt):
                patched_file = repo_dict[f"patched_file_{i}"]
                source_file = patched_file['source_file']
                target_file = patched_file['target_file']
                if source_file.endswith(".py") or target_file.endswith(".py"):
                    has_py_patch = True
                    break
            if not has_py_patch:
                is_a_bug = False
                logger.info(f"has_py_patch = False {sha}")
            
            # check api code change
            has_api = False
            cc_file_sh_paths = general_util.get_all_file_paths(commit_dir_path, ".sh")
            for sh_path in cc_file_sh_paths:
                cc_file_txt_path = sh_path.replace(".sh", ".txt")
                cc_file_api_path = sh_path.replace(".sh", ".txt.api")
                if not os.path.exists(cc_file_txt_path) or not os.path.exists(cc_file_api_path):
                    logger.error(f"imcomplete gumtree run. {sh_path}")
                    has_api = True
                    break
                api_str = general_util.read_file_to_str(cc_file_api_path).strip()
                if len(api_str) != 0:
                    has_api = True
            if not has_api:
                is_a_bug = False
                logger.info(f"has_api = False {sha}")

            if is_a_bug:
                general_util.write_str_to_file(is_a_bug_file, "", False)
                # get_issues
                g = github_util.new_github_instance(api_tokens, logger)
                query=f"{sha} repo:{repo_full_name}"
                results = g.search_issues(query)

                repo_dict_extend = collections.OrderedDict({})
                repo_dict_extend['issues_cnt'] = results.totalCount
                for i in range(results.totalCount):
                    result = results[i]
                    issue_dict = collections.OrderedDict({})
                    issue_dict['html_url'] = result.html_url
                    issue_dict['title'] = result.title
                    issue_dict['body'] = result.body
                    repo_dict_extend[f'issue_{i}'] = issue_dict
                
                for key, value in repo_dict.items():
                    repo_dict_extend[key] = value
                yaml_util.write_to_yaml(bug_info_file, repo_dict_extend)

            general_util.write_str_to_file(filter_done_file, "", False)
        general_util.write_str_to_file(repo_filter_done_file, "", False)

if __name__ == "__main__":
    filter_commits()
