"""
Declarative models for SQLAlchemy.
This module provides the base classes and utilities to define
models using SQLAlchemy's declarative system.
"""
from __future__ import annotations

# Importar la instancia global
from .manager import db
from .core import datasource, generate, env, connection_string, params
from .orm import Table, column, relation
from sqlalchemy.types import BigInteger as bigint

# Exportar los elementos principales
__all__ = [
    'db',
    'datasource', 
    'generate',
    'env',
    'connection_string',
    'params',
    'Table',
    'column',
    'relation',
    'bigint'
]