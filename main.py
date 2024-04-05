import os
import hashlib
import time
from typing import Optional
from messages import MSG_UPDATED, MSG_COPIED, MSG_DELETED, MSG_REG_SOURCE_FOLDER, MSG_REG_REPLICA_FOLDER, \
    MSG_CONFIG_FILE, MSG_FOLDER_FOUND, MSG_FOLDER_NF, MSG_REPLICA_FOUND, MSG_REPLICA_NF, MSG_INSERT_TIME, \
    MSG_INSERT_TIME_ERROR, MSG_INSERT_LOG

CONFIG_FILE = 'config.txt'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = ''


def write_log(message: str) -> None:
    now = time.strftime(TIME_FORMAT, time.localtime())
    with open(LOG_FILE, 'a') as f:
        f.write(f'[{now}] {message}\n')


def get_config() -> tuple[Optional[str], Optional[str]]:
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            lines = f.readlines()
            folder = lines[0].split(':')[1].strip()
            replica = lines[1].split(':')[1].strip()
        return folder, replica
    else:
        return None, None


def compare_files(file1: str, file2: str) -> bool:
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            return hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest()


def sync_files(folder: str, replica: str) -> None:
    sync_count = 0
    delete_count = 0
    update_count = 0

    # get all files in folder and replica
    files = os.listdir(folder)
    files_replica = os.listdir(replica)

    # compare
    for file in files_replica:
        if file in files:
            if compare_files(os.path.join(folder, file), os.path.join(replica, file)):
                write_log(f'{file} is up to date')
                sync_count += 1
            else:
                os.remove(os.path.join(replica, file))
                os.system(f'copy "{os.path.join(folder, file)}" "{replica}"')
                print(f'{file} {MSG_UPDATED}')
                write_log(f'{file} {MSG_UPDATED}')
                sync_count += 1

        if file not in files:
            os.remove(os.path.join(replica, file))
            print(f'{file} {MSG_DELETED}')
            write_log(f'{file} {MSG_DELETED}')
            delete_count += 1

    for file in files:
        if file not in files_replica:
            os.system(f'copy "{os.path.join(folder, file)}" "{replica}"')
            print(f'{file} {MSG_COPIED}')
            write_log(f'{file} {MSG_COPIED}')
            update_count += 1

    print(f'sync: {sync_count}; update: {update_count}; delete: {delete_count}')
    write_log(f'sync: {sync_count}; update: {update_count}; delete: {delete_count}')


def check_and_register_folders() -> tuple[str,str]:
    folder, replica = get_config()

    if folder is None or replica is None:
        # register folders
        folder = input(MSG_REG_SOURCE_FOLDER)
        replica = input(MSG_REG_REPLICA_FOLDER)
        # create config file
        with open(CONFIG_FILE, 'w') as f:
            f.write('folder:' + folder)
            f.write('\n')
            f.write('replica:' + replica)
        print(MSG_CONFIG_FILE)
        write_log(MSG_CONFIG_FILE)

    return folder, replica


def check_folder_existance(folder: str, replica: str) -> bool:
    # check if the folder exists
    if os.path.isdir(folder):
        print(MSG_FOLDER_FOUND)
        write_log(MSG_FOLDER_FOUND)
    else:
        print(MSG_FOLDER_NF)
        write_log(MSG_FOLDER_NF)
        return False

    # check if the replica folder still exists
    if os.path.isdir(replica):
        print(MSG_REPLICA_FOUND)
        write_log(MSG_REPLICA_FOUND)
    else:
        print(MSG_REPLICA_NF)
        write_log(MSG_REPLICA_NF)
        return False

    return True


def get_sync_time() -> float:
    while True:
        try:
            time_sync = float(input(MSG_INSERT_TIME))
            return time_sync
        except ValueError:
            print(MSG_INSERT_TIME_ERROR)


if __name__ == '__main__':

    log_file_path = input(MSG_INSERT_LOG)
    LOG_FILE = log_file_path

    write_log('Start')

    folder, replica = check_and_register_folders()
    time_sync = get_sync_time()

    while True:
        if not check_folder_existance(folder, replica):
            break

        sync_files(folder, replica)
        time.sleep(time_sync)
