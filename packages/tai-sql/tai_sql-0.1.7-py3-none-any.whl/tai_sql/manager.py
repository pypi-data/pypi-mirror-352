"""
Gestor central de base de datos usando patrón Singleton.
"""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from sqlalchemy import create_engine, Engine

if TYPE_CHECKING:
    from .generators import BaseGenerator
    from .core import Provider

@dataclass
class EngineParams:
    """Parámetros para la creación del motor SQLAlchemy"""
    sqlalchemy_logs: bool = False
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    pool_size: int = 5
    max_overflow: int = 5
    pool_timeout: int = 30

    def to_dict(self) -> dict:
        return {
            'sqlalchemy_logs': self.sqlalchemy_logs,
            'pool_pre_ping': self.pool_pre_ping,
            'pool_recycle': self.pool_recycle,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout
        }

class DatabaseManager:
    """
    Gestor central para la configuración de la base de datos y generadores.
    Implementa patrón Singleton para garantizar una única instancia.
    """
    
    _instance: Optional[DatabaseManager] = None
    
    def __new__(cls) -> DatabaseManager:
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de base de datos solo una vez"""
        if not self._initialized:
            self._provider = None
            self.schema = 'public'
            self.engine_params = EngineParams()
            self._generators = []
            self._engine = None
            self._initialized = True
            self._tables = []  # Lista para almacenar tablas definidas por el usuario
            self._views = []  # Lista para almacenar vistas definidas por el usuario
    
    @property
    def provider(self) -> Optional[Provider]:
        """Proveedor de la base de datos"""
        return self._provider
    
    @provider.setter
    def provider(self, value: Provider):
        """Establece el proveedor de la base de datos"""
        self._provider = value
    
    @property
    def engine(self) -> Engine:
        """Obtiene o crea el motor SQLAlchemy"""
        if not self._engine and self._provider:
            engine_args = {
                'echo': self.engine_params.sqlalchemy_logs,
                'pool_pre_ping': self.engine_params.pool_pre_ping,
                'pool_recycle': self.engine_params.pool_recycle,
                'pool_size': self.engine_params.pool_size,
                'max_overflow': self.engine_params.max_overflow,
                'pool_timeout': self.engine_params.pool_timeout
            }
            self._engine = create_engine(self.provider.url, **engine_args)
        return self._engine
    
    @property
    def generators(self) -> list[BaseGenerator]:
        """Lista de generadores configurados"""
        return self._generators
    
    @generators.setter
    def generators(self, value: list[BaseGenerator]):
        """Establece la lista de generadores"""
        self._generators = value
    
    @property
    def tables(self) -> list:
        """Lista de tablas definidas por el usuario"""
        return self._tables
    
    @tables.setter
    def tables(self, value: list):
        """Establece la lista de tablas definidas por el usuario"""
        self._tables = value

# Instancia global única
db = DatabaseManager()