# File Integrity Checks (SHA3-512)

Python을 사용하여 디렉토리 내 파일들의 **SHA3-512 해시를 계산**하고, 저장된 해시와 **무결성**을 비교하는 프로젝트입니다.  
멀티 스레드를 사용해 빠르게 해시를 계산하고, 진행 바를 통해 작업 상황을 직관적으로 확인할 수 있습니다.

---

## 프로젝트 구성 (Files)

- **get_hash.py**  
  현재 디렉토리와 하위 디렉토리에 있는 파일들을 해시 계산하여, `list.csv`로 저장합니다.  
  - `exclude.txt`에 명시된 파일·폴더는 해시 계산에서 제외됩니다.
  - 해시 계산 도중 권한 부족(PermissionError) 등이 발생하면 `result.txt`에 관련 정보가 저장됩니다.
  - 정상적으로 모든 파일을 해시 계산한 경우, `result.txt`가 생성되지 않습니다.

- **hash.py**  
  `get_hash.py`에서 생성한 `list.csv`(파일경로와 SHA3-512 해시값 정보를 가짐)를 기준으로 실제 파일과의 무결성을 검사합니다.  
  - 해시가 변경된 파일, 새로 생긴 파일, 누락된 파일 정보를 `result.txt`에 기록합니다.
  - 권한 부족인 파일은 `error.txt`에 기록됩니다.
  - `result.txt`가 없으면 무결성 검사에 통과한 것입니다.

- **exclude.txt** (옵션)  
  해시 계산과 무결성 검사 모두에서 **제외**할 파일명(또는 디렉토리명, 패턴)을 작성합니다.  
  - 예:  
    ```
    exclude_file1.txt
    folder1/exclude_file2.txt
    C:/Users/user/documents/exclude_file3.txt
    ./logs
    *.txt
    ./hello/*.cs
    /games
    ```
  - 상대/절대 경로 및 와일드카드(`*`) 가능.

- **list.csv**  
  `get_hash.py` 실행 시 생성되는 파일.  
  - CSV 형식: `[파일경로, 해시값]`  
  - `hash.py`에서 이 파일을 읽어 원본 해시와 비교.

- **result.txt**, **error.txt**  
  무결성 검사를 진행한 뒤 달라진 파일, 새로 생긴 파일, 누락된 파일(`result.txt`) 및 권한 문제(`error.txt`) 등이 기록됩니다.  

---

## 사용 방법 (Usage)

1. **해시 계산**  
   ```bash
   python get_hash.py
   ```
   - `get_hash.py`가 실행되면, 현재 디렉토리와 하위 디렉토리의 모든 파일을 대상으로 SHA3-512 해시값을 계산하여 `list.csv`에 저장합니다.
   - 만약 권한 문제가 있는 파일이 있으면 `result.txt`에 해당 파일 정보를 기록합니다.

2. **무결성 검사**  
   ```bash
   python hash.py
   ```
   - `hash.py`가 실행되면, `list.csv`에 기록된 해시값과 실제 파일 해시값을 비교하여 결과를 `result.txt`에 기록합니다.
     - [파일 변경]: 기존 해시와 현재 해시가 다른 경우
     - [새로운 파일]: `list.csv`에 없는 파일이 새로 발견된 경우
     - [파일 누락]: `list.csv`에는 있지만 실제 파일이 존재하지 않는 경우
   - 권한 문제가 있는 파일은 별도로 `error.txt`에 기록합니다.
   - `result.txt`가 생성되지 않았다면 무결성 검사를 통과한 것입니다.

3. **스레드 개수 조정**  
   - `get_hash.py`와 `hash.py` 내의 `use_thread` 변수를 수정하여 사용 스레드 수를 변경할 수 있습니다.
   - `use_thread = 0` → CPU 스레드 수만큼 자동 할당  
   - `use_thread > CPU 스레드 수` → 경고 메시지 출력 후 5초 대기, 이후 모든 스레드를 사용

4. **제외 파일/폴더 설정**  
   - `exclude.txt`에 제외할 파일 혹은 폴더, 패턴을 추가합니다.
   - 예: `*.txt`, `C:/Temp`, `./logs`, `folder/subfolder/*.log` 등

---

## 예시 시나리오
1. 어떤 디렉토리(예: `C:/workspace/test`) 안에 이 스크립트(`get_hash.py`와 `hash.py`)와 `exclude.txt`가 있다고 가정합니다.
2. `exclude.txt`에는 해시를 계산하지 않을 파일 혹은 폴더, 예: `*.tmp` 파일을 제외하려고 작성합니다.
3. `python get_hash.py` 실행 → 모든 `.tmp`를 제외한 파일들이 해시 계산되어 `list.csv` 생성
4. `python hash.py` 실행 → `list.csv`의 정보와 현재 디렉토리를 비교하여 변경 사항을 `result.txt`에 기록
5. 변경된 파일이 없다면 `result.txt`가 생성되지 않음 → 무결성 통과!

---

## 라이선스 (License)
본 프로젝트는 [MIT 라이선스](https://github.com/prj-uiharu/file_integrity_checks/blob/main/LICENSE)를 따릅니다.  
(원본 코드 출처나 라이선스 관련 규정은 필요에 따라 README에 기재하십시오.)

---

## 기여 (Contributing)
- 버그 리포트나 기능 제안 등은 이슈(issues)로 등록해주세요.
- 본 프로젝트를 사용했다면, 이슈나 PR로 알려주시면 감사하겠습니다. (별도로 자랑하고 싶어서 그래요!)