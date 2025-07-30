import logging
from pathlib import Path

from git import GitError, Repo

LOGGER = logging.getLogger(__name__)


def get_repo_remote(path: str | Path) -> str | None:
    try:
        repo: Repo = Repo(search_parent_directories=True, path=path)
        remotes = repo.remotes
        if remotes:
            url = remotes[0].url
            if url and not url.startswith("http"):
                url = f"ssh://{url}"
            return url

    except GitError:
        LOGGER.exception("Computing active branch")
        return None

    return None


def get_repo_head_hash(path: str | Path) -> str | None:
    try:
        repo: Repo = Repo(search_parent_directories=True, path=path)
        head_hash: str = repo.head.commit.hexsha
    except (GitError, ValueError, BrokenPipeError):
        LOGGER.exception("Unable to find commit HEAD on analyzed directory")
        return None
    return head_hash


def get_repo_branch(path: str | Path) -> str | None:
    try:
        repo: Repo = Repo(search_parent_directories=True, path=path)
    except GitError:
        LOGGER.exception("Computing active branch")
    except IndexError:
        return None
    else:
        return repo.active_branch.name

    return None
