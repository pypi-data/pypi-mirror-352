import pprint
import json
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
        existing_handler_names = set()
        handlers = {}
        handler_count = 1
        for logger in logger_details:
            handler_names = set()
            for handler in logger['handler_type']:
                handler_class = f"logging.{handler_map[handler] if logger.get('time_rotation') and handler in handler_map else handler}"
                interval = logger.get('interval',0) if handler in handler_map else 0
                backup_count = logger.get('backup_counts',0) if handler in handler_map else 0
                current_config = (handler_class,logger['level'],interval,backup_count)
                if current_config not in handlers:
                    handler_name = f"handler{handler_count}"
                    handler_count += 1
                    handlers_str += (
                        f"        '{handler_name}': {{\n"
                        f"            'level': '{logger['level'].upper()}',\n"
                        f"            'class': '{handler_class}',\n"
                        f"            'filename': os.path.join(LOG_DIR, '{logger['level'].lower()}.log'),\n"
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
                    existing_handler_names.add(handler_name)
                handler_names.add(handlers[current_config])

            handlers_list_str = ", ".join(f"'{name}'" for name in handler_names)
            loggers_str += (
                f"        '{logger['name']}': {{\n"
                f"            'handlers': [{handlers_list_str}],\n"
                f"            'level': '{logger['level'].upper()}',\n"
                f"        }},\n"
            )
        logging_config = (
            "import os\n"
            "LOG_DIR = os.path.join(BASE_DIR, 'logs')\n\n"
            "LOGGING = {\n"
            "    'version': 1,\n"
            "    'disable_existing_loggers': False,\n\n"
            "    'formatters': {\n"
            "        'default_formater': {\n"
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