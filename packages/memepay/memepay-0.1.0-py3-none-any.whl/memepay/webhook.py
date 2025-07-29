"""
Модуль для интеграции вебхуков MemePay с FastAPI
"""

import hmac
import hashlib
import json
import importlib
import threading
import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable, Union, Awaitable, List, Literal, Tuple
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, Header, HTTPException, status, FastAPI

class ColorFormatter(logging.Formatter):
    """Форматтер для вывода цветных логов"""
    GREEN = "\033[92m"
    WHITE = "\033[97m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

    def format(self, record):
        """Форматирование сообщений лога с цветами"""

        colored_name = f"{self.GREEN}Meme{self.WHITE}Pay{self.RED}SDK{self.RESET}"
        msg = super().format(record)
        return msg.replace("MemePaySDK", colored_name)

logger = logging.getLogger("memepay")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = ColorFormatter('[MemePaySDK]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

for uvicorn_logger in ['uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logging.getLogger(uvicorn_logger).handlers = []
    logging.getLogger(uvicorn_logger).propagate = False

class WebhookEventType(str, Enum):
    """Типы событий вебхуков"""
    PAYMENT_CREATED = "payment.created"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"

EventType = Literal["payment_created", "payment_completed", "payment_failed", "error"]

class PaymentData(BaseModel):
    """Данные платежа в вебхуке"""
    id: str
    amount: str  
    method: Optional[str] = None
    status: str
    shop_id: Optional[str] = None

    customer: Optional[Dict[str, Any]] = Field(default_factory=dict)
    payment_url: Optional[str] = None
    commission: Optional[str] = None
    webhook_sent: Optional[int] = None
    expires_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        """Конфигурация модели"""

        extra = "ignore"  

class ClientWebhookPayload(BaseModel):
    """Входящая полезная нагрузка вебхука от клиента"""
    event: str
    payment: PaymentData
    timestamp: int

class WebhookPayload(BaseModel):
    payment_id: str = Field(..., description="ID платежа")
    amount: float = Field(..., description="Сумма платежа")
    status: str = Field(..., description="Статус платежа")
    method: Optional[str] = Field(None, description="Метод оплаты")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")

class WebhookResponse(BaseModel):
    success: bool = Field(..., description="Успешность обработки")
    warning: Optional[str] = Field(None, description="Предупреждение")

class MemePayWebhook:
    """
    Класс для интеграции вебхуков MemePay с FastAPI
    """

    def __init__(self, webhook_secret: str):
        """
        Инициализация вебхук-обработчика MemePay

        Args:
            webhook_secret: Секретный ключ для проверки подписи вебхуков
        """
        self.webhook_secret = webhook_secret
        self.router = APIRouter()
        self._server_thread = None
        self._should_stop = False

        self.handlers = {
            "payment_created": [],

            "payment_completed": [],
            "payment_failed": [],
            "error": []
        }

        self.router.post("/webhook", response_model=WebhookResponse)(self.webhook_handler)

    def register(
        self, 
        handler: Union[
            Callable[[WebhookPayload], Union[None, Awaitable[None]]], 
            Callable[[Exception], Union[None, Awaitable[None]]]
        ],
        event_type: EventType
    ):
        """
        Регистрирует функцию-обработчик для указанного типа события

        Args:
            handler: Функция-обработчик
            event_type: Тип события ('payment_created', 'payment_completed',
                        'payment_failed' или 'error')

        Returns:
            Зарегистрированная функция (для поддержки композиции)
        """
        if event_type not in self.handlers:
            raise ValueError(f"Неизвестный тип события: {event_type}")

        self.handlers[event_type].append(handler)
        return handler

    def initialize_app(self, app: FastAPI, prefix: str = "/api/memepay", tags: List[str] = None) -> None:
        """
        Интегрирует вебхук с FastAPI приложением

        Args:
            app: FastAPI приложение
            prefix: Префикс URL для вебхука
            tags: Список тегов для API документации
        """
        if tags is None:
            tags = ["memepay"]

        app.include_router(self.router, prefix=prefix, tags=tags)

    @classmethod
    def create_app(
        cls, 
        webhook_secret: str,
        title: str = "MemePay Webhook API",
        description: str = None,
        version: str = "1.0.0",
        webhook_prefix: str = "/api/memepay",
        webhook_tags: List[str] = None
    ) -> Tuple[FastAPI, "MemePayWebhook"]:
        """
        Создает FastAPI приложение с интегрированным обработчиком вебхуков

        Args:
            webhook_secret: Секретный ключ для проверки подписи вебхуков
            title: Название API
            description: Описание API
            version: Версия API
            webhook_prefix: Префикс URL для вебхука
            webhook_tags: Список тегов для API документации

        Returns:
            Кортеж из (FastAPI приложение, объект MemePayWebhook)
        """

        app = FastAPI(
            title=title,
            description=description,
            version=version
        )

        webhook_handler = cls(webhook_secret=webhook_secret)

        webhook_handler.initialize_app(app, prefix=webhook_prefix, tags=webhook_tags)

        @app.get("/", tags=["status"])
        async def root():
            """
            Проверка работоспособности API
            """
            return {
                "status": "online",
                "service": title,
                "webhook_url": f"{webhook_prefix}/webhook"
            }

        return app, webhook_handler

    @staticmethod
    def run_server(
        app: FastAPI, 
        host: str = "0.0.0.0", 
        port: int = 8000, 
        log_level: str = "info",
        reload: bool = False
    ) -> None:
        """
        Запускает сервер используя uvicorn

        Args:
            app: FastAPI приложение
            host: Хост для прослушивания
            port: Порт для прослушивания
            log_level: Уровень логирования (debug, info, warning, error, critical)
            reload: Включить автоперезагрузку при изменении кода
        """
        try:

            uvicorn = importlib.import_module("uvicorn")

            logger.info(f"Сервер запущен на http://{host}:{port}")

            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="critical", 
                reload=reload
            )
        except ImportError:
            raise ImportError("Не удалось найти uvicorn. Пожалуйста, установите пакет: pip install uvicorn")
        except Exception as e:
            raise RuntimeError(f"Ошибка запуска сервера: {e}")

    def start_server_in_thread(
        self, 
        app: FastAPI, 
        host: str = "0.0.0.0", 
        port: int = 8000,
    ) -> None:
        """
        Запускает сервер в отдельном потоке

        Args:
            app: FastAPI приложение
            host: Хост для прослушивания
            port: Порт для прослушивания
            log_level: Уровень логирования
        """
        self._should_stop = False

        def run_server():
            try:

                uvicorn = importlib.import_module("uvicorn")

                logger.info(f"Сервер запущен на http://{host}:{port}")

                config = uvicorn.Config(
                    app=app, 
                    host=host, 
                    port=port, 
                    log_level="critical", 
                    access_log=False
                )
                server = uvicorn.Server(config=config)
                server.run()
            except Exception as e:
                logger.error(f"Ошибка при запуске сервера: {e}")

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

    def stop_server(self, timeout: int = 5) -> bool:
        """
        Останавливает сервер, запущенный в отдельном потоке

        Args:
            timeout: Максимальное время ожидания остановки в секундах

        Returns:
            bool: True если сервер успешно остановлен, False в противном случае
        """
        if not self._server_thread or not self._server_thread.is_alive():
            return True

        self._should_stop = True
        self._server_thread.join(timeout=timeout)
        return not self._server_thread.is_alive()

    def on_payment_created(self, handler):
        """
        Декоратор для регистрации обработчика payment_created (устарело)

        Args:
            handler: Функция-обработчик
        """
        return self.register(handler, "payment_created")

    def on_payment_completed(self, handler):
        """
        Декоратор для регистрации обработчика payment_completed (устарело)

        Args:
            handler: Функция-обработчик
        """
        return self.register(handler, "payment_completed")

    def on_payment_failed(self, handler):
        """
        Декоратор для регистрации обработчика payment_failed (устарело)

        Args:
            handler: Функция-обработчик
        """
        return self.register(handler, "payment_failed")

    def on_error(self, handler):
        """
        Декоратор для регистрации обработчика ошибок (устарело)

        Args:
            handler: Функция-обработчик ошибок
        """
        return self.register(handler, "error")

    def verify_signature(self, webhook_data: ClientWebhookPayload, signature: str) -> bool:
        """
        Проверяет подпись вебхука

        Args:
            webhook_data: Данные вебхука
            signature: Подпись из заголовка

        Returns:
            bool: True, если подпись верна
        """
        try:

            payload_data = {
                "payment_id": webhook_data.payment.id,
                "amount": webhook_data.payment.amount,  
                "status": webhook_data.payment.status,
                "method": webhook_data.payment.method or ""
            }

            sorted_keys = sorted(payload_data.keys())
            sorted_payload = {k: payload_data[k] for k in sorted_keys}

            payload_str = json.dumps(sorted_payload, separators=(',', ':'))
            timestamp_str = str(webhook_data.timestamp)
            string_to_sign = f"{payload_str}.{timestamp_str}"

            hmac_obj = hmac.new(
                self.webhook_secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            )
            calculated_signature = hmac_obj.hexdigest()

            return hmac.compare_digest(calculated_signature, signature)
        except Exception:
            return False

    def _map_client_event_to_sdk(self, client_event: str) -> Optional[str]:
        """
        Преобразует тип события из клиентского формата в формат SDK

        Args:
            client_event: Тип события в клиентском формате (payment_created, payment_completed, etc.)

        Returns:
            str: Тип события в формате SDK или None если не распознан
        """
        event_map = {
            "payment_created": "payment_created",
            "payment_completed": "payment_completed",
            "payment_failed": "payment_failed",
        }
        return event_map.get(client_event)

    def _convert_to_webhook_payload(self, client_data: ClientWebhookPayload) -> WebhookPayload:
        """
        Преобразует клиентские данные в формат SDK

        Args:
            client_data: Данные вебхука от клиента

        Returns:
            WebhookPayload: Данные в формате SDK
        """
        return WebhookPayload(
            payment_id=client_data.payment.id,
            amount=float(client_data.payment.amount),
            status=client_data.payment.status,
            method=client_data.payment.method,
            metadata={"shop_id": client_data.payment.shop_id} if client_data.payment.shop_id else None
        )

    async def webhook_handler(
        self, 
        request: Request,
        x_memepay_signature: Optional[str] = Header(None, alias="X-MemePay-Signature")
    ) -> WebhookResponse:
        """
        Обработчик вебхуков

        Args:
            request: FastAPI запрос
            x_memepay_signature: Заголовок с подписью

        Returns:
            WebhookResponse: Ответ на вебхук
        """

        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Получен запрос: {request.method} {request.url.path} от {client_host}")

        headers = dict(request.headers.items())

        signature_headers = [
            "X-MemePay-Signature", 
            "X-Memepay-Signature", 
            "x-memepay-signature"
        ]

        if not x_memepay_signature:
            for header_name in signature_headers:
                if header_name in headers:
                    x_memepay_signature = headers[header_name]
                    break

        if not x_memepay_signature:
            logger.warning(f"Отклонен запрос: {request.url.path} (401 - отсутствует подпись)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing signature"
            )

        webhook_data_raw = await request.body()
        webhook_data_str = webhook_data_raw.decode("utf-8")
        webhook_data = json.loads(webhook_data_str)

        try:

            client_payload = ClientWebhookPayload(**webhook_data)

            if not self.verify_signature(client_payload, x_memepay_signature):
                logger.warning(f"Отклонен запрос: {request.url.path} (401 - неверная подпись)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )

            sdk_event_type = self._map_client_event_to_sdk(client_payload.event)
            if not sdk_event_type:
                logger.warning(f"Неизвестный тип события: {client_payload.event}")
                return WebhookResponse(success=True, warning=f"Unknown event type: {client_payload.event}")

            sdk_payload = self._convert_to_webhook_payload(client_payload)

            try:
                logger.info(f"Обработка события '{sdk_event_type}' для платежа {sdk_payload.payment_id}")
                await self._execute_handlers(self.handlers[sdk_event_type], sdk_payload)
                logger.info(f"Обработка успешно завершена (200)")
            except Exception as e:

                logger.error(f"Ошибка при обработке платежа {sdk_payload.payment_id}: {e}")
                await self._execute_error_handlers(e)

                return WebhookResponse(success=True, warning=f"Error processing webhook: {str(e)}")

            return WebhookResponse(success=True)

        except Exception as e:

            logger.error(f"Ошибка формата данных: {e}")
            await self._execute_error_handlers(e)
            return WebhookResponse(success=False, warning=f"Invalid payload format: {str(e)}")

    async def _execute_handlers(
        self, 
        handlers: List[Callable[[WebhookPayload], Union[None, Awaitable[None]]]],
        payload: WebhookPayload
    ) -> None:
        """
        Выполняет все зарегистрированные обработчики

        Args:
            handlers: Список обработчиков
            payload: Полезная нагрузка вебхука
        """
        for handler in handlers:
            result = handler(payload)
            if result is not None and hasattr(result, "__await__"):
                await result

    async def _execute_error_handlers(self, error: Exception) -> None:
        """
        Выполняет все зарегистрированные обработчики ошибок

        Args:
            error: Объект исключения
        """
        for handler in self.handlers["error"]:
            result = handler(error)
            if result is not None and hasattr(result, "__await__"):
                await result