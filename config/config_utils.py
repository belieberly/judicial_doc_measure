import os

def create_dir_if_not_exist(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return

def create_dirs_if_not_exist(*dir_paths: str) -> None:
    for dir_path in dir_paths:
        create_dir_if_not_exist(dir_path)
    return