import csv
import inspect
import os
import pathlib
import pickle
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import omegaconf
import tqdm
import ujson
import yaml


def get_files_in_directory(
    dir_path: str, filter_func: Optional[callable] = None, return_with_dir=False
) -> List:
    """Get paths of files in a directory
    :param dir_path: path of directory that you want to get files from
    :type dir_path: str
    :param filter_func: function that returns True if the file name is valid
    :type filter_func: callable
    :return: list of file paths in the directory which are valid
    :rtype: list
    """
    file_names = [
        f
        for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
        and (filter_func is None or filter_func(f))
    ]
    if return_with_dir:
        return [os.path.join(dir_path, f) for f in file_names]
    return file_names


def get_files_in_all_sub_directories(
    root_dir_path: str, filter_func: Optional[callable] = None
) -> List:
    """Get paths of files in all sub directories
    :return: list of file paths in all sub directories which are valid
    :rtype: list
    """
    return [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(root_dir_path)
        for f in filenames
        if (filter_func is None or filter_func(f))
    ]


def create_directory(dir_path: str):
    """Creates all directories of the given path (if not exists)

    :param dir_path: directory path
    :type dir_path: str
    """
    return pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def split_path_into_dir_and_file_name(file_path: str) -> Tuple[str, str]:
    """Split a file path into directory path and file name

    :param file_path: file path
    :type file_path: str
    :return: directory path and file name
    :rtype: Tuple[str, str]
    """
    return os.path.dirname(file_path), os.path.basename(file_path)


def path_from_current_file(relative_path: str) -> str:
    """convert relative path to absolute path with respect to the caller's file path"""
    file_path_of_caller = inspect.stack()[1].filename
    dir_path_of_caller = os.path.dirname(file_path_of_caller)
    full_path = os.path.join(dir_path_of_caller, relative_path)
    return os.path.normpath(full_path)


# Related to json files
def read_json_file(
    file_path: str,
    auto_detect_extension: bool = False,
    encoding: Optional[str] = None,
) -> Dict:
    """Read a json file

    :param file_path: json file path
    :type file_path: str
    :return: json data
    :rtype: dict
    """
    if auto_detect_extension and file_path.endswith(".jsonl"):
        return read_jsonl_file(file_path, encoding=encoding)
    else:
        with open(file_path, "r", encoding=encoding) as f:
            return ujson.load(f)


def read_jsonl_file(file_path: str, encoding: Optional[str] = None) -> Dict:
    with open(file_path, "r", encoding=encoding) as f:
        return [ujson.loads(line) for line in f.readlines()]


def write_json_file(
    dict_object: Dict,
    file_path: str,
    indent: int = 4,
    auto_detect_extension: bool = False,
    encoding: Optional[str] = None,
    ensure_ascii: Optional[bool] = False,
) -> None:
    if auto_detect_extension and file_path.endswith(".jsonl"):
        return write_jsonl_file(
            dict_object=dict_object,
            file_path=file_path,
            encoding=encoding,
            ensure_ascii=ensure_ascii,
        )
    else:
        with open(file_path, "w", encoding=encoding) as f:
            ujson.dump(dict_object, f, indent=indent, ensure_ascii=ensure_ascii)


def write_jsonl_file(
    list_of_dict_object: List[Dict],
    file_path: str,
    encoding: Optional[str] = None,
    ensure_ascii: Optional[bool] = False,
):
    with open(file_path, "w", encoding=encoding) as f:
        for dict_line in list_of_dict_object:
            f.write(f"{ujson.dumps(dict_line, ensure_ascii=ensure_ascii)}\n")


# Related to yaml files
def read_yaml_file(file_path: str) -> Dict:
    """Read a yaml file

    :param file_path: yaml file path
    :type file_path: str
    :return: yaml data
    :rtype: dict
    """
    with open(file_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None


def write_yaml_file(dict_object: dict, file_path: str) -> None:
    with open(file_path, "w") as yaml_file:
        yaml.dump(dict_object, yaml_file, default_flow_style=False)


# Related to pickle files
def write_pickle_file(object_to_save, file_path: str) -> None:
    """Write a pickle file

    :param object_to_save: object to save
    :type object_to_save: any
    :param file_path: pickle file path
    :type file_path: str
    """
    with open(file_path, "wb") as f:
        pickle.dump(object_to_save, f)


def read_pickle_file(file_path: str) -> any:
    """Read a pickle file

    :param file_path: pickle file path
    :type file_path: str
    :return: object
    :rtype: any
    """
    with open(file_path, "rb") as f:
        return pickle.load(f)


# Related to config files


def read_config_file(file_path: str) -> omegaconf.OmegaConf:
    """Load a config file

    :param file_path: config file path
    :type file_path: str
    :return: config data
    :rtype: omegaconf.OmegaConf
    """
    return omegaconf.OmegaConf.load(file_path)


def load_config_file(file_path: str) -> omegaconf.OmegaConf:
    """Load a config file

    :param file_path: config file path
    :type file_path: str
    :return: config data
    :rtype: omegaconf.OmegaConf
    """
    raise RuntimeError("load_config_file is deprecated. Use read_config_file instead.")


def write_config_file(config: omegaconf.OmegaConf, file_path: str) -> None:
    """Write a config file

    :param config: config data
    :type config: omegaconf.OmegaConf
    :param file_path: config file path
    :type file_path: str
    """
    omegaconf.OmegaConf.save(config, file_path)


# Related to csv file
def read_csv_file(
    file_path: str,
    delimiter: str = ",",
    quotechar: str = '"',
    show_progress: bool = False,
    first_row_as_header: bool = True,
    process_row_func: Callable = None,
) -> List[Union[Dict[str, Any], List[Any]]]:
    """Read csv like files (e.g., tsv, csv, etc.)"""
    dict_list = []
    with open(file_path, "r") as f:
        tsv_file_reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
        if first_row_as_header:
            # Get headers
            header = next(tsv_file_reader)
        # Get values
        file_iterator = tqdm.tqdm(tsv_file_reader) if show_progress else tsv_file_reader
        for row in file_iterator:
            row = process_row_func(row) if process_row_func else row
            if first_row_as_header:
                # Save a dict if header is available
                dict_list.append(dict(zip(header, row)))
            else:
                # Save a list if header is not available
                dict_list.append(row)
    return dict_list


def write_csv_file(
    list_of_item: List[Union[Dict[str, Any], List[Any]]],
    file_path: str,
    delimiter: str = ",",
) -> None:
    """Write csv like data (e.g., tsv, csv, etc.) into a file"""
    assert len(list_of_item) > 0, "list_of_item is empty"
    with open(file_path, "w") as f:
        tsv_file_writer = csv.writer(f, delimiter=delimiter)
        if isinstance(list_of_item[0], dict):
            # Add header
            tsv_file_writer.writerow(list_of_item[0].keys())
            # Add values
            for dict_item in list_of_item:
                tsv_file_writer.writerow(dict_item.values())
        elif isinstance(list_of_item[0], list):
            # Add values
            for list_item in list_of_item:
                tsv_file_writer.writerow(list_item)
        else:
            raise RuntimeError(f"Invalid type of list_of_item: {type(list_of_item[0])}")


def get_directory_size(directory: str, recursive: bool = True) -> int:
    """
    Calculate the total logical size of a directory, optionally including subdirectories.

    This function sums up the actual file sizes (logical size) without considering
    filesystem block alignment, sparse files, or compression.

    Args:
        directory (str): Path to the directory.
        recursive (bool): Whether to include subdirectories in the size calculation.

    Returns:
        int: Total logical size of the directory in bytes.
    """
    total_size: int = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total_size += entry.stat().st_size  # Logical file size
            elif entry.is_dir() and recursive:
                total_size += get_directory_size(entry.path, recursive=recursive)
    except PermissionError:
        print(f"Permission denied: {directory}")
    return total_size


def get_disk_usage(directory: str, recursive: bool = True) -> int:
    """
    Calculate the actual disk space used by a directory, optionally including subdirectories.

    This function considers filesystem block size, sparse files, and metadata overhead,
    providing an estimate similar to `du -sh`.

    Args:
        directory (str): Path to the directory.
        recursive (bool): Whether to include subdirectories in the size calculation.

    Returns:
        int: Total disk usage of the directory in bytes.
    """
    total_size: int = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total_size += (
                    entry.stat().st_blocks * 512
                )  # Convert blocks (512-byte) to actual usage
            elif entry.is_dir() and recursive:
                total_size += get_disk_usage(entry.path, recursive=recursive)
    except PermissionError:
        print(f"Permission denied: {directory}")
    return total_size


def bytes_to_readable(size_bytes: int) -> str:
    """
    Convert a size in bytes to a human-readable format (B, KB, MB, GB, TB, etc.).

    Args:
        size_bytes (int): Size in bytes.

    Returns:
        str: Human-readable size with appropriate unit.
    """
    if size_bytes < 0:
        raise ValueError("Size cannot be negative.")

    if size_bytes == 0:
        return "0 B"

    size_units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]  # Extended to Exabytes
    unit_index = 0

    while size_bytes >= 1024 and unit_index < len(size_units) - 1:
        size_bytes /= 1024.0
        unit_index += 1

    return f"{size_bytes:.2f} {size_units[unit_index]}"
