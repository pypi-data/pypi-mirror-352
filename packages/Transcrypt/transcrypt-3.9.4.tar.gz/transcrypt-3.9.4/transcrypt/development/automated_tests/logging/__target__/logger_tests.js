// Transcrypt'ed from Python, 2024-06-22 19:22:25
var logging = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, complex, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, format, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {TestHandler, resetLogging} from './utils.js';
import * as __module_logging__ from './logging.js';
__nest__ (logging, '', __module_logging__);
export {TestHandler, resetLogging};
var __all__ = dict ({get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get console_test () {return console_test;}, set console_test (value) {console_test = value;}, get formatter_tests () {return formatter_tests;}, set formatter_tests (value) {formatter_tests = value;}, get logger_basics () {return logger_basics;}, set logger_basics (value) {logger_basics = value;}, get logging_api_tests () {return logging_api_tests;}, set logging_api_tests (value) {logging_api_tests = value;}, get placeholder_testing () {return placeholder_testing;}, set placeholder_testing (value) {placeholder_testing = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'logger_tests';
export var logger_basics = function (test) {
	resetLogging ();
	var logger = logging.getLogger ('tester');
	test.check (logger.py_name);
	test.check (logger.level);
	test.check (logger.hasHandlers ());
	test.check (logger.getEffectiveLevel ());
	logger.setLevel (10);
	test.check (logger.level);
	var testLevel = 'USERDEFLEVEL';
	test.check (test.expectException ((function __lambda__ () {
		return logger.setLevel (testLevel);
	})));
	test.check (logging.getLevelName (testLevel));
	for (var i = 0; i < 50; i += 5) {
		test.check (logging.getLevelName (i));
	}
	logging.addLevelName (35, testLevel);
	test.check (logging.getLevelName (testLevel));
	for (var i = 0; i < 50; i += 5) {
		test.check (logging.getLevelName (i));
	}
	for (var i = 0; i < 50; i += 5) {
		test.check (logger.isEnabledFor (i));
	}
	var hdlr = TestHandler (test, 30);
	var fmt = logging.Formatter (__kwargtrans__ ({style: '{'}));
	hdlr.setFormatter (fmt);
	logger.addHandler (hdlr);
	test.check (logger.hasHandlers ());
	logger.debug ('This is a debug message');
	logger.info ('This is an info message');
	logger.warning ('This is a warning message');
	logger.error ('This is an error message');
	logger.critical ('The house is on fire');
	logger.setLevel (0);
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logger.debug ('This is a debug msg {}', 1);
	}
	else {
		logger.debug ('This is a debug msg %d', 1);
	}
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logger.info ('This is an info message: {}', 'blarg');
	}
	else {
		logger.info ('This is an info message: %s', 'blarg');
	}
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logger.warning ('This is a {} warning message in the {}', 'blue', 'barn');
	}
	else {
		logger.warning ('This is a %s warning message in the %s', 'blue', 'barn');
	}
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logger.error ('This is an error message: {} {} {}', 3, '23', 4);
	}
	else {
		logger.error ('This is an error message: %d %s %d', 3, '23', 4);
	}
	logger.critical ('The house is on fire');
	hdlr.setLevel (30);
	logger.debug ('This is a debug msg {}', 1);
	logger.info ('This is an info message: {}', 'blarg');
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logger.warning ('This is a {} warning message in the {}', 'blue', 'barn');
	}
	else {
		logger.warning ('This is a %s warning message in the %s', 'blue', 'barn');
	}
	if (__envir__.executor_name == __envir__.transpiler_name) {
		logger.error ('This is an error message: {} {} {}', 3, '23', 4);
	}
	else {
		logger.error ('This is an error message: %d %s %d', 3, '23', 4);
	}
	logger.critical ('The house is on fire');
};
export var logging_api_tests = function (test) {
	resetLogging ();
	var logger = logging.getLogger ();
	logger.setLevel (20);
	var hdlr = TestHandler (test, 30);
	var fmt = logging.Formatter (__kwargtrans__ ({style: '{'}));
	hdlr.setFormatter (fmt);
	logger.addHandler (hdlr);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
	logger.setLevel (40);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
	hdlr.setLevel (20);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
	hdlr.setLevel (39);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
	hdlr.setLevel (41);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
	hdlr.setLevel (40);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
	logger.setLevel (39);
	logging.critical ('Another Crazy Message!');
	logging.error ('Oh the humanity');
	logging.warning ('Is it hot in here?');
	logging.info ('Big Bird says Hello!');
	logging.debug ('No body gonna see this message');
};
export var formatter_tests = function (test) {
	resetLogging ();
	var logger = logging.getLogger ('fmttest');
	logger.setLevel (10);
	var hdlr = TestHandler (test, 30);
	var fmt = logging.Formatter ('{levelname}:{name}:{message}', __kwargtrans__ ({style: '{'}));
	test.check (fmt.usesTime ());
	hdlr.setFormatter (fmt);
	logger.addHandler (hdlr);
	hdlr.setLevel (30);
	test.check (hdlr.py_name);
	hdlr.py_name = 'Asdf';
	test.check (hdlr.py_name);
	test.check (hdlr.level);
	test.check (logger.hasHandlers ());
	logger.debug ('This is a debug message');
	logger.info ('This is an info message');
	logger.warning ('This is a warning message');
	logger.error ('This is an error message');
	logger.critical ('The house is on fire');
	hdlr.setLevel (0);
	logger.debug ('This is a debug message');
	logger.info ('This is an info message');
	logger.warning ('This is a warning message');
	logger.error ('This is an error message');
	logger.critical ('The house is on fire');
};
export var console_test = function (test) {
	resetLogging ();
	var logger = logging.getLogger ('consoleTest');
	logger.setLevel (10);
	var hdlr = TestHandler (test, 30);
	var fmt = logging.Formatter ('{name}:{message}', __kwargtrans__ ({style: '{'}));
	test.check (fmt.usesTime ());
	hdlr.setFormatter (fmt);
	hdlr.setLevel (20);
	logger.addHandler (hdlr);
	var shdlr = logging.StreamHandler ();
	shdlr.setFormatter (fmt);
	shdlr.setLevel (20);
	logger.addHandler (shdlr);
	logger.debug ('This is a debug message');
	logger.info ('This is an info message');
	logger.warning ('This is a warning message');
	logger.error ('This is an error message');
	logger.critical ('The house is on fire');
	shdlr.setLevel (10);
	logger.debug ('This is a debug message');
	logger.info ('This is an info message');
	logger.warning ('This is a warning message');
	logger.error ('This is an error message');
	logger.critical ('The house is on fire');
	shdlr.setLevel (40);
	logger.debug ('This is a debug message');
	logger.info ('This is an info message');
	logger.warning ('This is a warning message');
	logger.error ('This is an error message');
	logger.critical ('The house is on fire');
};
export var placeholder_testing = function (test) {
	var logger = logging.getLogger ('phtest.middle.testme');
	logger.setLevel (10);
	var hdlr = TestHandler (test, 5);
	var fmt = logging.Formatter ('{levelname}:{name}:{message}', __kwargtrans__ ({style: '{'}));
	hdlr.setFormatter (fmt);
	logger.addHandler (hdlr);
	logger.error ('Gen a message');
	var log2 = logging.getLogger ('phtest.middle');
	log2.setLevel (10);
	log2.addHandler (hdlr);
	log2.info ('This is another message');
	var log3 = logging.getLogger ('phtest');
	log3.setLevel (10);
	log3.addHandler (hdlr);
	log3.info ('Yet another message');
	var logger = logging.getLogger ('mngtest');
	logger.setLevel (10);
	logger.addHandler (hdlr);
	logger.error ('Gen a message 2 - the generating');
	var log2 = logging.getLogger ('mngtest.mid');
	log2.setLevel (10);
	log2.addHandler (hdlr);
	log2.info ('This is another message 2 - the anothering');
	var log3 = logging.getLogger ('mngtest.mid.end');
	log3.setLevel (10);
	log3.addHandler (hdlr);
	log3.info ('Yet another message 2 - the whatever...');
};
export var run = function (test) {
	logger_basics (test);
	logging_api_tests (test);
	formatter_tests (test);
	console_test (test);
	placeholder_testing (test);
};

//# sourceMappingURL=logger_tests.map