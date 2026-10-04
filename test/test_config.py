from pathlib import Path

from cofe.config.configure import PackageConfigParser


def test_package_config_parser_initializes_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"

    config = PackageConfigParser(config_path)

    assert config.has_section("env")
    assert config.has_section("available")
    assert config.has_section("active")
    assert config["env"]["extension"] == ".y"
    assert config["env"]["test"] == "False"


def test_package_config_parser_tracks_transformers(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config = PackageConfigParser(config_path)
    plugin = tmp_path / "plugin.py"
    plugin.write_text("class ExampleTransform:\n    pass\n", encoding="utf-8")

    config.add_transformer("ExampleTransform", plugin)
    config.add_active("ExampleTransform")

    assert config.get_available()["ExampleTransform"] == str(plugin)
    assert "ExampleTransform" in config.get_active()


def test_package_config_parser_can_restore_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    config = PackageConfigParser(config_path)
    config.set_default("extension", ".custom")
    config.restore()

    assert config["env"]["extension"] == ".y"
