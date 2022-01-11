GITIGNORE = """
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/
*.mo
*.pot
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
instance/
.webassets-cache
.scrapy
docs/_build/
.pybuilder/
target/
.ipynb_checkpoints
profile_default/
ipython_config.py
__pypackages__/
celerybeat-schedule
celerybeat.pid
*.sage.py
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.spyderproject
.spyproject
.ropeproject
/site
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/
.pytype/
cython_debug/
"""

MAIN_FILE = """
import uvicorn
from fastapi import FastAPI
app = FastAPI()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
"""





import os

def try_except_init(path):
    "Creates __init__.py file for every directory"
    p = os.path.join(path, "__init__.py")
    try:
        os.mknod(p)
    except Exception:
        pass


def task_create_directories():
    """
    Create the base directory structure for service.
    """
    try:
        os.mkdir("app")
        os.mknod("__init__.py")
        root_path = 'app'
        for items in ['api', "core", "db", "test", "utils","it","static"]:
            path = os.path.join(root_path, items)
            os.mkdir(path)
            try_except_init(path)
            if path == "app/api":
                for dir in ['controller', 'service', 'schema', 'exceptions', 'security','tasks']:
                    pa = os.path.join(path, dir)
                    os.mkdir(pa)
                    try_except_init(pa)
            if path == "app/test":
                for dir in ['api', 'resources']:
                    pa = os.path.join(path, dir)
                    os.mkdir(pa)
                    try_except_init(pa)
            if path == "app/core":
                for dir in ['localization', 'settings']:
                    pa = os.path.join(path, dir)
                    os.mkdir(pa)
                    try_except_init(pa)
    except OSError:
        pass
    try:
        for item in [".gitignore", "app/main.py"]:
            if item == ".gitignore":
                with open(item, "a") as output:
                        output.write(GITIGNORE)
            else:
                with open(item, "a") as output:
                        output.write(MAIN_FILE)

        return {
            'actions': ["git init", ],
            }
    except OSError:
        pass


def task_create_venv():
    """
    Create virtual environment and activate for future actions
    """
    return{
        'actions':["virtualenv -p python3.7 venv", ". venv/bin/activate"],

    }

def task_install_dependencies():
    return {
        'actions': ['venv/bin/pip install uvicorn fastapi alembic'],
    }

def task_freeze():
    return {
        'actions': ['venv/bin/pip freeze -> requirements.txt'],
    }

def task_alembic():
    return {
        'actions': ['venv/bin/alembic init app/db/migrations'],
    }

def task_run_server():
    return {
        'actions': ['venv/bin/uvicorn app.main:app --reload --port 5000'],
    }