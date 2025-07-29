// Transcrypt'ed from Python, 2024-06-22 19:22:21
var logging = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
var __all__ = dict ({get TestHandler () {return TestHandler;}, set TestHandler (value) {TestHandler = value;}, get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get resetLogging () {return resetLogging;}, set resetLogging (value) {resetLogging = value;}});
var __name__ = 'utils';
export var TestHandler =  __class__ ('TestHandler', [logging.Handler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, test, lvl) {
		if (arguments.length) {
			var __ilastarg0__ = arguments.length - 1;
			if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
				var __allkwargs0__ = arguments [__ilastarg0__--];
				for (var __attrib0__ in __allkwargs0__) {
					switch (__attrib0__) {
						case 'self': var self = __allkwargs0__ [__attrib0__]; break;
						case 'test': var test = __allkwargs0__ [__attrib0__]; break;
						case 'lvl': var lvl = __allkwargs0__ [__attrib0__]; break;
					}
				}
			}
		}
		else {
		}
		logging.Handler.__init__ (self, lvl);
		self._test = test;
	});},
	get emit () {return __get__ (this, function (self, record) {
		if (arguments.length) {
			var __ilastarg0__ = arguments.length - 1;
			if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
				var __allkwargs0__ = arguments [__ilastarg0__--];
				for (var __attrib0__ in __allkwargs0__) {
					switch (__attrib0__) {
						case 'self': var self = __allkwargs0__ [__attrib0__]; break;
						case 'record': var record = __allkwargs0__ [__attrib0__]; break;
					}
				}
			}
		}
		else {
		}
		var msg = self.format (record);
		self._test.check (msg);
	});}
});
export var resetLogging = function () {
	if (arguments.length) {
		var __ilastarg0__ = arguments.length - 1;
		if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
			var __allkwargs0__ = arguments [__ilastarg0__--];
			for (var __attrib0__ in __allkwargs0__) {
			}
		}
	}
	else {
	}
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logging._resetLogging ();
	}
};

//# sourceMappingURL=utils.map