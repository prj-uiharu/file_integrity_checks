
# file_integrity_checks
File integrity check using Python to compare SHA3-512 hashes
SHA3-512 해시를 비교하여 무결성 검사를 하는 파이썬 코드입니다.

# File Configuration(파일 구성)
The file composition for this project is as follows:
본 프로젝트의 파일 구성은 다음과 같습니다.

* get_hash.py
* hash.py

## get_hash.py

Stores the SHA3-512 hash value of all files in the current directory and subdirectories in the list.txt file.
현재 디렉토리와 하위 디렉토리들에 있는 모든 파일의 SHA3-512 해시값을 `list.txt` 파일에 저장합니다.

The storage format is as follows:
저장 형태는 다음과 같습니다.

> 1.exe, 7b57d8b5e14917ae81966b13200c48fe40371766f520743bc27ea99a918c1417963962f9339da31c1a8c44cb3baa3a7756d5e01f277c7ba7ab9b80bd78f23ce1
> 2.pdf, b95d0e7a804a16756e39455efeaf185ef12181edf6b5184a7b0316f88ac319d6cad721c6c7eff7e2cf1db9c034aa347ba41544e781e4b2afb2240a9645368931
> 3.jpg, 7a7a1cf8cb35946e1bae52e6e9216d5139381a7f68bb16a11e208c386dd461401be5e540d72c5af88dd5f68ddb2544a24440b2edd4f4a714ca97bb960b4290fb
> 4.jpg, 61430fa8857f80b0d57cd682242e2f90cc4bc3f4eec0e9d6e51e6d3b6a51529255a11b8e5558292aaed3f998bbade075668eaeb730d9cfaf47af8931d4af3427
> 6.jpg, 85c89961d9fc59d4eda403c57bc7c21fddec97b6ae7056aa8f196b64dddeef2dcc33a052c25239caacf18bf9eff5e3903cfc2f2172e3e3609285500ea1dfce2f

Save it as **`filename, hash value`**.
**`파일명, 해시값`** 형태로 저장합니다.

## hash.py
Compare the hash values in the `list.txt` file with the hash values of all files in the current directory and subdirectories to check for equality.
`list.txt` 파일에 있는 해시값과 현재 디렉토리와 하위 디렉토리들에 있는 모든 파일의 해시값을 비교하여 동일 여부를 확인합니다.

If they are not the same, you will see the hash value in the `list.txt` file, the hash value of the current file, and the date it was modified.
만약 동일하지 않다면 `list.txt` 파일에 있는 해시값과 현재 파일의 해시값, 수정된 날짜가 표시됩니다.

If a file is found that is not in the `list.txt` file, the hash value of the current file is displayed.
`list.txt` 파일에 없는 파일이 발견된 경우, 현재 파일의 해시값이 표시됩니다.

If the `result.txt` file does not exist, the integrity check passes; if it does exist, the integrity check fails.
`result.txt` 파일이 없다면 무결성 검사를 통과한 것이고, 파일이 존재한다면 무결성 검사를 통과하지 못한 것입니다.

Files that you don't want to compare hash values to can be written in a `exclude.txt` file in the same directory.
해시값 비교를 원치 않는 파일들은 동일한 디렉토리에 `exclude.txt` 파일 안에 파일명을 작성하면 됩니다.

# Commonalities(공통사항)
## Specify files/directories to exclude(제외할 파일/디렉토리 지정)
You can specify files or directories to exclude.
제외할 파일 또는 디렉토리를 지정할 수 있습니다.

Files that you don't want to store/verify hash values can be written in a `exclude.txt` file in the same directory.
해시값 저장/확인을 원치 않는 파일들은 동일한 디렉토리에 `exclude.txt` 파일 안에 파일명을 작성하면 됩니다.

The `exclude.txt` file can be entered in the following format
`exclude.txt` 파일은 다음의 형식대로 입력하면 됩니다.

> exclude_file1.txt
> folder1/exclude_file2.txt
> C:/Users/user/documents/exclude_file3.txt
> ./logs
> \*\.txt
> ./hello/\*\.cs
> /games

Recognizes both relative and absolute paths. You can also exclude entire directories. Wildcarding with * (asterisk) is also possible.
상대경로, 절대경로 모두 인식합니다. 디렉토리 전체 제외도 가능합니다. *(애스터리스크)로 와일드 카드 지정도 가능합니다.

On Windows, the root directory starts with the drive letter (C:, D:\, etc.), so `/directory` is not actually a valid absolute path, so change it to a valid absolute path. It is not guaranteed to work.  On Linux or macOS, it doesn't matter because `/directory` points to the `directory` folder in the root directory, just like `C:/directory`.
윈도우에서는 루트 디렉터리가 드라이브 문자(C:, D:\ 등)로 시작하기 때문에, `/directory`는 실제로는 올바른 절대 경로가 아니기에 유효한 절대 경로로 변경하길 바랍니다. 정상 작동을 보장하지 않습니다.  `C:/directory`와 같이 말이죠. 리눅스나 macOS에서는 `/directory`가 루트 디렉터리에 있는 `directory` 폴더를 가리키기에 상관 없습니다.

## 멀티 스레드 사용
You can use multiple threads to make your work even faster. You can do this by entering the number of threads to use in the `use_threads` variable. The default value is `4`.
멀티 스레드를 사용하여 작업을 더욱 빠르게 할 수 있습니다. `use_threads` 변수에 사용할 스레드 수를 입력하면 됩니다. 기본값은 `4` 입니다.

If you enter 0, all threads are used. If you enter a number greater than the number of threads on the CPU, it prints `Warning! The number of threads you entered is greater than the number of threads on the CPU. You have enabled all threads.'` and then waits 5 seconds. All threads are then enabled.
만약 0을 입력하면 모든 스레드를 사용합니다. CPU의 스레드 수보다 큰 수를 입력하면 `'Warning! The number of threads you entered is greater than the number of threads on the CPU. You have enabled all threads.'` 라고 출력 후, 5초동안 대기합니다. 이후 모든 스레드를 사용합니다.

## Show progress bar(진행 바 표시)
Displays a progress bar at the bottom.
하단에 진행 바가 표시됩니다.

# License(라이선스)
This project is available under the [MIT License](https://github.com/prj-uiharu/file_integrity_checks/blob/main/LICENSE).
본 프로젝트는 [MIT 라이선스](https://github.com/prj-uiharu/file_integrity_checks/blob/main/LICENSE)로 제공됩니다.

If you use this project, I'd really appreciate it if you'd let me know in the issues tab, it's no big deal, I just like to show off.
혹시 본 프로젝트를 사용하신다면, 이슈 탭으로 알려주시면 정말 감사하겠습니다. 별건 아니고, 자랑하고 싶어서 그런 거니깐요.