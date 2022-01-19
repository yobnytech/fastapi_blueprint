import os
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

GENERIC_SCHEMA = """
from typing import Any, Optional
from uuid import UUID
from app.utils.helper import to_camel
import asyncpg.pgproto.pgproto
import pydantic.json
from pydantic import BaseModel

pydantic.json.ENCODERS_BY_TYPE[asyncpg.pgproto.pgproto.UUID] = str


class GenericErrorResponseSchema(BaseModel):
    type: Optional[str]
    code: int
    message: str
    details: Any

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SuccessResponseSchema(BaseModel):
    type: str
    code: int
    details: Any
    message: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
"""
TEST_MODELS = """
from typing import Awaitable
from uuid import UUID
from app.core.dbsetup import Model, db
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy_utils.types.choice import ChoiceType
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM as pgEnum

class Test(Model):
    
    __tablename__ = "test"

"""

TEST_CONTROLLER = """
from fastapi.openapi.models import APIKey
from fastapi.param_functions import Depends
from fastapi import APIRouter
from app.db.models import Test

router = APIRouter()

"""

DOT_ENV = """
export settings=dev
export DB_NAME=testdb
export DB_USER=test_user
export DB_PASSWORD=test_pass
export DB_HOST=127.0.0.1
export DB_PORT=5432
"""

MAIN_FILE = """

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint)
from app.core.extensions import db
from app.core.factories import settings
from app.api.exceptions.generic_exception import CustomHTTPException
from app.api.controller.test_controller import router as test_router

app = FastAPI()
db.init_app(app)
app.include_router(test_router)


class CustomSuccessHeader(BaseHTTPMiddleware):
    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if response.headers["Content-Type"] == "application/json":
            response.headers["Content-Type"] = "application/vnd+yobny.____________.success+json"
        return response


app.add_middleware(CustomSuccessHeader)


@app.exception_handler(CustomHTTPException)
async def http_exception_handler(request, exc):
    from app.api.schema.generic_schema import GenericErrorResponseSchema
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=jsonable_encoder(GenericErrorResponseSchema(
            code=exc.status_code,
            message=exc.message,
            type=exc.type,
            details=exc.details
        )))

cors_origins = [i.strip() for i in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@ app.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="______________ Service",
        swagger_favicon_url="")  # noqa


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="____________ Service",
        version="0.0.1",
        description=("<div font-size='10px'>Sequence flow for this \
            microservice: <br /><br /> " +
                     "<li>Step 1: __________________________________. \
                        </li><br /> "),
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"] = {
        "url": ""  # noqa
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

"""
GENERIC_EXCEPTION = """
from typing import Any, Dict, Optional
from starlette.exceptions import HTTPException as StarletteHTTPException

class NotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class BadRequestException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class NotAcceptableException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class InvalidRequestError(Exception):

    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class CustomHTTPException(StarletteHTTPException):

    def __init__(
        self,
        status_code: int,
        message: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        type: str = None,
        details: Any = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=details)
        self.headers = headers
        self.type = type
        self.message = message
        self.details = details

"""
HELPER = """
from typing import Any, Optional, Tuple
from humps import camelize
from functools import wraps
from app.api.exceptions.generic_exception import CustomHTTPException
from app.utils.types import *
from app.utils.headers import *
from app.api.exceptions.generic_exception import BadRequestException, NotFoundException


def to_camel(string):
    return camelize(string)


def exception_handler(f):
    @wraps(f)
    async def decorator(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except NotFoundException as e:
            raise CustomHTTPException(
                status_code=404,
                message="Not Found",
                details=str(e.msg),
                headers=NOT_FOUND_HEADER,
                type=NOT_FOUND_TYPE)
        except BadRequestException as e:
            raise CustomHTTPException(
                status_code=400,
                message="Bad Request",
                details=str(e.msg),
                headers=BAD_REQUEST_HEADER,
                type=BAD_REQUEST_TYPE)
        except Exception as e:
            # e can be empty sometimes
            if str(e) in ["", None, " ", False]:
                e = "Internal Server Error"
            raise CustomHTTPException(
                status_code=500,
                message="Internal Server Error",  # "INTERNAL SERVER ERROR in production"
                details=str(e),
                headers=INTERNAL_SERVER_ERROR_HEADER,
                type=INTERNAL_SERVER_ERROR_TYPE
            )
    return decorator

"""
SINGLETONE_TYPE = """
class Singleton(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

"""
SETTINGS = """
import os
from typing import Any, List
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

project_name = "_______________"


class BaseConfig:
    config = Config()

    INCLUDE_SCHEMA = config("INCLUDE_SCHEMA", cast=bool, default=True)
    SECRET_KEY = config("SECRET_KEY", default=os.urandom(32))
    SQLALCHEMY_ECHO = config("SQLALCHEMY_ECHO", cast=bool, default=False)
    SQLALCHEMY_TRACK_MODIFICATIONS = config(
        "SQLALCHEMY_TRACK_MODIFICATIONS", cast=bool, default=False)
    LOGGER_NAME = "%s_log" % project_name
    LOG_FILENAME = "/var/tmp/app.%s.log" % project_name
    CORS_ORIGINS = config("CORS_HOSTS", default="*")
    DEBUG = config("DEBUG", cast=bool, default=True)
    TESTING = config("TESTING", cast=bool, default=False)

    # Authentication
    AUTH_IDENTITY_VERIFY_URL = config(
        "AUTH_IDENTITY_VERIFY_URL", cast=str, default="")
    AUTH_IDENTITY_CLIENT_ID = config(
        "AUTH_IDENTITY_CLIENT_ID", cast=str, default="")
    AUTH_COOKIE_NAME = config(
        "AUTH_COOKIE_NAME", cast=str, default="OAuth.AccessToken.EP")
    AUTH_EXEMPTED_AUTH_ROUTES = config(
        "AUTH_EXEMPTED_AUTH_ROUTES", cast=CommaSeparatedStrings,
        default=(
            "/docs, /openapi.json,"
            "/static/css/styles.css,"
        ))

"""
DEV_SETTINGS = """
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret
from app.core.settings.settings import BaseConfig


class DevSettings(BaseConfig):

    config = Config()

    DEBUG = config("DEBUG", cast=bool, default=True)
    DB_USER = config("DB_USER", cast=str)
    DB_PASSWORD = config("DB_PASSWORD", cast=Secret)
    DB_HOST = config("DB_HOST", cast=str)
    DB_PORT = config("DB_PORT", cast=str)
    DB_NAME = config("DB_NAME", cast=str)
    INCLUDE_SCHEMA = config("INCLUDE_SCHEMA", cast=bool, default=False)
    AUTHORISED_CLIENT_KEYS = config("AUTHORISED_CLIENT_KEYS", cast=CommaSeparatedStrings, default="")  # noqa
    DATABASE_URL = config("DATABASE_URL", default=f"asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",)  # noqa

    FIREBASE_API_KEY = config("FIREBASE_API_KEY", cast=str, default="")  # noqa
    FIREBASE_AUTH_DOMAIN = config("FIREBASE_AUTH_DOMAIN", cast=str, default="")  # noqa
    FIREBASE_DB_URL = config("FIREBASE_DB_URL", cast=str, default="")  # noqa
    FIREBASE_STORAGE_BUCKET = config("FIREBASE_STORAGE_BUCKET", cast=str, default="")  # noqa

    FIREBASE_TYPE = config("FIREBASE_TYPE", cast=str, default="")  # noqa
    FIREBASE_PROJECT_ID = config("FIREBASE_PROJECT_ID", cast=str, default="")  # noqa
    FIREBASE_PRIVATE_KEY_ID = config("FIREBASE_PRIVATE_KEY_ID", cast=str, default="")  # noqa
    FIREBASE_PRIVATE_KEY = config("FIREBASE_PRIVATE_KEY", cast=str, default="")  # noqa
    FIREBASE_CLIENT_EMAIL = config("FIREBASE_CLIENT_EMAIL", cast=str, default="")  # noqa
    FIREBASE_CLIENT_ID = config("FIREBASE_CLIENT_ID", cast=str, default="")  # noqa
    FIREBASE_AUTH_URI = config("FIREBASE_AUTH_URI", cast=str, default="")  # noqa
    FIREBASE_TOKEN_URI = config("FIREBASE_TOKEN_URI", cast=str, default="")  # noqa
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL = config("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", cast=str, default="")  # noqa
    FIREBASE_CLIENT_X509_CERT_URL = config("FIREBASE_CLIENT_X509_CERT_URL", cast=str, default="")  # noqa

"""

FACTORIES = """
import os


envsettings = os.getenv("settings")

if envsettings in ["dev", "default"]:
    from app.core.settings.devsettings import DevSettings
    settings = DevSettings()
else:
    raise SystemExit(
        "settings for app not exported. example:  ```export settings=dev```")

"""


DB_SETUP = """
from uuid import uuid4
# add created,updated columns to model
from sqlalchemy_utils import UUIDType, Timestamp
from app.core.extensions import db


class SurrogatePK(object):
    __table_args__ = {"extend_existing": True}

    id = db.Column(UUIDType(binary=False), primary_key=True)


class SurrogateAudit(object):

    __table_args__ = {"extend_existing": True}

    _created = db.Column(db.Time(), nullable=True)
    _modified = db.Column(db.Time(), nullable=True)
    _created_by = db.Column(db.String(), nullable=True)
    _modified_by = db.Column(db.String(), nullable=True)


class Model(Timestamp, SurrogatePK, SurrogateAudit, db.Model):
    __abstract__ = True

    @classmethod
    async def create(cls, **kwargs):
        if issubclass(cls, SurrogatePK):
            unique_id = uuid4()
            if not kwargs.get("id"):
                kwargs["id"] = unique_id
        return await cls(**kwargs)._create()

"""
UTIL_HEADERS = """
from typing_extensions import Final

AUTH_ERROR_MEDIA_HEADER: Final = {"Content-Type": "application/vnd+test.identity.auth-failurer+json"}  # noqa
NOT_FOUND_HEADER: Final = {"Content-Type": "application/vnd+test.service.entity.not-found+json"}  # noqa
NOT_ACCEPTABLE_HEADER: Final = {"Content-Type": "application/vnd+test.service.entity.not-acceptable+json"}  # noqa
INTERNAL_SERVER_ERROR_HEADER: Final = {"Content-Type": "application/vnd+test.service.internal-server-error+json"}  # noqa
BAD_REQUEST_HEADER: Final = {"Content-Type": "application/vnd+test.service.bad-request+json"}  # noqa
"""
UTIL_TYPES = """
from typing_extensions import Final

CONFIG_CREATED_TYPE: Final = "vnd.test.service.config-created"
ENTITY_CREATED_TYPE: Final = "vnd.test.service.config-created"
CONFIG_UPDATED_TYPE: Final = "vnd.test.service.config-updated"
NOT_FOUND_TYPE: Final = "vnd.test.service.entity.not-found"
NOT_ACCEPTABLE_TYPE: Final = "vnd.test.service.entity.not-acceptable"
INTERNAL_SERVER_ERROR_TYPE: Final = "vnd.test.service.internal-server-error"
BAD_REQUEST_TYPE: Final = "vnd.test.service.bad_request"
PARTIAL_CONTENT_TYPE: Final = "vnd.test.service.partial-content"
"""

EXTENTIONS = """
from app.core.factories import settings
from ssl import create_default_context
from gino_starlette import Gino


if not settings.DEBUG:
    ssl_object = create_default_context(cafile=settings.SSL_CERT_FILE)
    db: Gino = Gino(
        dsn=settings.DATABASE_URL,
        echo=False,
        ssl=ssl_object,
        pool_min_size=3,
        pool_max_size=20,
        retry_limit=1,
        retry_interval=1,
    )
else:
    db: Gino = Gino(
        dsn=settings.DATABASE_URL,
        echo=False)

"""

DOCKER_COMPOSE = """
version: '3.3'
services:
  db:
      image: postgres:11
      container_name: testdb-pg
      ports:
        - "5432:5432"
      environment:
        POSTGRES_DB: testdb
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_pass
      volumes:
        - pgdata_schedule:/var/lib/postgresql/data
volumes:
    pgdata_schedule:
        driver: local
"""

ALEMBIC_ENV ="""
from logging.config import fileConfig
import pathlib
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import sqlalchemy_utils
from alembic import context
import sys
import os
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
section = config.config_ini_section
config.set_section_option(section, "DB_USER", os.environ.get("DB_USER"))
config.set_section_option(section, "DB_PASSWORD",
                          os.environ.get("DB_PASSWORD"))
config.set_section_option(section, "DB_HOST", os.environ.get("DB_HOST"))
config.set_section_option(section, "DB_PORT", os.environ.get("DB_PORT"))
config.set_section_option(section, "DB_NAME", os.environ.get("DB_NAME"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.main import db as target_metadata      # noqa

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def render_item(type_, obj, autogen_context):
    
    if type_ == "type" and isinstance(obj,
                                      sqlalchemy_utils.types.uuid.UUIDType):
        # Add import for this type
        autogen_context.imports.add("import sqlalchemy_utils")
        autogen_context.imports.add("import uuid")
        autogen_context.imports.add("import gino")

        return "sqlalchemy_utils.types.uuid.UUIDType(), default=uuid.uuid4"

    # Default rendering for other objects
    return False


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            render_item=render_item
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

ALEMBIC = """
[alembic]
script_location = app/db/migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://test_user:test_pass@127.0.0.1:5432/testdb
[post_write_hooks]
[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers =
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""


def try_except_init(path):
    "Creates __init__.py file for every directory"
    p = os.path.join(path, "__init__.py")
    try:
        open(p, 'w').close()
    except Exception:
        pass


def task_create_directories():
    """
    Create the base directory structure for service.
    """
    try:
        os.mkdir("app")
        os.mkdir("docs")
        open('__init__.py', 'w').close()
        root_path = 'app'
        for items in ['api', "core", "db", "test", "utils", "it", "static"]:
            path = os.path.join(root_path, items)
            os.mkdir(path)
            try_except_init(path)
            if path == "app/api":
                for dir in ['controller', 'service', 'schema', 'exceptions', 'security', 'tasks']:
                    pa = os.path.join(path, dir)
                    os.mkdir(pa)
                    try_except_init(pa)
                    if pa == "app/api/exceptions":
                        for item in ["generic_exception.py"]:
                            p = os.path.join(pa, item)
                            if item == "generic_exception.py":
                                with open(p, "a") as output:
                                    output.write(GENERIC_EXCEPTION)
                    if pa == "app/api/schema":
                        for item in ["generic_schema.py"]:
                            p = os.path.join(pa, item)
                            if item == "generic_schema.py":
                                with open(p, "a") as output:
                                    output.write(GENERIC_SCHEMA)
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
                    if dir == "settings":
                        for item in ["devsettings.py", "settings.py"]:
                            p = os.path.join(pa, item)
                            if item == "devsettings.py":
                                with open(p, "a") as output:
                                    output.write(DEV_SETTINGS)
                            if item == "settings.py":
                                with open(p, "a") as output:
                                    output.write(SETTINGS)
                


                with open(os.path.join(path, "factories.py"), "a") as output:
                    output.write(FACTORIES)
                with open(os.path.join(path, "dbsetup.py"), "a") as output:
                    output.write(DB_SETUP)
                with open(os.path.join(path, "extensions.py"), "a") as output:
                    output.write(EXTENTIONS)

            if path == "app/utils":
                try_except_init(path)
                for item in ["helper.py", "singleton_type.py", "types.py", "headers.py"]:
                    p = os.path.join(path, item)
                    if item == "helper.py":
                        with open(p, "a") as output:
                            output.write(HELPER)
                    if item == "singleton_type.py":
                        with open(p, "a") as output:
                            output.write(SINGLETONE_TYPE)
                    if item == "types.py":
                        with open(p, "a") as output:
                            output.write(UTIL_TYPES)
                    if item == "headers.py":
                        with open(p, "a") as output:
                            output.write(UTIL_HEADERS)
    except OSError as e:
        print (e)
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
    except OSError as e:
        print(e)
        pass


def task_create_venv():
    """
    Create virtual environment and activate for future actions
    """
    return{
        'actions': ["virtualenv -p python3.7 venv", ". venv/bin/activate"],

    }


def task_install_dependencies():
    packages = (
        "alembic==1.7.5 anyio==3.4.0 asgiref==3.4.1 asyncpg==0.25.0"
        " autopep8==1.6.0 CacheControl==0.12.10 cachetools==4.2.4"
        " certifi==2021.10.8 charset-normalizer==2.0.10 click==8.0.3"
        " cron-validator==1.0.3 fastapi==0.70.1 firebase-admin==5.2.0"
        " gino==1.0.1 gino-starlette==0.1.3 google-api-core==2.3.2" 
        " google-api-python-client==2.34.0 google-auth==2.3.3"
        " google-auth-httplib2==0.1.0 google-cloud-core==2.2.1"
        " google-cloud-firestore==2.3.4 google-cloud-storage==1.44.0"
        " google-crc32c==1.3.0 google-resumable-media==2.1.0"
        " googleapis-common-protos==1.54.0 greenlet==1.1.2 grpcio==1.43.0"
        " grpcio-status==1.43.0 h11==0.12.0 httplib2==0.20.2 idna==3.3"
        " importlib-metadata==1.7.0 importlib-resources==5.4.0 Mako==1.1.6"
        " MarkupSafe==2.0.1 msgpack==1.0.3 packaging==21.3 proto-plus==1.19.8"
        " protobuf==3.19.3 psycopg2==2.9.3 pyasn1==0.4.8 pyasn1-modules==0.2.8"
        " pycodestyle==2.8.0 pydantic==1.9.0 pyhumps==3.5.0 pyparsing==3.0.6"
        " python-dateutil==2.8.2 pytz==2021.3 requests==2.27.1 rsa==4.8"
        " six==1.16.0 sniffio==1.2.0 SQLAlchemy==1.3.24 SQLAlchemy-Utils==0.38.2"
        " starlette==0.16.0 toml==0.10.2 typing-extensions==4.0.1"
        " uritemplate==4.1.1 urllib3==1.26.8 uvicorn==0.16.0 zipp==3.7.0"
    )
    return {
        'actions': [f'venv/bin/pip install {packages}'],
        'verbosity': 2
    }


def task_freeze():
    return {
        'actions': ['venv/bin/pip freeze -> requirements.txt'],
    }


def task_alembic():
    return {
        'actions': ['venv/bin/alembic init app/db/migrations'],
    }

def task_create_env():
    def create_env():
        with open(".env", "w") as output:
            output.write(DOT_ENV)
    return {
        'actions': [create_env],
    }

def task_replace_alembic():
    def rm_alembic():
        os.remove("alembic.ini")
        with open("alembic.ini", "a") as output:
            output.write(ALEMBIC)
    return {
        'actions': [rm_alembic],
    }

def task_replace_alembic_env():
    def rm_alembic_env():
        os.remove("app/db/migrations/env.py")
        with open("app/db/migrations/env.py", "a") as output:
            output.write(ALEMBIC_ENV)
    return {
        'actions': [rm_alembic_env],
    }

def task_dockercompose():
    def setup_dockercompose():
        with open("docker-compose.yaml", "a") as output:
            output.write(DOCKER_COMPOSE)
    return {
        'actions': [setup_dockercompose],
    }

def task_setup_test_controller():
    def setup_test_controller():
        with open("app/api/controller/test_controller.py", "w") as output:
            output.write(TEST_CONTROLLER)
    return {
        'actions': [setup_test_controller],
    }

def task_setup_model():
    def setup_model():
        with open("app/db/models.py", "w") as output:
            output.write(TEST_MODELS)
    return {
        'actions': [setup_model],
    }

def task_set_env():
    return {
        'actions': ['source .env'],
    }

def task_docker_db():
    return {
        'actions': ['docker compose up -d'],
    }

def task_execute_first_migration():
    return {
        'actions': ['venv/bin/alembic revision --autogenerate -m "First Migration"'],
    }

def task_sync_first_migration():
    return {
        'actions': ['venv/bin/alembic upgrade heads'],
    }

def task_run_server():
    return {
        'actions': ['venv/bin/uvicorn app.main:app --reload --port 5000'],
    }