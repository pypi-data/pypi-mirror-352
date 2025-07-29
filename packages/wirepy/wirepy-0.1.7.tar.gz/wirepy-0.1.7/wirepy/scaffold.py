# wirepy/scaffold.py

import os
import shutil
from pathlib import Path
import importlib.resources as pkg_resources

def create_project(name):
    import wirepy  # required to access package resources

    dst = Path.cwd() / name
    dst.mkdir(parents=True, exist_ok=True)

    # Recursively copy the contents of the 'templates' folder inside wirepy package
    template_root = pkg_resources.files(wirepy).joinpath("templates")

    def copy_all(src, dest):
        for item in src.iterdir():
            dest_path = dest / item.name
            if item.is_dir():
                dest_path.mkdir(exist_ok=True)
                copy_all(item, dest_path)
            else:
                with item.open("rb") as fsrc:
                    with dest_path.open("wb") as fdst:
                        shutil.copyfileobj(fsrc, fdst)

    copy_all(template_root, dst)
    print(f"✔ Project '{name}' created at {dst}")

def make_file(file_type, name):
    base_path = Path.cwd() / "app"
    type_folder = {
        "controller": "controllers",
        "model": "models",
        "service": "services",
        "route": "routes",
        "schema": "schemas"
    }

    template = {
        "controller": f"class {name.capitalize()}Controller:\n    pass\n",
        "model": f"class {name.capitalize()}(Base):\n    __tablename__ = '{name.lower()}s'\n    id = Column(Integer, primary_key=True)\n",
        "service": f"class {name.capitalize()}Service:\n    pass\n",
        "route": f"from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get('/{name.lower()}s')\ndef get_all():\n    return []\n",
        "schema": f"from pydantic import BaseModel\n\nclass {name.capitalize()}Schema(BaseModel):\n    id: int"
    }

    folder = base_path / type_folder[file_type]
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / f"{name.lower()}_{file_type}.py"
    if file_path.exists():
        print(f"⚠ {file_path} already exists")
    else:
        file_path.write_text(template[file_type])
        print(f"✔ Created {file_type}: {file_path}")
