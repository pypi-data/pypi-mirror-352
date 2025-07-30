from cascade_filter.compliance_checker.single import SingleChecker
from cascade_filter.clause import Clause

from typing import Callable, TypeVar
from functools import wraps


T = TypeVar("T", bound=SingleChecker)
Method = Callable[[T, object], bool]


class Missing:
	pass


def nullable(method: Method):
	@wraps
	def inner(checker: SingleChecker, obj: object) -> bool:
		attr_value = getattr(obj, checker.cascade_filter.table_field, Missing)

		if attr_value is Missing:
			return False

		if checker.cascade_filter.clause is Clause.IS_NULL:
			return attr_value is None
		elif checker.cascade_filter.clause is Clause.IS_NOT_NULL:
			return attr_value is not None

		return method(checker, obj)

	return inner
