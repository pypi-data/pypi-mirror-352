import os
from pathlib import Path

from envix.envname import ENVIX_CONFIG_DIR
from pytest import fixture

from tests.config_builder import ConfigV1Builder


@fixture(autouse=True)
def setup_env(data_dir: Path) -> None:
    """テスト用の環境変数を設定する。"""
    os.environ[ENVIX_CONFIG_DIR] = os.fspath(data_dir)


@fixture
def data_dir() -> Path:
    return Path(__file__).parent.joinpath("data")


@fixture
def config_builder() -> ConfigV1Builder:
    return ConfigV1Builder()
