// Transcrypt'ed from Python, 2024-06-22 19:22:25
var logging = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {TestHandler, resetLogging} from './utils.js';
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
export {TestHandler, resetLogging};
var __all__ = dict ({get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'basicConfig_tests';
export var run = function (test) {
	resetLogging ();
	var basehdlr = TestHandler (test, 5);
	var fmt = logging.Formatter (__kwargtrans__ ({style: '{'}));
	basehdlr.setFormatter (fmt);
	logging.basicConfig (__kwargtrans__ ({handlers: [basehdlr], level: logging.INFO}));
	var root = logging.getLogger ();
	test.check (root.hasHandlers ());
	test.check (root.level);
	test.check (len (root.handlers));
	var hdlr = root.handlers [0];
	test.check (hdlr.level);
	logging.debug ('Never gonna give you up');
	logging.info ('Never gonna let you go');
	logging.warning ('Never gonna run around and desert you');
	logging.error ('Never gonna make you cry');
	root.setLevel (logging.DEBUG);
	logging.debug ('Never gonna give you up');
	logging.info ('Never gonna let you go');
	logging.warning ('Never gonna run around and desert you');
	logging.error ('Never gonna make you cry');
};

//# sourceMappingURL=basicConfig_tests.map