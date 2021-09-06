# MisuAPI

- [MisuAPI](#misuapi)
  - [1. Introduction](#1-introduction)
  - [2. Dataset](#2-dataset)
  - [3. Reproduction](#3-reproduction)
    - [3.1. Environment Setup](#31-environment-setup)
    - [3.2. Reproduction](#32-reproduction)
  - [4. Usage](#4-usage)
  - [5. Future Schedule](#5-future-schedule)
  - [6. LICENSE](#6-license)

## 1. Introduction

All artifacts of our study "Demystifying API Misuses in Deep Learning Applications" are available in this repository, including:

1. The curated dataset **MisuAPI**;
2. The Python implementation to identify, collect and parse TensorFlow dependent repositories for constructing the dataset;
3. The results of all questions investigated in our study.

## 2. Dataset

Our dataset **MisuAPI** is publicly [available](./dataset/MisuAPI) now. Each API misuse corresponds to a folder (e.g., [./dataset/MisuAPI/activeloopai_Hub/c23c1d94b490dd1f9fc0c08838801c3666e7bc4c](./dataset/MisuAPI/activeloopai_Hub/c23c1d94b490dd1f9fc0c08838801c3666e7bc4c))

The structure of each API misuse folder is as follows:

```yaml
.
├── 1_mypy.txt: result of the static analyzer "mypy"
├── 1_pylint.txt: result of the static analyzer "pylint"
├── 1_pyre.txt: result of the static analyzer "pyre"
├── 1_pyright.txt: result of the static analyzer "pyright"
├── a          : buggy file
│   └── hub
│       └── api
│           └── dataset.py
├── b          : fixed file
│   └── hub
│       └── api
│           └── dataset.py
├── bug_info.yaml: collected information for this API misuse, including related issue links and messages
├── CC_file_0.txt.api: GumTree output that contains API related code changes
├── ori_patch.diff: original patch
├── validated_patch.diff: manually validated patch that discards all unrelated code changes
└── readme.yaml: basic information for this API misuse
```

In addition, the statistics of MisuAPI, including the two-dimensional category and symptoms, are available at the [dataset/statistics](./dataset/statistics) directory.


## 3. Reproduction

### 3.1. Environment Setup

**Environment of GumTree:**
1. JDK 11 (for [GumTree 3.0.0-beta1](https://github.com/GumTreeDiff/gumtree/tree/v3.0.0-beta1))
2. [Gradle v6.8](https://gradle.org/releases/)

**Environment of Python:**
3. Python 3.6
4. pygithub 1.55
5. pyyaml 5.4.1
6. unidiff 0.5.5 (installed via `conda install -c conda-forge unidiff`)

The environment of Python could be easily installed by the following commands (*please make sure that you have conda installed on your machine*):

```shell
conda env create -f MisuAPI_env.yaml
pip install -r MisuAPI_pip_env
```

### 3.2. Reproduction

Notes: some configurations should be configured (e.g., [the GitHub personal access tokens](https://github.com/settings/tokens)) by yourself. This has been specified in the [config.py](./src/config.py) file of corresponding folders.

To collect the most popular TensorFlow projects from GitHub:

```shell
cd src/
export PYTHONPATH=./utils:${PYTHONPATH}
python3 identify_repo/collect_repos.py
```

To download and parse these TensorFlow projects from GitHub:

```shell
cd src/
export PYTHONPATH=./utils:${PYTHONPATH}
python3 parse_repo/repo_download_and_parse.py
python3 parse_repo/filter.py
```

To run the four state-of-the-art static analyzers to detect API misuses in **MisuAPI**:

```shell
cd src/
export PYTHONPATH=./utils:${PYTHONPATH}
python3 static_analyzer/run_static_analyzers.py
```

## 4. Usage

This repository is dedicated to serve the following groups:

1. **practitioners** who want to take a closer look at API misuses in DL applications and obtain a better understanding of these bugs.
2. **researchers** who aim to propose automated detection or repair approaches targeting at API misuses in DL applications.
3. **other potential users** who are interested in API misuses in DL applications.

## 5. Future Schedule

We will consistently maintain this project to make it a better infrastructure for the community. Also, all contributions or questions are welcome.

## 6. LICENSE

The repository is licensed under the [GNU GPLv3 license](https://www.gnu.org/licenses/gpl-3.0-standalone.html). See [LICENSE](./LICENSE) for details.

