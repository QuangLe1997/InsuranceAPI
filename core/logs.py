"""Some formater classes of log"""
import decimal
import json
import traceback
import uuid
from datetime import datetime, date
from logging import Formatter, LogRecord, Handler, INFO

import requests


# pylint: disable=line-too-long
# pylint: disable=too-many-arguments
# pylint: disable=consider-using-f-string
# pylint: disable=broad-except
# pylint: disable=try-except-raise


class ExtendedJsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder class
    """

    def default(self, o):
        """
        Default encoder function
        :param o:
        :return:
        """
        if isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class LogStashV1Formatter(Formatter):
    """
    Formatter for Log stash, using version v1.0
    """

    skip_list = (
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "id",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "thread",
        "threadName",
        "extra",
    )

    easy_types = (str, bool, dict, float, int, list, type(None))

    @classmethod
    def format_exception(cls, exc_info):
        """
        Formats exception as string
        :param exc_info: execption info
        :return:
        """
        return "".join(traceback.format_exception(*exc_info)) if exc_info else ""

    def get_extra_fields(self, record):
        """
        Get extra fields as fields of message
        :param record: log record
        :return:
        """
        fields = {}

        for key, value in record.__dict__.items():
            if key not in self.skip_list:
                if isinstance(value, self.easy_types):
                    fields[key] = value
                else:
                    fields[key] = repr(value)

        return fields

    def get_stack_trace(self, record: LogRecord):
        """
        Gets stack trace of exception
        :param record: log record
        :return:
        """
        fields = {
            "stack_trace": self.format_exception(record.exc_info),
        }

        # funcName was added in 2.5
        if not getattr(record, "funcName", None):
            fields["funcName"] = record.funcName

        # processName was added in 2.6
        if not getattr(record, "processName", None):
            fields["processName"] = record.processName

        return fields

    def format(self, record: LogRecord):
        """
        Formats a log record into message
        :param record: log record
        :return:
        """
        # Create message dict
        message = {
            "@timestamp": record.created,
            "@version": "1",
            "datetime": datetime.utcfromtimestamp(record.created).strftime(
                self.datefmt
            ),
            "process": record.process,
            "process_name": record.processName,
            "thread": record.thread,
            "message": record.getMessage(),
            "path": record.pathname,
            "level": record.levelname,
            "logger_name": record.name,
            "func": record.funcName,
            "module": record.module,
            "lineno": record.lineno,
            "file_name": record.filename,
        }

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_stack_trace(record))

        return json.dumps(message, cls=ExtendedJsonEncoder)


class LogTelegramHandler(Handler):
    """Log Handler send messages to telegram

    [Telegram Bot API](https://core.telegram.org/bots/api)

    1. Register bot:
        - Login Telegram
        - Search for `BotFather` with **verify sign**.
        - Follow `BotFather`'s instructions to register a bot.
        - Bot's token is like this `111111111:AxxxxxxxxxxxxxxxxxxxxxxxxE`
    2. Find `chat_id`:
        - Add your bot to group chat and set it as an admin
        - Call POST to URL `https://api.telegram.org/bot<token>/getUpdates`, you will get result like

            ```javascript
            {
                "ok": true,
                "result": [
                    {
                        "update_id": 879273682,
                        "message": {
                            "message_id": 1,
                            "from": {
                                ...
                            },
                            "chat": {
                                "id": -222222,
                                "title": "Group name",
                                "type": "supergroup"
                            },
                            "date": 1585919398,
                            "migrate_from_chat_id": -33333
                        }
                    }
                ]
            }
            ```

        - Group chat id is `result.message.chat.id`, the negative number `-222222`.
    3. Configure handler like this example:

        ```python
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'test_telegram': {
                    'class': 'handlers.telegram_handler.LogTelegramHandler',
                    'token': '<your_token>',
                    'chat_id': '<your_chat_id>'
                },
            },
            'loggers': {
                'test_logger': {
                    'handlers': ['test_telegram'],
                    'level': 'INFO',
                    'propagate': True,
                },
            }
        }
        ```
    """

    def __init__(
        self, token: str, chat_id: int, parse_mode: str = "HTML", level=INFO, prefix=""
    ):
        super().__init__(level=level)
        self.token = token
        self.chat_id = chat_id
        self.parse_mode = parse_mode
        self.prefix = prefix
        self.send_webhook = "https://api.telegram.org/bot{token}/sendMessage".format(
            token=self.token
        )
        self.session = requests.Session()

    def format(self, record) -> str:
        message = record.msg % record.args
        args_str = ""
        if bool(record.args):
            for key, val in record.args.items():
                args_str += f"<b>{key}</b>:<pre>{val}</pre> \n"
        message = (
            f"<b>{self.prefix}[{record.levelname}]</b> \n"
            f"<i>{message}</i> \n" + args_str
        )
        if bool(record.exc_text):
            message += (
                f" ```python {record.exc_text[:3800]}```"  # limit length of message
            )
        return message[:4096]

    def emit(self, record):
        try:
            message = self.format(record)
            data = {
                "chat_id": int(self.chat_id),
                "text": message,
                "parse_mode": self.parse_mode,
            }
            self.session.post(self.send_webhook, data=data, timeout=10)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
