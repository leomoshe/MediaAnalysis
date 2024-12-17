ROOT_SRC = "/home/leo/Public/export1/"
ROOT_DST = "/home/leo/Public/export2/aaa/"

MAPPING_FILE = "file_mapping.json"
import os
import fnmatch
import shutil
import base64
import uuid
import json


def copy_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy2(src_path, dst_path)


def copy_with_structure(src_dir, dst_dir):
    result = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            base, extension = os.path.splitext(file)
            src_file_path = os.path.join(root, file)
            if extension == ".obf":
                with open(MAPPING_FILE, 'r', encoding="utf-8") as f:
                    mapping = json.load(f)

                entry = mapping[src_file_path.replace(src_dir, '')]
                org_path = entry["org_path"]
                obf_content = entry["obf_content"]
                dst_file_path = os.path.join(dst_dir, org_path)

                if obf_content:
                    with open(src_file_path, 'r', encoding="utf-8") as f:
                        obf_data = f.read()
                    org_content = base64.b64decode(obf_data.encode("utf-8"))
                    os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)                    
                    with open(dst_file_path, 'wb') as f:
                        f.write(org_content)
                else:
                    copy_file(src_file_path, dst_file_path)
            else:
                org_path = src_file_path.replace(src_dir, '')
                copy_file(src_file_path, os.path.join(dst_dir, org_path))


if __name__ == "__main__":
    copy_with_structure(ROOT_SRC, ROOT_DST)
