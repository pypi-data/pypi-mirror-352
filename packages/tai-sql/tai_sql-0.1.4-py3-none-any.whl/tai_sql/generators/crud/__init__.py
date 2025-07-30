import os
import jinja2
from typing import List, Union, Optional, Literal, Dict
from pathlib import Path

from tai_sql import db
from ..base import BaseGenerator
from .sync import SyncCRUDGenerator
from .asyn import AsyncCRUDGenerator

class CRUDGenerator(BaseGenerator):
    """
    Generador de clases CRUD para modelos SQLAlchemy con soporte sync/async.
    """
    
    def __init__(self, 
                 output_dir: Optional[str] = None, 
                 models_import_path: str = "database.models",
                 mode: Literal['sync', 'async', 'both'] = 'sync'):
        """
        Inicializa el generador CRUD.
        
        Args:
            output_dir: Directorio de salida para los archivos CRUD
            models_import_path: Ruta de importación donde están los modelos generados
            mode: Modo de generación ('sync', 'async', 'both')
        """
        super().__init__(output_dir)
        self.models_import_path = models_import_path
        self.mode = mode
    
    @property
    def sync_generator(self) -> SyncCRUDGenerator:
        output_dir = os.path.join(self.config.output_dir, 'syn')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return SyncCRUDGenerator(
            output_dir=output_dir,
            models_import_path=self.models_import_path
        )
    
    @property
    def async_generator(self) -> AsyncCRUDGenerator:
        output_dir = os.path.join(self.config.output_dir, 'asyn')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return AsyncCRUDGenerator(
            output_dir=output_dir,
            models_import_path=self.models_import_path
        )
    
    def generate(self) -> Union[tuple[str, str], str]:
        """
        Genera las clases CRUD según el modo especificado.
        
        Returns:
            Ruta al directorio generado
        """
        if self.validate_configuration():
            if self.mode in ['sync', 'both']:
                sync_result = self.sync_generator.generate()
            
            if self.mode in ['async', 'both']:
                async_result = self.async_generator.generate()
            
            if self.mode == 'both':
                return sync_result, async_result
            
            elif self.mode == 'sync':
                return sync_result
            
            elif self.mode == 'async':
                return async_result
    
    def get_generated_structure(self) -> Dict[str, List[str]]:
        """
        Retorna la estructura de archivos que se generarán
        
        Returns:
            Diccionario con la estructura de directorios y archivos
        """
        structure = {}
        
        if self.mode == 'both':
            structure['sync'] = ['__init__.py', 'session_manager.py', 'endpoints.py']
            structure['async'] = ['__init__.py', 'session_manager.py', 'endpoints.py']
        else:
            structure[self.mode] = ['__init__.py', 'session_manager.py', 'endpoints.py']
        
        return structure
    
    def validate_configuration(self) -> bool:
        """
        Valida que la configuración del generador sea correcta
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ValueError: Si la configuración es inválida
        """
        if not db.provider:
            raise ValueError("No se ha configurado un provider. Usa datasource() primero.")
        
        if not db.provider.source_input_type:
            raise ValueError("El provider no tiene source_input_type configurado.")
        
        if self.mode not in ['sync', 'async', 'both']:
            raise ValueError(f"Modo no válido: {self.mode}. Debe ser 'sync', 'async' o 'both'.")
        
        if not self.models:
            raise ValueError("No se encontraron modelos para generar CRUDs.")
        
        return True
    
    def __str__(self) -> str:
        return f"CRUDGenerator(mode={self.mode}, output_dir={self.config.output_dir})"
    
    def __repr__(self) -> str:
        return self.__str__()