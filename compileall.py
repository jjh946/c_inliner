import os
import subprocess

def compile_c_files(src_directory, build_directory):
    # 소스 디렉토리에서 모든 .c 파일 목록을 가져옴
    src_files = [f for f in os.listdir(src_directory) if f.endswith('.c')]
    
    # 빌드 디렉토리로 작업 디렉토리 변경
    os.chdir(build_directory)

    # 각 소스 파일에 대해 make 명령 실행
    for src_file in src_files:
        # 소스 파일명에서 확장자 제거
        target_name = os.path.splitext(src_file)[0]
        # make 명령 구성
        command = ['make', f'src/{target_name}']

        try:
            subprocess.run(command, check=True)
            print(f'Compilation of {src_file} with "{command}" succeeded.')
        except subprocess.CalledProcessError as e:
            print(f'Compilation of {src_file} with "{command}" failed: {e}')
            continue
            # 에러 무시하고 계속 진행

if __name__ == "__main__":
    src_directory = '/home/junh/coreutils-9.3/src'
    build_directory = '/home/junh/buildcoreutil'
    compile_c_files(src_directory, build_directory)
