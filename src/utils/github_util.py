from github import Github
import re, time
import sys
import os
sys.path.append(os.path.join(os.path.abspath(__file__).rsplit("/", 1)[0], "../"))

import utils
REMAIN_RATE_LIMIT = 15

def search_repos(api_tokens, logger, query):
    g = new_github_instance(api_tokens, logger)
    # keyword = 'torch'
    # query = f"{keyword} language:python" # stars:<=100"
    results = g.search_repositories(query, sort="stars", order="desc")

    return g, results

def search_code_in_a_repo(api_tokens, logger, query):
    g = new_github_instance(api_tokens, logger)
    # keyword = "import torch"
    # query = f'"{keyword}" in:file extension:py repo:{repo.full_name}'
    results = g.search_code(query, order='desc')

    return g, results

def search_code(api_tokens, logger, query):
    g = new_github_instance(api_tokens, logger)
    results = g.search_code(query, order='desc')

    return g, results


def getPrintSize(list_size, limit = 10):
    if list_size > limit:
        return limit
    else:
        return list_size

def get_remain_rate(g, logger = None):
    rate_limit = g.get_rate_limit()
    rate = rate_limit.search
    if rate.remaining == 0:
        print(f'You have 0/{rate.limit} API calls remaining. Reset time: {rate.reset}')
        if logger:
            logger.info(f'You have 0/{rate.limit} API calls remaining. Reset time: {rate.reset}')
        return
    else:
        print(f'You have {rate.remaining}/{rate.limit} API calls remaining')
        if logger:
            logger.info(f'You have {rate.remaining}/{rate.limit} API calls remaining')
    return rate.remaining

def update_remain_rate(github_instance, logger = None, remain_rate_limit = REMAIN_RATE_LIMIT):
    loop_cnt = 0
    while loop_cnt < 10:
        loop_cnt += 1
        remain_rate = get_remain_rate(github_instance)
        logger.info(f"current remain_rate_limit: {remain_rate}")
        if remain_rate <= remain_rate_limit:
            logger.info("Sleep Start : %s" % time.ctime())
            time.sleep(8)
            logger.info("Sleep End : %s" % time.ctime())
            logger.info(f"remain_rate_limit after sleep: {remain_rate}")
        else:
            break
    
def new_github_instance(api_tokens, logger, remain_rate_limit = REMAIN_RATE_LIMIT):
    for token in api_tokens:
        g = Github(token)
        update_remain_rate(g, logger, remain_rate_limit)
        return g
    # cnt = j
    # loop_limit = 10 # 10min
    # loop_cnt = 0
    # while (loop_cnt < loop_limit):
    #     loop_cnt += 1
    #     for token in api_tokens:
    #         g = Github(token)
    #         remain_rate = get_remain_rate(g)
    #         cnt += 1
    #         if remain_rate <= remain_rate_limit:
    #             continue
    #         else:
    #             if len(api_tokens) > 1:
    #                 utils.printInfo(f"existing GitHub api token No.{cnt}: {token}", logger)
    #             return g
    #     logger.info("Sleep Start : %s" % time.ctime())
    #     time.sleep(30)
    #     logger.info("Sleep End : %s" % time.ctime())
    utils.raiseExp("No available token.")

def containKeywords(message, keywords):
    contain_keywords = ""
    for keyword in keywords:
        result = re.search(keyword, message, re.I)
        if result is not None:
            # anti-pattern 
            if "Merge pull request" in message:
                continue

            contain_keywords += keyword + " "
            contain = True
            span = result.span()
            print(f"current commit message contain keyword: {keyword}. Corresponding match string is: {message[span[0]:]}")
    return contain_keywords.strip()