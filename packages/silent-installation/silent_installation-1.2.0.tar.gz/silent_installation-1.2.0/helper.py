import os
import re
import logging
import psutil
import traceback
import subprocess


def remove_folder(root, remove_root=True):
    for file in os.listdir(root):
        abs_path = os.path.join(root, file)
        if os.path.isfile(abs_path):
            try:
                os.remove(abs_path)
            except:
                logging.warning(f'failed to delete {abs_path}.')
        else:
            try:
                remove_folder(abs_path)
            except:
                pass
    try:
        if remove_root:
            os.rmdir(root)
    except:
        logging.warning(f'failed to delete {root}.')


def kill_process(process_name, search_re: bool = False, except_ok=True):
    logging.info(f"kill process: {process_name}")
    hit_proc = False
    for process in psutil.process_iter():
        if search_re:
            if re.search(process_name, process.name(), re.IGNORECASE):
                hit_proc = True
        else:
            if process.name().lower() == process_name.lower():
                hit_proc = True
        try:
            if hit_proc:
                hit_proc = False
                process.kill()
                logging.info(f"{process.name()} is killed successfully.")
        except:
            if not except_ok:
                raise
            else:
                logging.warning(traceback.format_exc())


def unzip_file(zip_file: str, target_dir: str):
    try:
        subprocess.check_call(f'7z x {zip_file} -o{target_dir}', shell=True)
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while extracting {zip_file}: {str(e)}')
        raise
