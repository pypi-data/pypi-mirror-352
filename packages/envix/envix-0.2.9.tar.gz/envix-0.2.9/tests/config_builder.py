from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Self, cast

from envix.config.v1.config import ConfigV1
from envix.config.v1.envix_v1 import EnvixV1
from envix.config.v1.envs.raw_envs_v1 import RawEnvsV1


class ConfigV1Builder:
    def __init__(self):
        self.config = ConfigV1(envix=EnvixV1(version=1), envs=[])
        self._raw_envs_index: int | None = None

    def add_include(self, path: Path | str) -> Self:
        self.config.includes.append(Path(path))
        return self

    def add_env(self, envname: str, secret: str) -> Self:
        if not self._raw_envs_index:
            self._raw_envs_index = len(self.config.envs)
            self.config.envs.append(RawEnvsV1(type="Raw", items={}))

        raw_env = cast(RawEnvsV1, self.config.envs[self._raw_envs_index])
        raw_env.items[envname] = secret

        return self

    def build(self) -> ConfigV1:
        return self.config

    def chain(self) -> Self:
        return self

    @contextmanager
    def build_file(self):
        with NamedTemporaryFile("w", suffix=".json") as f:
            f.write(self.config.model_dump_json())
            f.seek(0)
            yield f
