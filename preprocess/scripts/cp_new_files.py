import os
import re
from pathlib import Path
import shutil

def folder_files(folder):
    posfix = ".tsrt.csv"
    filenames = os.listdir(folder)
    #res = filename in filenames if filename.endswith(posfix)
    res = [filename for filename in filenames if filename.endswith(posfix)]
    return res


def copy_files(src_full_path_filenames, dst_folder):
    try:
        #[shutil.copy2(os.path.join(dst_folder, filename)) for ]
        [shutil.copy2(filename, os.path.join(dst_folder, Path(filename).name)) for filename in src_full_path_filenames]
        [print(filename + "->" + os.path.join(dst_folder, Path(filename).name)) for filename in src_full_path_filenames]
    except Exception as exc:
        print(f"Error copying files: {exc}")

def main():
    postfix_len = len("_XXXXXXXX_XXXXXX.tsrt.csv")

    folder_a = "/mnt/prsecspma/tsrt/History_2024_06_19/"
    filenames_a = folder_files(folder_a)#[15:20]

    folder_b = "/mnt/prsecspma/tsrt/History/"
    filenames_b = folder_files(folder_b)#[:3]

    filenames_a_without_postfix = [filename[:-postfix_len] for filename in filenames_a]
    filenames_b_without_postfix = [filename[:-postfix_len] for filename in filenames_b]

    new_files_prefix = set(filenames_a_without_postfix) - set(filenames_b_without_postfix)
    common_files_prefix = list(set(filenames_a_without_postfix) & set(filenames_b_without_postfix))


    dst_folder = "/mnt/prsecspma/tsrt/History_last/"
    #Path(dst_folder).mkdir(parents=True, exist_ok=True)

    #src_full_path = [os.path.join(folder_b, filename) for filename in filenames_b]
    #copy_files(src_full_path, dst_folder)

    common_files_prefix_re = "|".join(common_files_prefix)
    pattern = re.compile(fr"({common_files_prefix_re})_\d{{8}}_\d{{6}}\.tsrt\.csv")
    src_full_path = [os.path.join(folder_a, filename) for filename in filenames_a if not pattern.match(filename)]
    copy_files(src_full_path, dst_folder)

    #common_files_prefix = ["aa", "bb", "cc"]
    common_files_prefix_re = "|".join(common_files_prefix)
    #pattern = re.compile(fr"(aa|bb|cc)_\d{{8}}_?\d{{8}}\.tsrt\.csv")
    pattern = re.compile(fr"({common_files_prefix_re})_\d{{8}}_\d{{6}}\.tsrt\.csv")
    #pattern = re.compile(fr"({'"|".join(common_files_prefix)})_\d{{8}}_?\d{{8}}\.tsrt\.csv")
    #pattern = re.compile(fr"({"("|".join(common_files_prefix)})})_\d{{8}}_?\d{{8}}\.tsrt\.csv")
    complete_filename = [os.path.join(folder_a, filename) for filename in filenames_a if pattern.match(filename)]
    res = [print(filename[:-postfix_len]) for filename in filenames]



if __name__ == "__main__":
    
    main()