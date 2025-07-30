from __future__ import annotations
import click
from dataclasses import dataclass, field
from typing import List, Union, Dict
from sqlalchemy import Column, text
from sqlalchemy.schema import Table, ForeignKeyConstraint

from tai_sql import db
from tai_sql.orm import Table

@dataclass
class Statement:
    """
    Clase para representar una sentencia DDL
    """
    text: str | List[str]
    table_name: str

@dataclass
class CreateStatement(Statement):
    """
    Clase para representar una sentencia CREATE TABLE
    """
    columns: List[Column] = field(default_factory=list)

@dataclass
class AlterColumnStatement(Statement):
    """
    Clase para representar una sentencia ALTER TABLE ADD COLUMN
    """
    column_name: str
    column: Column

    def check_unique_constraints(self) -> None:

        """
        Verifica y muestra las restricciones únicas de una tabla
        """
        # Verificar si hay datos duplicados antes de añadir constraint UNIQUE
        check_duplicates_query = f"""
        SELECT {self.column_name}, COUNT(*) as count
        FROM {self.table_name}
        GROUP BY {self.column_name}
        HAVING COUNT(*) > 1
        """

        with db.engine.connect() as connection:
            result = connection.execute(text(check_duplicates_query))
        
        return result.first()

@dataclass
class ForeignKeyStatement(Statement):
    """
    Clase para representar una sentencia ALTER TABLE ADD FOREIGN KEY
    """
    fk: ForeignKeyConstraint
    local: Table
    target: Table


@dataclass
class DDLs:

    dialect: str = field(default_factory=lambda: db.engine.dialect)
    
    def create_table_statement(self, table: Table) -> str:
        """
        Genera una sentencia CREATE TABLE personalizada con manejo mejorado de DEFAULT
        
        Args:
            table: Tabla SQLAlchemy
            
        Returns:
            str: Sentencia CREATE TABLE completa
        """

        # Escapar nombre de tabla si es necesario
        table_name = self.reserved_word_mapper(table.name)
        
        # Comenzar la sentencia CREATE TABLE
        lines = [f"CREATE TABLE {table_name} ("]
        
        # Procesar columnas
        column_definitions = []
        for column in table.columns:
            column_def = self.get_column_definition(column)
            column_definitions.append(f"    {column_def}")
        
        # Procesar constraints (PRIMARY KEY, FOREIGN KEY, etc.)
        constraint_definitions = []
        
        # Primary Key
        pk_columns = [col.name for col in table.columns if col.primary_key]
        if pk_columns:
            pk_def = f"    PRIMARY KEY ({', '.join(pk_columns)})"
            constraint_definitions.append(pk_def)
        
        # # Foreign Keys
        # for fk in table.foreign_keys:
        #     fk_def = self.foreign_key_inline_statement(fk)
        #     if fk_def:
        #         constraint_definitions.append(f"    {fk_def}")
        
        # Unique constraints
        for constraint in table.constraints:
            if hasattr(constraint, 'columns') and len(constraint.columns) > 1:
                # Constraint multi-columna
                if constraint.__class__.__name__ == 'UniqueConstraint':
                    col_names = [col.name for col in constraint.columns]
                    unique_def = f"    UNIQUE ({', '.join(col_names)})"
                    constraint_definitions.append(unique_def)
        
        # Combinar definiciones
        all_definitions = column_definitions + constraint_definitions
        lines.append(',\n'.join(all_definitions))
        lines.append(")")
        
        return '\n'.join(lines)
    
    def foreign_key_statement(self, table: Table, fk: ForeignKeyConstraint) -> str:
        """
        Genera una sentencia ALTER TABLE ADD CONSTRAINT para Foreign Key
        
        Args:
            table: Tabla SQLAlchemy
            fk: ForeignKeyConstraint de SQLAlchemy (soporta relaciones simples y compuestas)
            
        Returns:
            str: Sentencia ALTER TABLE ADD CONSTRAINT
        """
        try:
            # Escapar nombre de tabla
            table_name = self.reserved_word_mapper(table.name)
            
            # Obtener columnas locales (puede ser múltiples para FK compuestas)
            local_columns_names = [self.reserved_word_mapper(col.name) for col in fk.columns]
            
            # Obtener tabla y columnas de referencia
            # Para ForeignKeyConstraint, las columnas referenciadas están en fk.elements
            if not fk.elements:
                raise ValueError(f"ForeignKeyConstraint sin elementos de referencia en tabla {table.name}")
            
            # Obtener tabla objetivo usando fk.parent
            target_table_name = self.reserved_word_mapper(fk.referred_table.name)

            # Obtener todas las columnas referenciadas
            target_columns_names: list[str] = []
            for element in fk.elements:
                if element.column.table.name != target_table_name:
                    raise ValueError(f"ForeignKeyConstraint con referencias a múltiples tablas no soportado")
                target_columns_names.append(self.reserved_word_mapper(element.column.name))
            
            # Asegurar el mismo orden
            local_columns_names.sort()
            target_columns_names.sort()

            # Verificar que el número de columnas locales y referenciadas coincida
            if len(local_columns_names) != len(target_columns_names):
                raise ValueError(
                    f"Número de columnas locales ({len(local_columns_names)}) no coincide "
                    f"con columnas referenciadas ({len(target_columns_names)}) en tabla {table.name}"
                )
            
            # Generar nombre del constraint
            # Para FK compuestas, incluir todas las columnas en el nombre
            local_cols_str = "_".join([col.strip('"') for col in local_columns_names])
            target_cols_str = "_".join([col.strip('"') for col in target_columns_names])
            constraint_name = f"fk_{table.name}_{local_cols_str}_{target_table_name}_{target_cols_str}"
            
            # Limitar longitud del nombre del constraint (algunos DBs tienen límites)
            if len(constraint_name) > 63:  # PostgreSQL limit
                # Usar hash para nombres muy largos
                import hashlib
                hash_suffix = hashlib.md5(constraint_name.encode()).hexdigest()[:8]
                constraint_name = f"fk_{table.name}_{hash_suffix}"
            
            # Construir statement base
            local_columns_str = ", ".join(local_columns_names)
            target_columns_str = ", ".join(target_columns_names)
            
            statement = (
                f"ALTER TABLE {table_name} "
                f"ADD CONSTRAINT {self.reserved_word_mapper(constraint_name)} "
                f"FOREIGN KEY ({local_columns_str}) "
                f"REFERENCES {target_table_name} ({target_columns_str})"
            )
            
            # Añadir ON DELETE y ON UPDATE si están definidos
            if hasattr(fk, 'ondelete') and fk.ondelete:
                statement += f" ON DELETE {fk.ondelete}"
            
            if hasattr(fk, 'onupdate') and fk.onupdate:
                statement += f" ON UPDATE {fk.onupdate}"
            
            return statement
            
        except Exception as e:
            click.echo(f"   ⚠️  Error generando Foreign Key para {table.name}: {e}")
            return ""
    
    def foreign_key_inline_statement(self, fk: ForeignKeyConstraint) -> str:
        """
        Genera la definición inline de una foreign key (para uso dentro de CREATE TABLE)
        
        Args:
            fk: ForeignKeyConstraint de SQLAlchemy
            
        Returns:
            str: Definición de FOREIGN KEY inline
        """
        try:
            # Obtener columnas locales
            local_columns = [self.reserved_word_mapper(col.name) for col in fk.columns]
            
            # Obtener información de referencia
            if not fk.elements:
                raise ValueError("ForeignKeyConstraint sin elementos de referencia")
            
            # Obtener tabla objetivo usando fk.parent
            target_table_name = self.reserved_word_mapper(fk.parent.name)
            
            # Obtener columnas referenciadas
            target_columns = []
            for element in fk.elements:
                if element.column.table.name != target_table_name:
                    raise ValueError("ForeignKeyConstraint con referencias a múltiples tablas no soportado")
                target_columns.append(self.reserved_word_mapper(element.column.name))
            
            # Construir definición
            local_columns_str = ", ".join(local_columns)
            target_columns_str = ", ".join(target_columns)
            
            statement = f"FOREIGN KEY ({local_columns_str}) REFERENCES {target_table_name} ({target_columns_str})"
            
            # Añadir ON DELETE y ON UPDATE si están definidos
            if hasattr(fk, 'ondelete') and fk.ondelete:
                statement += f" ON DELETE {fk.ondelete}"
            
            if hasattr(fk, 'onupdate') and fk.onupdate:
                statement += f" ON UPDATE {fk.onupdate}"
            
            return statement
            
        except Exception as e:
            raise Exception(f"Error generando Foreign Key inline: {e}")
    
    def get_column_definition(self, column: Column) -> str:
        """
        Genera la definición de columna para CREATE TABLE o ALTER TABLE
        
        Args:
            column: Columna SQLAlchemy
            
        Returns:
            str: Definición de la columna (ej: "name VARCHAR(100) NOT NULL DEFAULT 'John'")
        """
        # Obtener el tipo compilado
        column_type = str(column.type.compile(dialect=self.dialect))

        if column_type in ('INTEGER', 'BIGINT') and column.autoincrement and column.primary_key:
            # Para MySQL/MariaDB, usar AUTO_INCREMENT
            if 'mysql' in str(self.dialect):
                column_type = 'INT AUTO_INCREMENT'
            # Para PostgreSQL, usar SERIAL
            elif 'postgresql' in str(self.dialect):
                if column_type == 'INTEGER':
                    column_type = 'SERIAL'
                elif column_type == 'BIGINT':
                    column_type = 'BIGSERIAL'
        
        # Construir definición base
        definition_parts = [column.name, column_type]
        
        # Añadir NOT NULL
        if not column.nullable:
            definition_parts.append("NOT NULL")
        
        # Manejar DEFAULT - Lógica mejorada
        if column.server_default is not None:
            definition_parts.append(f"DEFAULT NOW()")
        
        # Añadir UNIQUE para columnas únicas individuales
        if column.unique:
            definition_parts.append("UNIQUE")
        
        return " ".join(definition_parts)
    
    def alter_column_statements(self, table_name: str, column: Column) -> list[str]:
        """
        Genera sentencias ALTER COLUMN específicas para cada motor de BD
        
        Args:
            table_name: Nombre de la tabla
            column: Columna SQLAlchemy a modificar
            
        Returns:
            Lista de sentencias ALTER COLUMN
        """

        def alter_postgres(table_name: str, column: Column):
            """
            Genera sentencias ALTER COLUMN específicas para PostgreSQL
            """

            def using_clause(column_name: str, target_type: str) -> str:
                """
                Genera la cláusula USING apropiada para conversión de tipos en PostgreSQL
                
                Args:
                    column_name: Nombre de la columna
                    target_type: Tipo objetivo
                    
                Returns:
                    str: Cláusula USING o cadena vacía si no es necesaria
                """
                target_type_lower = target_type.lower()
                column_name = self.reserved_word_mapper(column_name)
                
                # Mapeo de conversiones comunes
                if 'integer' in target_type_lower or 'int' in target_type_lower:
                    # Para convertir a INTEGER
                    return f"{column_name}::integer"
                
                elif 'varchar' in target_type_lower or 'text' in target_type_lower or 'char' in target_type_lower:
                    # Para convertir a VARCHAR/TEXT
                    return f"{column_name}::text"
                
                elif 'boolean' in target_type_lower or 'bool' in target_type_lower:
                    # Para convertir a BOOLEAN
                    return f"CASE WHEN {column_name} IN ('true', '1', 'yes', 't', 'y') THEN true ELSE false END"
                
                elif 'numeric' in target_type_lower or 'decimal' in target_type_lower or 'float' in target_type_lower:
                    # Para convertir a NUMERIC/DECIMAL/FLOAT
                    return f"{column_name}::numeric"
                
                elif 'timestamp' in target_type_lower or 'datetime' in target_type_lower:
                    # Para convertir a TIMESTAMP
                    return f"{column_name}::timestamp"
                
                elif 'date' in target_type_lower:
                    # Para convertir a DATE
                    return f"{column_name}::date"
                
                elif 'time' in target_type_lower:
                    # Para convertir a TIME
                    return f"{column_name}::time"
                
                elif 'uuid' in target_type_lower:
                    # Para convertir a UUID
                    return f"{column_name}::uuid"
                
                elif 'json' in target_type_lower:
                    # Para convertir a JSON
                    return f"{column_name}::json"
                
                else:
                    # Para otros tipos, intentar conversión directa
                    clean_type = target_type_lower.split('(')[0]  # Remover tamaño si existe
                    return f"{column_name}::{clean_type}"
                
            statements = []
        
            # Cambiar tipo de datos
            column_type = str(column.type.compile(dialect=self.dialect))
            column_name = self.reserved_word_mapper(column.name)

            using = using_clause(column_name, column_type)

            alter_type_stmt = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {column_type}"

            if using:
                alter_type_stmt += f" USING {using}"

            statements.append(alter_type_stmt)
            
            # Manejar NULL/NOT NULL
            if column.nullable:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP NOT NULL"
                )
            else:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL"
                )
            
            # Manejar DEFAULT
            if column.default is not None:
                default_value = self.get_default_value(column.default)
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT {default_value}"
                )
            else:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP DEFAULT"
                )
            
            # Manejar UNIQUE
            if column.unique:
                statements.append(
                    f"ALTER TABLE {table_name} ADD CONSTRAINT {self.reserved_word_mapper(f'unique_{column.name}')}"
                    f" UNIQUE ({column_name})"
                )
            else:
                # Si no es única, eliminar constraint si existe
                statements.append(
                    f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {self.reserved_word_mapper(f'unique_{column.name}')}"
                )
            
            return statements
        
        def alter_mysql(table_name: str, column) -> list[str]:
            """
            Genera sentencias ALTER COLUMN específicas para MySQL
            """
            # MySQL usa MODIFY COLUMN con la definición completa
            column_def = self.get_column_definition(column)
            
            return [f"ALTER TABLE {table_name} MODIFY COLUMN {column_def}"]
        
        def alter_generic(table_name: str, column: Column) -> list[str]:
            """
            Genera sentencias ALTER COLUMN genéricas
            """
            # Intentar con sintaxis estándar SQL
            column_type = str(column.type.compile(dialect=self.dialect))
            
            statements = []

            column_name = self.reserved_word_mapper(column.name)
            
            # Cambiar tipo
            statements.append(
                f"ALTER TABLE {table_name} ALTER COLUMN {column_name} {column_type}"
            )
            
            # Manejar constraints por separado
            if not column.nullable:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL"
                )
            
            if column.default is not None:
                default_value = self.get_default_value(column.default)
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT {default_value}"
                )
            
            return statements
            
        statements = []
        table_name = self.reserved_word_mapper(table_name)
        
        if 'postgresql' in str(self.dialect):
            statements.extend(alter_postgres(table_name, column))

        elif 'mysql' in str(self.dialect):
            statements.extend(alter_mysql(table_name, column))

        else:
            # Fallback genérico
            statements.extend(alter_generic(table_name, column))
        
        return statements

    
    def get_default_value(self, default) -> str:
        """
        Procesa el valor DEFAULT de una columna
        
        Args:
            default: Objeto default de SQLAlchemy
            
        Returns:
            str: Valor DEFAULT formateado para SQL
        """

        def format_sql_function(func_str: str) -> str:
            """
            Formatea una función SQL para uso en DEFAULT
            
            Args:
                func_str: String que representa una función SQL
                
            Returns:
                str: Función SQL formateada
            """
            func_lower = func_str.lower()
            
            # Mapeo de funciones comunes
            function_mapping = {
                'func.now': 'NOW()',
                'func.current_timestamp': 'CURRENT_TIMESTAMP',
                'func.current_date': 'CURRENT_DATE',
                'func.current_time': 'CURRENT_TIME',
                'datetime.now': 'NOW()',
                'now': 'NOW()',
                'current_timestamp': 'CURRENT_TIMESTAMP',
                'current_date': 'CURRENT_DATE',
                'current_time': 'CURRENT_TIME',
            }
            
            # Buscar coincidencia exacta
            if func_lower in function_mapping:
                return function_mapping[func_lower]
            
            # Buscar coincidencias parciales
            for key, value in function_mapping.items():
                if key in func_lower:
                    return value
            
            # Si no se encuentra mapeo, intentar formatear como función
            clean_func = func_str.replace('func.', '').replace('datetime.', '')
            if not clean_func.endswith('()'):
                clean_func += '()'
            
            return clean_func.upper()
        
        # Caso 1: Default con valor específico (default.arg)
        if hasattr(default, 'arg'):
            value = default.arg
            
            if isinstance(value, str):
                # Verificar si es una función SQL disfrazada de string
                if value.startswith('func.') or value in ['datetime.now', 'current_timestamp', 'now']:
                    return format_sql_function(value)
                # String literal normal
                return f"'{value}'"
            
            elif isinstance(value, bool):
                # Boolean - usar TRUE/FALSE en mayúsculas
                return 'TRUE' if value else 'FALSE'
                
            elif isinstance(value, (int, float)):
                # Número
                return str(value)

            elif value is None:
                return 'NULL'
                
            else:
                # Intentar detectar si es una función
                str_value = str(value)
                if any(func in str_value.lower() for func in ['now', 'current_timestamp', 'datetime']):
                    return format_sql_function(str_value)
                # Otros tipos como string literal
                return f"'{str_value}'"
        
        # Caso 2: Default con función SQL (default.name)
        elif hasattr(default, 'name'):
            return format_sql_function(default.name)
        
        # Caso 3: Default escalar directo
        elif hasattr(default, 'is_scalar') and default.is_scalar:
            if isinstance(default.value, bool):
                return 'TRUE' if default.value else 'FALSE'
            elif isinstance(default.value, str):
                return f"'{default.value}'"
            else:
                return str(default.value)
        
        # Caso 4: Valor directo (fallback)
        else:
            str_value = str(default)
            
            # Detectar booleanos en string
            if str_value.lower() in ['true', 'false']:
                return str_value.upper()
            
            # Detectar funciones
            if any(func in str_value.lower() for func in ['now', 'current_timestamp', 'datetime']):
                return format_sql_function(str_value)
            
            # Default como string literal
            return f"'{str_value}'"
    
    @property
    def reserved_words(self) -> set[str]:
        # Lista de palabras reservadas comunes en PostgreSQL
        return {
            'user', 'order', 'group', 'table', 'index', 'view', 'database',
            'schema', 'column', 'row', 'select', 'insert', 'update', 'delete',
            'create', 'drop', 'alter', 'grant', 'revoke', 'commit', 'rollback',
            'transaction', 'begin', 'end', 'function', 'procedure', 'trigger',
            'constraint', 'primary', 'foreign', 'unique', 'check', 'default',
            'null', 'not', 'and', 'or', 'in', 'exists', 'between', 'like',
            'is', 'as', 'on', 'from', 'where', 'having', 'limit', 'offset'
        }
    
    def reserved_word_mapper(self, identifier: str) -> str:
        """
        Escapa identificadores que pueden ser palabras reservadas
        
        Args:
            identifier: Nombre de tabla o columna
            
        Returns:
            str: Identificador escapado si es necesario
        """
        
        # Verificar si necesita escape
        if identifier.lower() in self.reserved_words:
            # Para PostgreSQL usar comillas dobles
            if 'postgresql' in str(self.dialect):
                return f'"{identifier}"'
            # Para MySQL usar backticks
            elif 'mysql' in str(self.dialect):
                return f'`{identifier}`'
            # Para SQLite usar corchetes o comillas dobles
            else:
                return f'"{identifier}"'
        
        return identifier


@dataclass
class DDLManager:
    """
    Clase para gestionar las sentencias DDL generadas
    """
    statements: List[Union[CreateStatement, AlterColumnStatement, ForeignKeyStatement]] = field(default_factory=list)
    ddl: DDLs = field(default_factory=DDLs)

    def add_statement(self, statement: Statement):
        """Añade una sentencia DDL a la lista"""
        self.statements.append(statement)

    def clear(self):
        """Limpia todas las sentencias DDL"""
        self.statements.clear()

    def generate_creations(self, tables: list[Table]) -> list[CreateStatement]:
        """
        Genera sentencias DDL para crear tablas nuevas con manejo mejorado de DEFAULT
        
        Returns:
            Lista de sentencias DDL de creación
        """
        if tables:
            click.echo("🛠️  Generando sentencias CREATE TABLE...")
        
        for table in tables:
            
            stmt = CreateStatement(
                text=self.ddl.create_table_statement(table),
                table_name=table.name,
                columns=list(table.columns.values())
            )
            self.add_statement(stmt)
            click.echo(f"   🆕 Nueva tabla: {table.name}")
        
        # Generar Foreign Keys como statements separados
        self.generate_foreign_key_statements(tables)
        
        return self.statements

    def generate_foreign_key_statements(self, tables: list[Table]) -> None:
        """
        Genera statements ALTER TABLE ADD CONSTRAINT para todas las Foreign Keys
        """
        if not tables:
            return
            
        click.echo("🔗 Generando Foreign Key constraints...")
        
        for table in tables:
            
            for fk in table.foreign_key_constraints:
                fk_statement = self.ddl.foreign_key_statement(table, fk)

                local = fk.parent
                target = fk.referred_table
                local_columns_names = [col.name for col in fk.columns]
                target_columns_names = [element.column.name for element in fk.elements]

                # Asegurar el mismo orden
                local_columns_names.sort()
                target_columns_names.sort()

                if fk_statement:
                    stmt = ForeignKeyStatement(
                        text=fk_statement,
                        table_name=table.name,
                        fk=fk,
                        local=local,
                        target=target,
                    )
                    self.add_statement(stmt)
                    click.echo(f'   🔗 Foreign Key: {local.name}[{", ".join(local_columns_names)}] → {target.name}[{", ".join(target_columns_names)}]')
    
    def generate_migrations(
            self,
            new_cols: Dict[str, list[Column]],
            delete_cols: Dict[str, list[Column]],
            modified_cols: Dict[str, list[Column]]
    ) -> list[Statement]:
        """
        Genera sentencias DDL para las migraciones incrementales
        """
        if new_cols or delete_cols or modified_cols:
            click.echo("🛠️  Generando sentencias de migración...")
        
        # Añadir columnas nuevas
        if new_cols:
            for table_name, columns in new_cols.items():
                for column in columns:
                    # Usar el mismo método para generar definición de columna
                    column_def = self.ddl.get_column_definition(column)
                    stmt = AlterColumnStatement(
                        text=f"ALTER TABLE {column.table.name} ADD COLUMN {column_def}",
                        table_name=column.table.name,
                        column_name=column.name,
                        column=column
                    )
                    self.add_statement(stmt)
                    click.echo(f'   ➕ Añadir columna "{column.name}" a "{column.table.name}"')
        
        # Eliminar columnas
        if delete_cols:
            for table_name, columns in delete_cols.items():
                for column in columns:
                    stmt = AlterColumnStatement(
                        text=f"ALTER TABLE {column.table.name} DROP COLUMN {self.ddl.reserved_word_mapper(column.name)}",
                        table_name=column.table.name,
                        column_name=column.name,
                        column=column
                    )
                    self.add_statement(stmt)
                    click.echo(f'   ➖ Eliminar columna "{column.name}" de "{column.table.name}"')

        if modified_cols:
            for table_name, columns in modified_cols.items():
                for column in columns:
                    # Generar nueva definición de columna
                    alter_statements = self.ddl.alter_column_statements(table_name, column)

                    stmt = AlterColumnStatement(
                        text=alter_statements,
                        table_name=column.table.name,
                        column_name=column.name,
                        column=column
                    )

                    self.add_statement(stmt)
                    click.echo(f'   🔄 Modificar columna "{column.name}" en "{column.table.name}"')
        
        return self.statements
    
    
    def show(self) -> None:
        """Muestra las sentencias DDL que se van a ejecutar"""
        click.echo()
        click.echo("📄 DDLs:")
        click.echo("=" * 30)
        click.echo()
        
        for i, statement in enumerate(self.statements, 1):
            # click.echo(f"\n-- Sentencia {i}")
            if isinstance(statement.text, List):
                for line in statement.text:
                    click.echo(line)
                    click.echo()
            else:
                click.echo(statement.text)
                click.echo()
        
        click.echo("=" * 30)
        click.echo()

