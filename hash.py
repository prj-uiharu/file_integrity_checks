import os
import hashlib
import fnmatch
from pathlib import Path
from datetime import datetime
from alive_progress import alive_bar
import time
from concurrent.futures import ThreadPoolExecutor
import csv

def sha3_512_hash(file_path):
    """
    주어진 파일의 SHA3-512 해시값을 반환합니다.
    """
    hasher = hashlib.sha3_512()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except PermissionError:
        return None

def read_list_csv(csv_path):
    """
    list.csv 파일을 읽어 (파일 경로, 해시값)을 딕셔너리로 반환합니다.
    CSV 형식: [파일경로, 해시값]
    """
    file_hash_map = {}
    with open(csv_path, 'r', newline='', encoding='utf-8') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            if len(row) < 2:
                continue
            file_name, file_hash = row
            file_hash_map[Path(file_name).resolve()] = file_hash
    return file_hash_map

def read_exclude_txt(file_path):
    """
    exclude.txt 파일을 읽어 제외 패턴을 세트로 반환합니다.
    """
    excluded_patterns = set()
    if Path(file_path).exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                pattern = line.strip()
                if pattern:
                    excluded_patterns.add(pattern)
    return excluded_patterns

def is_excluded(file_path, excluded_patterns):
    """
    지정된 exclude_patterns에 해당하는지 여부를 반환합니다.
    """
    file_path_str = str(file_path)
    file_path_abs_str = str(file_path.resolve())

    for pattern in excluded_patterns:
        if (fnmatch.fnmatch(file_path_str, pattern) or
            fnmatch.fnmatch(file_path_abs_str, pattern) or
            file_path_str.startswith(pattern) or
            file_path_abs_str.startswith(pattern)):
            return True
    return False

def check_file_integrity(file_hash_map, root_dir, result_file_path, exclude_patterns):
    """
    CSV로부터 읽어들인 원본 해시(file_hash_map)와 실제 파일들의 해시를 비교한 뒤,
    달라진 파일, 새로 생긴 파일 등을 result.txt에 기록합니다.
    """
    # 누락된 파일 체크를 위해 복사본
    remaining_originals = dict(file_hash_map)

    # 실제 검사할 파일 목록(제외 대상 제외)을 수집
    all_files = []
    for folder, _, files in os.walk(root_dir):
        folder_path = Path(folder)
        if is_excluded(folder_path, exclude_patterns):
            continue

        for file in files:
            file_path = folder_path / file
            if not is_excluded(file_path, exclude_patterns):
                all_files.append(file_path)

    with ThreadPoolExecutor() as executor:
        with open("error.txt", "w", encoding="utf-8") as error_file:
            with open(result_file_path, 'w', encoding='utf-8') as result_file:
                with alive_bar(len(all_files), title="Checking files") as bar:
                    future_to_path = {
                        executor.submit(sha3_512_hash, file_path): file_path
                        for file_path in all_files
                    }

                    for future in future_to_path:
                        current_hash = future.result()
                        file_path = future_to_path[future]
                        file_path_abs = file_path.resolve()

                        if current_hash is None:
                            # Permission denied
                            error_file.write(f"Permission denied: {file_path_abs}\n")
                        else:
                            # 파일 수정 시간
                            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            mod_time_str = mod_time.strftime('%Y-%m-%d %H:%M:%S')

                            # 기존 목록에 있는지 확인
                            if file_path_abs in remaining_originals:
                                original_hash = remaining_originals[file_path_abs]
                                # 해시값이 달라졌다면 변경 기록
                                if current_hash.lower() != original_hash.lower():
                                    result_file.write(
                                        f"[파일 변경]\n"
                                        f"파일 이름: {file_path.name}\n"
                                        f"Original SHA3-512: {original_hash}\n"
                                        f"Current  SHA3-512: {current_hash}\n"
                                        f"Modified on: {mod_time_str}\n\n"
                                    )
                                # 처리한 항목은 remaining_originals에서 제거
                                del remaining_originals[file_path_abs]
                            else:
                                # 기존 목록에 없는(새로운) 파일
                                result_file.write(
                                    f"[새로운 파일]\n"
                                    f"파일 이름: {file_path.name}\n"
                                    f"SHA3-512: {current_hash}\n"
                                    f"Modified on: {mod_time_str}\n\n"
                                )

                        bar()

                # 누락된 파일(원래 목록에 있었지만 실제로는 없는 파일) 기록
                for missing_file, orig_hash in remaining_originals.items():
                    result_file.write(
                        f"[파일 누락]\n"
                        f"파일 경로: {missing_file}\n"
                        f"Original SHA3-512: {orig_hash}\n"
                        f"상태: 파일이 존재하지 않음\n\n"
                    )

def main():
    list_csv_path = "list.csv"
    root_dir = "."
    result_txt_path = "result.txt"
    exclude_txt_path = "exclude.txt"

    # CSV에서 (파일 경로, 해시값) 맵핑 정보 읽기
    file_hash_map = read_list_csv(list_csv_path)
    # 제외 패턴 읽기
    excluded_patterns = read_exclude_txt(exclude_txt_path)
    # 검사에서 제외할 파일들
    excluded_patterns |= {
        list_csv_path,
        result_txt_path,
        exclude_txt_path,
        __file__
    }

    check_file_integrity(file_hash_map, root_dir, result_txt_path, excluded_patterns)
    print("\n\n * Integrity Checks Complete! * \n\n")

if __name__ == "__main__":
    main()
