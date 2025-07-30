import os
import subprocess
import platform
import click
from Osdental.Shared.Logger import logger
from Osdental.Shared.Message import Message

SRC_PATH = 'src'
APP_PATH = os.path.join(SRC_PATH, 'Application')
DOMAIN_PATH = os.path.join(SRC_PATH, 'Domain')
INFRA_PATH = os.path.join(SRC_PATH, 'Infrastructure')
GRAPHQL_PATH = os.path.join(INFRA_PATH, 'Graphql')
SCHEMAS_PATH = os.path.join(GRAPHQL_PATH, 'Schemas')

@click.group()
def cli():
    """Comandos personalizados para gestionar el proyecto."""
    pass

@cli.command()
def clean():
    """Borrar todos los __pycache__."""
    if platform.system() == 'Windows':
        subprocess.run('for /d /r . %d in (__pycache__) do @if exist "%d" rd /s/q "%d"', shell=True)
    else:
        subprocess.run("find . -name '__pycache__' -type d -exec rm -rf {} +", shell=True)

    logger.info(Message.PYCACHE_CLEANUP_SUCCESS_MSG)


@cli.command(name='start-app')
@click.argument('app')
def start_app(app: str):
    """Crear un servicio con estructura hexagonal y CRUD básico."""
    app = app.capitalize()

    data = 'data: Dict[str,str]'
    token = 'token: AuthToken'
    api_type_response = 'Response!'
    
    directories = [
        os.path.join(APP_PATH, 'UseCases'),
        os.path.join(APP_PATH, 'Interfaces'),
        os.path.join(DOMAIN_PATH, 'Interfaces'),
        os.path.join(GRAPHQL_PATH, 'Resolvers'),
        os.path.join(SCHEMAS_PATH),
        os.path.join(SCHEMAS_PATH, app, 'Queries'),
        os.path.join(SCHEMAS_PATH, app, 'Mutations'),
        os.path.join(INFRA_PATH, 'Repositories', app)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Contenidos CRUD
    use_case_content = f'''class {app}UseCase:
        def get_all(self, {token}, {data}):
            pass
            
        def get_by_id(self, {token}, {data}):
            pass
            
        def create(self, {token}, {data}):
            pass

        def update(self, {token}, {data}):
            pass

        def delete(self, {token}, {data}):
            pass
    '''

    interface_content = f'''class {app}UseCaseInterface:
        def get_all(self, {token}, {data}): ...
        def get_by_id(self, {token}, {data}): ...
        def create(self, {token}, {data}): ...
        def update(self, {token}, {data}): ...
        def delete(self, {token}, {data}): ...
    '''

    repository_interface_content = f'''class {app}RepositoryInterface:
        def get_all(self, {data}): ...
        def get_by_id(self, id: str): ...
        def create(self, {data}): ...
        def update(self, id: str, {data}): ...
        def delete(self, id: str): ...
    '''

    resolver_content = f'''class {app}Resolver:
        def resolve_get_all(self, _, info, data): pass
        def resolve_get_by_id(self, _, info, data): pass
        def resolve_create(self, _, info, data): pass
        def resolve_read(self, _, info, data): pass
        def resolve_update(self, _, info, data): pass
        def resolve_delete(self, _, info, data): pass
    '''

    query_graphql = f'''type Query {{
        getAll{app}(data: String!): {api_type_response}
        get{app}ById(data: String!): {api_type_response}
    }}
    '''

    mutation_graphql = f'''type Mutation {{
        create{app}(data: String!): {api_type_response}
        update{app}(data: String!): {api_type_response}
        delete{app}(data: String!): {api_type_response}
    }}
    '''

    response_content = '''
        type Response {
            status: String
            message: String
            data: String
        }
    '''

    repository_init_content = ''
    repository_content = f'''class {app}Repository:
        def get_all(self, {data}): 
            pass
            
        def get_by_id(self, id: str): 
            pass
            
        def create(self, {data}): 
            pass
            
        def update(self, id: str, {data}): 
            pass
            
        def delete(self, id: str): 
            pass
    '''

    files = {
        os.path.join(APP_PATH, 'UseCases', f'{app}UseCase.py'): use_case_content,
        os.path.join(APP_PATH, 'Interfaces', f'{app}UseCaseInterface.py'): interface_content,
        os.path.join(DOMAIN_PATH, 'Interfaces', f'{app}RepositoryInterface.py'): repository_interface_content,
        os.path.join(GRAPHQL_PATH, 'Resolvers', '__init__.py'): f'{app.lower()}_query_resolvers = {{}}\n{app.lower()}_mutation_resolvers = {{}}\n',
        os.path.join(GRAPHQL_PATH, 'Resolvers', f'{app}Resolver.py'): resolver_content,
        os.path.join(GRAPHQL_PATH, 'Response.graphql'): response_content,
        os.path.join(SCHEMAS_PATH, app, 'Queries', 'Query.graphql'): query_graphql,
        os.path.join(SCHEMAS_PATH, app, 'Mutations', 'Mutation.graphql'): mutation_graphql,
        os.path.join(INFRA_PATH, 'Repositories', app, '__init__.py'): repository_init_content,
        os.path.join(INFRA_PATH, 'Repositories', app, f'{app}Repository.py'): repository_content
    }

    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)

    logger.info(Message.HEXAGONAL_SERVICE_CREATED_MSG)

@cli.command()
@click.argument('port')
def start(port:int):
    """Levantar el servidor FastAPI."""
    try:
        subprocess.run(['uvicorn', 'app:app', '--port', str(port), '--reload'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'{Message.SERVER_NETWORK_ACCESS_ERROR_MSG}: {e}')


@cli.command()
@click.argument('port')
def serve(port:int):
    """Levantar el servidor FastAPI accesible desde cualquier máquina."""
    try:
        # Levanta el servidor en el puerto 8000 accesible desde cualquier IP
        subprocess.run(['uvicorn', 'app:app', '--host', '0.0.0.0', '--port', str(port), '--reload'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'{Message.SERVER_NETWORK_ACCESS_ERROR_MSG}: {e}')


if __name__ == "__main__":
    cli()
