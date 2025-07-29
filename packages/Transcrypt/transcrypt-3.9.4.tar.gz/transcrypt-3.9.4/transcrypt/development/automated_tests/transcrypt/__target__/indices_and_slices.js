// Transcrypt'ed from Python, 2025-05-30 20:15:55
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _copy, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, complex, delattr, dict, dir, divmod, filter, float, format, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {py_copy} from './copy.js';
export {py_copy};
var __all__ = dict ({get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'indices_and_slices';
export var run = function (autoTester) {
	var all = range (32);
	autoTester.check (all);
	autoTester.check (all.__getslice__ (8, 24, 1));
	autoTester.check (all.__getslice__ (8, 24, 2));
	var aList = [3, 4, 7, 8];
	autoTester.check (aList);
	aList.__setslice__ (4, 4, null, [9, 10]);
	autoTester.check (aList);
	aList.__setslice__ (2, 2, null, [5, 6]);
	autoTester.check (aList);
	aList.__setslice__ (0, 0, null, [1, 2]);
	autoTester.check (aList);
	aList.__setslice__ (0, null, 2, (function () {
		var __accu0__ = [];
		for (var x = 0; x < 10; x++) {
			if (__mod__ (x, 2)) {
				__accu0__.append (x + 0.001);
			}
		}
		return __accu0__;
	}) ());
	autoTester.check (aList);
	var allLists = [[], ['a', 'b', 'c', 'd', 'e', 'f', 'g'], ['a', 'b', 'c', 'd'], 'abcdefg', 'abc'];
	for (var aList of allLists) {
		autoTester.check (aList);
		autoTester.check (aList.__getslice__ (null, null, 1));
		autoTester.check (aList.__getslice__ (null, null, 1));
		autoTester.check (aList.__getslice__ (null, null, 1));
		autoTester.check (aList.__getslice__ (null, null, -(1)));
		autoTester.check (aList.__getslice__ (-(1), -(8), -(1)));
		autoTester.check (aList.__getslice__ (null, null, 2));
		autoTester.check (aList.__getslice__ (null, null, -(2)));
		autoTester.check (aList.__getslice__ (null, 4, 1));
		autoTester.check (aList.__getslice__ (null, 4, -(1)));
		autoTester.check (aList.__getslice__ (4, null, 1));
		autoTester.check (aList.__getslice__ (4, null, 1));
		autoTester.check (aList.__getslice__ (4, null, 1));
		autoTester.check (aList.__getslice__ (4, null, -(1)));
		autoTester.check (aList.__getslice__ (1, 4, 1));
		autoTester.check (aList.__getslice__ (1, 4, 1));
		autoTester.check (aList.__getslice__ (1, 4, 2));
		autoTester.check (aList.__getslice__ (1, 4, -(2)));
		autoTester.check (aList.__getslice__ (4, 1, -(2)));
		autoTester.check (aList.__getslice__ (4, 1, 1));
		autoTester.check (aList.__getslice__ (-(1), -(4), 1));
		autoTester.check (aList.__getslice__ (-(4), -(1), 1));
		autoTester.check (aList.__getslice__ (-(4), -(1), 2));
		autoTester.check (aList.__getslice__ (-(4), -(1), -(2)));
		autoTester.check (aList.__getslice__ (9, -(9), 1));
		autoTester.check (aList.__getslice__ (-(9), 9, 1));
		autoTester.check (aList.__getslice__ (9, -(9), -(1)));
		autoTester.check (aList.__getslice__ (-(9), 9, -(1)));
		autoTester.check (aList.__getslice__ (-(9), 9, -(1)));
		autoTester.check ('zero step slice', autoTester.expectException ((function __lambda__ () {
			return print (aList.__getslice__ (null, null, 0));
		})));
	}
	var sample_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
	autoTester.check ('old:', sample_list);
	var new1 = sample_list.py_copy ();
	autoTester.check ('new1:', new1);
	var new2 = sample_list.__getslice__ (null, null, 1);
	autoTester.check ('new2:', new2);
	var new3 = list (sample_list);
	autoTester.check ('new3:', new3);
	new1 [1] = 'x';
	new2 [2] = 'y';
	new3 [3] = 'z';
	autoTester.check ('updated:', sample_list, new1, new2, new3);
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 3, null, ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 1, null, ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (0, null, null, ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 5, null, ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 5, null, 'xyz');
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (0, 5, 2, ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	var aTest1 = function (test_list) {
		test_list.__setslice__ (1, 5, 2, ['x', 'y', 'z']);
	};
	autoTester.check ('Invalid slice assignment', autoTester.expectException ((function __lambda__ () {
		return aTest1 (aList);
	})));
	var aList = py_copy (sample_list);
	aList.__setslice__ (5, 2, -(1), ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (5, 0, -(2), ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 5, null, []);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 5, 1, []);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	var aTest3 = function (test_list) {
		test_list.__setslice__ (5, 1, -(1), []);
	};
	autoTester.check ('Invalid slice assignment', autoTester.expectException ((function __lambda__ () {
		return aTest3 (aList);
	})));
	var aList = py_copy (sample_list);
	var aTest4 = function (test_list) {
		test_list.__setslice__ (5, 1, -(1), ['x', 'y', 'z']);
	};
	autoTester.check ('Invalid slice assignment', autoTester.expectException ((function __lambda__ () {
		return aTest4 (aList);
	})));
	var aList = py_copy (sample_list);
	aList.__setslice__ (1, 5, -(1), []);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	var aTest2 = function (test_list) {
		test_list.__setslice__ (0, 5, -(1), ['x', 'y', 'z']);
	};
	autoTester.check ('Invalid slice assignment', autoTester.expectException ((function __lambda__ () {
		return aTest2 (aList);
	})));
	var aList = py_copy (sample_list);
	aList.__setslice__ (0, 7, 3, ['x', 'y', 'z']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	var aTest5 = function (test_list) {
		test_list.__setslice__ (1, 7, 3, ['x', 'y', 'z']);
	};
	autoTester.check ('Invalid slice assignment', autoTester.expectException ((function __lambda__ () {
		return aTest5 (aList);
	})));
	var aList = py_copy (sample_list);
	var aTest6 = function (test_list) {
		test_list.__setslice__ (7, 0, -(3), ['x', 'y', 'z']);
	};
	autoTester.check ('Invalid slice assignment', autoTester.expectException ((function __lambda__ () {
		return aTest6 (aList);
	})));
	var aList = py_copy (sample_list);
	aList.__setslice__ (7, 0, -(3), ['x', 'y']);
	autoTester.check (aList);
	var aList = py_copy (sample_list);
	var aTest7 = function (test_list) {
		test_list.__setslice__ (7, 0, 0, ['x', 'y', 'z']);
	};
	autoTester.check ('zero step slice', autoTester.expectException ((function __lambda__ () {
		return aTest7 (aList);
	})));
	var aList = ['a', 'b', 'c'];
	aList.remove ('b');
	autoTester.check (aList);
	aList.remove ('a');
	autoTester.check (aList);
	autoTester.check ('not in list', autoTester.expectException ((function __lambda__ () {
		return aList.remove ('d');
	})));
	autoTester.check (aList);
	aList.remove ('c');
	autoTester.check (aList);
	autoTester.check ('not in list', autoTester.expectException ((function __lambda__ () {
		return aList.remove ('c');
	})));
	autoTester.check (aList);
	var aList = ['a', 'b', 'c', 'd', 'e', 'f'];
	aList.py_pop (2);
	autoTester.check (aList);
	aList.py_pop (0);
	autoTester.check (aList);
	aList.py_pop (-(3));
	autoTester.check (aList);
	aList.py_pop (-(1));
	autoTester.check (aList);
	autoTester.check ('out of range', autoTester.expectException ((function __lambda__ () {
		return aList.py_pop (-(3));
	})));
	autoTester.check ('out of range', autoTester.expectException ((function __lambda__ () {
		return aList.py_pop (3);
	})));
	aList.py_pop ();
	autoTester.check (aList);
	aList.py_pop ();
	autoTester.check (aList);
	autoTester.check ('empty list', autoTester.expectException ((function __lambda__ () {
		return aList.py_pop ();
	})));
	autoTester.check ('empty list', autoTester.expectException ((function __lambda__ () {
		return aList.py_pop (-(1));
	})));
	autoTester.check ('empty list', autoTester.expectException ((function __lambda__ () {
		return aList.py_pop (0);
	})));
	autoTester.check ('empty list', autoTester.expectException ((function __lambda__ () {
		return aList.py_pop (1);
	})));
	var allLists = [['a', 'b', 'c'], 'abc'];
	for (var aList of allLists) {
		(function () {
			var __accu0__ = autoTester;
			return __call__ (__accu0__.check, __accu0__, 'valid index', (function () {
				var __accu1__ = autoTester;
				return __call__ (__accu1__.expectException, __accu1__, (function __lambda__ () {
					return __getitem__ (aList, 1);
				}));
			}) ());
		}) ();
		(function () {
			var __accu0__ = autoTester;
			return __call__ (__accu0__.check, __accu0__, __getitem__ (aList, 1));
		}) ();
		(function () {
			var __accu0__ = autoTester;
			return __call__ (__accu0__.check, __accu0__, 'valid index', (function () {
				var __accu1__ = autoTester;
				return __call__ (__accu1__.expectException, __accu1__, (function __lambda__ () {
					return __getitem__ (aList, __neg__ (2));
				}));
			}) ());
		}) ();
		(function () {
			var __accu0__ = autoTester;
			return __call__ (__accu0__.check, __accu0__, __getitem__ (aList, __neg__ (2)));
		}) ();
		(function () {
			var __accu0__ = autoTester;
			return __call__ (__accu0__.check, __accu0__, 'invalid index', (function () {
				var __accu1__ = autoTester;
				return __call__ (__accu1__.expectException, __accu1__, (function __lambda__ () {
					return __getitem__ (aList, 3);
				}));
			}) ());
		}) ();
		(function () {
			var __accu0__ = autoTester;
			return __call__ (__accu0__.check, __accu0__, 'invalid index', (function () {
				var __accu1__ = autoTester;
				return __call__ (__accu1__.expectException, __accu1__, (function __lambda__ () {
					return __getitem__ (aList, __neg__ (4));
				}));
			}) ());
		}) ();
		autoTester.check (aList [1]);
	}
};

//# sourceMappingURL=indices_and_slices.map