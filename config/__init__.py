# MySQL connection
# DB_URI = 'mysql+mysqldb://{}:{}@{}/{}.format(USERNAME，PASSWORD，HOSTNAME，PORT，DATABASE)'
from .global_vars import *
from .config_utils import create_dirs_if_not_exist

create_dirs_if_not_exist(upload_base_dir, writ_report_base_dir, task_report_base_dir, transfer_config_dir)