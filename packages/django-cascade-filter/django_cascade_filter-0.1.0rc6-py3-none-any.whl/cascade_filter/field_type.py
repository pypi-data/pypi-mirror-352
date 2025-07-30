from cascade_filter.generic.enum import ExtendedEnum


class FieldType(ExtendedEnum):
	DATE = "date"
	CHOICE = "choice"
	TEXT = "text"
	UUID = "uuid"
	NUMERIC = "numeric"
	BOOLEAN = "boolean"
	ARRAY = "array"
