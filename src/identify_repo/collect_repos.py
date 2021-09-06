"""
Identify 1000 top-rated repos, and consider top-200 repos.
"""
import os
import collections

import github

import config
from utils import general_util, github_util, yaml_util

# get path of current py file and directory
cur_file_abspath, cur_dir, cur_file_name = general_util.get_cur_path(__file__)

# constants
MAX_REPO_CNT = 500
CREATE_FORK = True
MAX_FORK_CNT = 220

# init logger
logger = general_util.init_logger(cur_file_name, cur_dir)

"""
the keyword list inlcude the keywords from the two publications: 
1) An empirical study on TensorFlow program bugs:
    bug, fix, wrong, error, nan, inf, issue, fault, fail, crash
2) Taxonomy of real faults in deep learning systems:
    ("fix" or "solve") and ("bug" or "issue" or "problem" or "defect" or "error").
"""
keywords = [
    'bug', 'defect', 'issue', 'problem', 'error', 'fault', 'fail', 'wrong', 'nan', 'inf', 'crash', 'fix', 'solve', 'repair'
]

# init a user
api_tokens = config.API_TOKENS

# file to save
dataset_yaml_file = os.path.join(cur_dir, "dataset", "dataset.yml")
general_util.mk_dir_from_file_path(dataset_yaml_file)
general_util.remove_all_content_in_dir(os.path.join(cur_dir, "dataset"))

# 2) collect repos
def collect_repos():
    """
    this is to 1) fork repos; 2) save info as yaml.
    however, httperror will occur if 1) and 2) are done simutaneously. To solve this issue, i first comment 2) and perform 1), 
    and then perform the rest.

    v1: 2020-12-1 2:00pm
    v2: (update) 2021-3-25
    """
    # new a github instance
    g = github_util.new_github_instance(api_tokens, logger)
    user = g.get_user()
    username = user.login
    # email = user.email

    # http://developer.github.com/v3/search
    # https://api.github.com/search/repositories?q=tensorflow+language:Python&sort=stars&order=desc
    keyword = 'tensorflow'
    query = f"{keyword} language:python" # stars:<=100"
    results = g.search_repositories(query, sort="stars", order="desc")

    logger.info(f"number of repos related to tensorflow: {results.totalCount}")

    repo_dict_cnt = 0
    repo_dict = {}
    # for i in range(utils_github.getPrintSize(results.totalCount, 200)):
    for i in range(results.totalCount):
        loop_cnt = 0
        succeed = False
        while(loop_cnt < 10):
            loop_cnt += 1
            succeed, repo_dict_cnt = update_repo_dict(results, i, repo_dict, repo_dict_cnt, user, username)
            if succeed:
                break
            else:
                logger.info("[timeout] retry due to ReadTimeoutError")
                general_util.sleep(60, logger)
                succeed, repo_dict_cnt = update_repo_dict(results, i, repo_dict, repo_dict_cnt, user, username)

                if succeed:
                    break
        if not succeed:
            logger.error(f"[fail to download repo No. {i} repo: {results[i].full_name}")
        if repo_dict_cnt == MAX_REPO_CNT:
            logger.info("[DONE] [Info collection of %s repos] current repo index: %s (start at 0)", repo_dict_cnt, i)
            break

    # write
    yaml_util.write_to_yaml(dataset_yaml_file, repo_dict)

def update_repo_dict(results, i, repo_dict, repo_dict_cnt, user, username):
    ori_dict_cnt = repo_dict_cnt # maintain original value
    try:
        g = github_util.new_github_instance(api_tokens, logger)
        repo = results[i]
        logger.info(f"[Repo index] No. {i} cur repo: {repo.full_name}  {repo.clone_url}")

        # refer to: https://docs.github.com/en/free-pro-team@latest/github/searching-for-information-on-github/searching-code
        keyword = "import tensorflow"
        query = f'"{keyword}" in:file extension:py repo:{repo.full_name}'
        results2 = g.search_code(query, order='desc')
        if results2.totalCount == 0:
            logger.warn(f"No. {i} repo: {repo.full_name} {repo.clone_url} has no 'import tensorflow' string.")
            return True, ori_dict_cnt # should return true to avoid loop

        # refer to: pygithub test file Repository.py 
        repo_dict_cnt += 1
        
        organization = "null"
        if repo.organization:
            organization = repo.organization.login

        repo_dict[repo_dict_cnt] = collections.OrderedDict({
            'repo_index' : repo_dict_cnt,
            'repo.full_name' : repo.full_name,
            'repo.organization' : organization,
            'repo.owner' : repo.owner.login,
            'repo.name' : repo.name,
            'repo.clone_url' : repo.clone_url,
            'repo.git_url' : repo.git_url,
            'repo.stargazers_count' : repo.stargazers_count,
            'contributors' : repo.get_contributors().totalCount,
            'repo.fork' : repo.fork,
            'repo.forks' : repo.forks,
            'repo.has_issues' : repo.has_issues,
            'repo.open_issues' : repo.open_issues, 
            "commits count": repo.get_commits().totalCount,
            'repo.created_at' : repo.created_at,
            'repo.pushed_at' : repo.pushed_at,
            'repo.updated_at' : repo.updated_at,
            'repo.description' : repo.description
        })

        # create a fork
        if CREATE_FORK and repo_dict_cnt <= MAX_FORK_CNT:
            fork_repo = user.create_fork(repo)
            repo_dict[repo_dict_cnt]['fork_user'] = username
            repo_dict[repo_dict_cnt]['fork_repo_name'] = fork_repo.name
        
        return True, repo_dict_cnt
    except:
        return False, ori_dict_cnt

if __name__ == "__main__":
    collect_repos()