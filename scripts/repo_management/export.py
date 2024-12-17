ROOT_SRC = "../../"
ROOT_DST = "/home/leo/Public/export1/"
#ROOT_DST = "~/Public/export"

OBF_FOLDERS = [
    "../../.vscode",
    "../../documents",
    "../../MediaAnalysisViewer",
    "../../models",
    "../../preprocess",
    "../../scripts"
]

OBF_FILES = [
    "../../.gitignore",
    "../../readme.md"
]

OBF_NAME_FILES = [
    "../../preprocess/data/media/d1.mp4",
    "../../preprocess/data/media/d2.mp3",
    "../../preprocess/data/media/d3.mp4",
    "../../preprocess/data/shabtay.wav",
    "import.py"
]

EXCLUDE_DIRS = [
    ".venv",
    "wheels",
    "output*",
    "../../MediaAnalysisViewer/Lahav Pilot",
    "../../MediaAnalysisViewer/tsrt"
]

EXCLUDE_FILES = [
    "*.log",
    "*.pyc",
    "*.doc",
    "*.tsrt.csv",
    "*.wav",
    "*.mp3",
    "*.mp4",
    "import.py"
]

MAPPING_FILE = "file_mapping.json"
import os
import fnmatch
import shutil
import base64
import uuid
import json

def find_files_dir(directory, exclude_dirs, exclude_files):
    result = []
    for root, dirs, files in os.walk(directory):
        # filter out dirs
        dirs[:] = [dir for dir in dirs if not any(fnmatch.fnmatch(os.path.join(root, dir), pattern) for pattern in exclude_dirs)]

        # filter out files
        for file in files:
            if not any(fnmatch.fnmatch(file, pattern) for pattern in exclude_files):
                result.append(os.path.join(root, file))

    return result


def find_files_dirs(directories, exclude_dirs, exclude_files):
    result = []
    for directory in directories:
        result.extend(find_files_dir(directory, exclude_dirs, exclude_files))

    return result


def copy_with_structure(dst_root, src_root, files, obfuscate_content=True, obfuscate_name=True) :

    for file_path in files:
        rel_path = os.path.relpath(file_path, src_root)
        dst_path = os.path.join(dst_root, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        if obfuscate_name:
            new_dst_path = os.path.join(os.path.dirname(dst_path), f"{uuid.uuid4().hex}.obf")

            mapping = {}
            if os.path.exists(MAPPING_FILE):
                with open(MAPPING_FILE, "r", encoding="utf-8") as fm:
                    mapping = json.load(fm)
            mapping[new_dst_path.replace(dst_root, '')] = {
                "org_path": dst_path.replace(dst_root, ''),
                "obf_content": obfuscate_content
            }
            with open(MAPPING_FILE, "w", encoding="utf-8") as fm:
                json.dump(mapping, fm, indent=4)
                
        else:
            new_dst_path = dst_path

        if obfuscate_content:
            with open(file_path, "rb") as f:
                data = f.read()
            obfuscated_data = base64.b64encode(data).decode("utf-8")
            
            with open(new_dst_path, "w", encoding="utf-8") as f:
                f.write(obfuscated_data)
        else:
            shutil.copy2(file_path, new_dst_path)

        print(f"Copied: {file_path} -> {new_dst_path}")


if __name__ == "__main__":
    os.remove(MAPPING_FILE) if os.path.exists(MAPPING_FILE) else None

    files_dirs = find_files_dirs(OBF_FOLDERS, EXCLUDE_DIRS, EXCLUDE_FILES)
    copy_with_structure(ROOT_DST, ROOT_SRC, files_dirs)
    copy_with_structure(ROOT_DST, ROOT_SRC, OBF_FILES)

    copy_with_structure(ROOT_DST, ROOT_SRC, OBF_NAME_FILES, False)

    copy_with_structure(ROOT_DST, ROOT_SRC, [MAPPING_FILE], False, False)


