from pathlib import Path


def get_project_root() -> Path:
    cloud_path = Path("/mount/src/hdb-kaki")

    if cloud_path.exists():
        return cloud_path
    return Path(__file__).parent.parent
