# py-fastapi-logging

## ENV-переменные для управления логами
#### Уровень логов. debug - для площадок отладки, info - для PROM
LOG_LEVEL=info
#### Формат логов: SIMPLE (обычный) или JSON (JSON-STDOUT - лог в формате json в поток stdout)
LOG_FORMAT=SIMPLE
#### Папка, в которой будут лежать логи
LOG_DIR=/var/log/<APP NAME>
#### Название файла лога
LOG_FILENAME=production.log
#### Добавление переменных в лог (JSON-формат) из переменных окружения
LOG_ENV_EXTRA="field1:ENV_VAR_NAME_1,field2:ENV_VAR_NAME_2"
#### Количество старых лог файлов, которые сохраняются при ротации логов
LOG_FILES_COUNT=5
#### Максимальный размер лог файла в мегабайтах для ротации логов
LOG_FILE_SIZE=10

## Интеграция в FastAPI приложение
```python
from fastapi import FastAPI
from py_fastapi_logging.middlewares.logging import LoggingMiddleware
app = FastAPI()
app.add_middleware(LoggingMiddleware, app_name='my_app_name')
```

## Использование логгера в приложениях не на FastAPI
```python
import logging
from py_fastapi_logging.config.config import init_logger
init_logger(app_name='my_app_name')
logger = logging.getLogger()
```
