class LoggerInjector():
    def inject_logging_config(self,logger,settings_path):
        try:
            with open(settings_path, "a") as f:
                f.write("\n\n" + logger)
            print(f"✅ Logger successfully injected into: {settings_path}")
        except Exception as e:
            print(f"❌ Failed to inject logger: {e}")