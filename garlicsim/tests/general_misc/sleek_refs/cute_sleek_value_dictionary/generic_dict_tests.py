import UserDict
import random
import string
import gc
import weakref

from garlicsim.general_misc.third_party import unittest2

from garlicsim.general_misc.sleek_refs import CuteSleekValueDictionary


null_callback = lambda: None


class GenericDictTest(unittest2.TestCase):
    def test_constructor(self):
        # calling built-in types without argument must return empty
        self.assertEqual(
            CuteSleekValueDictionary(null_callback),
            CuteSleekValueDictionary(null_callback)
        )
        self.assertIsNot(
            CuteSleekValueDictionary(null_callback),
            CuteSleekValueDictionary(null_callback)
        )

    def test_bool(self):
        self.assertIs(
            not CuteSleekValueDictionary(null_callback),
            True
        )
        self.assertTrue(CuteSleekValueDictionary(null_callback, {1: 2}))
        self.assertIs(bool(CuteSleekValueDictionary(null_callback)), False)
        self.assertIs(
            bool(CuteSleekValueDictionary(null_callback, {1: 2})),
            True
        )

    def test_keys(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertEqual(d.keys(), [])
        d = CuteSleekValueDictionary(null_callback, {'a': 1, 'b': 2})
        k = d.keys()
        self.assertTrue(d.has_key('a'))
        self.assertTrue(d.has_key('b'))

        self.assertRaises(TypeError, d.keys, None)

    def test_values(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertEqual(d.values(), [])
        d = CuteSleekValueDictionary(null_callback, {1:2})
        self.assertEqual(d.values(), [2])

        self.assertRaises(TypeError, d.values, None)

    def test_items(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertEqual(d.items(), [])

        d = CuteSleekValueDictionary(null_callback, {1:2})
        self.assertEqual(d.items(), [(1, 2)])

        self.assertRaises(TypeError, d.items, None)

    def test_has_key(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertFalse(d.has_key('a'))
        d = CuteSleekValueDictionary(null_callback, {'a': 1, 'b': 2})
        k = d.keys()
        k.sort()
        self.assertEqual(k, ['a', 'b'])

        self.assertRaises(TypeError, d.has_key)

    def test_contains(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertNotIn('a', d)
        self.assertFalse('a' in d)
        self.assertTrue('a' not in d)
        d = CuteSleekValueDictionary(null_callback, {'a': 1, 'b': 2})
        self.assertIn('a', d)
        self.assertIn('b', d)
        self.assertNotIn('c', d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertEqual(len(d), 0)
        d = CuteSleekValueDictionary(null_callback, {'a': 1, 'b': 2})
        self.assertEqual(len(d), 2)

    def test_getitem(self):
        d = CuteSleekValueDictionary(null_callback, {'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        del d['b']
        self.assertEqual(d, CuteSleekValueDictionary(null_callback, {'a': 4, 'c': 3}))

        self.assertRaises(TypeError, d.__getitem__)

        class BadEq(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 24

        d = CuteSleekValueDictionary(null_callback)
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)

    def test_clear(self):
        d = CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3})
        d.clear()
        self.assertEqual(d, CuteSleekValueDictionary(null_callback))

        self.assertRaises(TypeError, d.clear, None)

    def test_update(self):
        d = CuteSleekValueDictionary(null_callback)
        d.update(CuteSleekValueDictionary(null_callback, {1:100}))
        d.update(CuteSleekValueDictionary(null_callback, {2:20}))
        d.update(CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3}))
        self.assertEqual(d, CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3}))

        d.update()
        self.assertEqual(d, CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3}))

        self.assertRaises((TypeError, AttributeError), d.update, None)

        class SimpleUserDict:
            def __init__(self):
                self.d = CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3})
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3}))

        class Exc(Exception): pass

        d.clear()
        class FailingUserDict:
            def keys(self):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        return self
                    def next(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc
                return BogonIter()
            def __getitem__(self, key):
                return key
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        return self
                    def next(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        raise StopIteration
                return BogonIter()
            def __getitem__(self, key):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        class badseq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()

        self.assertRaises(Exc, CuteSleekValueDictionary(null_callback).update, badseq())

        self.assertRaises(ValueError, CuteSleekValueDictionary(null_callback).update, [(1, 2, 3)])

    def test_fromkeys(self):
        self.assertEqual(dict.fromkeys('abc'), CuteSleekValueDictionary(null_callback, {'a':None, 'b':None, 'c':None}))
        d = CuteSleekValueDictionary(null_callback)
        self.assertIsNot(d.fromkeys('abc'), d)
        self.assertEqual(d.fromkeys('abc'), CuteSleekValueDictionary(null_callback, {'a':None, 'b':None, 'c':None}))
        self.assertEqual(d.fromkeys((4,5),0), CuteSleekValueDictionary(null_callback, {4:0, 5:0}))
        self.assertEqual(d.fromkeys([]), CuteSleekValueDictionary(null_callback))
        def g():
            yield 1
        self.assertEqual(d.fromkeys(g()), CuteSleekValueDictionary(null_callback, {1:None}))
        self.assertRaises(TypeError, CuteSleekValueDictionary(null_callback).fromkeys, 3)
        class dictlike(dict): pass
        self.assertEqual(dictlike.fromkeys('a'), CuteSleekValueDictionary(null_callback, {'a':None}))
        self.assertEqual(dictlike().fromkeys('a'), CuteSleekValueDictionary(null_callback, {'a':None}))
        self.assertIsInstance(dictlike.fromkeys('a'), dictlike)
        self.assertIsInstance(dictlike().fromkeys('a'), dictlike)
        class mydict(dict):
            def __new__(cls):
                return UserDict.UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, CuteSleekValueDictionary(null_callback, {'a':None, 'b':None}))
        self.assertIsInstance(ud, UserDict.UserDict)
        self.assertRaises(TypeError, dict.fromkeys)

        class Exc(Exception): pass

        class baddict1(dict):
            def __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()

        self.assertRaises(Exc, dict.fromkeys, BadSeq())

        class baddict2(dict):
            def __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

        # test fast path for dictionary inputs
        d = CuteSleekValueDictionary(null_callback, zip(range(6), range(6)))
        self.assertEqual(dict.fromkeys(d, 0), CuteSleekValueDictionary(null_callback, zip(range(6), [0]*6)))

    def test_copy(self):
        d = CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), CuteSleekValueDictionary(null_callback, {1:1, 2:2, 3:3}))
        self.assertEqual(CuteSleekValueDictionary(null_callback).copy(), CuteSleekValueDictionary(null_callback))
        self.assertRaises(TypeError, d.copy, None)

    def test_get(self):
        d = CuteSleekValueDictionary(null_callback)
        self.assertIs(d.get('c'), None)
        self.assertEqual(d.get('c', 3), 3)
        d = CuteSleekValueDictionary(null_callback, {'a': 1, 'b': 2})
        self.assertIs(d.get('c'), None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

    def test_setdefault(self):
        # dict.setdefault()
        d = CuteSleekValueDictionary(null_callback)
        self.assertIs(d.setdefault('key0'), None)
        d.setdefault('key0', [])
        self.assertIs(d.setdefault('key0'), None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)
        self.assertRaises(TypeError, d.setdefault)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])

    def test_popitem(self):
        # dict.popitem()
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = CuteSleekValueDictionary(null_callback)
                b = CuteSleekValueDictionary(null_callback)
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assertFalse(copymode < 0 and ta != tb)
                self.assertFalse(a)
                self.assertFalse(b)

        d = CuteSleekValueDictionary(null_callback)
        self.assertRaises(KeyError, d.popitem)

    def test_pop(self):
        # Tests for pop with specified key
        d = CuteSleekValueDictionary(null_callback)
        k, v = 'abc', 'def'
        d[k] = v
        self.assertRaises(KeyError, d.pop, 'ghi')

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)

        # verify longs/ints get same value when key > 32 bits
        # (for 64-bit archs).  See SF bug #689659.
        x = 4503599627370496L
        y = 4503599627370496
        h = CuteSleekValueDictionary(null_callback, {x: 'anything', y: 'something else'})
        self.assertEqual(h[x], h[y])

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)

        self.assertRaises(TypeError, d.pop)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    def test_mutatingiteration(self):
        # changing dict size during iteration
        d = CuteSleekValueDictionary(null_callback)
        d[1] = 1
        with self.assertRaises(RuntimeError):
            for i in d:
                d[i+1] = 1

    def test_le(self):
        self.assertFalse(CuteSleekValueDictionary(null_callback) < CuteSleekValueDictionary(null_callback))
        self.assertFalse(CuteSleekValueDictionary(null_callback, {1: 2}) < CuteSleekValueDictionary(null_callback, {1L: 2L}))

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 42

        d1 = CuteSleekValueDictionary(null_callback, {BadCmp(): 1})
        d2 = CuteSleekValueDictionary(null_callback, {1: 1})

        with self.assertRaises(Exc):
            d1 < d2

    def test_missing(self):
        # Make sure dict doesn't have a __missing__ method
        self.assertFalse(hasattr(dict, "__missing__"))
        self.assertFalse(hasattr(CuteSleekValueDictionary(null_callback), "__missing__"))
        # Test several cases:
        # (D) subclass defines __missing__ method returning a value
        # (E) subclass defines __missing__ method raising RuntimeError
        # (F) subclass sets __missing__ instance variable (no effect)
        # (G) subclass doesn't define __missing__ at a all
        class D(dict):
            def __missing__(self, key):
                return 42
        d = D(CuteSleekValueDictionary(null_callback, {1: 2, 3: 4}))
        self.assertEqual(d[1], 2)
        self.assertEqual(d[3], 4)
        self.assertNotIn(2, d)
        self.assertNotIn(2, d.keys())
        self.assertEqual(d[2], 42)

        class E(dict):
            def __missing__(self, key):
                raise RuntimeError(key)
        e = E()
        with self.assertRaises(RuntimeError) as c:
            e[42]
        self.assertEqual(c.exception.args, (42,))

        #class F(dict):
            #def __init__(self):
                ## An instance variable __missing__ should have no effect
                #self.__missing__ = lambda key: None
        #f = F()
        #with self.assertRaises(KeyError) as c:
            #f[42]
        #self.assertEqual(c.exception.args, (42,))

        #class G(dict):
            #pass
        #g = G()
        #with self.assertRaises(KeyError) as c:
            #g[42]
        #self.assertEqual(c.exception.args, (42,))

    #def test_tuple_keyerror(self):
        ## SF #1576657
        #d = CuteSleekValueDictionary(null_callback)
        #with self.assertRaises(KeyError) as c:
            #d[(1,)]
        #self.assertEqual(c.exception.args, ((1,),))

    def test_bad_key(self):
        # Dictionary lookups should fail if __cmp__() raises an exception.
        class CustomException(Exception):
            pass

        class BadDictKey:
            def __hash__(self):
                return hash(self.__class__)

            def __cmp__(self, other):
                if isinstance(other, self.__class__):
                    raise CustomException
                return other

        d = CuteSleekValueDictionary(null_callback)
        x1 = BadDictKey()
        x2 = BadDictKey()
        d[x1] = 1
        locals()['CuteSleekValueDictionary'] = CuteSleekValueDictionary
        locals()['null_callback'] = null_callback
        for stmt in ['d[x2] = 2',
                     'z = d[x2]',
                     'x2 in d',
                     'd.has_key(x2)',
                     'd.get(x2)',
                     'd.setdefault(x2, 42)',
                     'd.pop(x2)',
                     'd.update(CuteSleekValueDictionary(null_callback, {x2: 2}))']:
            with self.assertRaises(CustomException):
                exec stmt in locals()

    def test_resize1(self):
        # Dict resizing bug, found by Jack Jansen in 2.2 CVS development.
        # This version got an assert failure in debug build, infinite loop in
        # release build.  Unfortunately, provoking this kind of stuff requires
        # a mix of inserts and deletes hitting exactly the right hash codes in
        # exactly the right order, and I can't think of a randomized approach
        # that would be *likely* to hit a failing case in reasonable time.

        d = CuteSleekValueDictionary(null_callback)
        for i in range(5):
            d[i] = i
        for i in range(5):
            del d[i]
        for i in range(5, 9):  # i==8 was the problem
            d[i] = i

    def test_resize2(self):
        # Another dict resizing bug (SF bug #1456209).
        # This caused Segmentation faults or Illegal instructions.

        class X(object):
            def __hash__(self):
                return 5
            def __eq__(self, other):
                if resizing:
                    d.clear()
                return False
        d = CuteSleekValueDictionary(null_callback)
        resizing = False
        d[X()] = 1
        d[X()] = 2
        d[X()] = 3
        d[X()] = 4
        d[X()] = 5
        # now trigger a resize
        resizing = True
        d[9] = 6

    def test_empty_presized_dict_in_freelist(self):
        # Bug #3537: if an empty but presized dict with a size larger
        # than 7 was in the freelist, it triggered an assertion failure
        with self.assertRaises(ZeroDivisionError):
            d = {'a': 1 // 0, 'b': None, 'c': None, 'd': None, 'e': None,
                 'f': None, 'g': None, 'h': None}
        d = CuteSleekValueDictionary(null_callback)

    
    def test_container_iterator(self):
        # Bug #3680: tp_traverse was not implemented for dictiter objects
        class C(object):
            pass
        iterators = (dict.iteritems, dict.itervalues, dict.iterkeys)
        for i in iterators:
            obj = C()
            ref = weakref.ref(obj)
            container = CuteSleekValueDictionary(null_callback, {obj: 1})
            obj.x = i(container)
            del obj, container
            gc.collect()
            self.assertIs(ref(), None, "Cycle was not collected")
    

    


