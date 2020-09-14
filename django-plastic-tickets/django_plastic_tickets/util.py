import shutil
from pathlib import Path
from typing import List

from django.contrib.auth.models import User

from . import models


def get_cached_dir(user: User) -> Path:
    return Path('cached_files/', user.username)


def get_cached_filenames_for_user(user: User) -> List[Path]:
    cached_dir = get_cached_dir(user)
    cached_dir.mkdir(parents=True, exist_ok=True)

    files: List[Path] = []
    for file in cached_dir.glob('*'):
        files.append(file)

    return files


def get_configured_filenames_for_user(user: User) -> List[Path]:
    return [Path(f.config.file) for f in
            models.CachedPrintConfig.objects.filter(user=user).all()]


def delete_all_cached_files_for_user(user: User):
    shutil.rmtree(get_cached_dir(user))
    models.CachedPrintConfig.objects.filter(user=user).delete()
