from cascade_filter.filter import UUIDFilter
from cascade_filter.clause import Clause

from django.db.models.query import Q


class UUIDFilterMixin:
	def make_uuid_filter(self, uuid_filter: UUIDFilter):
		if uuid_filter.clause is Clause.EQUAL:
			return Q(**{uuid_filter.table_field: uuid_filter.value.value})
		elif uuid_filter.clause is Clause.NOT_EQUAL:
			return ~Q(**{uuid_filter.table_field: uuid_filter.value.value})

		raise NotImplementedError(f"Unknown UUID filter clause: \"{uuid_filter.clause}\"")
