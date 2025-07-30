# -*- coding: utf-8 -*-
"""
Declarative models for SQLAlchemy.
This module provides the base classes and utilities to define
models using SQLAlchemy's declarative system.
"""
from __future__ import annotations
from typing import (
    Any,
    Dict,
    ClassVar,
    List,
    get_type_hints
)
from sqlalchemy import Table as SQLAlchemyTable, MetaData

from tai_sql import db
from .columns import Column
from .relations import Relation, ForeignKey
from .utils import (
    is_native_python_type,
    find_custom_type,
    get_relation_direction,
    is_optional,
    mapped_type
)


class Table:
    """
    Clase base para definir tablas. Esta clase proporciona
    la estructura para definir el esquema de la tabla y análisis
    de los atributos definidos en las subclases.
    """

    __abstract__ = True
    __tablename__: ClassVar[str]

    # Registro centralizado de todos los modelos (subclases de Table)
    registry: ClassVar[List[Table]] = []
    
    # Diccionarios para almacenar columnas y relaciones
    columns: ClassVar[Dict[str, Column]] = {}
    relations: ClassVar[Dict[str, Relation]] = {}
    foreign_keys: ClassVar[List[ForeignKey]] = []
    
    def __init_subclass__(cls) -> None:
        """
        Este método se ejecuta automáticamente cuando se define una subclase.
        Analiza los atributos de la subclase y clasifica las columnas y relaciones.
        """
        super().__init_subclass__()
        
        # Inicializar diccionarios para esta clase específica
        cls.columns = {}
        cls.relations = {}
        cls.foreign_keys = []

        if not hasattr(cls, '__tablename__'):
            raise ValueError(f"El modelo {cls.__name__} debe definir un atributo __tablename__")
        
        cls.tablename = cls.__tablename__
        
        # Añadir al registro central
        Table.registry.append(cls)
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """
        Devuelve un diccionario con la información del modelo.
        """
        return {
            'name': cls.__name__,
            'tablename': cls.tablename,
            'columns': [col.info() for col in cls.columns.values()],
            'relations': [rel.info() for rel in cls.relations.values()],
            'foreign_keys': [fk.info() for fk in cls.foreign_keys],
            'has_foreign_keys': len(cls.foreign_keys) > 0
        }

    @classmethod
    def analyze(cls) -> None:
        """
        Analiza la clase para descubrir sus atributos y clasificarlos
        como columnas o relaciones. Este método debe ser llamado
        después de definir la clase para que pueda procesar los atributos
        definidos con hint hints.
        Este método se encarga de:
        - Recoger los hint hints de la clase.
        - Procesar cada atributo para determinar si es una columna o una relación.
        - Registrar las columnas y relaciones en los diccionarios correspondientes.
        - Registrar la clase en el registro central de modelos.
        """
        for model in cls.registry:
            # Obtener hint hints con el contexto completo
            type_hints = get_type_hints(model)
            
            # Procesar cada atributo de la clase
            for name, hint in type_hints.items():
                # Ignorar atributos especiales, privados o classvars
                if name.startswith('__') or name.startswith('_') or name in ('registry', 'columns', 'relations', 'foreign_keys'):
                    continue
                
                value = getattr(model, name, None)
                mappedtype = mapped_type(hint)
                
                # Procesar como columna
                if isinstance(value, Column):
                    # Ya es una Column (definida con column())
                    column = value
                    column.name = name
                    column.type = mappedtype
                    column.model = model
                    column.nullable = is_optional(hint)
                    column.save()

                elif isinstance(value, Relation):
                    # Ya es una relación explícita
                    relation = value
                    relation.name = name
                    relation.local = model
                    relation.target = find_custom_type(hint)
                    relation.direction = get_relation_direction(hint)
                    relation.save()
                
                elif value is None:

                    if is_native_python_type(hint):
                        column = Column(
                            name=name,
                            type=mappedtype,
                            model=model,
                            nullable=is_optional(hint)
                        )
                        column.save()
                    
                    else:
                        relation = Relation(
                            name=name,
                            local=model,
                            target=find_custom_type(hint),
                            direction=get_relation_direction(hint),
                            implicit=True
                        )
                        relation.store()
                
                else:
                    # Si value es cualquier otro tipo, se asume que es un valor por defecto
                    if is_native_python_type(hint):

                        if mappedtype != mapped_type(type(value)):
                            raise TypeError(f"El tipo del valor por defecto [{value}] no coincide con el tipo esperado '{mappedtype}' para el atributo '{name}' en el modelo '{model.__name__}'")
                        
                        column = Column(
                            name=name,
                            type=mappedtype,
                            model=model,
                            default=value,
                            nullable=is_optional(hint)
                        )
                        column.save()
                    else:
                        raise TypeError(f"El tipo {mappedtype} no es compatible para el atributo '{name}' en el modelo '{model.__name__}'")

        for model in cls.registry:
            for implicit_relation in model.relations.values():
                if implicit_relation.implicit:
                    implicit_relation.lazy_save()
    
    @classmethod
    def validate(cls) -> None:
        """
        Valida que todos los modelos en el registro tengan una primary key definida.
        Lanza un error si algún modelo no tiene una primary key.
        """
        for model in cls.registry:
            if not any(col.primary_key for col in model.columns.values()):
                raise ValueError(f"El modelo {model.__name__} debe tener al menos una columna definida como primary key.")
    
    @classmethod
    def to_sqlalchemy_table(cls, metadata: MetaData) -> SQLAlchemyTable:
        """
        Convierte la definición de tai_sql a una tabla SQLAlchemy
        
        Args:
            metadata: MetaData de SQLAlchemy donde registrar la tabla
            
        Returns:
            Table: Tabla SQLAlchemy equivalente
        """
        
        # Convertir columnas
        cols = []
        for col in cls.columns.values():
            alchemy_col = col.to_sqlalchemy_column()
            cols.append(alchemy_col)
        
        # Convertir relaciones que sean foreign keys
        fks = []
        for fk in cls.foreign_keys:
            alchemy_fk = fk.to_sqlalchemy_foreign_key()
            fks.append(alchemy_fk)
        
        # Crear tabla SQLAlchemy
        table = SQLAlchemyTable(
            cls.tablename,
            metadata,
            *cols,
            *fks,
            schema=db.schema if db.provider.drivername == 'postgresql' else None,
        )
        
        return table
                    