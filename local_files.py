"""Small local-file primitives; callers still own project containment checks."""
import os
import tempfile
from pathlib import Path


def temporary_path(destination: Path) -> Path:
    descriptor, name = tempfile.mkstemp(prefix='.' + destination.name + '-', suffix='.tmp', dir=destination.parent)
    os.close(descriptor)
    return Path(name)


def atomic_write(destination: Path, data: bytes) -> None:
    temporary = temporary_path(destination)
    try:
        with temporary.open('wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
