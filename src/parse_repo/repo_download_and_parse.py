"""
this is to download repos
"""
import os
import collections
import sys

import yaml
from unidiff import PatchSet

cur_dir = os.path.abspath(__file__).rsplit("/", 1)[0]

import config
from utils import yaml_util, github_util, cmd_util, repo_util, general_util
KEYWORDS = repo_util.KEYWORDS

# init
cur_file_abspath, cur_dir_path, cur_file_name = general_util.get_cur_path(__file__)

logger = general_util.init_logger(cur_file_name, cur_dir_path)

download_dir = os.path.join(cur_dir, "downloaded_repos")
general_util.mk_dir_from_dir_path(download_dir)

parse_dir = os.path.join(cur_dir_path, "parsed_repos")
general_util.mk_dir_from_dir_path(parse_dir)

PYTHON_PATCH_PARSER_JAR = os.path.join(cur_dir_path, "Python_Patch_Parser/core/build/libs/core-jar-with-dependencies-0.0.1.jar")
JAVA_ARGS = config.JAVA_ARGS
RSA_PATH = config.RSA_PATH
MY_ACCOUNT = config.MY_ACCOUNT
GUMTREE_JAR = config.GUMTREE_JAR
DEBUG_FLAG = False

assert os.path.exists(PYTHON_PATCH_PARSER_JAR), f"{PYTHON_PATCH_PARSER_JAR} does not exists."
assert os.path.exists(GUMTREE_JAR), f"{GUMTREE_JAR} does not exists."

dataset_yaml_dir = os.path.join(cur_dir, "../identify_repo")
dataset_yaml_file = os.path.join(dataset_yaml_dir, "repo_collection", f"dataset", "dataset.yml")


def download_and_parse(repo_dict):
    repo_downloaded_cnt = 0
    for i in range(1, len(repo_dict) + 1):
        if i == 85 or i == 183: # too large to download
            continue
        cur_repo_dict = repo_dict[i]

        # check if this repo dir already exists locally
        already_exists, local_repo_dir = download_repo(cur_repo_dict)
        parse_repo(cur_repo_dict)

        repo_downloaded_cnt += 1
        if repo_downloaded_cnt == 200:
            break

        # break # debugging mode (just download the first repo)

def parse_repo(cur_repo_dict):
    """try GitPython https://gitpython.readthedocs.io/en/stable/intro.html#requirements
    But I think it is unnecessary to learn a new module usage. I prefer using git command.
    """
    full_name = cur_repo_dict['repo.full_name']

    info_dict = collections.OrderedDict()
    simple_name = get_real_name_gitee(cur_repo_dict)

    # check repo_downloaded dir
    cur_repo_dir = os.path.join(download_dir, simple_name)
    if not os.path.exists(cur_repo_dir):
        general_util.raiseExp(f"{cur_repo_dir} does not exist.")

    # create repo_parsed dir to prepare commit history parsing
    replace_name = full_name.replace("/", "_")
    cur_parse_dir = os.path.join(parse_dir, replace_name)
    general_util.mk_dir_from_dir_path(cur_parse_dir)

    cur_parse_dir_done_flag_dir = os.path.join(cur_parse_dir, "DONE")
    if os.path.exists(cur_parse_dir_done_flag_dir) and not DEBUG_FLAG:
        return

    info_dict["simple_name"] = simple_name
    info_dict["cur_folder_name"] = replace_name
    info_dict["full_name"] = full_name

    # number of commits
    cmd = f""" cd {cur_repo_dir};
    git log --pretty=format:"%H" | wc -l;
    """
    output = cmd_util.run_cmd_with_output(cmd, logger)
    commits_num = int(output.strip())
    info_dict["number of commits"] = commits_num

    # save info dict
    info_file = os.path.join(cur_parse_dir, 'repo_info.yaml')
    yaml_util.write_to_yaml(info_file, info_dict)
    # return

    # get all SHAs of commilts
    sha_txt = os.path.join(cur_parse_dir, "sha.txt")
    cmd = f""" cd {cur_repo_dir};
    git log --pretty=format:"%H" > {sha_txt};
    """
    output = cmd_util.run_cmd_with_output(cmd, logger)
    sha_list = general_util.read_file(sha_txt)
    
    for sha_i in range(len(sha_list)):
        sha = sha_list[sha_i]

        # DEBUG_MODE
        # if sha != "b0ccdb113e252563003930a1ff5f179d61070519":
        #     continue
        
        cmd = f""" cd {cur_repo_dir};
        git log --pretty=format:'%B' -n 1 {sha};
        """
        output = cmd_util.run_cmd_with_output(cmd, logger)
        commit_message = output.strip()

        contained_keywords = repo_util.contain_keywords_extend(commit_message, KEYWORDS, logger)
        if len(contained_keywords) == 0:
            continue

        cmd = f""" cd {cur_repo_dir};
        git log -n 1 {sha};
        """
        output = cmd_util.run_cmd_with_output(cmd, logger)
        commit_log = output.strip()

        # get commit time
        cmd = f""" cd {cur_repo_dir};
        git log --pretty=format:'%ai' -n 1 {sha};
        """
        commit_time = cmd_util.run_cmd_with_output(cmd, logger).strip()

        # get commit author
        cmd = f""" cd {cur_repo_dir};
        git log --pretty=format:'%an' -n 1 {sha};
        """
        commit_author = cmd_util.run_cmd_with_output(cmd, logger).strip()

        if len(contained_keywords) > 0:
            # logger.info(f"Commit {sha} may be a bug fixing commit. Message: {commit_message}")
            
            readme_folder = os.path.join(cur_parse_dir, sha)
            general_util.mk_dir_from_dir_path(readme_folder)
            readme_file = os.path.join(readme_folder, "readme.yaml")

            # avoid re-do
            cur_commit_done_flag_file = os.path.join(readme_folder, "DONE")
            if os.path.exists(cur_commit_done_flag_file):
                continue
            else:
                general_util.remove_all_content_in_dir(readme_folder)

            readme_dict = collections.OrderedDict()
            readme_dict['sha'] = sha
            readme_dict['message'] = commit_message
            readme_dict['commit_log'] = commit_log
            readme_dict['contained_keywords'] = contained_keywords
            readme_dict['commit_time'] = commit_time
            readme_dict['commit_author'] = commit_author

            # get patch diff & use unidiff
            # usage of unidiff. Refer to: https://pypi.org/project/unidiff/
            diff_file = os.path.join(readme_folder, "patch.diff")
            cmd = f""" cd {cur_repo_dir};
            git show {sha} > {diff_file};
            """
            output = utils_cmd.run_cmd_with_output(cmd, logger)
            patch = PatchSet.from_filename(diff_file, encoding='utf-8')
            readme_dict['added_files'] = len(patch.added_files)
            readme_dict['removed_files'] = len(patch.removed_files)
            readme_dict['modified_files'] = len(patch.modified_files)
            # logger.debug(f"""patch: {repr(patch)}
            # {patch.modified_files[0]}
            # """)

            operate_on_patch(sha, patch, readme_dict, readme_folder, cur_repo_dir)

            yaml_util.write_to_yaml(readme_file, readme_dict)
            general_util.write_str_to_file(cur_commit_done_flag_file, "", False)
    general_util.write_str_to_file(cur_parse_dir_done_flag_dir, "", False)

def operate_on_patch(sha, patch, readme_dict, readme_folder, cur_repo_dir):
    """to get patched_file_dict
    """
    for i in range(len(patch)):
        patched_file = patch[i]
        patched_file_dict = collections.OrderedDict()
        
        # get file type
        patched_file_dict["is_added_file"] = patched_file.is_added_file
        patched_file_dict["is_removed_file"] = patched_file.is_removed_file
        patched_file_dict["is_modified_file"] = patched_file.is_modified_file
        patched_file_dict["is_binary_file"] = patched_file.is_binary_file
        patched_file_dict["is_rename"] = patched_file.is_rename

        # get info
        patched_file_dict["path"] = patched_file.path
        patched_file_dict["source_file"] = patched_file.source_file
        patched_file_dict["target_file"] = patched_file.target_file
        patched_file_dict["added"] = patched_file.added
        patched_file_dict["removed"] = patched_file.removed

        # get patched file
        src_file = patched_file_dict["source_file"]
        dst_file = patched_file_dict["target_file"]

        # need to judge if it is .py file
        src_is_null = False
        dst_is_null = False
        if repo_util.isDevNull(src_file):
            src_file = os.path.join(readme_folder, "empty_src.py")
            repo_util.write_str_to_file(src_file, "", False)
            src_is_null = True
        if repo_util.isDevNull(dst_file):
            dst_file = os.path.join(readme_folder, "empty_dst.py")
            dst_is_null = True
            repo_util.write_str_to_file(dst_file, "", False)

        if src_file.endswith(".py") and dst_file.endswith(".py"):
            # checkout dst file
            checkout_file(readme_folder, cur_repo_dir, dst_file, sha, file_is_null = dst_is_null)

            # get parent commit
            cmd = f""" cd {cur_repo_dir};
            git log --pretty=format:'%P' -n 1 {sha};
            """
            parent_commit_id = cmd_util.run_cmd_with_output(cmd, logger).strip()
            if " " in parent_commit_id: # multiple parents
                parent_ids = parent_commit_id.split(' ')
                logger.warn(f"Current commit {sha} has {len(parent_ids)} parent commits.")
                for pid_i in range(len(parent_ids)):
                    parent_id = parent_ids[pid_i]
                    src_file_path, file_exist = checkout_file(readme_folder, cur_repo_dir, src_file, parent_id, pid_i, check_file_exist = True, file_is_null = src_is_null)

                    if file_exist:
                        # gumtree: get diff and write to file
                        cmd = f"""cd {readme_folder};
                        echo "java {JAVA_ARGS} -cp {PYTHON_PATCH_PARSER_JAR}:{GUMTREE_JAR} apr.myapr.parser.main.Main -sfp {src_file_path}  \
                            -dfp {dst_file} -op {os.path.join(readme_folder, f'CC_file_{i}_{pid_i}.txt')}" > CC_file_{i}_{pid_i}.sh;
                        java {JAVA_ARGS} -cp {PYTHON_PATCH_PARSER_JAR}:{GUMTREE_JAR} apr.myapr.parser.main.Main -sfp {src_file_path}  \
                            -dfp {dst_file} -op {os.path.join(readme_folder, f'CC_file_{i}_{pid_i}.txt')};
                        """
                        output = cmd_util.run_cmd_with_output(cmd, logger)
            else:
                checkout_file(readme_folder, cur_repo_dir, src_file, parent_commit_id, file_is_null = src_is_null)
                # gumtree: get diff and write to file
                cmd = f"""cd {readme_folder};
                echo "java {JAVA_ARGS} -cp {PYTHON_PATCH_PARSER_JAR}:{GUMTREE_JAR} apr.myapr.parser.main.Main -sfp {src_file}  \
                    -dfp {dst_file} -op {os.path.join(readme_folder, f'CC_file_{i}.txt')}" > CC_file_{i}.sh;
                java {JAVA_ARGS} -cp {PYTHON_PATCH_PARSER_JAR}:{GUMTREE_JAR} apr.myapr.parser.main.Main -sfp {src_file}  \
                    -dfp {dst_file} -op {os.path.join(readme_folder, f'CC_file_{i}.txt')};
                """
                output = cmd_util.run_cmd_with_output(cmd, logger)    

        # for hunk in patched_file:
        # refer to: https://stackoverflow.com/questions/39423122/python-git-diff-parser
        add_line_no = [(line.target_line_no, line.value) 
                        for hunk in patched_file for line in hunk 
                        if line.is_added]  # the row number of deleted lines     #  and line.value.strip() != ''
        # print('added lines : ' + str(add_line_no))
        del_line_no = [(line.target_line_no, line.value) 
                        for hunk in patched_file  for line in hunk 
                        if line.is_removed]   # the row number of added liens    #  and line.value.strip() != ''
        # print('deleted lines : ' + str(del_line_no))

        patched_file_dict['add_line_no'] = add_line_no
        patched_file_dict['del_line_no'] = del_line_no

        # save to readme_dict
        readme_dict[f'patched_file_{i}'] = patched_file_dict

def checkout_file(readme_folder, cur_repo_dir, file_path, cur_sha, multi_index = -1, check_file_exist = False, file_is_null = False):
    """
    some commit may have multiple parent commits. multi_index is for this
    """
    if file_is_null:
        return file_path, True
    save_file_path = os.path.join(readme_folder, file_path)
    if multi_index > 0:
        save_file_path = os.path.join(readme_folder, f"{multi_index}_{file_path}")
    real_file_path = file_path.split("/", 1)[1]
    # logger.debug(f"file_path: {file_path}, real_file_path: {real_file_path}")

    general_util.mk_dir_from_file_path(save_file_path)
    cmd = f""" cd {cur_repo_dir};
    git show {cur_sha}:{real_file_path} > {save_file_path};
    """

    file_exist = True
    if check_file_exist:
        # check if file exists
        cmd_tmp = f""" cd {cur_repo_dir};
        git reset --hard master;
        """
        cmd_util.run_cmd_with_output(cmd_tmp, logger)

        # check if file exists
        cmd_tmp = f""" cd {cur_repo_dir};
        git checkout {cur_sha};
        """
        cmd_util.run_cmd_with_output(cmd_tmp, logger)

        if not os.path.exists(os.path.join(cur_repo_dir, real_file_path)):
            logger.warn(f"{cur_sha}:{real_file_path} does not exist!")
            file_exist = False

        # get back to master
        cmd_tmp = f""" cd {cur_repo_dir};
        git checkout master;
        """
        cmd_util.run_cmd_with_output(cmd_tmp, logger)
    if file_exist:
        output = cmd_util.run_cmd_with_output(cmd, logger)

    return save_file_path, file_exist
    
def get_real_name_gitee(cur_repo_dict):
    full_name = cur_repo_dict['repo.full_name']
    short_name = full_name.rsplit("/", 1)[-1]

    fork_name_gitee = cur_repo_dict['fork_repo_name']

    if fork_name_gitee != short_name:
        logger.warn(f"different names: {fork_name_gitee} {short_name}")
    return fork_name_gitee

def download_repo(cur_repo_dict):
    name = get_real_name_gitee(cur_repo_dict)
    gitee_clone_url = f"git@gitee.com:{MY_ACCOUNT}/{name}.git"

    # if already exists, return true
    local_repo_dir = os.path.join(download_dir, name)
    if os.path.exists(local_repo_dir) and os.path.exists(os.path.join(local_repo_dir, ".git")):
        logger.warn(f"this repo {name} already exists at: {local_repo_dir}")
        return True, local_repo_dir
    
    # else
    ssh_cmd = f"""cd {download_dir};
        pwd;
        eval "$(ssh-agent -s)";
        ssh-add {RSA_PATH};
        git clone {gitee_clone_url};
    """
    # git clone {gitee_clone_url};

    cmd_util.run_cmd_with_output(ssh_cmd, logger)
    return False, local_repo_dir

if __name__ == "__main__":
    repo_dict = repo_util.get_top_200_repos(dataset_yaml_file, logger)
    download_and_parse(repo_dict)