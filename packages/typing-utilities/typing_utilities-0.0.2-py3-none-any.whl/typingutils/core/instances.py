from typing import Callable, Type, TypeVar, Any, Generic, Union, NamedTuple, overload, cast
from types import UnionType, NoneType
from collections import abc
from inspect import stack as get_stack

from typingutils.core.attributes import  ORIGIN, ORIGINAL_CLASS, ARGS, TYPE_PARAMS
from typingutils.core.types import (
    TypeParameter, TypeVarParameter, UnionParameter, AnyType, SetOfAny, TypeArgs,
    is_subscripted_generic_type, is_generic_type, get_generic_origin, issubclass_typing
)

class TypeCheck(NamedTuple):
    is_type: bool
    is_generic_type: bool
    is_subscripted_generic_type: bool

def get_original_class(obj: Any) -> TypeParameter:
    """
    Returns the original generic type from a class instance.
    This is useful for generic types because instances of these doesn't derive from them,
    thus having no generic arguments specified. Will even work when called from within a constructor of a class.

    Notes:
        Won't work with builtin generic types like list and tuple.

    Examples:
        class GenClass[T]:
            def __init__(self): # self == GenClass
                self.org = get_original_class(self) # org == GenClass[x]

        t = GenClass[str]() # type(t) == GenClass
        g = get_original_class(t) # g == GenClass[str]

    Args:
        obj (Any): An instance of a class.

    Returns:
        type: The objects original class if any - otherwise the class itself is returned.
    """

    cls: TypeParameter = type(obj) if not is_type(obj) else obj # pyright: ignore[reportUnknownVariableType]

    if hasattr(obj, ORIGINAL_CLASS):
        return getattr(obj, ORIGINAL_CLASS)
    elif is_generic_type(cls) or is_subscripted_generic_type(cls):
        stack = get_stack()
        for frame in stack[2:]:
            if frame.filename == __file__:
                continue # pragma: no cover
            locals = frame[0].f_locals
            if "self" in locals:
                self = locals["self"]
                if hasattr(self, ORIGIN) and getattr(self, ORIGIN) == cls:
                    return self

    return cls

def _extract_args(obj: Any) -> tuple[tuple[TypeParameter, ...] | None, tuple[TypeVarParameter, ...] | None, tuple[TypeParameter | UnionParameter, ...] | None]:
    """
    Extracts arguments from a generic object or type.

    Examples:
        T = TypeVar('T', bound=str)
        class GenClass(Generic[T]): pass
        params, args, types = _extract_args(GenClass) # => (~T<str>, None, (str,))
        params, args, types = _extract_args(GenClass[str]) # => (None, (str,), (str,))

    Args:
        obj (Any): A class or an instance of a class.

    Returns:
        tuple[
            tuple[TypeParameter, ...] | None,
            tuple[TypeVarParameter, ...] | None,
            tuple[TypeParameter | UnionParameter, ...] | None
        ]: Three sequences corresponding to parameters, arguments and types.
    """

    for attr in (ARGS, TYPE_PARAMS):
        if hasattr(obj, attr):
            from typingutils.core.types import get_types_from_typevar

            args = tuple(
                (
                    arg,
                    get_types_from_typevar(arg) if isinstance(arg, TypeVar) else arg,
                    isinstance(arg, TypeVar)
                )
                for arg in cast(tuple[Any], getattr(obj, attr))
            )
            parameters = tuple( arg for arg, _, typevar in args if typevar )
            arguments = tuple( arg for arg, _, typevar in args if not typevar )
            parameter_types = tuple( arg if not typevar else value for arg, value, typevar in args if not typevar )

            # in python 3.13 certain types may contain both typevars and types in the __args__ attribyte,
            # case in point typing.ContextManager[T] which has ` ~T, bool |None ` except of the expected ` ~T `
            # which is why either parameters or arguments must be None when returned

            if parameters and any(parameters):
                return parameters, None, parameter_types
            elif arguments and any(arguments):
                return None, arguments, parameter_types
            else:
                return None, None, None # pragma: no cover

    return None, None, None

def get_generic_arguments(obj: Any) -> TypeArgs:
    """
    Returns the type arguments used to create a subscripted generic type.
    Will even work when called from within a constructor of the class.

    Notes:
        The class must inherit Generic[T], and it must me the first inherited type to work.

    Examples:
        T = TypeVar('T')
        class GenClass(Generic[T]): pass
        a = get_generic_arguments(GenClass[str]) => (str,)

    Args:
        obj (Any): A type, object or instance of an object.

    Returns:
        TypeArgs: A sequence of types.
    """

    _, args, _ = _extract_args(obj)
    if args is not None:
        return args
    elif not is_type(obj):
        orig_class = get_original_class(obj)
        if orig_class is not type(obj):
            return cast(Callable[[Any], tuple[type, ...]], get_generic_arguments)(orig_class)
    elif isinstance(obj, type) and Generic in obj.__bases__:
        orig_class = get_original_class(obj)
        if orig_class != obj:
            return cast(Callable[[Any], tuple[type, ...]], get_generic_arguments)(orig_class)


    return ()


def is_type(obj: Any) -> bool:
    """
    Checks if object is a type (or a generic type) or not.

    Notes:
        TypeVar's aren't recognized as types.

    Args:
        obj (Any): A type, object or instance of an object.

    Returns:
        bool: A boolean value indicating if object is a type.
    """

    if type(obj) is TypeVar:
        return False
    elif obj is object:
        return False
    elif obj is Any:
        return False
    elif isinstance(obj, UnionType) or get_generic_origin(obj) == Union:
        return True

    return isinstance(obj, type) or is_generic_type(obj) or is_subscripted_generic_type(obj)



def check_type(obj: Any) -> TypeCheck:
    """
    Checks if object is a type.

    Args:
        obj (Any): An instance of an object or a type.

    Returns:
        TypeCheck: Returns a TypeCheck tuple.
    """
    if is_subscripted_generic_type(obj):
        return TypeCheck(True, False, True)
    elif is_generic_type(obj):
        return TypeCheck(True, True, False)
    elif is_type(obj):
        return TypeCheck(True, False, False)
    else:
        return TypeCheck(False, False, False)


@overload
def isinstance_typing(obj: Any) -> bool:
    """
    Checks if object is an instance of an object or not.

    Args:
        obj (Any): A type, object or instance of an object.

    Returns:
        bool: A boolean value indicating if object is an instance of an object or not.
    """
    ...
@overload
def isinstance_typing(obj: Any, cls: AnyType | TypeArgs, *, recursive: bool = False) -> bool:
    """
    Checks if object is an instance of the specified type/types. This implementation
    works similarly to the builtin isinstance(), but supports generics as well.

    Args:
        obj (Any): An object or instance of an object.
        cls (type): A type or sequence of types.

    Returns:
        bool: A boolean value indicating if object is an instance of the specified type/types.
    """
    ...
def isinstance_typing(obj: Any, cls: AnyType | TypeArgs | None = None, *, recursive: bool = False) -> bool:
    obj_is_type = is_type(obj)

    if cls is None and not obj_is_type:
        return True
    elif obj is cls is object:
        return True # object is always an instance of itself
    elif cls is Any:
        return True # all objects are an instance of Any
    elif obj is cls:
        return False # an object is never an instance of itself (unless it is object - see previous line)
    elif obj is type and cls in (object, type[Any], Type, Type[Any]):
        return True # types are only derived from object and type[Any]
    elif type(obj) is type and cls in (object, type, type[Any], Type, Type[Any]):
        return True # all classes are derived from type and object
    elif type(obj) is not type and cls in (object, type[Any], Type[Any]):
        return True # all class instances are derived from type and object
    elif type(obj) is NoneType and cls in (object, type[Any], Type[Any], NoneType):
        return True # None is derived from type and object

    if isinstance(cls, abc.Collection):
        for cls1 in cls:
            if isinstance_typing(obj, cls1):
                return True
        return False

    if obj_is_type:
        return cls is object # all other types are only an instance of object
    if not obj_is_type and cls is type:
        return False # only other types are derived from type object
    if get_generic_origin(cast(type, cls)) is Union:
        for cls1 in getattr(cls, ARGS):
            if isinstance_typing(obj, cls1):
                return True
        return False
    if issubclass_typing(type(obj), cast(type, cls)): # pyright: ignore[reportUnknownArgumentType]
        return True

    obj_has_orig_cls_attr = hasattr(obj, ORIGINAL_CLASS)
    cls_has_args_attr = hasattr(cls, ARGS)
    cls_has_origin_attr = hasattr(cls, ORIGIN)

    if obj_has_orig_cls_attr and getattr(obj, ORIGINAL_CLASS) != type:
        origin = getattr(obj, ORIGINAL_CLASS)
        if origin == cls:
            return True

    if not obj_has_orig_cls_attr and cls_has_origin_attr and cls_has_args_attr and set(get_generic_arguments(cls)) == SetOfAny:
        cls = getattr(cls, ORIGIN)

    if not is_subscripted_generic_type(cast(TypeParameter | UnionParameter, cls)) and not is_generic_type(cast(TypeParameter, type(obj))):
        return isinstance(obj, cast(type, cls))

    elif isinstance(cls, TypeVar):
        from typingutils.core.types import get_types_from_typevar
        return isinstance_typing(obj, get_types_from_typevar(cls))


    if recursive and ( args := get_generic_arguments(cls) ):
        cls_origin = cast(type[Any], getattr(cls, ORIGIN) if cls_has_origin_attr else cls)

        if issubclass(cls_origin, abc.Sequence) and isinstance(obj, abc.Sequence) and isinstance_typing(obj, cast(type[Any], cls_origin)):
            for item in cast(abc.Sequence[Any], obj):
                if not isinstance_typing(item, args[0]):
                    return False
            return True

        if issubclass(cls_origin, abc.Mapping) and isinstance(obj, abc.Mapping) and isinstance_typing(obj, cast(type[Any], cls_origin)):
            for key in cast(abc.Mapping[Any, Any], obj):
                if not isinstance_typing(key, args[0]):
                    return False
                if not isinstance_typing(obj[key], args[1]):
                    return False
            return True

        if issubclass(cls_origin, abc.Set) and isinstance(obj, abc.Set) and isinstance_typing(obj, cast(type[Any], cls_origin)):
            for item in cast(abc.Set[Any], obj):
                if not isinstance_typing(item, args[0]):
                    return False
            return True


        if issubclass(cls_origin, abc.Iterable) and isinstance(obj, abc.Iterable) and isinstance_typing(obj, cast(type[Any], cls_origin)):
            if isinstance_typing(obj, abc.Iterator):
                raise Exception("Recursive instance checks on iterators cannot be done at it would deplete the iterator for further use")
            for item in cast(abc.Iterable[Any], obj):
                if not isinstance_typing(item, args[0]):
                    return False
            return True

    return False