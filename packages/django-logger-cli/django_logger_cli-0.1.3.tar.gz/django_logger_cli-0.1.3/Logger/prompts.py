import os
import click
AVAILABLE_LOGGERS = [
    "django",
    "django.request",
    "django.server",
    "django.template",
    "django.db.backends",
    "django.utils.autoreload",
    "django.contrib.auth",
    "django.contrib.gis",
    "django.dispatch",
    "django.security.*",
    "django.db.backends.schema",
    "django.contrib.sessions",
    "custom"
]
HANDLER_OPTIONS = ["FileHandler", "StreamHandler"]

class LoggerPrompts():
    def get_logger_details(self):
        """
        Interactively collect logger details from the user.
        Returns a list of dicts, e.g., [{'name': 'django', 'level': 'INFO'}, ...]
        """
        logger_details = []
        logger_names = set()
        try:
            num_loggers = click.prompt("🔢 How many loggers do you want to configure?", type=int, default=1)
            for i in range(num_loggers):
                context = {}
                click.secho(f"\n🛠️ Configuring Logger #{i + 1}", fg="cyan")
                level = click.prompt(
                    "📊 Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                    default="INFO",
                    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False)
                )
                context["level"] = level
                click.secho("🗂️ Available Logger Names:", fg="cyan")
                for idx, logger_name in enumerate(AVAILABLE_LOGGERS, start=1):
                    click.secho(f"{idx}. {logger_name}", fg="blue")

                while True:
                    choice = click.prompt("🔍 Select a logger by number (e.g., 1)", type=int)
                    if 1 <= choice <= len(AVAILABLE_LOGGERS):
                        selected_logger = AVAILABLE_LOGGERS[choice - 1]
                        if selected_logger in logger_names:
                            click.secho("❌ Logger already taken.", fg="red")
                            continue
                        else:
                            if selected_logger == "custom":
                                custom_name = click.prompt("✏️ Enter your custom logger name", type=str)
                                custom_name.strip()
                                if custom_name in logger_names:
                                    click.secho("❌ Logger already taken.", fg="red")
                                    continue
                                else:
                                    context["name"] = custom_name
                                    logger_names.add(custom_name)
                                    break
                            else:
                                context["name"] = selected_logger
                                logger_names.add(selected_logger)
                                break
                    else:
                        click.secho("❌ Invalid choice. Please select a valid option.", fg="red")

                click.secho("\n🔧 Available Handler Types:", fg="cyan")
                for idx, handler in enumerate(HANDLER_OPTIONS, start=1):
                    click.secho(f"{idx}. {handler}", fg="blue")

                while True:
                    num_handlers = click.prompt("🔢 How many handlers do you want to configure? (1 or 2)", type=int)
                    if 1 <= num_handlers <= 2:
                        break
                    click.secho("❌ Please enter either 1 or 2.", fg="red")

                selected_handlers = set()
                while len(selected_handlers) < num_handlers:
                    handler_choice = click.prompt(f"📌 Select handler {len(selected_handlers)+1} by number (1 for FileHandler, 2 for StreamHandler)", type=int)
                    if 1 <= handler_choice <= len(HANDLER_OPTIONS):
                        selected_handler = HANDLER_OPTIONS[handler_choice - 1]
                        if selected_handler in selected_handlers:
                            click.secho("❌ Handler already configured select another.", fg="red")
                            continue
                        selected_handlers.add(HANDLER_OPTIONS[handler_choice - 1])
                    else:
                        click.secho("❌ Invalid choice. Please select 1 or 2.", fg="red")

                context['handler_type'] = selected_handlers
                context['time_rotation'] = False

                if "FileHandler" in selected_handlers:
                    need_time_rotation = click.confirm("🔢 Would you like to enable time-based log rotation?", default=False)
                    if need_time_rotation:
                        interval = click.prompt("- Please specify the rotation interval (in days)?", type=int, default=30)
                        backup_counts = click.prompt("- Please specify the number of backup files to keep?", type=int, default=5)
                        context['time_rotation'] = True
                        context['interval'] = interval
                        context['backup_counts'] = backup_counts

                logger_details.append(context)
        except (click.Abort, KeyboardInterrupt):
            click.secho("\n❌ Logger config cancelled by user.", fg="red")
            exit()

        return logger_details

    def create_logs_folder(self):
        logs_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

    def ask_settings_path(self):
        while True:
            settings_path = click.prompt("🔢 Please provide the django settings path")
            if settings_path and os.path.exists(settings_path):
                return settings_path
            click.secho("\n❌ Please provide a valid path.", fg="yellow")