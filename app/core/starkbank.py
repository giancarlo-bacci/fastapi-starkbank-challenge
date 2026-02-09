import logging
from pathlib import Path

import starkbank
from app.core.config import settings

logger = logging.getLogger(__name__)
_initialized = False


def get_starkbank():
    global _initialized

    if _initialized:
        return starkbank

    # 1) Prefer env var (cloud / Render)
    if settings.starkbank_private_key:
        private_key = settings.starkbank_private_key
        logger.info("StarkBank initialized using private key from environment")

    # 2) Fallback para arquivo (local/dev)
    elif settings.starkbank_private_key_path:
        private_key = Path(settings.starkbank_private_key_path).read_text()
        logger.info("StarkBank initialized using private key from file")

    else:
        raise RuntimeError(
            "Missing StarkBank private key. "
            "Set starkbank_private_key or starkbank_private_key_path."
        )

    user = starkbank.Project(
        environment=settings.starkbank_environment,
        id=settings.starkbank_project_id,
        private_key=private_key,
    )

    starkbank.user = user
    _initialized = True

    return starkbank
