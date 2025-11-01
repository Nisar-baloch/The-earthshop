import shutil
from datetime import datetime

def backup_database():
    src = 'db.sqlite3'
    dst = f'backup/db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
    shutil.copy(src, dst)
    print(f"Backup created: {dst}")