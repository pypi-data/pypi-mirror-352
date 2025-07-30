from typing import get_origin, get_args, Union, Optional, List
from datetime import datetime, date

def is_native_python_type(type_hint) -> bool:
    """
    Verifica si un tipo es nativo de Python, incluyendo tipos genéricos.
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es un tipo nativo, False en caso contrario
    """
    # Tipos básicos nativos

    NATIVE_TYPES = {
        str, int, float, bool, bytes, list, dict, set, tuple,
        type(None), complex, frozenset, bytearray, memoryview
    }
    
    # Verificar si es un tipo básico nativo
    if type_hint in NATIVE_TYPES:
        return True
    
    if type_hint is datetime or type_hint is date:
        return True
    
    # Verificar si es un tipo builtin
    if hasattr(type_hint, '__module__') and type_hint.__module__ == 'builtins':
        return True
    
    # Manejar tipos genéricos como List[str], Dict[str, int], etc.
    origin = get_origin(type_hint)
    if origin is not None:
        for arg in get_args(type_hint):
            # Verificar si el origen es un tipo nativo
            if arg in NATIVE_TYPES:
                return True
        
        # Verificar Union (como Optional[str])
        if origin is Union:
            
            args = get_args(type_hint)
            # Optional[X] es Union[X, None]
            if len(args) == 2 and type(None) in args:
                other_type = args[0] if args[1] is type(None) else args[1]
                return is_native_python_type(other_type)
            # Para otros Union, verificar si todos los tipos son nativos
            return all(is_native_python_type(arg) for arg in args)
    return False


def find_custom_type(type_hint) -> Optional[type]:
    """
    Encuentra el tipo customizado (no nativo) en un type hint.
    
    Esta función busca recursivamente en el type hint para encontrar
    el primer tipo que no sea nativo de Python. Útil para identificar
    clases Table en relaciones.
    
    Args:
        type_hint: El tipo a analizar (puede ser simple, Union, List, etc.)
        
    Returns:
        Optional[type]: El tipo customizado encontrado, o None si no hay ninguno
        
    Examples:
        find_custom_type(str) -> None (es nativo)
        find_custom_type(User) -> User (si User hereda de Table)
        find_custom_type(List[User]) -> User
        find_custom_type(Optional[Post]) -> Post
        find_custom_type(Union[str, User]) -> User
    """
    
    # Si es None, retornar None
    if type_hint is None or type_hint is type(None):
        return None
    
    # Si es un tipo nativo, retornar None
    if is_native_python_type(type_hint):
        return None
    
    # Si es un tipo simple y no es nativo, es nuestro tipo customizado
    if isinstance(type_hint, type):
        return type_hint
    
    # Manejar tipos genéricos
    origin = get_origin(type_hint)
    if origin is not None:
        args = get_args(type_hint)
        
        # Para List[CustomType], Dict[str, CustomType], etc.
        if origin in (list, dict, set, tuple):
            for arg in args:
                custom_type = find_custom_type(arg)
                if custom_type is not None:
                    return custom_type
        
        # Para Union (incluyendo Optional)
        elif origin is Union:
            for arg in args:
                # Saltar type(None) en Optional[CustomType]
                if arg is type(None):
                    continue
                custom_type = find_custom_type(arg)
                if custom_type is not None:
                    return custom_type
    
    # Si llegamos aquí y es una string (forward reference), intentar resolverla
    if isinstance(type_hint, str):
        # Buscar en el registro de Table para ver si coincide con algún modelo
        from . import Table
        for model in Table.registry:
            if model.__name__ == type_hint:
                return model
    
    return None

def is_optional(type_hint) -> bool:
    """
    Verifica si un tipo es Optional (Union[X, None]).
    
    Args:
        type_hint: El tipo a verificar
        
    Returns:
        bool: True si es Optional, False en caso contrario
    """
    
    # Manejar Optional[X] que es Union[X, None]
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        return len(args) == 2 and type(None) in args
    
    return False

def mapped_type(type_hint) -> str:
    """
    Convierte un tipo Python a un tipo SQLAlchemy Mapped
    
    Args:
        type_hint: Tipo Python
        
    Returns:
        Nombre del tipo Mapped correspondiente
    """
    
    # Manejar Optional[X]
    if is_optional(type_hint):
        return get_args(type_hint)[0].__name__
    
    # Manejar tipos básicos
    if isinstance(type_hint, type):
        # Casos especiales para tipos con nombres específicos
        if type_hint is datetime:
            return "datetime"
        if type_hint is date:
            return "date"
        return type_hint.__name__
    
    # En caso de no poder determinar, devolver 'str'
    return "str"
    
def get_relation_direction(type_hint) -> Optional[str]:
    """
    Determina la dirección de una relación basándose en el type hint.
    
    Esta función analiza el type hint para determinar si la relación es:
    - 'one-to-many': cuando el tipo es List[CustomType] o list[CustomType]
    - 'many-to-one': cuando el tipo es CustomType directamente
    
    Args:
        type_hint: El tipo a analizar
        
    Returns:
        Optional[str]: 'one-to-many', 'many-to-one', o None si no es una relación
        
    Examples:
        get_relation_direction(User) -> 'many-to-one'
        get_relation_direction(List[Post]) -> 'one-to-many'
        get_relation_direction(list[Comment]) -> 'one-to-many'
        get_relation_direction(Optional[User]) -> 'many-to-one'
        get_relation_direction(str) -> None (no es una relación)
    """
    from typing import get_origin, get_args, Union
    
    # Si no hay tipo customizado, no es una relación
    custom_type = find_custom_type(type_hint)
    if custom_type is None:
        return None
    
    # Obtener el origen del tipo
    origin = get_origin(type_hint)
    
    # Si es una lista (List[CustomType] o list[CustomType])
    if origin is list or origin is List:
        return 'one-to-many'
    
    # Si es Union (como Optional[CustomType])
    if origin is Union:
        args = get_args(type_hint)
        # Para Optional[CustomType] = Union[CustomType, None]
        if len(args) == 2 and type(None) in args:
            # Obtener el tipo que no es None
            non_none_type = args[0] if args[1] is type(None) else args[1]
            # Verificar recursivamente el tipo no-None
            return get_relation_direction(non_none_type)
    
    # Si es un tipo customizado directo (CustomType)
    if isinstance(type_hint, type) and custom_type is not None:
        return 'many-to-one'
    
    # Si es una forward reference (string) que apunta a un tipo customizado
    if isinstance(type_hint, str) and custom_type is not None:
        return 'many-to-one'
    
    return None