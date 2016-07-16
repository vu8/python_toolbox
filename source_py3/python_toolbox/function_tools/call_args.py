# Copyright 2009-2017 Ram Rachum.
# This program is distributed under the MIT license.

import abc

from python_toolbox import cute_inspect
from python_toolbox import cheat_hashing
from python_toolbox.sleek_reffing import SleekRef, CuteSleekValueDict


class BaseCallArgs(metaclass=abc.ABCMeta):
    '''
    blocktododoc
    A bunch of call args with a sleekref to them.
    
    "Call args" is a mapping of which function arguments get which values.
    For example, for a function:
    
        def f(a, b=2):
            pass
            
    The calls `f(1)`, `f(1, 2)` and `f(b=2, a=1)` all share the same call args.
    
    All the argument values are sleekreffed to avoid memory leaks. (See
    documentation of `python_toolbox.sleek_reffing.SleekRef` for more details.)
    '''
    
    make_ref = None 
    make_dict = None
    hash_function = None
    
    # What if we one of the args gets gc'ed before this SCA gets added to the
    # dictionary? It will render this SCA invalid, but we'll still be in the
    # dict. So make note to user: Always keep reference to args and kwargs
    # until the SCA gets added to the dict.
    def __init__(self, containing_dict, function, *args, **kwargs):
        '''
        Construct the `BaseCallArgs`.
        
        `containing_dict` is the `dict` we'll try to remove ourselves from when
        one of our sleekrefs dies. `function` is the function for which we
        calculate call args from `*args` and `**kwargs`.
        '''
        
        self.containing_dict = containing_dict
        '''
        `dict` we'll try to remove ourselves from when 1 of our sleekrefs dies.
        '''
        
        args_spec = cute_inspect.getargspec(function)
        star_args_name, star_kwargs_name = (args_spec.varargs,
                                            args_spec.keywords)
        
        call_args = cute_inspect.getcallargs(function, *args, **kwargs)
        del args, kwargs
        
        self.star_args_refs = ()
        
        star_args = call_args.pop(star_args_name, ()) if star_args_name else ()
        self.star_args_refs = tuple(self.make_ref(star_arg) for
                                                         star_arg in star_args)
        
        star_kwargs = (call_args.pop(star_kwargs_name, {}) if
                                                      star_kwargs_name else {})
        self.star_kwargs_refs = self.make_dict(star_kwargs)
        
        self.args_refs = self.make_dict(call_args)
        '''Mapping from argument name to value.'''
        
        # In the future the `.args`, `.star_args` and `.star_kwargs` attributes
        # may change, so we must record the hash now:
        self._hash = self.hash_function(
            (
                type(self),
                self.args,
                self.star_args,
                self.star_kwargs
            )
        )
        
    args = abc.abstractproperty()
    '''The arguments.'''
    
    star_args = abc.abstractproperty()
    '''Extraneous arguments. (i.e. `*args`.)'''
    
    star_kwargs = abc.abstractproperty()
    '''Extraneous keyword arguments. (i.e. `*kwargs`.)'''
          
        
    def __hash__(self):
        return self._hash

    
    def __eq__(self, other):
        return (
            type(self) == type(other) and 
            self.args == other.args and 
            self.star_args == other.star_args and
            self.star_kwargs == other.star_kwargs
        )

    
    def __ne__(self, other):
        return not self == other
    
    
class CallArgs(BaseCallArgs):
    make_ref = lambda self, thing: thing
    hash_function = lambda self, thing: hash(thing)
    def make_dict(self, items):
        from python_toolbox import nifty_collections
        return nifty_collections.FrozenDict(items)
        
    

    args = property(lambda self: self.args_refs)
    '''The arguments.'''
    
    star_args = property(lambda self: self.star_args_refs)
    '''Extraneous arguments. (i.e. `*args`.)'''
    
    star_kwargs = property(lambda self: self.star_kwargs_refs)
    '''Extraneous keyword arguments. (i.e. `*kwargs`.)'''
        
class SleekCallArgs(BaseCallArgs):
    make_ref = lambda self, thing: SleekRef(thing, self.destroy)
    make_dict = lambda self, items: CuteSleekValueDict(self.destroy, items)
    hash_function = lambda self, thing: cheat_hashing.cheat_hash(thing)
        
    def destroy(self, _=None):
        '''Delete ourselves from our containing `dict`.'''
        if self.containing_dict:
            try:
                del self.containing_dict[self]
            except KeyError:
                pass
        
    args = property(lambda self: dict(self.args_refs))
    '''The arguments.'''
    
    star_args = property(
        lambda self:
            tuple((star_arg_ref() for star_arg_ref in self.star_args_refs))
    )
    '''Extraneous arguments. (i.e. `*args`.)'''
    
    star_kwargs = property(lambda self: dict(self.star_kwargs_refs))
    '''Extraneous keyword arguments. (i.e. `*kwargs`.)'''
      