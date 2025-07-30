from cascade_filter.meta.field.field import Field
from cascade_filter.field_type import FieldType


class UUIDField(Field):
	type = FieldType.UUID
