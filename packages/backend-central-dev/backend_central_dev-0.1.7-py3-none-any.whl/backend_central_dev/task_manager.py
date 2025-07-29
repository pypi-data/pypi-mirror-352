import random
import string
import os

from .utils.mongodb_helper import Mon


def __get_random_string__(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join(random.choice(letters) for i in range(length))


def __get_random_string_no_low__(length):
    letters = string.ascii_uppercase + string.digits
    return "".join(random.choice(letters) for i in range(length))


class TaskComponent:

    def __init__(
        self, component_name: str, component_path: str, context_path: str, mongo=False
    ) -> None:
        self.context_path = context_path

        self.component_name = component_name
        self.component_path = component_path
        self.component_path_parent = os.path.abspath(
            os.path.dirname(self.component_path)
        )
        print("Context path: ", self.context_path)
        print("Component path: ", self.component_path)

        # TODO: temporary solution for retreving the task result
        self.static_path = os.path.join(self.component_path_parent, "static")

        self.storage_path = os.path.join(
            self.component_path_parent, f"{self.component_name.lower()}_storage"
        )
        self.tmp_path = os.path.join(self.storage_path, "tmp")
        self.db_path = os.path.join(self.storage_path, "db")

        self.module_path = os.path.join(self.storage_path, "module")
        self.training_save_path = os.path.join(
            self.storage_path, "training_save")

        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path, exist_ok=True)

        if not os.path.exists(self.static_path):
            os.makedirs(self.static_path, exist_ok=True)

        if not os.path.exists(self.module_path):
            os.makedirs(self.module_path, exist_ok=True)

        if not os.path.exists(self.training_save_path):
            os.makedirs(self.training_save_path, exist_ok=True)

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        self.executor_db_file_path = os.path.join(
            self.db_path, f"executor_{component_name.lower()}_db.json"
        )

        os.environ["EXECUTOR_DB_FILE_PATH"] = self.executor_db_file_path
        os.environ["COMPONENT_STORAGE_PATH"] = self.storage_path
        os.environ["COMPONENT_MODULE_PATH"] = self.module_path
        os.environ["COMPONENT_TRAINING_SAVE_PATH"] = self.training_save_path

        os.environ["COMPONENT_DB_PATH"] = self.db_path
        os.environ["COMPONENT_TMP_PATH"] = self.tmp_path
        os.environ["COMPONENT_STATIC_PATH"] = self.static_path
        os.environ["CONTEXT_PATH"] = self.context_path

        if mongo:
            self.mondb = Mon()
