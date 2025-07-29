from pydantic import BaseModel, Field
from typing import List, Optional, Union
from .base import BaseToolCallModel
import json


class Category(BaseModel):
    id: int
    name: str
    imagePath: Optional[str] = None
    s3Url: Optional[str] = None

    def filter_for_llm(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Supplier(BaseModel):
    id: int
    name: str
    categoryId: int
    s3Url: Optional[str] = None

    def filter_for_llm(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Value(BaseModel):
    value: int
    name: str

    def filter_for_llm(self):
        return {
            "value": self.value,
            "name": self.name,
        }


class FieldOptions(BaseModel):
    identName: str
    name: str
    order: int
    type: str
    pattern: Optional[str] = None
    minValue: Optional[int] = None
    maxValue: Optional[int] = None
    fieldSize: Optional[int] = None
    isMain: Optional[bool] = None
    valueList: Optional[List[Value]] = None

    def filter_for_llm(self):
        return {
            "identName": self.identName,
            "name": self.name,
            "order": self.order,
            "type": self.type,
            "pattern": self.pattern,
            "minValue": self.minValue,
            "maxValue": self.maxValue,
            "fieldSize": self.fieldSize,
            "isMain": self.isMain,
            "valueList": [x.filter_for_llm() for x in self.valueList],
        }


class Response(BaseModel):
    payload: List[Category] = Field(default_factory=list)
    code: Optional[Union[int, str]] = None


class SuppliersField(Response):
    checkUp: bool
    checkUpWithResponse: bool
    checkUpAfterPayment: bool
    fieldList: List[FieldOptions]


class SupplierFieldsResponse(BaseToolCallModel, Response):
    payload: SuppliersField = Field(default_factory=SuppliersField)

    def filter_for_llm(self):
        return json.dumps(
            self.payload.filter_for_llm(),
            ensure_ascii=False,
            indent=2,
        )


class SupplierByCategoryResponse(BaseToolCallModel, Response):
    payload: List[Supplier] = Field(default_factory=list)

    def filter_for_llm(self):
        return json.dumps(
            [x.filter_for_llm() for x in self.payload],
            ensure_ascii=False,
            indent=2,
        )


class CategoriesResponse(BaseToolCallModel, Response):
    payload: List[Category] = Field(default_factory=list)

    def filter_for_llm(self):
        return json.dumps(
            [x.filter_for_llm() for x in self.payload],
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    import sys
    import os

    sys.path.append(os.getcwd())
    from tests.cache_responses import (
        supplier_fields_response,
        suppliers_list_response,
    )

    a = SupplierByCategoryResponse(**suppliers_list_response)
    b = SupplierFieldsResponse(**supplier_fields_response)
    print(a)
    print(b)
