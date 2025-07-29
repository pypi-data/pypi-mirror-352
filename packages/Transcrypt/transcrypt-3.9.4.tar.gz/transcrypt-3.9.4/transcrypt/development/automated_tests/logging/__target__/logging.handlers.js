// Transcrypt'ed from Python, 2024-06-22 19:22:24
var logging = {};
var re = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_re__ from './re.js';
__nest__ (re, '', __module_re__);
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
var __all__ = dict ({get AJAXHandler () {return AJAXHandler;}, set AJAXHandler (value) {AJAXHandler = value;}, get BufferingHandler () {return BufferingHandler;}, set BufferingHandler (value) {BufferingHandler = value;}, get DEFAULT_HTTP_LOGGING_PORT () {return DEFAULT_HTTP_LOGGING_PORT;}, set DEFAULT_HTTP_LOGGING_PORT (value) {DEFAULT_HTTP_LOGGING_PORT = value;}, get DEFAULT_SOAP_LOGGING_PORT () {return DEFAULT_SOAP_LOGGING_PORT;}, set DEFAULT_SOAP_LOGGING_PORT (value) {DEFAULT_SOAP_LOGGING_PORT = value;}, get DEFAULT_TCP_LOGGING_PORT () {return DEFAULT_TCP_LOGGING_PORT;}, set DEFAULT_TCP_LOGGING_PORT (value) {DEFAULT_TCP_LOGGING_PORT = value;}, get DEFAULT_UDP_LOGGING_PORT () {return DEFAULT_UDP_LOGGING_PORT;}, set DEFAULT_UDP_LOGGING_PORT (value) {DEFAULT_UDP_LOGGING_PORT = value;}, get MemoryHandler () {return MemoryHandler;}, set MemoryHandler (value) {MemoryHandler = value;}, get QueueHandler () {return QueueHandler;}, set QueueHandler (value) {QueueHandler = value;}, get SYSLOG_TCP_PORT () {return SYSLOG_TCP_PORT;}, set SYSLOG_TCP_PORT (value) {SYSLOG_TCP_PORT = value;}, get SYSLOG_UDP_PORT () {return SYSLOG_UDP_PORT;}, set SYSLOG_UDP_PORT (value) {SYSLOG_UDP_PORT = value;}, get _MIDNIGHT () {return _MIDNIGHT;}, set _MIDNIGHT (value) {_MIDNIGHT = value;}, get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get threading () {return threading;}, set threading (value) {threading = value;}});
var __name__ = 'logging.handlers';
export var threading = null;
export var DEFAULT_TCP_LOGGING_PORT = 9020;
export var DEFAULT_UDP_LOGGING_PORT = 9021;
export var DEFAULT_HTTP_LOGGING_PORT = 9022;
export var DEFAULT_SOAP_LOGGING_PORT = 9023;
export var SYSLOG_UDP_PORT = 514;
export var SYSLOG_TCP_PORT = 514;
export var _MIDNIGHT = (24 * 60) * 60;
export var AJAXHandler =  __class__ ('AJAXHandler', [logging.Handler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, url, method, headers) {
		if (typeof method == 'undefined' || (method != null && method.hasOwnProperty ("__kwargtrans__"))) {;
			var method = 'GET';
		};
		if (typeof headers == 'undefined' || (headers != null && headers.hasOwnProperty ("__kwargtrans__"))) {;
			var headers = [];
		};
		logging.Handler.__init__ (self);
		var method = method.upper ();
		if (!__in__ (method, ['GET', 'POST'])) {
			var __except0__ = ValueError ('method must be GET or POST');
			__except0__.__cause__ = null;
			throw __except0__;
		}
		self.url = url;
		self.method = method;
		self.headers = headers;
	});},
	get mapLogRecord () {return __get__ (this, function (self, record) {
		return record.__dict__;
	});},
	get urlencode () {return __get__ (this, function (self, msg) {
		var repl = function (m) {
			var v = m.group (0);
			var v = ord (v);
			var hVal = v.toString (16);
			if (len (hVal) == 1) {
				var hVal = '0' + hVal;
			}
			var hVal = '%' + hVal;
			return hVal;
		};
		var p = re.compile ("[^-A-Za-z0-9\\-\\._~:/?#[\\]@!$&'()\\*+,;=`]");
		var ret = p.sub (repl, msg);
		return ret;
	});},
	get emit () {return __get__ (this, function (self, record) {
		if (py_typeof (record) === str) {
			var msg = record;
		}
		else {
			var msg = self.format (record);
		}
		try {
			var url = self.url;
			var data = null;
			if (self.method == 'GET') {
				if (url.find ('?') >= 0) {
					var sep = '&';
				}
				else {
					var sep = '?';
				}
				var url = url + '{}msg={}'.format (sep, msg);
				var url = self.urlencode (url);
			}
			else {
				var data = 'msg={}'.format (msg);
				var data = self.urlencode (data);
			}
			var ajaxCallback = function () {
				return 0;
			};
			var conn = null;
			var errObj = null;
			
			                       try {
			                         conn = new(XMLHttpRequest || ActiveXObject)('MSXML2.XMLHTTP.3.0');
			                       } catch( err ) {
			                         errObj = err
			                       }
			                       
			if (errObj !== null) {
				var __except0__ = Exception ('Failed Create AJAX Request', errObj);
				__except0__.__cause__ = null;
				throw __except0__;
			}
			if (conn === null) {
				var __except0__ = Exception ('Invalid Ajax Object');
				__except0__.__cause__ = null;
				throw __except0__;
			}
			conn.open (self.method, url, 1);
			for (var [key, val] of self.headers) {
				conn.setRequestHeader (key, val);
			}
			conn.onreadystatechange = ajaxCallback;
			conn.send (data);
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				self.handleError (record);
			}
			else {
				throw __except0__;
			}
		}
	});}
});
export var BufferingHandler =  __class__ ('BufferingHandler', [logging.Handler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, capacity) {
		logging.Handler.__init__ (self);
		self.capacity = capacity;
		self.buffer = [];
	});},
	get shouldFlush () {return __get__ (this, function (self, record) {
		return len (self.buffer) >= self.capacity;
	});},
	get emit () {return __get__ (this, function (self, record) {
		self.buffer.append (record);
		if (self.shouldFlush (record)) {
			self.flush ();
		}
	});},
	get flush () {return __get__ (this, function (self) {
		self.acquire ();
		try {
			self.buffer = [];
		}
		finally {
			self.release ();
		}
	});},
	get close () {return __get__ (this, function (self) {
		try {
			self.flush ();
		}
		finally {
			logging.Handler.close (self);
		}
	});}
});
export var MemoryHandler =  __class__ ('MemoryHandler', [BufferingHandler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, capacity, flushLevel, target, flushOnClose) {
		if (typeof flushLevel == 'undefined' || (flushLevel != null && flushLevel.hasOwnProperty ("__kwargtrans__"))) {;
			var flushLevel = logging.ERROR;
		};
		if (typeof target == 'undefined' || (target != null && target.hasOwnProperty ("__kwargtrans__"))) {;
			var target = null;
		};
		if (typeof flushOnClose == 'undefined' || (flushOnClose != null && flushOnClose.hasOwnProperty ("__kwargtrans__"))) {;
			var flushOnClose = true;
		};
		BufferingHandler.__init__ (self, capacity);
		self.flushLevel = flushLevel;
		self.target = target;
		self.flushOnClose = flushOnClose;
	});},
	get shouldFlush () {return __get__ (this, function (self, record) {
		return len (self.buffer) >= self.capacity || record.levelno >= self.flushLevel;
	});},
	get setTarget () {return __get__ (this, function (self, target) {
		self.target = target;
	});},
	get flush () {return __get__ (this, function (self) {
		self.acquire ();
		try {
			if (self.target) {
				for (var record of self.buffer) {
					self.target.handle (record);
				}
				self.buffer = [];
			}
		}
		finally {
			self.release ();
		}
	});},
	get close () {return __get__ (this, function (self) {
		try {
			if (self.flushOnClose) {
				self.flush ();
			}
		}
		finally {
			self.acquire ();
			try {
				self.target = null;
				BufferingHandler.close (self);
			}
			finally {
				self.release ();
			}
		}
	});}
});
export var QueueHandler =  __class__ ('QueueHandler', [logging.Handler], {
	__module__: __name__,
	get __init__ () {return __get__ (this, function (self, queue) {
		logging.Handler.__init__ (self);
		var __except0__ = NotImplementedError ('No Working Implementation Yet');
		__except0__.__cause__ = null;
		throw __except0__;
	});},
	get enqueue () {return __get__ (this, function (self, record) {
		self.queue.put_nowait (record);
	});},
	get prepare () {return __get__ (this, function (self, record) {
		self.format (record);
		record.msg = record.message;
		record.args = null;
		record.exc_info = null;
		return record;
	});},
	get emit () {return __get__ (this, function (self, record) {
		try {
			self.enqueue (self.prepare (record));
		}
		catch (__except0__) {
			if (isinstance (__except0__, Exception)) {
				self.handleError (record);
			}
			else {
				throw __except0__;
			}
		}
	});}
});

//# sourceMappingURL=logging.handlers.map