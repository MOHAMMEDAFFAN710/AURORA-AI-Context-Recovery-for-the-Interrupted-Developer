from typing import Any, Dict, List
from git import Repo, InvalidGitRepositoryError, NoSuchPathError


def summarize_recent_commits(repo_path: str, limit: int = 10) -> Dict[str, Any]:
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        return {"commits": [], "repo_found": False}
    commits_out: List[Dict[str, Any]] = []
    for c in list(repo.iter_commits(max_count=limit)):
        files_changed: List[str] = []
        if c.parents:
            diffs = c.diff(c.parents[0])
            for d in diffs:
                if d.a_path:
                    files_changed.append(d.a_path)
                if d.b_path and d.b_path != d.a_path:
                    files_changed.append(d.b_path)
        commits_out.append(
            {
                "commit": c.hexsha[:12],
                "author": str(c.author),
                "date": c.committed_datetime.isoformat(),
                "message": c.message.strip(),
                "files_changed": sorted(list(set(files_changed))),
            }
        )
    return {"commits": commits_out, "repo_found": True}
