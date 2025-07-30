from cascade_filter.field_type import FieldType
from cascade_filter.filter.single import SingleFilter
from cascade_filter.filter.value import FilterValue

from uuid import UUID


class UUIDFilterValue(FilterValue[UUID]):
	pass


class UUIDFilter(SingleFilter[UUID]):
	subtype = FieldType.UUID
