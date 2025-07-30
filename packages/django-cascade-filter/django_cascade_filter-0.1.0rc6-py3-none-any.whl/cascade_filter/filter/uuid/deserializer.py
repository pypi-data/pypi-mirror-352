from cascade_filter.clause import Clause
from cascade_filter.filter.uuid import UUIDFilter
from cascade_filter.filter.value.deserializer import FilterValueDeserializer as _FilterValueDeserializer
from cascade_filter.filter.value.dataclass import FilterValue

from typing import TypedDict
from uuid import UUID


class FilterValueExpectedValue(TypedDict):
	label: str
	value: UUID


class ExpectedValue(TypedDict):
	type: str
	subtype: str
	clause: str
	enabled: bool
	tableField: str
	value: FilterValueExpectedValue


class FilterValueDeserializer(_FilterValueDeserializer[UUID]):
	def deserialize(self, value) -> FilterValue[UUID]:
		return FilterValue(value["label"], UUID(value["value"]))


class UUIDFilterDeserializer:
	def __init__(self) -> None:
		self.value_deserializer = FilterValueDeserializer()

	def deserialize(self, value: ExpectedValue) -> UUIDFilter:
		return UUIDFilter(
			clause=Clause(value["clause"]),
			enabled=value["enabled"],
			table_field=value["tableField"],
			value=self.value_deserializer.deserialize(value["value"]),
		)
