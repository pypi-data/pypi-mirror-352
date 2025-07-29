// Transcrypt'ed from Python, 2024-06-22 19:17:32
var logging = {};
var warnings = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
import * as __module_warnings__ from './warnings.js';
__nest__ (warnings, '', __module_warnings__);
var __all__ = dict ({get TestHandler () {return TestHandler;}, set TestHandler (value) {TestHandler = value;}, get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'basic_tests';
export var TestHandler =  __class__ ('TestHandler', [logging.Handler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, test, level) {
		logging.Handler.__init__ (self, level);
		self._test = test;
	});},
	get emit () {return __get__ (this, function (self, record) {
		var msg = self.format (record);
		var content = msg.py_split ('\n');
		if (len (content) > 0) {
			var checkMsg = content [0].rstrip ();
			self._test.check (checkMsg);
		}
		else {
			self._test.check ('Invalid Content in Warning message');
		}
	});}
});
export var run = function (test) {
	warnings.warn_explicit ('Console Test Message', UserWarning, 'basic_tests.py', 37, 'asdf', dict ({}));
	logging.captureWarnings (true);
	var logger = logging.getLogger ('py.warnings');
	logger.setLevel (10);
	var hdlr = TestHandler (test, 10);
	logger.addHandler (hdlr);
	var msgStr = 'Test Message';
	var reg = dict ({});
	warnings.warn_explicit (msgStr, UserWarning, 'basic_tests.py', 50, 'asdf', reg);
	warnings.warn_explicit (msgStr, UserWarning, 'basic_tests.py', 53, 'asdf', reg);
	warnings.warn_explicit (msgStr, UserWarning, 'basic_tests.py', 57, 'asdf', reg);
	warnings.warn_explicit (msgStr, UserWarning, 'basic_tests.py', 57, 'asdf', reg);
	warnings.warn_explicit (msgStr + ' blarg', UserWarning, 'basic_tests.py', 57, 'asdf', reg);
	warnings.warn_explicit (msgStr + ' blarg', UserWarning, 'basic_tests.py', 57, 'asdf', reg);
	var reg = dict ({});
	var CustomWarning = __class__ ('CustomWarning', [Warning], {
		__module__: __name__,
	});
	if (__envir__.executor_name == __envir__.transpiler_name) {
		warnings.addWarningCategory (CustomWarning);
	}
	warnings.filterwarnings ('error', __kwargtrans__ ({category: CustomWarning}));
	test.check (test.expectException ((function __lambda__ () {
		return warnings.warn_explicit ('This is a custom msg', CustomWarning, 'basic_tests.py', 91, 'zxcv', reg);
	})));
	warnings.filterwarnings ('once', __kwargtrans__ ({category: RuntimeWarning}));
	var msg = 'This is a once message - should not occur more than once';
	warnings.warn_explicit (msg, RuntimeWarning, 'basic_tests.py', 100, 'trew', reg);
	for (var i = 0; i < 10; i++) {
		warnings.warn_explicit (msg, RuntimeWarning, 'basic_tests.py', 102 + i, 'qwerqwer' + str (i), reg);
	}
	warnings.filterwarnings ('always', __kwargtrans__ ({message: 'asdf', category: DeprecationWarning}));
	warnings.warn_explicit (' no Message Here ', DeprecationWarning, 'basic_tests.py', 112, 'itururue', reg);
	warnings.warn_explicit ('Warning - asdf of qwer', DeprecationWarning, 'basic_tests.py', 112, 'itururue', reg);
	warnings.warn_explicit ('Warning - asdfqwer of qwer', DeprecationWarning, 'basic_tests.py', 112, 'itururue', reg);
	warnings.warn_explicit ('asdf of qwer', DeprecationWarning, 'basic_tests.py', 112, 'itururue', reg);
	warnings.warn_explicit ('asdf of qwer', UserWarning, 'basic_tests.py', 112, 'itururue', reg);
	warnings.warn_explicit (UserWarning ('asdf'), null, 'basic_tests.py', 1234, 'qwerqwe', reg);
};

//# sourceMappingURL=basic_tests.map