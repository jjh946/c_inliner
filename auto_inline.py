import os
import sys
import clang.cindex

clang.cindex.Config.set_library_file("/home/junh/compiler/lib/libclang.so.14.0.0")

def modify_function_declarations(original_file, modifications):
    with open(original_file, 'r') as file:
        lines = file.readlines()

    for line_number, modify_func in modifications:
        lines[line_number - 1] = modify_func(lines[line_number - 1])

    with open(original_file, 'w') as file:
        file.writelines(lines)
    print(f"Modified file: {original_file}")

def collect_modifications(cursor, modify_func, file_name, modifications):
    if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL and cursor.location.file and cursor.location.file.name == file_name:
        if "main" not in cursor.spelling:  # main 함수는 제외합니다.
            print('Found function %s [line=%s, col=%s]' % (
                cursor.spelling, cursor.location.line, cursor.location.column))
            modifications.append((cursor.location.line, modify_func))
    for child in cursor.get_children():
        collect_modifications(child, modify_func, file_name, modifications)

def process_file(file_path):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)
    file_name = tu.spelling

    def modify_line(line):
         # 'ARGMATCH_VERIFY' 매크로를 포함하는 라인은 수정하지 않음
        if "ARGMATCH_VERIFY" in line:
            return line  # 매크로가 포함된 라인은 변경하지 않음

        # 이미 `inline`이 있는 경우 혹은 `static`이 있는 경우에만 수정합니다.
        if "static" in line and "inline" not in line:
            return line.replace("static", "static inline __attribute__((always_inline))")
        elif "inline" not in line:
            return "inline __attribute__((always_inline)) " + line
        return line  # 이미 inline이 있거나, static이 없는 경우는 변경하지 않습니다.

    modifications = []
    collect_modifications(tu.cursor, modify_line, file_name, modifications)
    modify_function_declarations(file_name, modifications)

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