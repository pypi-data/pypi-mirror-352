from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict
from .base import BaseToolCallModel
import json


class CardDetails(BaseModel):
    cardDetailsId: int
    cardName: str
    cardColor: str
    cardIsPrimary: bool


class CardBalance(BaseModel):
    balance: Union[int, str] = Field(..., description="Balance in cents")
    status: int

    def __init__(self, **data):
        if isinstance(data.get("balance"), str):
            data["balance"] = int(data["balance"]) // 100
        super().__init__(**data)


class BankIcon(BaseModel):
    bankLogo: str
    bankLogoMini: str
    bankWhiteLogo: str
    bankWhiteLogoMini: str


class Card(BaseModel):
    panMask: str
    panToken: str
    requestId: str
    pan: str
    expiry: str
    bankIssuer: str
    uzcardToken: Optional[str] = None
    processingSystem: str
    salaryAmount: Union[int, str] = Field(..., description="Salary amount in cents")
    isVerified: bool
    createdAt: str
    cardDetails: CardDetails
    cardBalance: CardBalance
    isVirtual: bool
    bankIcon: BankIcon

    def __init__(self, **data):
        if isinstance(data.get("salaryAmount"), (str, int)):
            data["salaryAmount"] = int(data["salaryAmount"]) // 100
        super().__init__(**data)


class CardsBalanceResponse(BaseToolCallModel, BaseModel):
    custNo: str
    phoneNumber: str
    firstname: str
    middlename: str
    lastname: str
    birthDate: str
    pinfl: str
    createdAt: str
    cardList: List[Card]

    def filter_for_llm(self):
        return json.dumps(
            [
                {
                    "pan": card.pan,
                    "balance": card.cardBalance.balance,
                    "bankIssuer": card.bankIssuer,
                    "processingSystem": card.processingSystem,
                    "cardDetails": card.cardDetails.cardName,
                }
                for card in self.cardList
            ],
            ensure_ascii=False,
            indent=2,
        )


class CardInfoByPhoneNumber(BaseModel):
    pan: str
    name: str
    processing: str
    mask: str


class CardsByPhoneNumberResponse(BaseToolCallModel, BaseModel):
    cards: List[CardInfoByPhoneNumber]

    def __init__(self, data):
        super().__init__(cards=[CardInfoByPhoneNumber(**x) for x in data])

    def filter_for_llm(self):
        return json.dumps(
            [x.model_dump(by_alias=True) for x in self.cards],
            ensure_ascii=False,
            indent=2,
        )


class CardInfoByCardNumberResponse(BaseToolCallModel, BaseModel):
    processingSystem: Optional[str] = None
    iconMini: Optional[str] = None
    isFound: bool
    maskedPan: Optional[str] = None
    errorMessage: Optional[str] = None
    icon: Optional[str] = None
    fullName: Optional[str] = None
    errorCode: Optional[str] = None
    token: Optional[str] = None

    def filter_for_llm(self):
        return self.model_dump_json(exclude=["iconMini", "icon"], indent=2)
