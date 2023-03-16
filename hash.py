import os
import hashlib
import fnmatch
from pathlib import Path
from datetime import datetime
from alive_progress import alive_bar
import threading
from concurrent.futures import ThreadPoolExecutor
import time

def sha3_512_hash(file_path):
    hasher = hashlib.sha3_512()
    with open(file_path, 'rb') as f:
        while (chunk := f.read(8192)):
            hasher.update(chunk)
    return hasher.hexdigest()

def read_list_txt(file_path):
    file_hash_map = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            file_name, file_hash = line.strip().split(', ')
            file_hash_map[Path(file_name).resolve()] = file_hash
    return file_hash_map

def read_exclude_txt(file_path):
    excluded_patterns = set()
    if Path(file_path).exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                excluded_patterns.add(line.strip())
    return excluded_patterns

def is_excluded(file_path, excluded_patterns):
    for pattern in excluded_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def check_files_and_write_results(file_hash_map, root_dir, result_file_path, script_file_path, excluded_patterns):
    excluded_patterns |= {list_txt_path, result_txt_path, script_file_path, exclude_txt_path}

    with open(result_file_path, 'w', encoding='utf-8') as result_file:
        with alive_bar(len(file_hash_map), title="Checking files") as bar:
            for folder, _, files in os.walk(root_dir):
                for file in files:
                    file_path = Path(folder) / file
                    file_path_absolute = file_path.resolve()

                    if is_excluded(str(file_path_absolute), excluded_patterns):
                        continue

                    current_hash = sha3_512_hash(file_path)
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                    if file_path_absolute in file_hash_map:
                        original_hash = file_hash_map[file_path_absolute]
                        if current_hash.lower() != original_hash.lower():
                            result_file.write(f"{file}\nOriginal SHA3-512: {original_hash}\nCurrent SHA3-512: {current_hash}\nModified on: {mod_time}\n\n")
                        del file_hash_map[file_path_absolute]
                    else:
                        result_file.write(f"{file}\nSHA3-512: {current_hash}\nModified on: {mod_time}\n\n")

                    bar()

        for file, original_hash in file_hash_map.items():
            result_file.write(f"{file}\nOriginal SHA3-512: {original_hash}\nMissing\n\n")

if __name__ == "__main__":
    list_txt_path = "list.txt"
    root_dir = "."
    result_txt_path = "result.txt"
    script_file_path = __file__
    exclude_txt_path = "exclude.txt"

    file_hash_map = read_list_txt(list_txt_path)
    excluded_patterns = read_exclude_txt(exclude_txt_path)

    use_threads = 4
    cpu_threads = os.cpu_count()

    if use_threads == 0:
        use_threads = cpu_threads
    elif use_threads > cpu_threads:
        print("Warning! The number of threads you entered is greater than the number of threads on the CPU. You have enabled all threads.")
        time.sleep(5)

    check_files_and_write_results(file_hash_map, root_dir, result_txt_path, script_file_path, excluded_patterns)

    print("\n\n * Integrity Checks Complete!* \n\n")
