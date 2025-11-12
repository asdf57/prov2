import os

def get_env_var_or_bust(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Environment variable {var_name} is not set.")
    return value

CONCOURSE_URL = get_env_var_or_bust("CONCOURSE_URL")
CONCOURSE_USERNAME = get_env_var_or_bust("CONCOURSE_USERNAME")
CONCOURSE_PASSWORD = get_env_var_or_bust("CONCOURSE_PASSWORD")
CONCOURSE_TEAM = get_env_var_or_bust("CONCOURSE_TEAM")
CONCOURSE_COMMANDS_PIPELINE = get_env_var_or_bust("CONCOURSE_COMMANDS_PIPELINE")
CONCOURSE_COMMANDS_FILE = get_env_var_or_bust("CONCOURSE_COMMANDS_FILE")
