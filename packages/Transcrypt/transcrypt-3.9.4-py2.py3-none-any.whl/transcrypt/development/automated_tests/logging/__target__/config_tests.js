// Transcrypt'ed from Python, 2024-06-22 19:22:25
var logging = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_logging_config__ from './logging.config.js';
__nest__ (logging, 'config', __module_logging_config__);
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
import {TestHandler, resetLogging} from './utils.js';
export {TestHandler, resetLogging};
var __all__ = dict ({get TestFilter () {return TestFilter;}, set TestFilter (value) {TestFilter = value;}, get TestFormatter () {return TestFormatter;}, set TestFormatter (value) {TestFormatter = value;}, get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'config_tests';
export var TestFilter =  __class__ ('TestFilter', [logging.Filter], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, modulo) {
		if (arguments.length) {
			var __ilastarg0__ = arguments.length - 1;
			if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
				var __allkwargs0__ = arguments [__ilastarg0__--];
				for (var __attrib0__ in __allkwargs0__) {
					switch (__attrib0__) {
						case 'self': var self = __allkwargs0__ [__attrib0__]; break;
						case 'modulo': var modulo = __allkwargs0__ [__attrib0__]; break;
					}
				}
			}
		}
		else {
		}
		if (modulo <= 0) {
			var __except0__ = ValueError ('Invalid Modulo Value');
			__except0__.__cause__ = null;
			throw __except0__;
		}
		self._modulo = modulo;
		self._cnt = 0;
	});},
	get filter () {return __get__ (this, function (self, record) {
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
		var ret = false;
		self._cnt++;
		if (self._cnt > self._modulo) {
			self._cnt = 0;
			var ret = true;
		}
		return ret;
	});}
});
export var TestFormatter =  __class__ ('TestFormatter', [logging.Formatter], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, format, datefmt, style) {
		if (typeof format == 'undefined' || (format != null && format.hasOwnProperty ("__kwargtrans__"))) {;
			var format = null;
		};
		if (typeof datefmt == 'undefined' || (datefmt != null && datefmt.hasOwnProperty ("__kwargtrans__"))) {;
			var datefmt = null;
		};
		if (typeof style == 'undefined' || (style != null && style.hasOwnProperty ("__kwargtrans__"))) {;
			var style = '{';
		};
		if (arguments.length) {
			var __ilastarg0__ = arguments.length - 1;
			if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
				var __allkwargs0__ = arguments [__ilastarg0__--];
				for (var __attrib0__ in __allkwargs0__) {
					switch (__attrib0__) {
						case 'self': var self = __allkwargs0__ [__attrib0__]; break;
						case 'format': var format = __allkwargs0__ [__attrib0__]; break;
						case 'datefmt': var datefmt = __allkwargs0__ [__attrib0__]; break;
						case 'style': var style = __allkwargs0__ [__attrib0__]; break;
					}
				}
			}
		}
		else {
		}
		logging.Formatter.__init__ (self, format, datefmt, style);
	});},
	get format () {return __get__ (this, function (self, record) {
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
		var msg = logging.Formatter.format (self, record);
		var msg = 'Custom: ' + msg;
		return msg;
	});}
});
export var run = function (test) {
	if (arguments.length) {
		var __ilastarg0__ = arguments.length - 1;
		if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
			var __allkwargs0__ = arguments [__ilastarg0__--];
			for (var __attrib0__ in __allkwargs0__) {
				switch (__attrib0__) {
					case 'test': var test = __allkwargs0__ [__attrib0__]; break;
				}
			}
		}
	}
	else {
	}
	resetLogging ();
	var d = dict ({'version': 1, 'formatters': dict ({'fmt1': dict ({'format': '{levelname}:{asctime}:{name}:{message}', 'datefmt': '%H:%M:%S', 'style': '{'}), 'fmt2': dict ({'format': '{name}_{levelname}_{message}', 'style': '{'}), 'fmt3': dict ({'()': TestFormatter, 'format': '[{name}]_{message}', 'style': '{'})}), 'filters': dict ({'filt1': dict ({'()': TestFilter, 'modulo': 2})}), 'handlers': dict ({'hdlr1': dict ({'class': 'logging.StreamHandler', 'formatter': 'fmt1', 'level': 'DEBUG', 'filters': ['filt1']}), 'hdlr2': dict ({'class': 'utils.TestHandler', 'formatter': 'fmt2', 'filters': [], 'level': 'WARNING', 'test': test, 'lvl': 1}), 'hdlr3': dict ({'class': 'utils.TestHandler', 'formatter': 'fmt3', 'level': 'INFO', 'test': test, 'lvl': 2})}), 'root': dict ({'level': 'INFO', 'handlers': ['hdlr1']}), 'loggers': dict ({'test1': dict ({'level': 30, 'filters': [], 'handlers': ['hdlr2', 'hdlr3']})})});
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logging.config.addResolvable ('utils.TestHandler', TestHandler);
	}
	logging.config.dictConfig (d);
	var tlog = logging.getLogger ('test1');
	test.check (len (tlog.handlers));
	test.check (len (tlog.filters));
	test.check (tlog.level);
	for (var i = 0; i < 10; i++) {
		logging.debug ('1234');
		logging.info ('asdf');
		logging.warning ('ioureoiu');
		logging.error ('jekwejrjek');
		logging.critical ('jlkjelkjwelkr');
		tlog.debug ('1234');
		tlog.info ('asdf');
		tlog.warning ('ioureoiu');
		tlog.error ('jekwejrjek');
		tlog.critical ('jlkjelkjwelkr');
	}
};

//# sourceMappingURL=config_tests.map