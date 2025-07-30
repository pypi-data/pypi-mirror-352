import sys
import importlib.util
from pathlib import Path
import click
from tai_sql import db

class Schema:

    def __init__(self, schema_path: str):
        self.schema_path = schema_path

    def pre_validations(self) -> None:
        """Validate the database configuration."""
        if not Path(self.schema_path).exists():
            click.echo(f'❌ Error: El archivo de esquema "{self.schema_path}" no existe.', err=True)
            sys.exit(1)
        
        if not self.schema_path.endswith('.py'):
            click.echo(f"❌ El archivo de schema debe ser un archivo Python: {self.schema_path}", err=True)
            sys.exit(1)

    def post_validations(self) -> None:
        if not db.provider:
            click.echo(f"❌ No se ha configurado un proveedor de datos en {self.schema_path}", err=True)
            click.echo(f"   Asegúrate de llamar a datasource()", err=True)
            sys.exit(1)
            
        if not db.engine:
            click.echo(f"❌ No se pudo crear el engine de base de datos", err=True)
            click.echo(f"   Verifica la configuración de tu proveedor", err=True)
            sys.exit(1)

        if not db.provider.database:
            click.echo(f"❌ No se pudo encontrar el nombre de la base de datos", err=True)
            click.echo(f"   Verifica la configuración de tu proveedor", err=True)
            sys.exit(1)

    def warnings(self) -> bool:
        """Check if the database is configured with generators and security warnings."""
        if not db.generators:
            click.echo("⚠️ Advertencia: No se han configurado generadores. No se generará ningún recurso.", err=True)
            sys.exit(1)
        
        if db.provider.source_input_type in ('connection_string', 'params'):
            click.echo(
                f'⚠️  ADVERTENCIA DE SEGURIDAD:\n'
                f'    El método "{db.provider.source_input_type}" expone credenciales en el código fuente.\n'
                f'    Se recomienda usar env() en su lugar.',
                err=True
            )

    def load_module(self) -> None:
        """Load the module from the schema path."""
        module_name = "schema_module"
        spec = importlib.util.spec_from_file_location(module_name, self.schema_path)
        if spec is None:
            raise ImportError(f"No se pudo cargar el archivo de esquema: {self.schema_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    

    
