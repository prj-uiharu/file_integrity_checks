import os
import sys
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar
import time
import fnmatch

def sha3_512_hash(file_path):
    BUF_SIZE = 65536
    sha3_512 = hashlib.sha3_512()

    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha3_512.update(data)
        return file_path, sha3_512.hexdigest()
    except PermissionError:
        return file_path, None

def load_exclude_list(exclude_file):
    exclude_list = []
    if os.path.isfile(exclude_file):
        with open(exclude_file, 'r', encoding='utf-8') as f:
            for line in f:
                exclude_list.append(line.strip().rstrip('/'))
    return exclude_list

def save_file_hashes(output_file, result_file, futures):
    permission_denied_files = []

    with open(output_file, 'w', encoding='utf-8') as out_f:
        for future in futures:
            file_path, file_hash = future.result()
            if file_hash is not None:
                out_f.write(f'{file_path}, {file_hash}\n')
            else:
                permission_denied_files.append(file_path)

    if permission_denied_files:
        with open(result_file, 'w', encoding='utf-8') as res_f:
            for file_path in permission_denied_files:
                res_f.write(f'파일명: {file_path.name}\n파일 경로: {file_path}\n설명: 권한 문제로 인해 파일을 열 수 없습니다.\n\n')

def process_file_hashes(thread_count, total_files):
    if thread_count == 0:
        thread_count = os.cpu_count() or 1

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []
        with alive_bar(total_files, bar='smooth', spinner='dots_waves') as bar:
            for root, _, files in os.walk(start_path):
                root_path = Path(root)
                if any(str(root_path).startswith(exclude) or str(root_path.absolute()).startswith(exclude) for exclude in exclude_files):
                    continue

                for file in files:
                    file_path = root_path / file
                    if (str(file_path) not in exclude_files and
                        not any(str(file_path).startswith(exclude) or str(file_path.absolute()).startswith(exclude) for exclude in exclude_files) and
                        not any(fnmatch.fnmatch(str(file_path), pattern) or fnmatch.fnmatch(str(file_path.absolute()), pattern) for pattern in exclude_files)):
                        futures.append(executor.submit(sha3_512_hash, file_path))
                        bar()
        return futures

if __name__ == "__main__":
    start_path = '.'  # 현재 폴더를 시작 위치로 지정
    output_file = 'list.txt'  # 결과를 저장할 파일 이름
    result_file = 'result.txt'  # 권한 문제로 건너뛴 파일 정보를 저장할 파일 이름
    exclude_file = 'exclude.txt'  # 제외할 파일들이 있는 파일 이름
    use_thread = 4  # 사용할 스레드 수

    if getattr(sys, 'frozen', False):
        current_executable = os.path.abspath(sys.executable)
    else:
        current_executable = os.path.abspath(__file__)

    exclude_files = load_exclude_list(exclude_file)
    exclude_files.extend([output_file, exclude_file, result_file, current_executable])

    cpu_thread_count = os.cpu_count() or 1
    if use_thread == 0:
        use_thread = cpu_thread_count
    elif use_thread > cpu_thread_count:
        print("Warning! The number of threads you entered is greater than the number of threads on the CPU. You have enabled all threads.")
        time.sleep(5)
        use_thread = cpu_thread_count

    # 전체 파일 개수 계산
    total_files = sum([len(files) for _, _, files in os.walk(start_path)])

    # 멀티 스레드로 파일 해시 처리 진행
    futures = process_file_hashes(use_thread, total_files)

    # 결과 및 오류 파일 저장
    save_file_hashes(output_file, result_file, futures)
    print("\n\n * Save Complete!* \n\n")