import os
import shutil
import json
from pathlib import Path
from hashlib import md5
from tqdm import tqdm

def file_md5(path):
    hash_md5 = md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_snapshot(snapshot_path):
    if not Path(snapshot_path).exists():
        return {}
    with open(snapshot_path, 'r') as f:
        return json.load(f)

def save_snapshot(snapshot_path, data):
    with open(snapshot_path, 'w') as f:
        json.dump(data, f, indent=2)

def incremental_backup(source_dir, snapshot_path, exclude_dirs=None):
    """
    执行增量备份，只返回有变化的文件和被删除的文件/目录列表。
    exclude_dirs: 需要排除的目录名列表（只排除一级目录名）
    """
    source = Path(source_dir)
    prev_snapshot = load_snapshot(snapshot_path)
    new_snapshot = {}
    changed_files = []
    current_paths = set()
    exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
    # 统计总文件数
    total_files = 0
    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        total_files += len(files)
    with tqdm(total=total_files, desc='增量快照', unit='file') as pbar:
        for root, dirs, files in os.walk(source):
            # 跳过排除目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                src_file = Path(root) / file
                file_stat = src_file.stat()
                file_hash = file_md5(src_file)
                file_info = {
                    'mtime': file_stat.st_mtime,
                    'size': file_stat.st_size,
                    'md5': file_hash
                }
                new_snapshot[str(src_file)] = file_info
                prev_info = prev_snapshot.get(str(src_file))
                if prev_info != file_info:
                    changed_files.append(str(src_file))
                current_paths.add(str(src_file))
                pbar.update(1)
            for d in dirs:
                dir_path = str(Path(root) / d)
                current_paths.add(dir_path)
    # 检查被删除的文件和目录
    deleted_files = []
    deleted_dirs = []
    for old_path in prev_snapshot:
        if old_path not in current_paths:
            deleted_files.append(old_path)
    # 额外检查快照中存在但当前不存在的目录
    prev_dirs = set()
    for p in prev_snapshot:
        parent = str(Path(p).parent)
        while parent and parent not in prev_dirs:
            prev_dirs.add(parent)
            parent = str(Path(parent).parent)
    for d in prev_dirs:
        if d not in current_paths and d not in deleted_dirs:
            deleted_dirs.append(d)
    # 目录按路径长度从长到短排序，保证先删子目录
    deleted_dirs = sorted(deleted_dirs, key=lambda x: -len(x))
    # 过滤掉源目录本身
    deleted_dirs = [d for d in deleted_dirs if str(source) != d]
    deleted_files = [f for f in deleted_files if str(source) != f]
    deleted_all = deleted_files + deleted_dirs
    save_snapshot(snapshot_path, new_snapshot)
    return changed_files, deleted_all 