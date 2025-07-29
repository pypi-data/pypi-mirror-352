// Transcrypt'ed from Python, 2024-06-22 19:22:25
var logging = {};
var re = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_re__ from './re.js';
__nest__ (re, '', __module_re__);
import * as __module_logging_handlers__ from './logging.handlers.js';
__nest__ (logging, 'handlers', __module_logging_handlers__);
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
var __all__ = dict ({get BaseConfigurator () {return BaseConfigurator;}, set BaseConfigurator (value) {BaseConfigurator = value;}, get DEFAULT_LOGGING_CONFIG_PORT () {return DEFAULT_LOGGING_CONFIG_PORT;}, set DEFAULT_LOGGING_CONFIG_PORT (value) {DEFAULT_LOGGING_CONFIG_PORT = value;}, get DictConfigurator () {return DictConfigurator;}, set DictConfigurator (value) {DictConfigurator = value;}, get IDENTIFIER () {return IDENTIFIER;}, set IDENTIFIER (value) {IDENTIFIER = value;}, get RESET_ERROR () {return RESET_ERROR;}, set RESET_ERROR (value) {RESET_ERROR = value;}, get UnresolvableError () {return UnresolvableError;}, set UnresolvableError (value) {UnresolvableError = value;}, get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get _create_formatters () {return _create_formatters;}, set _create_formatters (value) {_create_formatters = value;}, get _handle_existing_loggers () {return _handle_existing_loggers;}, set _handle_existing_loggers (value) {_handle_existing_loggers = value;}, get _install_loggers () {return _install_loggers;}, set _install_loggers (value) {_install_loggers = value;}, get _listener () {return _listener;}, set _listener (value) {_listener = value;}, get _resolvables () {return _resolvables;}, set _resolvables (value) {_resolvables = value;}, get _resolve () {return _resolve;}, set _resolve (value) {_resolve = value;}, get _strip_spaces () {return _strip_spaces;}, set _strip_spaces (value) {_strip_spaces = value;}, get addResolvable () {return addResolvable;}, set addResolvable (value) {addResolvable = value;}, get dictConfig () {return dictConfig;}, set dictConfig (value) {dictConfig = value;}, get dictConfigClass () {return dictConfigClass;}, set dictConfigClass (value) {dictConfigClass = value;}, get fileConfig () {return fileConfig;}, set fileConfig (value) {fileConfig = value;}, get listen () {return listen;}, set listen (value) {listen = value;}, get stopListening () {return stopListening;}, set stopListening (value) {stopListening = value;}, get thread () {return thread;}, set thread (value) {thread = value;}, get valid_ident () {return valid_ident;}, set valid_ident (value) {valid_ident = value;}});
var __name__ = 'logging.config';
export var thread = null;
export var DEFAULT_LOGGING_CONFIG_PORT = 9030;
export var RESET_ERROR = 1;
export var _listener = null;
export var fileConfig = function (fname, defaults, disable_existing_loggers) {
	if (typeof defaults == 'undefined' || (defaults != null && defaults.hasOwnProperty ("__kwargtrans__"))) {;
		var defaults = null;
	};
	if (typeof disable_existing_loggers == 'undefined' || (disable_existing_loggers != null && disable_existing_loggers.hasOwnProperty ("__kwargtrans__"))) {;
		var disable_existing_loggers = true;
	};
	var __except0__ = NotImplementedError ('No Filesystem to read file config from');
	__except0__.__cause__ = null;
	throw __except0__;
};
export var UnresolvableError =  __class__ ('UnresolvableError', [Exception], {
	__module__: __name__,
});
export var _resolvables = dict ({'logging.StreamHandler': logging.StreamHandler, 'logging.Formatter': logging.Formatter, 'logging.Filter': logging.Filter});
export var addResolvable = function (py_name, obj) {
	if (__in__ (py_name, _resolvables.py_keys ())) {
		var __except0__ = KeyError ('Resolvable by name {} already exists'.format (py_name));
		__except0__.__cause__ = null;
		throw __except0__;
	}
	if (obj === null) {
		var __except0__ = ValueError ('Resolvable cannot be None');
		__except0__.__cause__ = null;
		throw __except0__;
	}
	_resolvables [py_name] = obj;
};
export var _resolve = function (py_name) {
	if (__in__ (py_name, _resolvables)) {
		return _resolvables [py_name];
	}
	else {
		var __except0__ = UnresolvableError ('class {} is not resolvable in logging.config');
		__except0__.__cause__ = null;
		throw __except0__;
	}
};
export var _strip_spaces = function (alist) {
	return map ((function __lambda__ (x) {
		return x.strip ();
	}), alist);
};
export var _create_formatters = function (cp) {
	var flist = cp ['formatters'] ['keys'];
	if (!(len (flist))) {
		return dict ({});
	}
	var flist = flist.py_split (',');
	var flist = _strip_spaces (flist);
	var formatters = dict ({});
	for (var form of flist) {
		var sectname = 'formatter_{}'.format (form);
		var fs = cp.py_get (sectname, 'format', __kwargtrans__ ({raw: true, fallback: null}));
		var dfs = cp.py_get (sectname, 'datefmt', __kwargtrans__ ({raw: true, fallback: null}));
		var stl = cp.py_get (sectname, 'style', __kwargtrans__ ({raw: true, fallback: '{'}));
		var c = logging.Formatter;
		var class_name = cp [sectname].py_get ('class');
		if (class_name) {
			var c = _resolve (class_name);
		}
		var f = c (fs, dfs, stl);
		formatters [form] = f;
	}
	return formatters;
};
export var _handle_existing_loggers = function (existing, child_loggers, disable_existing) {
	var root = logging.root;
	for (var log of existing) {
		var logger = root.manager.loggerDict [log];
		if (__in__ (log, child_loggers)) {
			logger.level = logging.NOTSET;
			logger.handlers = [];
			logger.propagate = true;
		}
		else {
			logger.disabled = disable_existing;
		}
	}
};
export var _install_loggers = function (cp, handlers, disable_existing) {
	var llist = cp ['loggers'] ['keys'];
	var llist = llist.py_split (',');
	var llist = list (map ((function __lambda__ (x) {
		return x.strip ();
	}), llist));
	llist.remove ('root');
	var section = cp ['logger_root'];
	var root = logging.root;
	var log = root;
	if (__in__ ('level', section)) {
		var level = section ['level'];
		log.setLevel (level);
	}
	for (var h of root.handlers.__getslice__ (0, null, 1)) {
		root.removeHandler (h);
	}
	var hlist = section ['handlers'];
	if (len (hlist)) {
		var hlist = hlist.py_split (',');
		var hlist = _strip_spaces (hlist);
		for (var hand of hlist) {
			log.addHandler (handlers [hand]);
		}
	}
	var existing = list (root.manager.loggerDict.py_keys ());
	existing.py_sort ();
	var child_loggers = [];
	for (var log of llist) {
		var section = cp ['logger_{}'.format (log)];
		var qn = section ['qualname'];
		var propagate = section.getint ('propagate', __kwargtrans__ ({fallback: 1}));
		var logger = logging.getLogger (qn);
		if (__in__ (qn, existing)) {
			var i = existing.index (qn) + 1;
			var prefixed = qn + '.';
			var pflen = len (prefixed);
			var num_existing = len (existing);
			while (i < num_existing) {
				if (existing [i].__getslice__ (0, pflen, 1) == prefixed) {
					child_loggers.append (existing [i]);
				}
				i++;
			}
			existing.remove (qn);
		}
		if (__in__ ('level', section)) {
			var level = section ['level'];
			logger.setLevel (level);
		}
		for (var h of logger.handlers.__getslice__ (0, null, 1)) {
			logger.removeHandler (h);
		}
		logger.propagate = propagate;
		logger.disabled = 0;
		var hlist = section ['handlers'];
		if (len (hlist)) {
			var hlist = hlist.py_split (',');
			var hlist = _strip_spaces (hlist);
			for (var hand of hlist) {
				logger.addHandler (handlers [hand]);
			}
		}
	}
	_handle_existing_loggers (existing, child_loggers, disable_existing);
};
export var IDENTIFIER = re.compile ('^[a-z_][a-z0-9_]*$', re.I);
export var valid_ident = function (s) {
	var m = IDENTIFIER.match (s);
	if (!(m)) {
		var __except0__ = ValueError ('Not a valid Python identifier: {}'.format (str (s)));
		__except0__.__cause__ = null;
		throw __except0__;
	}
	return true;
};
export var BaseConfigurator =  __class__ ('BaseConfigurator', [object], {
	__module__: __name__,
	CONVERT_PATTERN: re.compile ('^([a-z]+)://(.*)$'),
	WORD_PATTERN: re.compile ('^\\s*(\\w+)\\s*'),
	DOT_PATTERN: re.compile ('^\\.\\s*(\\w+)\\s*'),
	INDEX_PATTERN: re.compile ('^\\[\\s*(\\w+)\\s*\\]\\s*'),
	DIGIT_PATTERN: re.compile ('^\\d+$'),
	value_converters: dict ({'ext': 'ext_convert', 'cfg': 'cfg_convert'}),
	importer: null,
	get __init__ () {return __get__ (this, function (self, config) {
		self.config = config;
	});},
	get resolve () {return __get__ (this, function (self, s) {
		return _resolve (s);
	});},
	get ext_convert () {return __get__ (this, function (self, value) {
		return self.resolve (value);
	});},
	get cfg_convert () {return __get__ (this, function (self, value) {
		var rest = value;
		var m = self.WORD_PATTERN.match (rest);
		if (m === null) {
			var __except0__ = ValueError ('Unable to convert {}'.format (value));
			__except0__.__cause__ = null;
			throw __except0__;
		}
		else {
			var rest = rest.__getslice__ (m.end (), null, 1);
			var d = self.config [m.groups () [0]];
			while (rest) {
				var m = self.DOT_PATTERN.match (rest);
				if (m) {
					var d = d [m.groups () [0]];
				}
				else {
					var m = self.INDEX_PATTERN.match (rest);
					if (m) {
						var idx = m.groups () [0];
						if (!(self.DIGIT_PATTERN.match (idx))) {
							var d = d [idx];
						}
						else {
							try {
								var n = int (idx);
								var d = d [n];
							}
							catch (__except0__) {
								if (isinstance (__except0__, py_TypeError)) {
									var d = d [idx];
								}
								else {
									throw __except0__;
								}
							}
						}
					}
				}
				if (m) {
					var rest = rest.__getslice__ (m.end (), null, 1);
				}
				else {
					var __except0__ = ValueError ('Unable to convert {} at {}'.format (str (value), str (rest)));
					__except0__.__cause__ = null;
					throw __except0__;
				}
			}
		}
		return d;
	});},
	get convert () {return __get__ (this, function (self, value) {
		if (isinstance (value, str)) {
			var m = self.CONVERT_PATTERN.match (value);
			if (m) {
				var d = m.groupdict ();
				var prefix = d [1];
				var converter = self.value_converters.py_get (prefix, null);
				if (converter) {
					var __except0__ = NotImplementedError ('Converters Not Well Tested!');
					__except0__.__cause__ = null;
					throw __except0__;
				}
			}
		}
		return value;
	});},
	get configure_custom () {return __get__ (this, function (self, config) {
		var c = self.convert (config.py_pop ('()'));
		if (!(callable (c))) {
			var c = self.resolve (c);
		}
		var props = config.py_pop ('.', null);
		var data = (function () {
			var __accu0__ = [];
			for (var k of config.py_keys ()) {
				if (valid_ident (k)) {
					__accu0__.append (tuple ([k, self.convert (config [k])]));
				}
			}
			return __accu0__;
		}) ();
		var kwargs = dict (data);
		var result = c (__kwargtrans__ (kwargs));
		if (props) {
			for (var [py_name, value] of props.py_items ()) {
				setattr (result, py_name, value);
			}
		}
		return result;
	});},
	get as_tuple () {return __get__ (this, function (self, value) {
		if (isinstance (value, list)) {
			var value = tuple (value);
		}
		return value;
	});}
});
export var DictConfigurator =  __class__ ('DictConfigurator', [BaseConfigurator], {
	__module__: __name__,
	get configure () {return __get__ (this, function (self) {
		var config = self.config;
		var version = self.convert (config.py_get ('version', null));
		if (version != 1) {
			var __except0__ = ValueError ('Unsupported version: {}'.format (config ['version']));
			__except0__.__cause__ = null;
			throw __except0__;
		}
		var incremental = self.convert (config.py_pop ('incremental', false));
		var EMPTY_DICT = dict ({});
		logging._acquireLock ();
		try {
			if (incremental) {
				var handlers = self.convert (config.py_get ('handlers', EMPTY_DICT));
				for (var py_name of handlers.py_keys ()) {
					if (!__in__ (py_name, logging._handlers)) {
						var __except0__ = ValueError ('No handler found with name {}'.format (py_name));
						__except0__.__cause__ = null;
						throw __except0__;
					}
					else {
						try {
							var handler = logging._handlers [py_name];
							var hconfig = self.convert (handlers [py_name]);
							var level = self.convert (hconfig.py_get ('level', null));
							if (level) {
								handler.setLevel (logging._checkLevel (level));
							}
						}
						catch (__except0__) {
							if (isinstance (__except0__, Exception)) {
								var e = __except0__;
								var __except1__ = ValueError ('Unable to configure handler {}'.format (py_name));
								__except1__.__cause__ = e;
								throw __except1__;
							}
							else {
								throw __except0__;
							}
						}
					}
				}
				var loggers = self.convert (config.py_get ('loggers', EMPTY_DICT));
				for (var py_name of loggers.py_keys ()) {
					try {
						self.configure_logger (py_name, self.convert (loggers [py_name]), true);
					}
					catch (__except0__) {
						if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure logger {}'.format (py_name));
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
				var root = self.convert (config.py_get ('root', null));
				if (root) {
					try {
						self.configure_root (root, true);
					}
					catch (__except0__) {
						if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure root logger');
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
			}
			else {
				var disable_existing = config.py_pop ('disable_existing_loggers', true);
				logging._handlers.py_clear ();
				logging._handlerList.__setslice__ (0, null, null, []);
				var formatters = self.convert (config.py_get ('formatters', EMPTY_DICT));
				for (var py_name of formatters.py_keys ()) {
					try {
						var fmtConfig = self.convert (formatters.py_get (py_name));
						formatters [py_name] = self.configure_formatter (fmtConfig);
					}
					catch (__except0__) {
						if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure formatter {}'.format (py_name));
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
				var filters = self.convert (config.py_get ('filters', EMPTY_DICT));
				for (var py_name of filters.py_keys ()) {
					try {
						var filtConfig = self.convert (filters.py_get (py_name));
						filters [py_name] = self.configure_filter (filtConfig);
					}
					catch (__except0__) {
						if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure filter {}'.format (py_name));
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
				var handlers = self.convert (config.py_get ('handlers', EMPTY_DICT));
				var deferred = [];
				for (var py_name of sorted (handlers.py_keys ())) {
					try {
						var handlerConfig = self.convert (handlers.py_get (py_name));
						var handler = self.configure_handler (handlerConfig);
						handler.py_name = py_name;
						handlers [py_name] = handler;
					}
					catch (__except0__) {
						if (isinstance (__except0__, UnresolvableError)) {
							var exc = __except0__;
							var __except1__ = exc;
							__except1__.__cause__ = null;
							throw __except1__;
						}
						else if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							if (__in__ ('target not configured yet', str (e.__cause__))) {
								deferred.append (py_name);
							}
							else {
								var __except1__ = ValueError ('Unable to config handler {}'.format (py_name));
								__except1__.__cause__ = e;
								throw __except1__;
							}
						}
						else {
							throw __except0__;
						}
					}
				}
				for (var py_name of deferred) {
					try {
						var handlerConfig = self.convert (handlers.py_get (py_name));
						var handler = self.configure_handler (handlerConfig);
						handler.py_name = py_name;
						handlers [py_name] = handler;
					}
					catch (__except0__) {
						if (isinstance (__except0__, UnresolvableError)) {
							var exc = __except0__;
							var __except1__ = exc;
							__except1__.__cause__ = null;
							throw __except1__;
						}
						else if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure handler {}'.format (py_name));
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
				var root = logging.root;
				var existing = list (root.manager.loggerDict.py_keys ());
				existing.py_sort ();
				var child_loggers = [];
				var loggers = self.convert (config.py_get ('loggers', EMPTY_DICT));
				for (var py_name of loggers.py_keys ()) {
					if (__in__ (py_name, existing)) {
						var i = existing.index (py_name) + 1;
						var prefixed = py_name + '.';
						var pflen = len (prefixed);
						var num_existing = len (existing);
						while (i < num_existing) {
							if (existing [i].__getslice__ (0, pflen, 1) == prefixed) {
								child_loggers.append (existing [i]);
							}
							i++;
						}
						existing.remove (py_name);
					}
					try {
						var loggerConfig = loggers.py_get (py_name);
						self.configure_logger (py_name, loggerConfig);
					}
					catch (__except0__) {
						if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure logger {}'.format (py_name));
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
				_handle_existing_loggers (existing, child_loggers, disable_existing);
				var root = self.convert (config.py_get ('root', null));
				if (root) {
					try {
						self.configure_root (root);
					}
					catch (__except0__) {
						if (isinstance (__except0__, Exception)) {
							var e = __except0__;
							var __except1__ = ValueError ('Unable to configure root logger');
							__except1__.__cause__ = e;
							throw __except1__;
						}
						else {
							throw __except0__;
						}
					}
				}
			}
		}
		finally {
			logging._releaseLock ();
		}
	});},
	get configure_formatter () {return __get__ (this, function (self, config) {
		if (__in__ ('()', config.py_keys ())) {
			var factory = self.convert (config ['()']);
			try {
				var result = self.configure_custom (config);
			}
			catch (__except0__) {
				if (isinstance (__except0__, py_TypeError)) {
					var te = __except0__;
					if (!__in__ ("'format'", str (te))) {
						var __except1__ = te;
						__except1__.__cause__ = null;
						throw __except1__;
					}
					config ['fmt'] = self.convert (config.py_pop ('format'));
					config ['()'] = factory;
					var result = self.configure_custom (config);
				}
				else {
					throw __except0__;
				}
			}
		}
		else {
			var fmt = self.convert (config.py_get ('format', null));
			var dfmt = self.convert (config.py_get ('datefmt', null));
			var style = self.convert (config.py_get ('style', '{'));
			var cname = self.convert (config.py_get ('class', null));
			if (!(cname)) {
				var c = logging.Formatter;
			}
			else {
				var c = _resolve (cname);
			}
			var result = c (fmt, dfmt, style);
		}
		return result;
	});},
	get configure_filter () {return __get__ (this, function (self, config) {
		if (__in__ ('()', config.py_keys ())) {
			var result = self.configure_custom (config);
		}
		else {
			var py_name = self.convert (config.py_get ('name', ''));
			var result = logging.Filter (py_name);
		}
		return result;
	});},
	get add_filters () {return __get__ (this, function (self, filterer, filters) {
		for (var f of filters) {
			try {
				filterer.addFilter (self.config ['filters'] [f]);
			}
			catch (__except0__) {
				if (isinstance (__except0__, Exception)) {
					var e = __except0__;
					var __except1__ = ValueError ('Unable to add filter {}'.format (str (f)));
					__except1__.__cause__ = e;
					throw __except1__;
				}
				else {
					throw __except0__;
				}
			}
		}
	});},
	get configure_handler () {return __get__ (this, function (self, config) {
		var config_copy = dict (config);
		var formatter = self.convert (config.py_pop ('formatter', null));
		if (formatter) {
			try {
				var formatter = self.config ['formatters'] [formatter];
			}
			catch (__except0__) {
				if (isinstance (__except0__, Exception)) {
					var e = __except0__;
					var __except1__ = ValueError ('Unable to set formatter {}'.format (str (formatter)));
					__except1__.__cause__ = e;
					throw __except1__;
				}
				else {
					throw __except0__;
				}
			}
		}
		var level = self.convert (config.py_pop ('level', null));
		var filters = self.convert (config.py_pop ('filters', null));
		if (__in__ ('()', config.py_keys ())) {
			var c = self.convert (config.py_pop ('()'));
			if (!(callable (c))) {
				var c = self.resolve (c);
			}
			var factory = c;
		}
		else {
			var cname = self.convert (config.py_pop ('class'));
			var klass = self.resolve (cname);
			var factory = klass;
		}
		var props = self.convert (config.py_pop ('.', null));
		var data = (function () {
			var __accu0__ = [];
			for (var k of config.py_keys ()) {
				if (valid_ident (k)) {
					__accu0__.append (tuple ([k, self.convert (config [k])]));
				}
			}
			return __accu0__;
		}) ();
		var kwargs = dict (data);
		try {
			var result = factory (__kwargtrans__ (kwargs));
		}
		catch (__except0__) {
			if (isinstance (__except0__, py_TypeError)) {
				var te = __except0__;
				if (!__in__ ("'stream'", str (te))) {
					var __except1__ = te;
					__except1__.__cause__ = null;
					throw __except1__;
				}
				kwargs ['strm'] = kwargs.py_pop ('stream');
				var result = factory (__kwargtrans__ (kwargs));
			}
			else {
				throw __except0__;
			}
		}
		if (formatter) {
			result.setFormatter (formatter);
		}
		if (level !== null) {
			result.setLevel (logging._checkLevel (level));
		}
		if (filters) {
			self.add_filters (result, filters);
		}
		if (props) {
			for (var [py_name, value] of props.py_items ()) {
				setattr (result, py_name, value);
			}
		}
		return result;
	});},
	get add_handlers () {return __get__ (this, function (self, logger, handlers) {
		for (var h of handlers) {
			try {
				logger.addHandler (self.config ['handlers'] [h]);
			}
			catch (__except0__) {
				if (isinstance (__except0__, Exception)) {
					var e = __except0__;
					var __except1__ = ValueError ('Unable to add handler {}'.format (str (h)));
					__except1__.__cause__ = e;
					throw __except1__;
				}
				else {
					throw __except0__;
				}
			}
		}
	});},
	get common_logger_config () {return __get__ (this, function (self, logger, config, incremental) {
		if (typeof incremental == 'undefined' || (incremental != null && incremental.hasOwnProperty ("__kwargtrans__"))) {;
			var incremental = false;
		};
		var level = self.convert (config.py_get ('level', null));
		if (level !== null) {
			logger.setLevel (logging._checkLevel (level));
		}
		if (!(incremental)) {
			for (var h of logger.handlers.__getslice__ (0, null, 1)) {
				logger.removeHandler (h);
			}
			var handlers = config.py_get ('handlers', null);
			if (handlers) {
				self.add_handlers (logger, handlers);
			}
			var filters = config.py_get ('filters', null);
			if (filters) {
				self.add_filters (logger, filters);
			}
		}
	});},
	get configure_logger () {return __get__ (this, function (self, py_name, config, incremental) {
		if (typeof incremental == 'undefined' || (incremental != null && incremental.hasOwnProperty ("__kwargtrans__"))) {;
			var incremental = false;
		};
		var logger = logging.getLogger (py_name);
		self.common_logger_config (logger, config, incremental);
		var propagate = self.convert (config.py_get ('propagate', null));
		if (propagate !== null) {
			logger.propagate = propagate;
		}
	});},
	get configure_root () {return __get__ (this, function (self, config, incremental) {
		if (typeof incremental == 'undefined' || (incremental != null && incremental.hasOwnProperty ("__kwargtrans__"))) {;
			var incremental = false;
		};
		var root = logging.getLogger ();
		self.common_logger_config (root, config, incremental);
	});}
});
export var dictConfigClass = DictConfigurator;
export var dictConfig = function (config) {
	dictConfigClass (config).configure ();
};
export var listen = function (port, verify) {
	if (typeof port == 'undefined' || (port != null && port.hasOwnProperty ("__kwargtrans__"))) {;
		var port = DEFAULT_LOGGING_CONFIG_PORT;
	};
	if (typeof verify == 'undefined' || (verify != null && verify.hasOwnProperty ("__kwargtrans__"))) {;
		var verify = null;
	};
	var __except0__ = NotImplementedError ();
	__except0__.__cause__ = null;
	throw __except0__;
};
export var stopListening = function () {
	// pass;
};

//# sourceMappingURL=logging.config.map