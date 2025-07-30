import os
from abc import ABC, abstractmethod
from typing import List, Optional, ClassVar

# Obtener modelos del registro centralizado
import tai_sql
from tai_sql.orm.mappers import Table

class BaseGenerator(ABC):
    """
    Clase base abstracta para todos los generadores de tai-sql.
    
    Todos los generadores deben heredar de esta clase e implementar
    el método `generate` para mantener una interfaz común.
    """

    _models: ClassVar[List[Table]] = []  # Atributo de clase privado
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa el generador.
        
        Args:
            output_dir: Directorio de salida para los archivos generados.
                        Si es None, se usará un directorio por defecto.
        """
        self.config = GeneratorConfig(output_dir)
    
    @classmethod
    def register_model(cls, model: Table) -> None:
        """
        Registra un modelo para ser procesado por el generador.
        
        Args:
            model: Clase del modelo a registrar
        """
        if model not in cls._models:
            cls._models.append(model)
    
    @classmethod
    def register_models(cls, *models: Table) -> None:
        """
        Registra múltiples modelos para ser procesados por el generador.
        
        Args:
            *models: Clases de modelos a registrar
        """
        for model in models:
            cls.register_model(model)
    
    @classmethod
    def clear_models(cls) -> None:
        """
        Limpia la lista de modelos registrados.
        Útil para testing o para reiniciar el estado.
        """
        cls._models.clear()
    
    @property
    def models(self) -> List[Table]:
        """
        Retorna la lista de modelos registrados.
        Si no hay modelos registrados, intenta descubrir los modelos automáticamente.
        
        Returns:
            Lista de modelos registrados
        """
        if not self._models:
            Table.analyze()
            Table.validate()
            self.register_models(*Table.registry)

        return self._models
    
    @abstractmethod
    def generate(self) -> Optional[str]:
        """
        Genera recursos basados en los modelos registrados.
        
        Este método debe ser implementado por todas las subclases.
        
        Returns:
            El resultado de la generación, específico de cada generador
        """
        pass

class GeneratorConfig:
    """
    Configuración para los generadores.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa la configuración del generador.
        
        Args:
            output_dir: Directorio de salida para los archivos generados
        """
        # Configurar el directorio de salida
        if output_dir is None:
            # Obtener el directorio de instalación del paquete
            output_dir = os.path.dirname(os.path.abspath(tai_sql.__file__))
            output_dir = os.path.join(output_dir, 'generated')
        
        # Crear el directorio si no existe
        os.makedirs(output_dir, exist_ok=True)

        self.output_dir = output_dir