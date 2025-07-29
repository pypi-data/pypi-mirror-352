"""
Модели данных для MemePay SDK
"""

from dataclasses import dataclass
from typing import Optional, Any, Dict, Union
from datetime import datetime


@dataclass
class ExpiresAt:
    """Дата истечения срока платежа"""
    _raw_data: Dict[str, str]
    
    def __init__(self, data: Dict[str, str]):
        self._raw_data = data or {"date": "", "time": ""}
    
    def data(self) -> str:
        """Возвращает дату"""
        date_str = self._raw_data.get("date", "")
        if date_str:
            try:
                if "T" in date_str:
                    iso_date = date_str.split("T")[0]
                    return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d.%m.%Y")
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
            except ValueError:
                return date_str
        return ""
    
    def time(self) -> str:
        """Возвращает время"""
        time_str = self._raw_data.get("time", "")
        if time_str:
            try:
                return datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M:%S")
            except ValueError:
                return time_str
        return ""
    
    def __str__(self) -> str:
        """Строковое представление"""
        return f"{self.data()} {self.time()}"
    
    def get(self, key: str) -> str:
        """Получение значения по ключу (для совместимости)"""
        return self._raw_data.get(key, "")


@dataclass
class PaymentInfo:
    """Информация о платеже"""
    id: str
    amount: float
    amount_with_commission: float
    status: str
    method: str
    created_at: datetime


@dataclass
class PaymentCreateResponse:
    """Ответ на создание платежа"""
    payment_id: str
    payment_url: str
    amount: float
    status: str
    expires_at: Union[ExpiresAt, datetime]
    created_at: datetime


@dataclass
class UserInfo:
    """Информация о пользователе"""
    name: str
    email: str
    balance: float
    created_at: datetime


@dataclass
class ApiResponse:
    """Общий ответ API"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None