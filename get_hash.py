import os
import sys
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar
import time
import fnmatch
import csv

def sha3_512_hash(file_path):
    """
    주어진 파일 경로에 대한 SHA3-512 해시값을 계산하여 반환합니다.
    권한 문제로 열 수 없는 경우 None을 반환합니다.
    """
    BUF_SIZE = 65536
    sha3_512 = hashlib.sha3_512()

    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha3_512.update(data)
        return sha3_512.hexdigest()
    except PermissionError:
        return None

def load_exclude_list(exclude_file):
    """
    exclude.txt에 적힌 제외 파일/디렉토리 목록을 불러옵니다.
    """
    exclude_list = []
    if os.path.isfile(exclude_file):
        with open(exclude_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().rstrip('/')
                if line:
                    exclude_list.append(line)
    return exclude_list

def is_excluded(file_path, exclude_patterns):
    """
    지정된 exclude_patterns와 매칭되는지 판단하여
    제외 대상인지 여부를 반환합니다.
    """
    file_path_str = str(file_path)
    file_path_abs_str = str(file_path.resolve())

    # 패턴 매칭 (fnmatch) 또는 시작 경로 일치 등을 확인
    for pattern in exclude_patterns:
        # 절대 경로/상대 경로, 와일드카드 등 상황 모두 고려
        if (fnmatch.fnmatch(file_path_str, pattern) or
            fnmatch.fnmatch(file_path_abs_str, pattern) or
            file_path_str.startswith(pattern) or
            file_path_abs_str.startswith(pattern)):
            return True
    return False

def save_file_hashes(output_csv, result_file, futures):
    """
    멀티 스레드 작업 결과(파일 해시값)를 CSV 형태로 저장하고,
    권한 문제가 있는 파일은 별도로 기록합니다.
    """
    permission_denied_files = []

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.writer(csv_out)
        for future in futures:
            file_path, file_hash = future.result()
            if file_hash is not None:
                # CSV 행: [파일경로, 해시값]
                writer.writerow([file_path, file_hash])
            else:
                permission_denied_files.append(file_path)

    if permission_denied_files:
        with open(result_file, 'w', encoding='utf-8') as res_f:
            for p_file in permission_denied_files:
                res_f.write(
                    f'파일명: {p_file.name}\n'
                    f'파일 경로: {p_file}\n'
                    f'설명: 권한 문제로 인해 파일을 열 수 없습니다.\n\n'
                )

def process_file_hashes(start_path, exclude_patterns, thread_count):
    """
    주어진 start_path 하위의 모든 파일에 대해 SHA3-512 해시를 계산한 뒤
    ThreadPoolExecutor를 통해 병렬 처리를 수행합니다.
    """
    # 0입력 시 CPU 코어 수 만큼 사용
    if thread_count == 0:
        thread_count = os.cpu_count() or 1
    # CPU 스레드 수보다 클 경우 경고 후 5초 대기
    elif thread_count > (os.cpu_count() or 1):
        print("Warning! The number of threads you entered is greater than the number of threads on the CPU. "
              "You have enabled all threads.")
        time.sleep(5)
        thread_count = os.cpu_count() or 1

    # 실제 해싱할 파일 목록 수집 (제외 대상 제외)
    all_files = []
    for root, _, files in os.walk(start_path):
        root_path = Path(root)
        # 디렉토리 자체가 제외 대상이면 건너뜀
        if is_excluded(root_path, exclude_patterns):
            continue

        for file in files:
            file_path = root_path / file
            if not is_excluded(file_path, exclude_patterns):
                all_files.append(file_path)

    futures = []
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        with alive_bar(len(all_files), bar='smooth', spinner='dots_waves') as bar:
            for file_path in all_files:
                futures.append(executor.submit(
                    lambda p: (p, sha3_512_hash(p)),
                    file_path
                ))
                bar()
    return futures

if __name__ == "__main__":
    # 기본 설정
    start_path = '.'                # 현재 폴더를 시작 위치로 지정
    output_csv = 'list.csv'         # 결과를 저장할 CSV 파일
    result_file = 'result.txt'      # 권한 문제로 건너뛴 파일 정보를 저장
    exclude_file = 'exclude.txt'    # 제외할 파일들이 적힌 파일
    use_thread = 4                  # 사용할 스레드 수

    if getattr(sys, 'frozen', False):
        current_executable = os.path.abspath(sys.executable)
    else:
        current_executable = os.path.abspath(__file__)

    # exclude 목록 불러오기
    exclude_patterns = load_exclude_list(exclude_file)
    # 결과 CSV, exclude.txt, result_file, 본인 스크립트 등은 제외 대상에 추가
    exclude_patterns.extend([output_csv, exclude_file, result_file, current_executable])

    # 해시 계산 (멀티 스레드)
    futures = process_file_hashes(start_path, exclude_patterns, use_thread)

    # CSV에 저장
    save_file_hashes(output_csv, result_file, futures)
    print("\n\n * Save Complete! * \n\n")
