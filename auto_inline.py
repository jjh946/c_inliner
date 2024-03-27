import os
import sys
import clang.cindex

clang.cindex.Config.set_library_file("/home/junh/compiler/lib/libclang.so.14.0.0")

def modify_function_declarations(original_file, modifications):
    # 파일의 전체 내용을 읽어 lines 배열에 저장.
    with open(original_file, 'r') as file:
        lines = file.readlines()

    for line_number, modify_func in modifications:
        lines[line_number - 1] = modify_func(lines[line_number - 1])

    with open(original_file, 'w') as file:
        file.writelines(lines)
    print(f"Modified file: {original_file}")

def collect_modifications(cursor, file_name, modifications):
    if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL and cursor.location.file and cursor.location.file.name == file_name:
        if "main" not in cursor.spelling:  # main 함수는 제외합니다.
            print('Found function %s [line=%s, col=%s]' % (
                cursor.spelling, cursor.location.line, cursor.location.column))
            modifications.append((cursor.location.line))
    for child in cursor.get_children():
        collect_modifications(child, file_name, modifications)

def process_file(file_path):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)
    file_name = tu.spelling

    def modify_line(lines, line_number):
        # 현재 라인이 함수 선언의 일부인지 확인합니다.
        current_line = lines[line_number - 1].strip()
        previous_line = lines[line_number - 2].strip() if line_number > 1 else ""

        # 이전 라인과 현재 라인을 검사하여 "static" 키워드 위치를 찾습니다.
        if "static" in previous_line or "static" in current_line:
            # "static"이 있는 라인을 찾습니다.
            target_line_index = line_number - 2 if "static" in previous_line else line_number - 1
            target_line = lines[target_line_index]

            # "static" 키워드를 "static inline __attribute__((always_inline))"로 변경합니다.
            modified_line = target_line.replace("static", "static inline __attribute__((always_inline))", 1)
            lines[target_line_index] = modified_line

            return True  # 성공적으로 수정되었음을 나타냅니다.

        return False  # 수정할 필요가 없음을 나타냅니다.


    # 파일 읽기
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # collect_modifications 함수를 호출하여 함수 선언을 찾고, modifications 배열에 추가합니다.
    modifications = []
    collect_modifications(tu.cursor, file_name, modifications)
    
    # 파일 내용 수정
    for line_number in modifications:
        modify_line(lines, line_number)  # 여기서 실제 내용을 수정

    # 파일 쓰기
    with open(file_name, 'w') as file:
        file.writelines(lines)

def main(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".c"):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                process_file(file_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    main(sys.argv[1])