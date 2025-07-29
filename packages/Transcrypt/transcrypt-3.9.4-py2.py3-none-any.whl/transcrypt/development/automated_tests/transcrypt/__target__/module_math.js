// Transcrypt'ed from Python, 2025-05-30 20:15:55
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __conj__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, _copy, _sort, abs, all, any, assert, bin, bool, bytearray, bytes, callable, chr, complex, delattr, dict, dir, divmod, filter, float, format, getattr, hasattr, hex, input, int, isinstance, issubclass, len, list, map, max, min, object, oct, ord, print, property, py_TypeError, py_enumerate, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import {acos, acosh, asin, asinh, atan, atan2, atanh, ceil, copysign, cos, cosh, degrees, e, exp, expm1, floor, hypot, inf, isclose, isnan, log, log10, log1p, log2, modf, nan, pi, pow, radians, sin, sinh, sqrt, tan, tanh, trunc} from './math.js';
export {modf, cosh, expm1, radians, tan, asin, ceil, log2, isclose, pow, trunc, inf, sqrt, log10, nan, acosh, tanh, asinh, atan, acos, atanh, pi, floor, atan2, e, sin, exp, sinh, degrees, log1p, cos, hypot, isnan, log, copysign};
var __all__ = dict ({get __name__ () {return __name__;}, set __name__ (value) {__name__ = value;}, get _check () {return _check;}, set _check (value) {_check = value;}, get run () {return run;}, set run (value) {run = value;}});
var __name__ = 'module_math';
export var _check = function (nr, autoTester) {
	if (isinstance (nr, float)) {
		var nr = str (nr).__getslice__ (null, 15, 1);
	}
	autoTester.check (nr);
};
export var run = function (autoTester) {
	var check = (function __lambda__ (nr) {
		return _check (nr, autoTester);
	});
	check (pi);
	check (e);
	check (exp (3));
	check (int (expm1 (5)));
	check (log (0.2));
	check (round (log (1024, 2)));
	check (log1p (5));
	check (int (log2 (257)));
	check (int (log10 (1001)));
	check (pow (3, 4.5));
	check (sqrt (25.1));
	check (sin (10));
	check (cos (10));
	check (tan (10));
	check (asin (0.5));
	check (acos (0.5));
	check (atan (0.5));
	check (atan2 (1, 2));
	check (int (hypot (3, 4.1)));
	check (degrees (pi / 2.1));
	check (radians (90));
	check (sinh (1));
	check (cosh (1));
	check (tan (1));
	check (asinh (70));
	check (acosh (70));
	check (atan (70));
	check (floor (3.5));
	check (ceil (3.5));
	check (trunc (3.5));
	autoTester.check ('{0:g}'.format (copysign (42.0, 99.0)));
	autoTester.check ('{0:g}'.format (copysign (-(42), 99.0)));
	autoTester.check ('{0:g}'.format (copysign (42, -(99.0))));
	autoTester.check ('{0:g}'.format (copysign (-(42.0), -(99.0))));
	autoTester.check (isclose (2.123456, 2.123457), isclose (2.12, 2.123457), isclose (2.1234567891, 2.1234567892), isclose (2.1, 2, __kwargtrans__ ({rel_tol: 0.05})), isclose (2.15, 2, __kwargtrans__ ({rel_tol: 0.05})), isclose (1, 1), isclose (1, 1.000000002), isclose (1, 1.0000000002), isclose (1.0, 1.02, __kwargtrans__ ({rel_tol: 0.02})), isclose (1.0, 1.02, __kwargtrans__ ({rel_tol: 0.0, abs_tol: 0.02})), isclose (1e-09, 0.0, __kwargtrans__ ({rel_tol: 1e-09})), isclose (1e-09, 0.0, __kwargtrans__ ({rel_tol: 0.0, abs_tol: 9.99e-10})), isclose (1e-09, 0.0, __kwargtrans__ ({rel_tol: 0.0, abs_tol: 1e-09})), isclose (0.0, 1e-09, __kwargtrans__ ({rel_tol: 0.0, abs_tol: 1e-09})));
	autoTester.check (isnan (3));
	autoTester.check (isnan (nan));
	autoTester.check ('2 ** 2 = {}'.format (Math.pow (2, 2)));
	autoTester.check ('2.0 ** 2 = {:g}'.format (Math.pow (2.0, 2)));
	autoTester.check ('math.pow(2, 2) = {:g}'.format (pow (2, 2)));
	autoTester.check ('math.pow(3, 2.9) = {}'.format (pow (3, 2.9)));
	autoTester.check ('math.pow(3, 2.0) = {:g}'.format (pow (3, 2.0)));
	autoTester.check ('math.pow(3.1, 2.0) = {}'.format (pow (3.1, 2.0)));
};

//# sourceMappingURL=module_math.map