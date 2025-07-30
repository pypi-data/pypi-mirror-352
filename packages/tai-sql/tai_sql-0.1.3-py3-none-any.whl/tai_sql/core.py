"""
Clases core para la configuración de conexiones.
"""
from __future__ import annotations
import os
from typing import Optional, Literal, ClassVar, Dict
from urllib.parse import urlparse, parse_qs
from sqlalchemy import URL
from sqlalchemy.util import EMPTY_DICT

from tai_sql import db
from .generators import BaseGenerator


class Provider:
    """
    Class to manage database connection parameters.
    """

    # Variable de clase para identificar el tipo de origen de datos
    source_input_type: ClassVar[Optional[Literal['env', 'connection_string', 'params']]] = None
    
    def __repr__(self) -> str:
        """Return a string representation of the Provider instance."""
        return f"Provider(DRIVER={self.drivername}, HOST={self.host}:{self.port}, DB={self.database})"

    @classmethod
    def from_environment(cls, var_name: str = 'DATABASE_URL') -> Provider:
        """
        Crea un Provider desde una variable de entorno.
        
        Args:
            variable_name: Nombre de la variable de entorno
            fallback: URL de fallback si la variable no existe
            
        Returns:
            Instancia de Provider configurada desde entorno
        """
        connection_string = os.getenv(var_name)
        if connection_string is None:
            raise ValueError(f'Debes añadir "{var_name}" como variable de entorno')
        
        instance = cls.from_connection_string(connection_string)
        instance.source_input_type = 'env'
        return instance
    
    @classmethod
    def from_connection_string(cls, connection_string: str) -> Provider:
        """
        Crea un Provider desde un string de conexión directo.
        
        ADVERTENCIA: Este método expone credenciales en el código fuente.
        
        Args:
            connection_string: String de conexión completo
            
        Returns:
            Instancia de Provider configurada desde string
        """
        try:
            instance = cls()
            parse = urlparse(connection_string)
            instance.url = URL.create(
                drivername=parse.scheme,
                username=parse.username,
                password=parse.password,
                host=parse.hostname,
                port=parse.port,
                database=parse.path[1:],  # Remove leading '/'
                query=parse_qs(parse.query)
            )
            instance.source_input_type = 'connection_string'
            return instance
        except Exception as e:
            raise ValueError(f"Error parsing connection string: {e}")
    
    @classmethod
    def from_params(
            cls,
            drivername: str,
            username: str,
            password: str,
            host: str,
            port: int,
            database: str,
            query: dict = EMPTY_DICT
    ) -> Provider:
        """
        Crea un Provider desde parámetros individuales.
        
        ADVERTENCIA: Este método expone credenciales en el código fuente.
        
        Args:
            host: Servidor de base de datos
            database: Nombre de la base de datos
            username: Usuario de conexión
            password: Contraseña de conexión
            port: Puerto de conexión
            driver: Driver de base de datos
            
        Returns:
            Instancia de Provider configurada desde parámetros
        """
        instance = cls()
        instance.url = URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            query=query
        )
        instance.source_input_type = 'params'
        return instance

    @property
    def url(self) -> URL:
        """Get the URL object."""
        return self._url
    
    @url.setter
    def url(self, value: URL):
        """Set the URL object."""
        self._url = value
    
    def get_url(self) -> str:
        """Get the connection string."""
        return self.url.render_as_string(hide_password=False)
    
    def get_connection_params(self) -> dict:
        """
        Get the connection parameters as a dictionary.
        
        Returns:
            Dictionary with connection parameters
        """
        return {
            'drivername': self.drivername,
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'query': self.query
        }

    @property
    def drivername(self) -> str:
        """Get the driver name."""
        return self.url.drivername
    
    @property
    def username(self) -> Optional[str]:
        """Get the username."""
        return self.url.username
    
    @property
    def password(self) -> str:
        """Get the password."""
        return self.url.password
    
    @property
    def host(self) -> Optional[str]:
        """Get the host."""
        return self.url.host
    
    @property
    def port(self) -> Optional[int]:
        """Get the port."""
        return self.url.port
    
    @property
    def database(self) -> Optional[str]:
        """Get the database name."""
        return self.url.database
    
    @property
    def query(self) -> dict:
        """Get the query parameters."""
        return self.url.query


def datasource(
    provider: Provider,
    schema: Optional[str] = 'public',
    sqlalchemy_logs: bool = False,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
    pool_size: int = 5,
    max_overflow: int = 5,
    pool_timeout: int = 30
) -> bool:
    """
    Configura el proveedor de base de datos y los parámetros de conexión del motor SQLAlchemy.
    
    Esta función establece la configuración global del datasource que será utilizada
    por el sistema para conectarse a la base de datos. Configura tanto el proveedor
    de base de datos como los parámetros del pool de conexiones.
    
    Args:
        provider (Provider): Datos de conexión. Usa env, connection_string o params para crear un Provider.
        schema (Optional[str], optional): Esquema de base de datos a utilizar por defecto. 
            Defaults to 'public'.
        sqlalchemy_logs (bool, optional): Habilita o deshabilita los logs de SQLAlchemy 
            para debugging. Defaults to False.
        pool_pre_ping (bool, optional): Verifica la conexión antes de usarla del pool.
            Útil para detectar conexiones perdidas. Defaults to True.
        pool_recycle (int, optional): Tiempo en segundos después del cual una conexión
            será reciclada. Previene timeouts de conexiones inactivas. Defaults to 3600.
        pool_size (int, optional): Número de conexiones que mantendrá el pool.
            Defaults to 5.
        max_overflow (int, optional): Número máximo de conexiones adicionales que se pueden
            crear más allá del pool_size cuando sea necesario. Defaults to 5.
        pool_timeout (int, optional): Tiempo máximo en segundos para esperar una conexión
            disponible del pool antes de generar un timeout. Defaults to 30.
    
    Returns:
        bool: True si la configuración se estableció correctamente.
        
    Example:
        >>> from tai_sql import env
        >>> datasource(
        ...     provider=env('DATABASE_URL'),
        ...     schema='mi_esquema',
        ...     pool_size=10,
        ...     pool_recycle=7200
        ... )
        True
        
    Note:
        Esta función debe llamarse antes de realizar cualquier operación con la base
        de datos. Los parámetros del pool son especialmente importantes para aplicaciones
        con alta concurrencia.
    """
    db.provider = provider
    db.schema = schema
    db.engine_params.sqlalchemy_logs = sqlalchemy_logs
    db.engine_params.pool_pre_ping = pool_pre_ping
    db.engine_params.pool_recycle = pool_recycle
    db.engine_params.pool_size = pool_size
    db.engine_params.max_overflow = max_overflow
    db.engine_params.pool_timeout = pool_timeout
    return True

def env(variable_name: str = 'DATABASE_URL') -> Provider:
    """
    Crea un Provider desde una variable de entorno (método recomendado).
    
    Args:
        variable_name: Nombre de la variable de entorno
        fallback: URL de fallback si la variable no existe
        
    Returns:
        Provider configurado desde variable de entorno
        
    Example:
        ```python
        from tai_sql import env, datasource
        
        # Leer desde DATABASE_URL
        datasource(provider=env())
        
        # Leer desde variable personalizada
        datasource(provider=env('MY_DB_URL'))
        ```
    """
    return Provider.from_environment(variable_name)


def connection_string(connection_string: str) -> Provider:
    """
    Crea un Provider desde un string de conexión directo.
    
    ⚠️  ADVERTENCIA: Este método expone credenciales en el código fuente.
    Se recomienda usar env() en su lugar.
    
    Args:
        connection_string: String de conexión completo
        
    Returns:
        Provider configurado desde string de conexión
        
    Example:
        ```python
        from tai_sql import connection_string, datasource
        
        # ❌ NO recomendado - credenciales expuestas
        datasource(provider=connection_string('driver://user:pass@host/db'))
        ```
    """
    return Provider.from_connection_string(connection_string)

def params(
        host: str,
        database: str,
        username: str,
        password: str,
        port: int = 5432,
        driver: str = 'postgresql',
        query: dict = EMPTY_DICT
) -> Provider:
    """
    Crea un Provider desde parámetros individuales de conexión.
    
    ⚠️  ADVERTENCIA DE SEGURIDAD: Este método expone credenciales en el código fuente.
    Se recomienda usar env() en su lugar.
    
    Args:
        host: Servidor de base de datos
        database: Nombre de la base de datos
        username: Usuario de conexión
        password: Contraseña de conexión
        port: Puerto de conexión (default: 5432)
        driver: Driver de base de datos (default: 'postgresql')
        
    Returns:
        Provider configurado desde parámetros
        
    Example:
        ```python
        from tai_sql import params, datasource
        
        # ❌ NO recomendado - credenciales expuestas
        datasource(provider=params(
            host='localhost',
            database='mydb',
            username='user',
            password='secret'
        ))
        ```
    """    
    return Provider.from_params(driver, username, password, host, port, database, query)

def generate(*generators) -> bool:
    """
    Configura los generadores a utilizar para la generación de recursos.
    
    Args:
        *generators: Funciones generadoras a configurar
    
    Custom:
    -
        Puedes crear tus propios generadores heredando de BaseGenerator y pasarlos aquí.
    
    Returns:
        bool: True si la configuración se estableció correctamente.
    
    Example:
        >>> from tai_sql.generators import ModelsGenerator, CRUDGenerator
        >>> generate(
        ...     ModelsGenerator(output_dir='models'),
        ...     CRUDGenerator(output_dir='crud', models_import_path='database.models')
        ... )
        True
    """
    for gen in generators:
        if not isinstance(gen, BaseGenerator):
            raise ValueError(f"{gen.__class__.__name__} debe heredar de BaseGenerator")

    db.generators = generators
    return True