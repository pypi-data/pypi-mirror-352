import sys
import click
from .commands.generate import GenerateCommand
from .commands.init import InitCommand, NewSchemaCommand
from .commands.push import PushCommand
from .commands.createdb import DBCommand

@click.group()
def cli():
    """CLI para tai-sql: Un framework de ORM basado en SQLAlchemy."""
    pass

@cli.command()
@click.option('--name', '-n', default='database', help='Nombre del proyecto a crear')
@click.option('--schema-name', default='main', help='Nombre del primer esquema a crear')
def init(name: str, schema_name: str):
    """Inicializa un nuevo proyecto tai-sql"""
    command = InitCommand(namespace=name, schema_name=schema_name)
    try:
        command.check_poetry()
        command.check_directory_is_avaliable()
        command.check_virtualenv()
        command.create_project()
        command.add_dependencies()
        command.add_schemas_folder()
        command.msg()
    except Exception as e:
        click.echo(f"❌ Error al inicializar el proyecto: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--schema', '-s', help='Ruta al archivo de esquema (default=main)', default='database/schemas/main.py')
@click.option('--createdb', '-c', is_flag=True, help='Crea la base de datos si no existe')
@click.option('--force', '-f', is_flag=True, help='Forzar la generación de recursos, incluso si ya existen')
@click.option('--dry-run', '-d', is_flag=True, help='Mostrar las sentencias DDL sin ejecutarlas')
@click.option('--verbose', '-v', is_flag=True, help='Mostrar información detallada durante la ejecución')
def push(schema: str, createdb: bool, force: bool, dry_run: bool, verbose: bool):
    """Genera las tablas definidas en el schema y las ejecuta en la base de datos configurada"""

    db_command = DBCommand(schema)
    db_command.pre_validations()
    db_command.load_module()
    db_command.post_validations()
    db_command.warnings()
    command = PushCommand(schema)
    try:
        # Validar la configuración del schema
        

        click.echo(f"🚀 Push schema: {schema}")

        if createdb:
            # Crear la base de datos si no existe
            db_command.create()
        
        # Cargar y procesar el schema
        command.load_schema()

        # Validar nombres
        command.validate_schema_names()
        
        # Generar DDL
        ddl = command.generate()
        
        # Mostrar DDL
        if ddl:
            if verbose or dry_run:
                command.ddl_manager.show()
            else:
                click.echo("   ℹ️  Modo silencioso: No se mostrarán las sentencias DDL")
        
        if dry_run:
            click.echo("🔍 Modo dry-run: No se ejecutaron cambios")
            return
        
        # Confirmar ejecución
        if not force:
            confirm = click.confirm("¿Deseas ejecutar estas sentencias en la base de datos?")
            if not confirm:
                click.echo("❌ Operación cancelada")
                return
        
        # Ejecutar DDL
        command.execute()
        
    except Exception as e:
        import logging
        logging.exception(e)
        click.echo(f"❌ Error al procesar schema: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--schema', '-s', help='Ruta al archivo de esquema (default=main)', default='database/schemas/main.py')
def generate(schema):
    """Genera recursos basados en los generadores configurados"""

    command = GenerateCommand(schema)

    try:
        command.pre_validations()
        command.load_module()
        command.post_validations()
        command.warnings()
        command.run_generators()
        
    except Exception as e:
        click.echo(f"❌ Error inesperado: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--project', default='database', help='Nombre del proyecto (default: database)')
@click.argument('name')
def new_schema(project: str, name: str):
    """Crea un nuevo esquema en el proyecto"""
    if not name:
        click.echo("❌ Error: Debes proporcionar un nombre para el esquema.", err=True)
        sys.exit(1)

    try:
        command = NewSchemaCommand(namespace=project, schema_name=name)
        command.create()
    except Exception as e:
        click.echo(f"❌ Error al crear el esquema: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()