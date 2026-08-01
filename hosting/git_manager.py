import git
import os
import shutil

def clone_repo(repo_url: str, target_dir: str):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    git.Repo.clone_from(repo_url, target_dir)

def pull_repo(target_dir: str):
    repo = git.Repo(target_dir)
    origin = repo.remotes.origin
    origin.pull()