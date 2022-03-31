import os

APP_DOT_PY = (
    """
from api.routers import register_routers
from config.environment import Settings
from core.utils.generic_exception import CustomHTTPException
from core.utils.generic_schema import GenericErrorResponseSchema
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from infra.database.gino import db
from starlette.middleware.base import (BaseHTTPMiddleware,
                                    RequestResponseEndpoint)
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from toolz import pipe

\ncors_origins = ""

class CustomSuccessHeader(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        if response.headers["Content-Type"] == "application/json":
            response.headers["Content-Type"] = "application/vnd+yobny.store.success+json"  # noqa
        return response


def create_instance(settings: Settings) -> FastAPI:
    cors_origins = [i.strip() for i in settings.CORS_ORIGINS.split(",")]
    return FastAPI(
        debug=settings.WEB_APP_DEBUG,
        title=settings.WEB_APP_TITLE,
        description=settings.WEB_APP_DESCRIPTION,
        version=settings.WEB_APP_VERSION,
    )

def init_databases(app: FastAPI) -> FastAPI:
    db.init_app(app=app)
    return app

def register_middlewares(app: FastAPI) -> FastAPI:
    app.add_middleware(CustomSuccessHeader)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

def init_app(settings: Settings) -> FastAPI:
    app: FastAPI = pipe(
        settings,
        create_instance,
        init_databases,
        register_middlewares,
        register_routers,
    )
    return app
""")

ENVIRONMENT_DOT_PY = (
    """
from typing import Callable

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    TEST_ENV: str = "Default"


def _configure_initial_settings() -> Callable[[], Settings]:
    load_dotenv()
    settings = Settings()

    def fn() -> Settings:
        return settings

    return fn


get_settings = _configure_initial_settings()
    """
)

GENERIC_EXCEPTION_DOT_PY = (
    """

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
)


GENERIC_SCHEMA_DOT_PY = (
    """
from typing import Any, Optional
from uuid import UUID
from .helper import to_camel
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
)

HEADERS_DOT_PY = (
    """
from typing_extensions import Final

AUTH_ERROR_MEDIA_HEADER: Final = {"Content-Type": "application/vnd+______.identity.auth-failurer+json"}  # noqa
NOT_FOUND_HEADER: Final = {"Content-Type": "application/vnd+______.service.entity.not-found+json"}  # noqa
NOT_ACCEPTABLE_HEADER: Final = {"Content-Type": "application/vnd+______.service.entity.not-acceptable+json"}  # noqa
INTERNAL_SERVER_ERROR_HEADER: Final = {"Content-Type": "application/vnd+______.service.internal-server-error+json"}  # noqa
BAD_REQUEST_HEADER: Final = {"Content-Type": "application/vnd+______.service.bad-request+json"}  # noqa
SUCCESS_RESPONSE_TYPE: Final = "application/vnd+yobny.______.success+json"
    """
)


HELPERS_DOT_PY = (
    """
from functools import wraps
from typing import Any, Callable, Dict, List

from humps import camelize

from .generic_exception import *
from .headers import *
from .types import *


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
                type=NOT_FOUND_TYPE,
            )
        except BadRequestException as e:
            raise CustomHTTPException(
                status_code=400,
                message="Bad Request",
                details=str(e.msg),
                headers=BAD_REQUEST_HEADER,
                type=BAD_REQUEST_TYPE,
            )
        except Exception as e:
            # e can be empty sometimes
            if str(e) in ["", None, " ", False]:
                e = "Internal Server Error"
            raise CustomHTTPException(
                status_code=500,
                message="Internal Server Error",  # "INTERNAL SERVER ERROR in production"
                details=str(e),
                headers=INTERNAL_SERVER_ERROR_HEADER,
                type=INTERNAL_SERVER_ERROR_TYPE,
            )

    return decorator

    """
)


TYPES_DOT_PY = (
    """
from typing_extensions import Final

CONFIG_CREATED_TYPE: Final = "vnd._____.service.config-created"
ENTITY_CREATED_TYPE: Final = "vnd._____.service.config-created"
CONFIG_UPDATED_TYPE: Final = "vnd._____.service.config-updated"
NOT_FOUND_TYPE: Final = "vnd._____.service.entity.not-found"
NOT_ACCEPTABLE_TYPE: Final = "vnd._____.service.entity.not-acceptable"
INTERNAL_SERVER_ERROR_TYPE: Final = "vnd._____.service.internal-server-error"
BAD_REQUEST_TYPE: Final = "vnd._____.service.bad_request"
PARTIAL_CONTENT_TYPE: Final = "vnd._____.service.partial-content"
    """
)


GINO_DOT_PY = (
    """
from contextlib import asynccontextmanager
from ssl import create_default_context

from config.environment import get_settings
from gino_starlette import Gino

settings = get_settings()

if settings.ENV == "prod":
    ssl_object = create_default_context(cafile=settings.SSL_CERT_FILE)
    db: Gino = Gino(
        dsn=settings.DATABASE_PG_URL,
        echo=False,
        ssl=ssl_object,
        pool_min_size=3,
        pool_max_size=20,
        retry_limit=1,
        retry_interval=1,
    )
else:
    db: Gino = Gino(
        dsn=settings.DATABASE_PG_URL,
        echo=True
    )
    """
)


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


def task_git_init():
    try:
        for item in [".gitignore"]:
            if item == ".gitignore":
                with open(item, "a") as output:
                    output.write(
                        """__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/
                            \ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/
                            \nparts/\nsdist/\nvar/\nwheels/\nshare/python-wheels/\n*.egg-info/
                            \n.installed.cfg\n*.egg\nMANIFEST\n*.manifest\n*.spec\npip-log.txt
                            \npip-delete-this-directory.txt\nhtmlcov/\n.tox/\n.nox/\n.coverage
                            \n.coverage.*\n.cache\nnosetests.xml\ncoverage.xml\n*.cover\n*.py,cover
                            \n.hypothesis/\n.pytest_cache/\ncover/\n*.mo\n*.pot\n*.log\nlocal_settings.py
                            \ndb.sqlite3\ndb.sqlite3-journal\ninstance/\n.webassets-cache\n.scrapy
                            \ndocs/_build/\n.pybuilder/\ntarget/\n.ipynb_checkpoints\nprofile_default/
                            \nipython_config.py\n__pypackages__/\ncelerybeat-schedule\ncelerybeat.pid
                            \n*.sage.py\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n.spyderproject
                            \n.spyproject\n.ropeproject\n/site\n.mypy_cache/\n.dmypy.json\ndmypy.json\n.pyre/
                            \n.pytype/\ncython_debug/
                            """
                    )
        return {
            'actions': ["git init", ],
        }
    except OSError as e:
        print(e)
        pass


def easy_dir(path, dir):
    dir = os.path.join(path, dir)
    p = os.path.join(dir, "__init__.py")
    os.mkdir(dir)
    try:
        open(p, 'w').close()
    except Exception:
        pass


def task_create_directories():
    """
    Create the base directory structure for service.
    """

    parent_dirs = ["tests", "project_name"]

    try:
        for dir in parent_dirs:
            os.mkdir(dir)
            p = os.path.join(dir, "__init__.py")
            open(p, 'w').close()

        open('__init__.py', 'w').close()
        root_path = 'project_name'

        for items in ['api', "core", "config", "infra"]:
            easy_dir(root_path, items)
            if items == 'api':
                easy_dir(f"{root_path}/api", "routers")
                with open(f"{root_path}/api/app.py", "a") as output:
                    output.write(APP_DOT_PY)

            if items == 'config':
                with open(f"{root_path}/config/environment.py", "a") as output:
                    output.write(ENVIRONMENT_DOT_PY)

            if items == 'core':

                easy_dir(f"{root_path}/core", "settings")
                easy_dir(f"{root_path}/core", "utils")

                with open(f"{root_path}/core/utils/generic_exception.py", "a") as output:
                    output.write(GENERIC_EXCEPTION_DOT_PY)
                with open(f"{root_path}/core/utils/generic_schema.py", "a") as output:
                    output.write(GENERIC_SCHEMA_DOT_PY)
                with open(f"{root_path}/core/utils/headers.py", "a") as output:
                    output.write(HEADERS_DOT_PY)
                with open(f"{root_path}/core/utils/helper.py", "a") as output:
                    output.write(HELPERS_DOT_PY)
                with open(f"{root_path}/core/utils/types.py", "a") as output:
                    output.write(TYPES_DOT_PY)

            if items == 'infra':
                easy_dir(f"{root_path}/infra", "database")
                next_dirs = ["alembic", "models", "repositories"]
                for di in next_dirs:
                    easy_dir(f"{root_path}/infra/database", di)
                with open(f"{root_path}/infra/database/gino.py", "a") as output:
                    output.write(GINO_DOT_PY)

    except:
        pass


def task_create_venv():
    """
    Create virtual environment and activate for future actions
    """
    return{
        'actions': ["virtualenv -p python3.7 venv", ". venv/bin/activate"],

    }


def task_create_env():
    def create_env():
        with open(".env", "w") as output:
            output.write(
                """
settings=dev
DB_NAME=testdb
DB_USER=test_user
DB_PASSWORD=test_pass
DB_HOST=127.0.0.1
DB_PORT=5432
                """
            )
    return {
        'actions': [create_env],
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


def task_dockercompose():
    def setup_dockercompose():
        with open("docker-compose.yaml", "a") as output:
            output.write(DOCKER_COMPOSE)
    return {
        'actions': [setup_dockercompose],
    }


def task_docker_db():
    return {
        'actions': ['docker-compose up -d'],
    }
