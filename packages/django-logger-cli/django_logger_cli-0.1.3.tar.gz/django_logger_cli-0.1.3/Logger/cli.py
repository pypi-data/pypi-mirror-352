# loggen/cli.py

import click
from Logger.prompts import LoggerPrompts
from Logger.logger_generator import LoggerGenerator, BASIC_LOGGER
from Logger.injector import LoggerInjector

@click.group(help="🛠️ A CLI tool to generate Django-style logger configurations.")
def cli():
    """🎯 Django Logger CLI - Configure Django logging without writing code."""
    pass

@cli.command()
@click.option('--basic-config', is_flag=True, help="Use default logging config without prompts")
def init(basic_config):
    LoggerInit(basic_config=basic_config)

class LoggerInit(LoggerPrompts,LoggerGenerator,LoggerInjector):
    """🔧 Initializes Django logging configuration."""
    def __init__(self,basic_config=False):
        click.echo("\n🚀 Django Logger Initialization Started")
        if basic_config:
            click.secho("⚙️ Generating basic logging config.\n", fg="cyan")
            settings_path = self.ask_settings_path()
            injected = self.inject_logging_config(BASIC_LOGGER, settings_path)
            injected = True
        else:
            # Step 1: Collect logger configurations
            logger_details = self.get_logger_details()

            # Step 3: Ask for settings.py path
            settings_path = self.ask_settings_path()

            # # Step 4: Generate LOGGING dictionary (Python code as string)
            logging_config = self.generate_logging_config(logger_details)

            print(logging_config)

            # # Step 5: Inject into settings.py
            injected = self.inject_logging_config(logging_config, settings_path)
            injected = True

        # Step 6: Finish
        if injected:
            click.secho("\n✅ Django logging setup completed successfully!", fg="green")
            click.secho("🔍 Check your settings.py to see the added LOGGING config.\n", fg="yellow")
        else:
            click.secho("\n❌ Failed to inject logging config. Check if path is correct.", fg="red")

if __name__ == "__main__":
    cli()
