import os
from .app_config import AppConfig, AppConfigError
from .secrets import SecretRetriever, SecretNotFound
from .dependencies import bake_deployment_image


def deploy_validations(app_config: AppConfig, cache_dir: str, logger):

    # First check if the secrets for the app exist.
    app_secrets = app_config.get("secrets", [])
    secret_retriever = SecretRetriever()
    for secret in app_secrets:
        try:
            secret_retriever.get_secret_as_dict(secret)
        except SecretNotFound:
            raise AppConfigError(f"Secret not found: {secret}")

    # TODO: Next check if the compute pool exists.
    logger("🍞 Baking Docker Image")
    baking_status = bake_deployment_image(
        app_config=app_config,
        cache_file_path=os.path.join(cache_dir, "image_cache"),
        logger=logger,
    )
    app_config.set_state(
        "image",
        baking_status.resolved_image,
    )
    app_config.set_state("python_path", baking_status.python_path)
    logger("🐳 Using The Docker Image : %s" % app_config.get_state("image"))


def run_validations(app_config: AppConfig):
    pass
