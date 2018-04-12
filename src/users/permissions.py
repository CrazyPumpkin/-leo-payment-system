from inspect import isclass

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import BasePermission as DRFBasePermission


def get_class(obj):
    return obj if isclass(obj) else obj.__class__


def get_object(cls):
    return cls() if isclass(cls) else cls


def has_permission(self, request, view, obj):
    self = get_object(self)
    if obj is None:
        return self.has_permission(request, view)
    else:
        return self.has_object_permission(request, view, obj)


class BasePermission(DRFBasePermission):
    """
    Переопределяет стандартный BasePermission из rest_framework для его более удобного наследования

    has_permission_ex - основной метод для переопределения
    """

    def has_permission_ex(self, request, view, obj):
        pass

    def has_permission(self, request, view):
        return self.has_permission_ex(request, view, obj=None)

    def has_object_permission(self, request, view, obj):
        return self.has_permission_ex(request, view, obj)

    def __call__(self):
        return self


class OrCombiner(BasePermission):
    """
    Возвращает True если хотя бы ОДНО ИЗ прав присутсвует у пользователя
    """

    def __init__(self, *perm):
        self.perm = perm

    def has_permission_ex(self, request, view, obj):
        for perm in self.perm:
            if has_permission(perm, request, view, obj):
                return True
        else:
            return False


class AndCombiner(BasePermission):
    """
    Возвращает True если ВСЕ права присутсвует у пользователя
    """

    def __init__(self, *perm):
        self.perm = perm

    def has_permission_ex(self, request, view, obj):
        for perm in self.perm:
            if not has_permission(perm, request, view, obj):
                return False
        else:
            return True


class MethodCombiner(BasePermission):
    """
    Объединяет разные классы прав для разных HTTP-методов
    """

    def __init__(self, dictionary):
        self.d = dictionary

    def has_permission_ex(self, request, view, obj):
        method = request.method.upper()
        if method in self.d:
            perm = self.d[method]
            if isinstance(perm, DRFBasePermission) or isclass(perm) and issubclass(perm, DRFBasePermission):
                # noinspection PyCallByClass
                return has_permission(perm, request, view, obj)
            elif hasattr(perm, '__iter__'):
                return AndCombiner(*perm).has_permission_ex(request, view, obj)
            elif perm in (False, True):
                return perm
            else:
                raise TypeError(perm, " is not valid permission")
        else:
            raise MethodNotAllowed(method)


class ActionCombiner(BasePermission):
    """
    Объединяет разные классы прав для разных action
    """

    def __init__(self, dictionary):
        from rest_framework.viewsets import GenericViewSet
        self.view_class = GenericViewSet
        self.d = dictionary

    def has_permission_ex(self, request, view, obj):
        if not isinstance(view, self.view_class):
            raise TypeError(view)
        if view.action is None:
            return True
        method = view.action.lower()
        if method in self.d:
            perm = self.d[method]
            if isinstance(perm, DRFBasePermission) or isclass(perm) and issubclass(perm, DRFBasePermission):
                # noinspection PyCallByClass
                return has_permission(perm, request, view, obj)
            elif hasattr(perm, '__iter__'):
                return AndCombiner(*perm).has_permission_ex(request, view, obj)
            elif perm in (False, True):
                return perm
            else:
                raise TypeError(perm, " is not valid permission")
        else:
            raise KeyError(method)
