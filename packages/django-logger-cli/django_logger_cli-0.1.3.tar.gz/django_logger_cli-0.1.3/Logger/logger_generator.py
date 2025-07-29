BASIC_LOGGER = (
"import os\n"
"LOG_DIR = os.path.join(BASE_DIR, 'logs')\n"
"os.makedirs(LOG_DIR, exist_ok=True)\n\n"
"LOGGING = {\n"
"    'version': 1,\n"
"    'disable_existing_loggers': False,\n"
"    'formatters': {\n"
"        'default_formatter': {\n"
"            'format': '%(asctime)s [%(levelname)s] (%(name)s.%(funcName)s:%(lineno)d) %(message)s',\n"
"            'datefmt': '%Y-%m-%d %H:%M:%S',\n"
"       }\n"
"    },\n"
"    'handlers': {\n"
"        'file_handler': {\n"
"            'level': 'INFO',\n"
"            'class': 'logging.FileHandler',\n"
"            'filename': os.path.join(LOG_DIR, 'app.log'),\n"
"            'formatter': 'default_formatter',\n"
"        },\n"
"        'stream_handler': {\n"
"            'level': 'INFO',\n"
"            'class': 'logging.StreamHandler',\n"
"            'formatter': 'default_formatter',\n"
"        },\n"
"    },\n"
"    'loggers': {\n"
"        'django': {\n"
"            'handlers': ['file_handler', 'stream_handler'],\n"
"            'level': 'INFO',\n"
"            'propagate': True,\n"
"        }\n"
"    }\n"
"}\n"
)
LOGGER_FILE_NAMES = {
    "django":"django",
    "django.request":"django_request",
    "django.server":"django_server",
    "django.template":"django_template",
    "django.db.backends":"django_db",
    "django.utils.autoreload":"django_autoreload",
    "django.contrib.auth":"django_auth",
    "django.contrib.gis":"django_gis",
    "django.dispatch":"django_dispatch",
    "django.security.*":"django_security",
    "django.db.backends.schema":"django_db_schema",
    "django.contrib.sessions":"django_session",
}
class LoggerGenerator():
    def dict_to_str(self, loggers, indent=12):
            import pprint
            return pprint.pformat(loggers, indent=indent)
    def generate_logging_config(self, logger_details):
        """Generate a Django LOGGING config string with lesson_app style."""
        handler_map = {
            "FileHandler" : "handlers.TimedRotatingFileHandler"
        }
        loggers_str = ""
        handlers_str = ""
        handlers = {}
        handler_count = 1
        for logger in logger_details:
            handler_names = set()
            for handler in logger['handler_type']:
                handler_class = f"logging.{handler_map[handler] if logger.get('time_rotation') and handler in handler_map else handler}"
                interval = logger.get('interval',0) if handler in handler_map else 0
                backup_count = logger.get('backup_counts',0) if handler in handler_map else 0
                current_config = (handler_class,logger['level'],interval,backup_count)
                logger_name = LOGGER_FILE_NAMES[logger['name']] if logger['name'] in LOGGER_FILE_NAMES else logger['name']
                if current_config not in handlers or handler == "FileHandler":
                    handler_name = f"handler{handler_count}"
                    handlers_str += (
                        f"        '{handler_name}': {{\n"
                        f"            'level': '{logger['level'].upper()}',\n"
                        f"            'class': '{handler_class}',\n"
                    )
                    if handler == "FileHandler":
                        handlers_str += (
                            f"            'filename': os.path.join(LOG_DIR, '{logger_name}.log'),\n"
                        )
                    if logger.get('time_rotation') and handler in handler_map:
                        handlers_str += (
                            f"            'when': 'D',\n"
                            f"            'interval': {interval},\n"
                            f"            'backupCount': {backup_count},\n"
                        )

                    handlers_str += (
                        f"            'formatter': 'default_formatter',\n"
                        f"        }},\n"
                    )
                    handlers[current_config] = handler_name
                    handler_count += 1
                handler_names.add(handlers[current_config])

            handlers_list_str = ", ".join(f"'{name}'" for name in handler_names)
            loggers_str += (
                f"        '{logger['name'].lower()}': {{\n"
                f"            'handlers': [{handlers_list_str}],\n"
                f"            'level': '{logger['level'].upper()}',\n"
                f"            'propagate': False,\n"
                f"        }},\n"
            )
        logging_config = (
            "import os\n"
            "LOG_DIR = os.path.join(BASE_DIR, 'logs')\n"
            "os.makedirs(LOG_DIR, exist_ok=True)\n\n"
            "LOGGING = {\n"
            "    'version': 1,\n"
            "    'disable_existing_loggers': False,\n\n"
            "    'formatters': {\n"
            "        'default_formatter': {\n"
            "            'format': (\n"
            "                '%(asctime)s [%(levelname)-8s] '\n"
            "                '(%(pathname)s/%(funcName)s.%(lineno)d) %(message)s'\n"
            "            ),\n"
            "            'datefmt': '%Y-%m-%d %H:%M:%S',\n"
            "        },\n"
            "    },\n\n"
            "    'handlers': {\n"
            f"{handlers_str}"
            "    },\n\n"
            "    'loggers': {\n"
            f"{loggers_str}"
            "    },\n"
            "}\n"
        )

        return logging_config