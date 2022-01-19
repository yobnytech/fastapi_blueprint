## fastapi_blueprint
fastapi_blueperint helps you to start your next project with just one command. No headache of initial setup anymore. Alembic setup and initial migration, gino adapter for SQLAlchemy, all covered.
- Virtual environment
- Project setup
- Directories
- Documentation (OpenAPI)
- Migration (Alembic)
- ORM (SQLAlchemy)
- async Adapter (Gino)
- PostgreSQL database (asyncpg)
- Docker image

Start writing your models and controllers. You're good to go.
## How to use
1. Open repo and copy dodo.py 
2. Paste dodo.py file to the target directory
3. Add .env to the directory
   ```
   export settings="dev"
   export DEBUG="True"
   export INCLUDE_SCHEMA="True"
   export DB_NAME="db_name"
   export DB_USER="db_user"
   export DB_PASSWORD="db_password"
   export DB_HOST="127.0.0.1"
   export DB_PORT="5432"
   ```

4. Install doit globally
    ```
    pip install doit
    ```
5. Run,
    ```
    doit
    ```
