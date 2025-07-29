import pytest
from envix.cli.app import App


class TestApp:
    def test_app(self):
        with pytest.raises(SystemExit):
            App.run(["--help"])
