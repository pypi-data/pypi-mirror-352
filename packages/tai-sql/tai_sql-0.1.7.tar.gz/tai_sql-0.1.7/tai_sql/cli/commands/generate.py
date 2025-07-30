import click

from tai_sql import db
from .utils.schema import Schema

class GenerateCommand(Schema):

    def run_generators(self):
        """Run the configured generators."""
        # Ejecutar cada generador
        for generator in db.generators:
            try:
                generator_name = generator.__class__.__name__
                click.echo(f"Ejecutando generador: {generator_name}")
                
                # El generador se encargará de descubrir los modelos internamente
                result = generator.generate()
                
                click.echo(f"✅ Generador {generator_name} completado con éxito.")
                if result:
                    click.echo(f"   Resultado: {result}")
            except Exception as e:
                import logging
                logging.exception(e)
                click.echo(f"❌ Error al ejecutar el generador {generator_name}: {str(e)}", err=True)
