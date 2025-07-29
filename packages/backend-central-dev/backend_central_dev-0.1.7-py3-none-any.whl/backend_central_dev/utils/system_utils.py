

import platform
import subprocess
import psutil
import logging


def getSystemInfo():
    try:
        info = {}
        info['platform'] = platform.system()
        info['platform-release'] = platform.release()
        info['platform-version'] = platform.version()
        info['architecture'] = platform.machine()
        info['processor'] = platform.processor()
        info['ram'] = str(
            round(psutil.virtual_memory().total / (1024.0 ** 3)))+" GB"
        return info
    except Exception as e:
        logging.exception(e)


def getCurrentCommitHash():
    try:
        # Run the git command
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        # Get the output and strip any extra whitespace
        commit_hash = result.stdout.strip()
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return None
