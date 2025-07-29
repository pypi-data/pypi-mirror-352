// Transcrypt'ed from Python, 2024-06-22 19:22:21
var logging = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {TestHandler, resetLogging} from './utils.js';
import * as hdlr from './logging.handlers.js';
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
export {TestHandler, resetLogging, hdlr};
var __all__ = dict ({get BetterBufferingHandler () {return BetterBufferingHandler;}, set BetterBufferingHandler (value) {BetterBufferingHandler = value;}, get DemoBufferingFormatter () {return DemoBufferingFormatter;}, set DemoBufferingFormatter (value) {DemoBufferingFormatter = value;}, get TestBuffering () {return TestBuffering;}, set TestBuffering (value) {TestBuffering = value;}, get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'buffering_tests';
export var DemoBufferingFormatter =  __class__ ('DemoBufferingFormatter', [logging.BufferingFormatter], {
	__module__: __name__,
	get formatHeader () {return __get__ (this, function (self, records) {
		return '------ {} Records ------\n'.format (len (records));
	});}
});
export var BetterBufferingHandler =  __class__ ('BetterBufferingHandler', [hdlr.MemoryHandler], {
	__module__: __name__,
	get flush () {return __get__ (this, function (self) {
		self.acquire ();
		try {
			if (self.target) {
				if (self.formatter) {
					var aggregate = self.formatter.format (self.buffer);
					self.target.handle (aggregate);
				}
				else {
					var __except0__ = NotImplementedError ();
					__except0__.__cause__ = null;
					throw __except0__;
				}
			}
			self.buffer = [];
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				__except0__.__cause__ = null;
				throw __except0__;
			}
			else {
				throw __except0__;
			}
		}
		finally {
			self.release ();
		}
	});}
});
export var TestBuffering =  __class__ ('TestBuffering', [logging.Handler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, test) {
		logging.Handler.__init__ (self);
		self._test = test;
	});},
	get emit () {return __get__ (this, function (self, record) {
		var msg = record;
		self._test.check (msg);
	});}
});
export var run = function (test) {
	resetLogging ();
	var thdlr = TestBuffering (test);
	thdlr.setLevel (2);
	var bufHdlr = BetterBufferingHandler (3);
	var linefmt = logging.Formatter ('{levelname}:{message}', __kwargtrans__ ({style: '{'}));
	var fmt = DemoBufferingFormatter (linefmt);
	bufHdlr.setFormatter (fmt);
	bufHdlr.setTarget (thdlr);
	var root = logging.getLogger ();
	root.setLevel (5);
	root.addHandler (bufHdlr);
	root.debug ('One');
	root.info ('Dos');
	root.warning ('Tres');
	root.debug ('One');
	root.info ('Dos');
	root.warning ('Tres');
	root.debug ('One');
	root.info ('Dos');
	root.warning ('Tres');
	root.debug ('One');
	root.error ('Dos');
	root.error ('Tres');
};

//# sourceMappingURL=buffering_tests.map