// Transcrypt'ed from Python, 2025-05-30 20:15:55
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _copy, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, complex, delattr, dict, dir, divmod, filter, float, format, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, pow, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
var __all__ = dict ({get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get canonizeString () {return canonizeString;}, set canonizeString (value) {canonizeString = value;}, get canonizeStringList () {return canonizeStringList;}, set canonizeStringList (value) {canonizeStringList = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'module_builtin';
export var canonizeString = function (aString) {
	if (__envir__.executor_name == 'transcrypt') {
		return aString.py_replace ('\t', '\\t').py_replace ('\n', '\\n').py_replace ('\r', '\\r');
	}
	else {
		return aString;
	}
};
export var canonizeStringList = function (stringList) {
	return (function () {
		var __accu0__ = [];
		for (var aString of stringList) {
			__accu0__.append (canonizeString (aString));
		}
		return __accu0__;
	}) ();
};
export var run = function (autoTester) {
	autoTester.check ('min', min (-(1.1), -(1), -(3)), min ([-(1.1), -(1), -(3)]), min (tuple ([-(1.1), -(1), -(3)])), min ('abc', 'ABC', 'xyz', 'XYZ'), min ('abc', 'ABC', 'xyz', 'XYZ', __kwargtrans__ ({key: (function __lambda__ (v) {
		return v [1];
	})})), min (['abc', 'ABC', 'xyz', 'XYZ']), min ([5, 6, 7, 8, 9], [1, 2, 3, 4], __kwargtrans__ ({key: len})), min ([[5, 6, 7, 8, 9], [1, 2, 3, 4]], __kwargtrans__ ({py_default: [1, 1, 1], key: len})), min ([], __kwargtrans__ ({py_default: 'zzz'})));
	autoTester.check ('max', max (-(1.1), -(1), -(3)), max ([-(1.1), -(1), -(3)]), max (tuple ([-(1.1), -(1), -(3)])), max ('abc', 'ABC', 'xyz', 'XYZ'), max ('abc', 'ABC', 'xyz', 'XYZ', __kwargtrans__ ({key: (function __lambda__ (v) {
		return v [1];
	})})), max (['abc', 'ABC', 'xyz', 'XYZ']), max ([5, 6, 7, 8, 9], [1, 2, 3, 4], __kwargtrans__ ({key: len})), max ([[5, 6, 7, 8, 9], [1, 2, 3, 4]], __kwargtrans__ ({py_default: [1, 1, 1], key: len})), max ([], __kwargtrans__ ({py_default: 'zzz'})));
	autoTester.check ('max', autoTester.expectException ((function __lambda__ () {
		return max ();
	})));
	autoTester.check ('max', autoTester.expectException ((function __lambda__ () {
		return max (1, 2, 3, 4, __kwargtrans__ ({py_default: 5}));
	})));
	autoTester.check ('max', autoTester.expectException ((function __lambda__ () {
		return max (__kwargtrans__ ({py_default: 5}));
	})));
	autoTester.check ('max', autoTester.expectException ((function __lambda__ () {
		return max ([]);
	})));
	autoTester.check ('max', autoTester.expectException ((function __lambda__ () {
		return max ([5, 6, 7, 8, 9], [1, 2, 3, 4], __kwargtrans__ ({py_default: [1, 1, 1], key: len}));
	})));
	autoTester.check ('abs', abs (-(1)), abs (1), abs (0), abs (-(0.1)), abs (0.1));
	autoTester.check ('pow', pow (2, 2), pow (0, 0), pow (1, 0), pow (2, 1), '{}'.format (pow (4, 0.5)));
	autoTester.check ('ord', ord ('a'), ord ('e´' [0]));
	autoTester.check ('chr', chr (97), chr (122), chr (65), chr (90));
	autoTester.check ('round', round (4.006), round (4.006, 2), round (4060, -(2)), round (-(4.006)), round (-(4.006), 2), round (-(4060), -(2)), round (1 / 2.0), round (1 / 2.0, 1), round (1 / 2, 1), round (1 / 3.0, 2), round (-(1) / 2.0), round (-(1) / 2.0, 1), round (-(1) / 2, 1), round (-(1) / 3.0, 2), round (0.5), round (0.51), round (1.5), round (1.51), round (1.51), round (2.5), round (2.59), round (3.5), round (3.59), round (-(0.5)), round (-(0.51)), round (-(1.5)), round (-(1.51)), round (-(1.51)), round (-(2.5)), round (-(2.59)), round (-(3.5)), round (-(3.59)));
	var strings = ['der des dem den die der den die das des dem das', 'an auf hinter ueber    neben vor   zwischen', '\n            durch\n            fuer\n            ohne\n            um\n            bis\n            gegen\n            entlang\n        ', 'eins,zwei,drie,vier,fuenf,sechs,sieben'];
	autoTester.check ('<br><br>split');
	for (var aString of strings) {
		autoTester.check (canonizeString (aString), canonizeStringList (aString.py_split ()), canonizeStringList (aString.py_split (' ')), canonizeStringList (aString.py_split (' ', 4)), canonizeStringList (aString.py_split ('\t')), canonizeStringList (aString.py_split ('\t', 4)), canonizeStringList (aString.py_split ('\n')), canonizeStringList (aString.py_split ('\n', 4)), canonizeStringList (aString.py_split (',')), canonizeStringList (aString.py_split (',', 4)), '<br>');
	}
	autoTester.check ('<br>rsplit');
	for (var aString of strings) {
		autoTester.check (canonizeString (aString), canonizeStringList (aString.rsplit ()), canonizeStringList (aString.rsplit (' ')), canonizeStringList (aString.rsplit (' ', 4)), canonizeStringList (aString.rsplit ('\t')), canonizeStringList (aString.rsplit ('\t', 4)), canonizeStringList (aString.rsplit ('\n')), canonizeStringList (aString.rsplit ('\n', 4)), canonizeStringList (aString.rsplit (',')), canonizeStringList (aString.rsplit (',', 4)), '<br>');
	}
	var lines_to_split = ['', '\n', 'abc\n', 'abc\ndef', 'abc\rdef', 'abc\r\ndef', '\nabc', '\nabc\n', 'abc\ndef\r\nghi\rjkl\n', 'abc\ndef\n\nghi\njkl'];
	autoTester.check ('<br>splitlines');
	for (var line of lines_to_split) {
		autoTester.check (canonizeStringList (line.splitlines ()), canonizeStringList (line.splitlines (true)));
	}
	autoTester.check ('isalpha', ''.isalpha (), '123'.isalpha (), 'abc'.isalpha (), 'abc123'.isalpha ());
	var replace_test = 'abcabcabcabc';
	autoTester.check ('replace', replace_test.py_replace ('c', 'x'), replace_test.py_replace ('c', 'x', -(1)), replace_test.py_replace ('c', 'x', 0), replace_test.py_replace ('c', 'x', 1), replace_test.py_replace ('c', 'x', 2), replace_test.py_replace ('c', 'x', 10));
	autoTester.check ('bin-oct-hex', bin (42), oct (42), hex (42), bin (0), oct (0), hex (0), bin (-(42)), oct (-(42)), hex (-(42)));
	var string_test = 'abcdefghijkl';
	autoTester.check ('startswith', string_test.startswith (''), string_test.startswith ('abcd'), string_test.startswith ('efgh'), string_test.startswith ('efgh', 2), string_test.startswith ('efgh', 4), string_test.startswith ('abcd', 0, 3), string_test.startswith ('abcd', 0, 5), string_test.startswith ('efgh', 4, -(2)), string_test.startswith ('efgh', 4, -(6)), string_test.startswith (tuple (['abc'])), string_test.startswith (tuple (['abc', 'de', 'gh'])), string_test.startswith (tuple (['abc', 'de', 'gh']), 2), string_test.startswith (tuple (['abc', 'de', 'gh']), 3), string_test.startswith (tuple (['abc', 'defgh']), 3, 9), string_test.startswith (tuple (['abc', 'defgh']), 3, 6));
	autoTester.check ('endswith', string_test.endswith (''), string_test.endswith ('ijkl'), string_test.endswith ('efgh'), string_test.endswith ('efgh', 2), string_test.endswith ('abcd', 0, 3), string_test.endswith ('abcd', 0, 4), string_test.endswith ('efgh', 4, -(2)), string_test.endswith ('efgh', 4, -(4)), string_test.endswith (tuple (['ijkl'])), string_test.endswith (tuple (['abc', 'de', 'gh'])), string_test.endswith (tuple (['abc', 'de', 'gh']), 3, -(4)), string_test.endswith (tuple (['abc', 'de', 'gh']), -(6), -(4)), string_test.endswith (tuple (['abc', 'defgh']), -(3), 8), string_test.endswith (tuple (['abc', 'defgh']), -(9), 8));
};

//# sourceMappingURL=module_builtin.map