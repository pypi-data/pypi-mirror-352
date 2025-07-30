"""
File Purpose: tools for simple properties
"""
import contextlib
import weakref

import numpy as np

from .sentinels import NO_VALUE, UNSET
from .pytools import format_docstring
from ..errors import InputConflictError


''' --------------------- Alias an attribute --------------------- '''

def alias(attribute_name, doc=None):
    '''returns a property which is an alias to attribute_name.
    if doc is None, use doc=f'alias to {attribute_name}'.
    '''
    return property(lambda self: getattr(self, attribute_name),
                    lambda self, value: setattr(self, attribute_name, value),
                    doc=f'''alias to {attribute_name}''' if doc is None else doc)

def alias_to_result_of(attribute_name, doc=None):
    '''returns a property which is an alias to the result of calling attribute_name.
    if doc is None, use doc=f'alias to {attribute_name}()'.
    '''
    return property(lambda self: getattr(self, attribute_name)(),
                    doc=f'''alias to {attribute_name}()''' if doc is None else doc)

def alias_child(child_name, attribute_name, doc=None):
    '''returns a property which is an alias to obj.child_name.attribute_name.
    if doc is None, use doc=f'alias to self.{child_name}.{attribute_name}'.
    includes getter AND setter methods.
    '''
    return property(lambda self: getattr(getattr(self, child_name), attribute_name),
                    lambda self, value: setattr(getattr(self, child_name), attribute_name, value),
                    doc=f'''alias to self.{child_name}.{attribute_name}''' if doc is None else doc)

def alias_key_of(dict_attribute_name, key, *, default=NO_VALUE, setdefault_value=NO_VALUE, doc=None):
    '''returns a property which is an alias to obj.dict_attribute_name[key].
    if doc is None, use doc=f'alias to self.{dict_attribute_name}[{key!r}]'.
    includes getter, setter, and deleter methods.

    if setting value to UNSET, delete the key from the dict instead.

    default: any object
        if provided (not NO_VALUE), then getter returns self.dict_attribute_name.get(key, default).
    setdefault_value: any object
        if provided (not NO_VALUE), then getter returns self.dict_attribute_name.setdefault(key, setdefault_value).
    '''
    if default is not NO_VALUE and setdefault_value is not NO_VALUE:
        raise InputConflictError('cannot provide both default and setdefault_value.')
    if default is not NO_VALUE:
        def getter(self):
            return getattr(self, dict_attribute_name).get(key, default)
    elif setdefault_value is not NO_VALUE:
        def getter(self):
            return getattr(self, dict_attribute_name).setdefault(key, setdefault_value)
    else:
        def getter(self):
            return getattr(self, dict_attribute_name)[key]
    def deleter(self):
        del getattr(self, dict_attribute_name)[key]
    def setter(self, value):
        if value is UNSET:
            deleter(self)
        else:
            getattr(self, dict_attribute_name)[key] = value
    doc = f'''alias to self.{dict_attribute_name}[{key!r}]''' if doc is None else doc
    return property(getter, setter, deleter, doc=doc)

def alias_in(cls, attr, new_attr):
    '''sets cls.new_attr to be an alias for cls.attr.'''
    setattr(cls, new_attr, alias(attr))


''' --------------------- Other properties --------------------- '''

def weakref_property_simple(internal_attr, doc=None):
    '''defines a property which behaves like the value it contains, but is actually a weakref.
    stores internally at internal_attr. Also set self.{internal_attr}_is_weakref = True.
    Setting the value actually creates a weakref. Getting the value calls the weakref.
    Note: if failing to create weakref due to TypeError,
        (e.g. "TypeError: cannot create weak reference to 'int' object")
        then just store the value itself. Also set self.{internal_attr}_is_weakref = False.
    '''
    internal_attr_is_weakref = f'{internal_attr}_is_weakref'
    @format_docstring(attr=internal_attr)
    def get_attr(self):
        '''gets self.{attr}(), or just self.{attr} if not self.{attr}_is_weakref.'''
        self_attr = getattr(self, internal_attr)
        if getattr(self, internal_attr_is_weakref):
            return self_attr()
        else:
            return self_attr

    @format_docstring(attr=internal_attr)
    def set_attr(self, val):
        '''sets self.{attr}'''
        try:
            result = weakref.ref(val)
        except TypeError:
            setattr(self, internal_attr_is_weakref, False)
            result = val
        else:
            setattr(self, internal_attr_is_weakref, True)
        setattr(self, internal_attr, result)

    @format_docstring(attr=internal_attr)
    def del_attr(self):
        '''deletes self.{attr}'''
        delattr(self, internal_attr)
    
    return property(get_attr, set_attr, del_attr, doc)

def simple_property(internal_name, *, doc=None, default=NO_VALUE, setable=True, delable=True):
    '''return a property with a setter and getter method for internal_name.
    if 'default' provided (i.e., not NO_VALUE):
        - getter will have this default, if attr has not been set.
    setable: bool
        whether to allow this attribute to be set (i.e., define fset.)
    delable: bool
        whether to allow this attribute to be set (i.e., define fdel.)
    '''
    if default is NO_VALUE:
        def getter(self):
            return getattr(self, internal_name)
    else:
        def getter(self):
            return getattr(self, internal_name, default)
    if setable:
        def setter(self, value):
            setattr(self, internal_name, value)
    else:
        setter = None
    if delable:
        def deleter(self):
            delattr(self, internal_name)
    else:
        deleter = None
    return property(getter, setter, deleter, doc=doc)

def simple_setdefault_property(internal_name, setdefault, *, doc=None):
    '''return a property with a setter and getter method for internal_name.
    setdefault: callable of 0 arguments
        called to set value of internal_name when getter is called but internal_name is not set.
        E.g., setdefault = lambda: dict().

    Benefits include:
        - no need to initialize internal_name in __init__.
        - if this property is never used, setdefault is never called.
        - if internal_name's value is deleted, and this property is accessed later,
            setdefault will be called, instead of causing a crash.
        - the value can be adjusted after it is set, and the getter will give the new value.
            E.g. setdefault = lambda: dict(); self.attr['a'] = 5; self.attr --> dict(a=5);
            c.f. property(lambda: dict()); self.attr['a'] = 5; self.attr --> dict()
    '''
    def getter(self):
        try:
            return getattr(self, internal_name)
        except AttributeError:
            result = setdefault()
            setattr(self, internal_name, result)
            return result
    def setter(self, value):
        setattr(self, internal_name, value)
    def deleter(self):
        delattr(self, internal_name)
    return property(getter, setter, deleter, doc=doc)

def simple_setdefaultvia_property(internal_name, setdefaultvia, *, doc=None):
    '''return a property with a setter and getter method for internal_name.
    setdefaultvia: str
        self.internal_name = self.setdefaultvia(), when setting value of internal_name.
            This occurs whenever when getter is called but internal_name is not set.

    similar to simple_setdefault_property, except here the default is set via a method call,
        from a method in the object where this property is defined,
        instead of via a setdefault callable of 0 arguments.
    '''
    def getter(self):
        try:
            return getattr(self, internal_name)
        except AttributeError:
            pass  # handled below, to avoid stacked error message in case setdefaultvia fails.
        setdefault = getattr(self, setdefaultvia)
        result = setdefault()
        setattr(self, internal_name, result)
        return result
    def setter(self, value):
        setattr(self, internal_name, value)
    def deleter(self):
        delattr(self, internal_name)
    return property(getter, setter, deleter, doc=doc)

def simple_tuple_property(*internal_names, doc=None, default=NO_VALUE):
    '''return a property which refers to a tuple of internal names.
    if 'default' provided (i.e., not NO_VALUE):
        - getter will have this default, if attr has not been set.
        - setter will do nothing if value is default.
        This applies to each name in internal_names, individually.
    '''
    if default is NO_VALUE:
        def getter(self):
            return tuple(getattr(self, name) for name in internal_names)
        def setter(self, value):
            for name, val in zip(internal_names, value):
                setattr(self, name, val)
    else:
        def getter(self):
            return tuple(getattr(self, name, default) for name in internal_names)
        def setter(self, value):
            for name, val in zip(internal_names, value):
                if val is not default:
                    setattr(self, name, val)
    def deleter(self):
        for name in internal_names:
            delattr(self, name)
    return property(getter, setter, deleter, doc=doc)

def elementwise_property(attr, *, as_array=True, doc=None, default=NO_VALUE):
    '''return property which returns tuple(element.attr for element in self).

    as_array: bool, default True
        return np.array of result instead of list.
    doc: None or str
        the docstring for this property
    default: any value, default NO_VALUE
        if provided, use this for any element missing the 'attr' attribute, instead of crashing.

    The property also supports setting values, e.g.:
        self.attr = ['a', 'b', 'c', 'd'] sets self[0].attr='a', self[1].attr='b', etc.
        self.attr = 'common_val' sets self[0].attr='common_val', self[1].attr='common_val', etc.
    NOTE: to avoid ambiguity, the only non-"common" values are lists and tuples;
        all other types will be treated as "common" (hence, set the same value for each element).

    This property does not support deleting values.
    '''
    def getter(self):
        if default is NO_VALUE:
            result = tuple(getattr(el, attr) for el in self)
        else:
            result = tuple(getattr(el, attr, default) for el in self)
        if as_array:
            result = np.array(result)
        return result
    def setter(self, value):
        if isinstance(value, (list, tuple)):
            for el, val in zip(self, value):
                setattr(el, attr, val)
        else:
            for el in self:
                setattr(el, attr, value)
    return property(getter, setter, doc=doc)

def simple_cachef_property(internal_attr, f_attr, *, doc=None):
    '''return a property which returns the result of calling f_attr, possibly cached.
    internal_attr: str
        the attribute to store the result of f_attr.
    f_attr: str
        the attribute to call to get the value to cache.
    doc: None or str
        docstring for the property.
        None --> "result of self.f_attr(), possibly cached.
            Use self.f_attr() if you want to force a recalculation."
    '''
    def getter(self):
        try:
            return getattr(self, internal_attr)
        except AttributeError:
            result = getattr(self, f_attr)()
            setattr(self, internal_attr, result)
            return result
    def deleter(self):
        '''deletes the cached value if it exists.'''
        if hasattr(self, internal_attr):
            delattr(self, internal_attr)
    if doc is None:
        doc = f'''result of self.{f_attr}(), possibly cached.
        Use self.{f_attr}() if you want to force a recalculation.'''
    return property(getter, fdel=deleter, doc=doc)
