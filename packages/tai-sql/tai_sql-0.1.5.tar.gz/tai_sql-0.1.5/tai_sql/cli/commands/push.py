from __future__ import annotations
import sys
import click
from dataclasses import dataclass, field
from typing import List
from sqlalchemy import MetaData, Column, text, Engine
from sqlalchemy.schema import Table, UniqueConstraint

from tai_sql import db
from tai_sql.orm import Table
from .utils.schema import Schema
from .utils.ddl import DDLManager, CreateStatement, AlterColumnStatement, ForeignKeyStatement


@dataclass
class DriftManager:
    """
    Clase para almacenar los cambios detectados en el esquema
    """
    engine: Engine = field(default_factory=lambda: db.engine)
    metadata: MetaData = field(default_factory=lambda: MetaData(db.schema if db.provider.drivername == 'postgresql' else None))
    existing_metadata: MetaData = field(default_factory=lambda: MetaData(db.schema if db.provider.drivername == 'postgresql' else None))
    new_tables: dict[str, list[Table]] = field(default_factory=dict)
    existing_tables: dict[str, list[Table]] = field(default_factory=dict)
    columns_to_add: dict[str, list[Column]] = field(default_factory=dict)
    columns_to_drop: dict[str, list[Column]] = field(default_factory=dict)
    columns_to_modify: dict[str, list[Column]] = field(default_factory=dict)

    def detect(self) -> None:
        """
        Detecta cambios entre el esquema definido y el esquema actual
        
        Returns:
            dict: Diccionario con los cambios detectados
        """
        click.echo("🔎 Detectando cambios en el esquema...")

        self.existing_metadata.reflect(bind=self.engine)
        
        db_tables = set(self.existing_metadata.tables.keys())
        schema_tables = set(self.metadata.tables.keys())
        
        # Tablas nuevas
        new_tables = list(schema_tables - db_tables)

        for table_name in new_tables:
            new_table = self.metadata.tables[table_name]
            self.new_tables[table_name] = new_table
        
        # Tablas existentes
        existing_tables = list(schema_tables & db_tables)

        # Analizar cambios en columnas para tablas existentes
        for table_name in existing_tables:
            current_table = self.existing_metadata.tables[table_name]
            self.existing_tables[table_name] = current_table
            new_table = self.metadata.tables[table_name]

            constraint_columns = []
            # Check constrains
            for constraint in current_table.constraints:
                if isinstance(constraint, UniqueConstraint):
                    constraint_columns = [col.name for col in constraint.columns]
            
            current_columns = {col.name: col for col in current_table.columns}
            new_columns = {col.name: col for col in new_table.columns}
            
            # Columnas a añadir
            columns_to_add = set(new_columns.keys()) - set(current_columns.keys())
            if columns_to_add:
                self.columns_to_add[table_name] = [
                    new_columns[col_name] for col_name in columns_to_add
                ]
            
            # Columnas a eliminar (comentado por seguridad)
            columns_to_drop = set(current_columns.keys()) - set(new_columns.keys())
            if columns_to_drop:
                self.columns_to_drop[table_name] = [
                    current_columns[col_name] for col_name in columns_to_drop
                ]
            
            # Columnas a modificar
            for col_name in set(current_columns.keys()) & set(new_columns.keys()):
                current_col = current_columns[col_name]
                new_col = new_columns[col_name]

                if str(current_col.type) == 'TIMESTAMP' and str(new_col.type) == 'DATETIME':
                    # Manejar caso especial de TIMESTAMP vs TIMESTAMP WITH TIME ZONE
                    type_changed = False
                else:
                    # Comparar tipo de dato
                    type_changed = str(current_col.type) != str(new_col.type)

                # Comparar nullable
                nullable_changed = current_col.nullable != new_col.nullable
                
                # Comparar valor por defecto
                # default_changed = str(current_col.server_default) != str(new_col.server_default)
                
                # Comparar primary key
                pk_changed = current_col.primary_key != new_col.primary_key
                
                # Comparar autoincrement
                autoincrement_changed = current_col.autoincrement != new_col.autoincrement

                if col_name in constraint_columns:
                    current_col.unique = True

                # Comparar uniqueness
                unique_changed = current_col.unique != new_col.unique
                
                if type_changed or nullable_changed or pk_changed or autoincrement_changed or unique_changed:
                    if table_name not in self.columns_to_modify:
                        self.columns_to_modify[table_name] = []
                    self.columns_to_modify[table_name].append(new_col)

    def show(self):
        """Muestra un resumen de los cambios detectados"""
        click.echo("📋 Resumen de cambios:")
        
        if self.new_tables:
            click.echo(f"   🆕 {len(self.new_tables)} tabla(s) nueva(s): {', '.join(self.new_tables)}")
        
        if self.columns_to_add:
            total_columns = sum(len(cols) for cols in self.columns_to_add.values())
            click.echo(f"   ➕ {total_columns} columna(s) a añadir en {len(self.columns_to_add)} tabla(s)")
        
        if self.columns_to_drop:
            total_columns = sum(len(cols) for cols in self.columns_to_drop.values())
            click.echo(f"   ⚠️  {total_columns} columna(s) serían eliminadas")
        
        if self.columns_to_modify:
            total_columns = sum(len(cols) for cols in self.columns_to_modify.values())
            click.echo(f"   ✏️  {total_columns} columna(s) a modificar en {len(self.columns_to_modify)} tabla(s)")
        
        if not self.new_tables and not self.columns_to_add and not self.columns_to_drop and not self.columns_to_modify:
            click.echo("   ✅ No se detectaron cambios")
        
        click.echo()

class PushCommand(Schema):
    """
    Comando para generar y ejecutar sentencias DDL CREATE TABLE basadas en un schema.
    
    Este comando procesa un archivo de schema, genera las sentencias DDL necesarias
    para crear las tablas definidas y las ejecuta en la base de datos configurada.
    """

    def __init__(self, schema_file: str):
        super().__init__(schema_file)
        self.schema_file = schema_file
        self.ddl_manager = DDLManager()
        self.drift_manager = DriftManager()

    def load_schema(self) -> MetaData:
        """
        Carga y ejecuta el archivo de schema para obtener las definiciones de tablas
        
        Returns:
            MetaData: Metadata de SQLAlchemy con las tablas definidas
        """
        click.echo("📖 Cargando definiciones de schema...")
        
        try:
            # Limpiar estado previo
            db.tables = []

            Table.analyze()
            Table.validate()

            db.tables = Table.registry

            for table in db.tables:
                # Convertir la definición de tai_sql a tabla SQLAlchemy
                sqlalchemy_table = table.to_sqlalchemy_table(self.drift_manager.metadata)
                click.echo(f"   📋 Tabla: {sqlalchemy_table.name}")

            return self.drift_manager.metadata
            
        except Exception as e:
            raise Exception(f"Error al cargar schema: {e}")
    
    def validate_schema_names(self):
        """
        Valida que los nombres de tablas y columnas no sean palabras reservadas
        """
        click.echo("🔍 Validando nombres de tablas y columnas...")
        
        warnings = []
        
        for table in self.drift_manager.metadata.tables.values():
            # Validar nombre de tabla
            if table.name.lower() in self.ddl_manager.ddl.reserved_words:
                warnings.append(f"⚠️  Tabla '{table.name}' es una palabra reservada")
            
            # Validar nombres de columnas
            for column in table.columns:
                if column.name.lower() in self.ddl_manager.ddl.reserved_words:
                    warnings.append(f"⚠️  Columna '{column.name}' en tabla '{table.name}' es una palabra reservada")
        
        if warnings:
            click.echo("❌ Se encontraron problemas con nombres:")
            for warning in warnings:
                click.echo(f"   {warning}")
            click.echo()
            click.echo("💡 Sugerencias:")
            click.echo("   - Cambia 'user' por 'users' o 'app_user'")
            click.echo("   - Cambia 'order' por 'orders' o 'user_order'")
            click.echo("   - Usa nombres descriptivos que no sean palabras reservadas")
            click.echo()
            
            if not click.confirm("¿Continuar de todas formas? (se manejará automáticamente)"):
                click.echo("❌ Operación cancelada por el usuario")
                sys.exit(1)
        
        click.echo("✅ Validación de nombres completada")
    
    def generate(self) -> None:
        """
        Genera las sentencias DDL considerando cambios incrementales
        
        Returns:
            Lista de sentencias DDL como strings
        """

        # Limpiar sentencias previas
        self.ddl_manager.clear()
        # Detectar cambios
        self.drift_manager.detect()
        
        # Mostrar resumen de cambios
        self.drift_manager.show()

        new_tables = self.drift_manager.new_tables
        new_cols = self.drift_manager.columns_to_add
        delete_cols = self.drift_manager.columns_to_drop
        modify_cols = self.drift_manager.columns_to_modify

        if new_tables:
            self.ddl_manager.generate_creations(new_tables.values())
        
        # Generar migraciones para tablas existentes
        if new_cols or delete_cols or modify_cols:
            self.ddl_manager.generate_migrations(new_cols, delete_cols, modify_cols)

        return self.ddl_manager.statements
    
    def execute(self):
        """Ejecuta las sentencias DDL en la base de datos"""
        if not self.ddl_manager.statements:
            click.echo("ℹ️  No hay cambios para aplicar")
            return
            
        click.echo("⚙️  Ejecutando sentencias DDL...")
        
        try:
            executed_count = 0
            
            with self.drift_manager.engine.connect() as conn:
                # Usar transacción para todas las operaciones
                trans = conn.begin()
                
                try:
                    for stmt in self.ddl_manager.statements:

                        if isinstance(stmt, CreateStatement):
                            # Ejecutar CREATE TABLE
                            conn.execute(text(stmt.text))
                            executed_count += 1
                            click.echo(f"   ⚙️  Crear tabla → {stmt.table_name}")
                            
                        elif isinstance(stmt, AlterColumnStatement):
                            # Ejecutar ALTER TABLE

                            if stmt.column.unique:
                                result = stmt.check_unique_constraints()

                                if result:
                                    click.echo("   ❌  UniqueConstraint error:")
                                    click.echo(f'   ⚠️  Columna "{stmt.column_name}" tiene valores duplicados en {stmt.table_name}, se omitirá la modificación')
                                    continue

                            if isinstance(stmt.text, List):
                                for sub_stmt in stmt.text:
                                    conn.execute(text(sub_stmt))
                            else:

                                conn.execute(text(stmt.text))

                            executed_count += 1

                            if stmt.column_name:
                                click.echo(f"   ⚙️ Añadir/modificar columna → {stmt.column_name} en {stmt.table_name}")

                        elif isinstance(stmt, ForeignKeyStatement):

                            # Ejecutar ALTER TABLE
                            conn.execute(text(stmt.text))
                            executed_count += 1

                            # Mostrar información de la ForeignKey
                            local_columns_names = [col.name for col in stmt.fk.columns]
                            target_columns_names = [element.column.name for element in stmt.fk.elements]
                            # Asegurar el mismo orden
                            local_columns_names.sort()
                            target_columns_names.sort()

                            click.echo(f'   ⚙️  Declarar ForeignKey: {stmt.local.name}[{", ".join(local_columns_names)}] → {stmt.target.name}[{", ".join(target_columns_names)}] en {stmt.local.name}')
                    
                    trans.commit()
                    click.echo(f"   🎉 {executed_count} operación(es) ejecutada(s) exitosamente")
                    
                except Exception as e:
                    trans.rollback()
                    raise e
                    
        except Exception as e:
            raise Exception(f"Error al ejecutar DDL: {e}")
    

    
