import logging
import os
import shutil

from strands import tool

log = logging.getLogger(__name__)


@tool
def path_list(file_path: str) -> dict:
    """
    List all files in a directory and its subdirectories using os.walk.

    Args:
        file_path: Path to the directory.

    Returns:
        A dictionary containing the list of files in the directory and subdirectories.
    """
    return _path_list(file_path)


def _path_list(file_path: str) -> dict:
    file_path = os.path.expanduser(file_path)

    if not os.path.exists(file_path):
        log.error(f"Directory not found: {file_path}")
        return {"status": "error", "message": f"Directory not found: {file_path}"}

    try:
        files = []
        for root, _, filenames in os.walk(file_path):
            for f in filenames:
                files.append(os.path.join(root, f))
        log.info(f"Files in {file_path}: {files}")
        return {"status": "success", "files": files}
    except Exception as e:
        log.error(f"Failed to list files: {e}")
        return {"status": "error", "message": str(e)}


@tool
def file_move(
    source_path: str,
    destination_path: str,
) -> dict:
    """
    Move a file from source to destination.

    Args:
        source_path: Path to the source file.
        destination_path: Path to the destination directory.

    Returns:
        A dictionary containing the status of the operation.
    """
    return _file_move(source_path, destination_path)


def _file_move(source_path: str, destination_path: str) -> dict:
    """
    Move a file from source to destination.
    Args:
        source_path: Path to the source file.
        destination_path: Path to the destination directory.

    Returns:
        A dictionary containing the status of the operation.
    """

    source_path = os.path.expanduser(source_path)
    destination_path = os.path.expanduser(destination_path)

    destination_dir = os.path.dirname(destination_path)
    os.makedirs(destination_dir, exist_ok=True)
    log.debug(f"Moving file from {source_path!r} to {destination_path!r}")
    try:
        try:
            os.remove(destination_path)
        except Exception:
            pass
        shutil.move(source_path, destination_path)
        log.info(f"Successfully moved {source_path!r} to {destination_path!r}")
        return {
            "status": "success",
            "message": f"Moved {source_path!r} to {destination_path!r}",
        }
    except Exception as e:
        log.error(f"Failed to move file {source_path!r} to {destination_path!r}: {e}")
        return {"status": "error", "message": str(e)}


@tool
def file_delete(file_path: str, is_directory: bool) -> dict:
    """
    Delete a file or directory recursively.

    Args:
        file_path: Path to the file or directory.
        is_directory: Required to be true in order to delete a directory

    Returns:
        A dictionary containing the status of the operation.
    """
    return _file_delete(file_path, is_directory)


def _file_delete(file_path: str, is_directory: bool) -> dict:
    file_path = os.path.expanduser(file_path)

    log.debug(f"Deleting file {file_path!r}")
    try:
        if is_directory:
            shutil.rmtree(file_path)
            log.info(f"Successfully deleted directory {file_path!r}")
            return {
                "status": "success",
                "message": f"Deleted directory {file_path!r}",
            }

        os.remove(file_path)
        log.info(f"Successfully deleted {file_path!r}")
        return {
            "status": "success",
            "message": f"Deleted {file_path!r}",
        }
    except Exception as e:
        log.error(f"Failed to delete file or directory {file_path!r}: {e}")
        return {"status": "error", "message": str(e)}
