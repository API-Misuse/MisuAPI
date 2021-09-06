import os, sys, shutil, time
from utils import yaml_util, cmd_util, general_util

cur_dir_path, cur_file_name = os.path.split(os.path.abspath(__file__))
logger = general_util.init_logger(cur_file_name, cur_dir_path)

NOT_IN_FORK = ["Artificial-Intelligence-Deep-Learning-Machine-Learning-Tutorials", "deepnlp"] # too large to include
data_yaml_path = os.path.join(cur_dir_path, "../identify_repo/dataset/dataset.yml")
parse_repo_dir = os.path.join(cur_dir_path, "../parse_repo/parsed_repos")
analyzer_list = ["pylint", "mypy", "pyright", "pyre"]

def get_all_commits(repo_dict):   
    commits_cnt = 0
    create_time = []
    update_time = []
    for key, value_dict in repo_dict.items():
        commits_cnt += value_dict["commits count"]
        create_time.append(value_dict["repo.created_at"])
        update_time.append(value_dict["repo.updated_at"])

    create_time.sort()
    update_time.sort()
    logger.info(f"commits_cnt: {commits_cnt}")
    logger.info(f"create_time: {create_time[0]} {create_time[-1]}")
    logger.info(f"update_time: {update_time[0]} {update_time[-1]}")

def get_top_200_repos():
    repo_dict_ori = yaml_util.read_yaml(data_yaml_path)
    not_in_gitee_cnt = 0
    repo_dict = {}

    repo_cnt = 0
    for index, info_dict in repo_dict_ori.items():
        repo_name = info_dict["repo.name"]
        if repo_name in NOT_IN_FORK:
            not_in_gitee_cnt += 1
            continue
        repo_dict[index] = info_dict
        repo_cnt += 1
        if repo_cnt == 200:
            break

    if not_in_gitee_cnt != len(NOT_IN_FORK):
        general_util.raiseExp(f"not_in_gitee_cnt {not_in_gitee_cnt} != len(NOT_IN_GITEE) {len(NOT_IN_GITEE)}")

    return repo_dict

def get_all_commit_folder():
    keyword_bug_fix_cnt = 0
    is_a_bug_cnt = 0
    no_py_change_cnt = 0
    total_cnt = 0
    gumtree_cnt = 0
    not_exist = 0
    repos_dir_paths = general_util.get_subdir_paths(parse_repo_dir)
    for repo_dir_path in repos_dir_paths:
        commit_dir_paths = general_util.get_subdir_paths(repo_dir_path)
        keyword_bug_fix_cnt += len(commit_dir_paths)

        for commit_dir_path in commit_dir_paths:
            is_a_bug_file = os.path.join(commit_dir_path, "bug_info.yaml") #IS_A_BUG
            if os.path.exists(is_a_bug_file):
                is_a_bug_cnt += 1
            else:
                readme_path = os.path.join(commit_dir_path, "readme.yaml")
                if not os.path.exists(readme_path):
                    not_exist += 1
                    continue

    logger.info(f"keyword_bug_fix_cnt: {keyword_bug_fix_cnt}")
    logger.info(f"is_a_bug_cnt: {is_a_bug_cnt}")
    logger.info(f"no_py_change_cnt: {no_py_change_cnt}")
    logger.info(f"gumtree_cnt: {gumtree_cnt}:\nno_py_change_cnt: {no_py_change_cnt}\nnot_exist: {not_exist}")

def copy_api_misuse_dir(ids, continue_flag = False):
    repos_dir_paths = general_util.get_subdir_paths(parse_repo_dir)
    for repo_dir_path in repos_dir_paths:
        commit_dir_paths = general_util.get_subdir_paths(repo_dir_path)

        for commit_dir_path in commit_dir_paths:
            dir_name = commit_dir_path.rsplit("/")[-1]
            if dir_name in ids:
                # dst path
                copy_dir = commit_dir_path.replace("/parsed_repos/", "/misuse_repos/")

                if continue_flag and os.path.exists(copy_dir):
                    logger.info("continue")
                    continue
                else:
                    general_util.init_clean_dir(copy_dir)
                    os.rmdir(copy_dir)
                    shutil.copytree(commit_dir_path, copy_dir)

def run_analyzers():
    misuse_repo_dir = parse_repo_dir.replace("/parsed_repos", "/misuse_repos")
    repos_dir_paths = general_util.get_subdir_paths(misuse_repo_dir)

    for repo_dir_path in repos_dir_paths:
        commit_dir_paths = general_util.get_subdir_paths(repo_dir_path)

        for commit_dir_path in commit_dir_paths:
            commit_dir_name = general_util.get_dir_name(commit_dir_path)
            pyre_txt = os.path.join(commit_dir_path, f"1_pyre.txt")
            if os.path.exists(pyre_txt):
                continue

            src = os.path.join(commit_dir_path, "a")
            dst = os.path.join(commit_dir_path, "b")

            assert os.path.exists(src), f"{src} does not exist!"
            assert len(general_util.get_subdir_paths(commit_dir_path)) == 2, "{commit_dir_path} has more than 2 folders"

            for analyzer in analyzer_list:
                analyzer_output_path = os.path.join(commit_dir_path, f"1_{analyzer}.txt")
                cmd = f"""
                    . /etc/profile;
                    cd {commit_dir_path};
                    {analyzer} {src} > {analyzer_output_path} 2>&1;
                """
                if analyzer == "pyre":
                    #pyre --source-directory 
                    cmd = f"""
                    . /etc/profile;
                    cd {commit_dir_path};
                    {analyzer} --source-directory {src} --noninteractive check > {analyzer_output_path} 2>&1;
                    """
                start = time.time()
                output = cmd_util.run_cmd_with_output(cmd, logger)
                end = time.time()
                general_util.write_line_to_file(analyzer_output_path, f"\ntime cost(in seconds): {end-start}")
                logger.debug(f"output:\n{general_util.read_file_to_str(analyzer_output_path)}")
                pass

def get_misuse_ids():
    ids = general_util.read_file(os.path.join(cur_dir_path, "api_misuse_ids.txt"))
    ids = [id for id in ids if id != ""]
    return ids

if __name__ == "__main__":
    ids = get_misuse_ids()
    copy_api_misuse_dir(ids, continue_flag = True)
    run_analyzers()