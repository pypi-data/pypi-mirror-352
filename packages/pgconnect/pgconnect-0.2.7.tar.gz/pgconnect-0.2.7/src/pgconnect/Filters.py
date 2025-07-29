from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

@dataclass
class Between:
    from_value: Optional[Any] = None
    to_value: Optional[Any] = None
    
    def to_sql(self, field_name: str, params: list) -> str:
        field_expression = field_name
        if isinstance(self.from_value, datetime) or isinstance(self.to_value, datetime):
            # Check if any of the datetime objects are timezone-aware
            is_tz_aware = (isinstance(self.from_value, datetime) and self.from_value.tzinfo is not None) or \
                          (isinstance(self.to_value, datetime) and self.to_value.tzinfo is not None)
            if is_tz_aware:
                field_expression = f"CAST({field_name} AS TIMESTAMPTZ)"
            else:
                field_expression = f"CAST({field_name} AS TIMESTAMP)"

        if self.from_value is not None and self.to_value is not None:
            params.extend([self.from_value, self.to_value])
            return f"{field_expression} BETWEEN ${len(params)-1} AND ${len(params)}"
        elif self.from_value is not None:
            params.append(self.from_value)
            return f"{field_expression} >= ${len(params)}"
        elif self.to_value is not None:
            params.append(self.to_value)
            return f"{field_expression} <= ${len(params)}"
        raise ValueError("Either from_value or to_value must be provided")

@dataclass
class Like:
    pattern: str
    
    def to_sql(self, field_name: str, params: list) -> str:
        params.append(f"%{self.pattern}%")
        return f"{field_name} ILIKE ${len(params)}"

@dataclass
class In:
    values: list
    
    def __post_init__(self):
        # Convert to list and remove duplicates
        self.values = list(dict.fromkeys(self.values))
        
        # Convert string numbers to integers
        if all(str(v).isdigit() for v in self.values):
            self.values = [int(v) for v in self.values]
    
    def to_sql(self, field_name: str, params: list) -> str:
        params.extend(self.values)
        placeholders = [f"${len(params)-len(self.values)+i+1}" for i in range(len(self.values))]
        
        if all(isinstance(v, int) for v in self.values):
            # Cast both the field and array elements to INTEGER for comparison
            return f"CAST({field_name} AS INTEGER) IN (SELECT UNNEST(ARRAY[{','.join(placeholders)}]::INTEGER[]))"
        else:
            return f"{field_name} IN ({','.join(placeholders)})"

class Filters:
    @staticmethod
    def Between(from_value: Any = None, to_value: Any = None) -> Between:
        if from_value is None and to_value is None:
            raise ValueError("Either from_value or to_value must be provided")
        return Between(from_value, to_value)
    
    @staticmethod
    def Like(pattern: str) -> Like:
        return Like(pattern)
    
    @staticmethod
    def In(values: list) -> In:
        return In(values)