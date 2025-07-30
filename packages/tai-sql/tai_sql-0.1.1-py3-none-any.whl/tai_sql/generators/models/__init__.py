import os
import jinja2
from typing import List, ClassVar
from datetime import datetime

from tai_sql import db
from ..base import BaseGenerator

class ModelsGenerator(BaseGenerator):
    """Generador de modelos SQLAlchemy a partir de clases Table"""

    _jinja_env: ClassVar[jinja2.Environment] = None
    _imports: ClassVar[List[str]] = None
    
    @property
    def jinja_env(self) -> jinja2.Environment:
        """
        Retorna el entorno Jinja2 configurado para renderizar las plantillas
        """
        if self._jinja_env is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            self._jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(templates_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )
        return self._jinja_env
    
    def generate(self) -> str:
        """
        Genera un único archivo con todos los modelos SQLAlchemy.
        
        Returns:
            Ruta al archivo generado
        """

        # Preparar datos para la plantilla
        models_data = []
        
        # Analizar cada modelo y recopilar información
        for model in self.models:
            model_info = model.info()
            models_data.append(model_info)
        
        # Cargar la plantilla
        template = self.jinja_env.get_template('__init__.py.jinja2')
        
        # Renderizar la plantilla
        code = template.render(
            imports=self.imports,
            models=models_data,
            is_postgres=db.provider.drivername == 'postgresql',
            schema_name=db.schema
        )
        
        # Escribir el archivo generado
        file_path = os.path.join(self.config.output_dir, '__init__.py')
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    @property
    def imports(self) -> List[str]:
        """
        Retorna una lista de imports necesarios para el archivo generado.
        
        Returns:
            Lista de strings con los imports
        """
        if self._imports is None:
            
            self._imports = [
                'from __future__ import annotations',
                'from typing import List, Optional',
                'from sqlalchemy import ForeignKeyConstraint',
                'from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship'
            ]

            has_datetime = any(
                any(col.type == 'datetime' for col in model.columns.values())
                for model in self.models
            )
            if has_datetime:
                self._imports.append('from datetime import datetime')

            has_bigint = any(
                any(col.type == 'BigInteger' for col in model.columns.values())
                for model in self.models
            )
            if has_bigint:
                self._imports.append('from sqlalchemy import BigInteger')
                
        return self._imports