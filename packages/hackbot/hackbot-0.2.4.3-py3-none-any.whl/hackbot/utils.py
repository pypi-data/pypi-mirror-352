import zipfile
import os
import traceback
from typing import Generator, Union, Dict, List
from git import Repo, InvalidGitRepositoryError
from loguru import logger as log
from pathlib import Path
import warnings

try:
    from tomllib import load as toml_load
except ImportError:
    from tomli import load as toml_load
import importlib.metadata
from termcolor import colored
from enum import Enum
import tempfile
import json
from pydantic import BaseModel, Field, ValidationError

GREEN = "\033[1;32m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
END = "\033[0m"


class Endpoint(str, Enum):
    RUN = "run"
    SCOPE = "scope"
    LEARN = "learn"


def compress_source_code(
    source_path: str,
    zip_path: str,
    size_limit: int = 256 * 1024 * 1024,
    git_info: Union[Dict[str, str], None] = None,
) -> None:
    """Compress the source code directory into a zip file.
    If git_info (from get_repo_info) is provided, we only add the files that are tracked by git."""
    # Filter out duplicate file warnings from zipfile
    warnings.filterwarnings("ignore", category=UserWarning, module="zipfile")

    ignore_paths = {
        "node_modules",
        "build",
        "_mocks",
    }

    def is_relative_to(path: Path, other: Path) -> bool:
        """Check if a path is relative to another path without using Path.is_relative_to()"""
        # Convert both to absolute paths and strings for comparison
        path_str = str(path.resolve())
        other_str = str(other.resolve())

        # Add trailing slash to ensure we match complete path components
        if not other_str.endswith(os.sep):
            other_str += os.sep

        return path_str.startswith(other_str)

    def keep_file(file_path: Path) -> bool:
        return not any(part in file_path.parts for part in ignore_paths)

    def file_iter() -> Generator[Path, None, None]:
        if git_info is not None:
            git_repo = Repo(source_path, search_parent_directories=True)
            source_path_abs = Path(source_path).resolve()

            # Get staged files (both new and modified)
            staged_files = {item.a_path for item in git_repo.index.diff("HEAD")}
            # Get modified but unstaged files
            modified_files = {item.a_path for item in git_repo.index.diff(None)}

            # First yield all files from the current commit that are under source_path
            for entry in git_repo.commit().tree.traverse():
                file_path = Path(git_repo.working_dir) / Path(entry.path)  # type: ignore
                if is_relative_to(file_path, source_path_abs):
                    if str(file_path.relative_to(git_repo.working_dir)) not in modified_files:
                        if keep_file(file_path):
                            yield file_path

            # Then yield all staged files that are under source_path
            for file_path in staged_files:
                assert file_path is not None
                full_path = Path(git_repo.working_dir) / Path(file_path)
                if is_relative_to(full_path, source_path_abs):
                    if keep_file(full_path):
                        yield full_path
        else:
            source_path_abs = Path(source_path).resolve()
            for file_path in source_path_abs.rglob("*"):
                if is_relative_to(file_path, source_path_abs):
                    if keep_file(file_path):
                        yield file_path

    # We need to track/send the .git folder too, due to it containing stuff about git modules that we need to setup dependencies in many setups.
    def git_folder_iter() -> Generator[Path, None, None]:
        for file_path in (Path(source_path) / ".git").glob("**/*"):
            if file_path.exists() and file_path.is_file():
                yield Path(file_path)

    def combined_iter() -> Generator[Path, None, None]:
        for file_path in git_folder_iter():
            yield file_path
        for file_path in file_iter():
            yield file_path

    try:
        zip_size = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in combined_iter():  # file: Path
                # Skip .zip files
                if not file_path.name.endswith(".zip"):
                    arcname = file_path.relative_to(source_path)
                    if not file_path.exists():
                        log.debug(
                            f"File not found (probably a broken symlink?), skipping sending to server: {file_path}"
                        )
                        continue
                    if file_path.stat().st_size + zip_size > size_limit:
                        raise RuntimeError(
                            f"Source code archive is too large to be scanned. Must be less than 256MB, but after adding {file_path} it is {(zip_size + file_path.stat().st_size) // 1024 // 1024}MB."
                        )
                    else:
                        zip_size += file_path.stat().st_size
                    zipf.write(str(file_path), str(arcname))
    except Exception:
        raise RuntimeError(f"Failed to compress source code: {traceback.format_exc()}")


def get_repo_info(repo_path: Union[Path, str]) -> Union[Dict[str, str], None]:
    """Returns the repo info of a github (specifically) repo at repo_path, or None if the repo is not a github repo
    The info includes repo name, commit, repo owner, and branch name.
    Info also includes relative path from the real repo root (since we search parent directories for the repo) to the repo_path
    """
    if isinstance(repo_path, str):
        repo_path = Path(repo_path)
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        return None
    repo_info: Dict[str, str] = {}
    repo_info["source_root"] = str(repo_path.relative_to(repo.working_dir))
    for remote in repo.remotes:
        if "github.com" in remote.url:
            if "git@" in remote.url:
                mode = "ssh"
            else:
                mode = "http"

            # Example repo url: git@github.com:GatlingX/some_repo.git
            repo_info["repo_name"] = remote.url.split("/")[-1]
            repo_info["commit_hash"] = repo.head.commit.hexsha

            if mode == "http":
                # Example repo url: https://github.com/GatlingX/some_repo
                repo_info["repo_owner"] = remote.url.split("/")[-2]
            else:
                # Example repo url: git@github.com:GatlingX/some_repo.git
                repo_info["repo_owner"] = remote.url.split(":")[-1].split("/")[0]
                # Remove the .git from the end of the repo name
                repo_info["repo_name"] = repo_info["repo_name"][:-4]
            for branch in repo.branches:
                if branch.commit == repo.head.commit:
                    repo_info["branch_name"] = branch.name
                    break
                else:
                    repo_info["branch_name"] = "HEAD"
            break
    else:
        return None
    return repo_info


def get_version() -> str:
    """Get the version of the hackbot package."""
    # In development mode, we use the version from the pyproject.toml file
    try:
        with open(str(Path(__file__).parent.parent.parent / "pyproject.toml"), "rb") as f:
            return toml_load(f)["project"]["version"]
    except FileNotFoundError:
        # In production mode, we use the version from the package metadata

        return importlib.metadata.version("hackbot")


def postprocess_scope_results(
    source_path: Union[Path, str],
    scope_files: Union[List[str], None],
    ambiguous_files: Union[List[str], None],
) -> None:
    """Postprocess the scope analysis results.

    Takes the scope and ambiguous files from the analysis and writes them to disk.
    If scope files exist, writes them to scope.txt and adds to git if in a repo.
    If ambiguous files exist, writes them to ambiguous.txt for manual review.

    Args:
        source_path: Path to the source code directory
        scope_files: List of files determined to be in scope
        ambiguous_files: List of files that need manual review

    Returns:
        None
    """
    save_scope_files: bool = False
    save_ambiguous_files: bool = False

    if scope_files is None or len(scope_files) == 0 or scope_files[0] is None:  # type: ignore
        if ambiguous_files is None or len(ambiguous_files) == 0 or ambiguous_files[0] is None:  # type: ignore
            log.error(colored("❌ No files in scope", "red"))
        else:
            save_ambiguous_files = True
            log.error(
                colored(
                    "❌ No files in scope, but ambiguous files found requiring manual review", "red"
                )
            )
    else:
        save_scope_files = True
        if ambiguous_files is None or len(ambiguous_files) == 0 or ambiguous_files[0] is None:  # type: ignore
            log.info(
                f"{GREEN}✅ Scope analysis completed successfully. Now try running {CYAN}hackbot run{GREEN} to run the hackbot campaign."
            )
        else:
            save_ambiguous_files = True
            log.warning(
                f"{YELLOW}⚠️ Some files are ambiguous and require manual review go check {BLUE}scope.txt{YELLOW} and {BLUE}ambiguous.txt{END}"
            )

    def check_name_exists(name: Union[str, Path]) -> str:
        """Check if a file already exists. If it does, write to a temporary file and return the new name."""
        if isinstance(name, Path):
            name = str(name)
        if os.path.exists(name):
            original_name = name
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                name = f"{name}_{temp_file.name.split('/')[-1]}"
            log.warning(
                colored(
                    f"⚠️ {original_name} already exists, writing to a temporary file {name}",
                    "yellow",
                )
            )
        return name

    if save_scope_files and scope_files is not None:
        # Check if scope.txt already exists
        scope_file = check_name_exists(Path(source_path) / "scope.txt")
        # Write the scope files to the scope.txt file
        with open(scope_file, "w") as f:
            for file in scope_files:
                f.write(file + "\n")
        repo_info = get_repo_info(source_path)
        if repo_info is not None:
            repo = Repo(source_path, search_parent_directories=True)
            repo.index.add([scope_file])  # type: ignore

    if save_ambiguous_files and ambiguous_files is not None:
        # Check if ambiguous.txt already exists
        ambiguous_file = check_name_exists(Path(source_path) / "ambiguous.txt")
        # Write the ambiguous files to the ambiguous.txt file
        with open(ambiguous_file, "w") as f:
            for file in ambiguous_files:
                f.write(file + "\n")


def postprocess_learn_results(checklist: Union[Dict[str, str], None]) -> None:
    if checklist is None or len(checklist) == 0:
        log.error(colored("❌ No checklist found", "red"))
    else:
        log.info(
            colored(
                "✅ Checklist analysis completed successfully, writing to checklist.json", "green"
            )
        )

    with open(Path.cwd() / "checklist.json", "w") as f:
        json.dump(checklist, f)


class UserChecklistItem(BaseModel):
    issue: str = Field(..., description="Issue related to solidity code vurnerabilitie.")
    description: str = Field(..., description="Description of the issue.")
    severity: str = Field(..., description="Severity of the issue.")
    reference: str = Field(..., description="Reference to the issue.")


class UserChecklist(BaseModel):
    items: List[UserChecklistItem] = Field(..., description="List of checklist items.")


def validate_checklist_file(checklist_path: Path) -> List[Dict[str, str]]:
    """Validate the checklist file."""
    try:
        with open(checklist_path, "r") as f:
            json_data = json.load(f)
            UserChecklist.model_validate(json_data)
            return json_data
    except FileNotFoundError:
        log.error(colored("❌ Error: checklist.json not found", "red"))
        raise
    except (json.JSONDecodeError, FileNotFoundError):
        log.error(colored("❌ Error: Could not parse existing checklist.json", "red"))
        raise
    except ValidationError as e:
        log.error(colored(f"❌ Error: Invalid checklist.json structure: {e}", "red"))
        raise
    except Exception as e:
        log.error(colored(f"❌ Error: Failed to send existing checklist.json: {e}", "red"))
        raise
