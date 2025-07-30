from cascade_filter.clause import Clause
from cascade_filter.filter import UUIDFilter
from cascade_filter.compliance_checker.single import SingleChecker
from cascade_filter.compliance_checker.decorator import nullable

from typing import cast
from uuid import UUID


class Missing:
	pass


class UUIDChecker(SingleChecker[UUIDFilter]):
	@nullable
	def is_fit(self, obj: object) -> bool:
		attr_value = getattr(obj, self.cascade_filter.table_field, Missing)

		if attr_value is Missing:
			return False

		if attr_value is None:
			return self.cascade_filter.clause is Clause.NOT_EQUAL

		attr_value = cast(UUID, attr_value)

		if self.cascade_filter.clause is Clause.EQUAL:
			return attr_value == self.cascade_filter.value.value
		elif self.cascade_filter.clause is Clause.NOT_EQUAL:
			return attr_value != self.cascade_filter.value.value

		raise NotImplementedError(f"Unknown UUID filter clause: {self.cascade_filter.clause}")
