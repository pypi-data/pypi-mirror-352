import tomlkit
from commitizen.providers.base_provider import TomlProvider
from build_wheel_metadata import prepare_metadata


__author__ = "Dhia Hmila"
__version__ = "0.1.0"
__all__ = ["WheelProvider"]


class WheelProvider(TomlProvider):
    """
    Wheel's Metadata-based version provider
    """

    filename = "pyproject.toml"

    def set_version(self, version: str):
        document = tomlkit.parse(self.file.read_text())
        if self.is_dynamic(document):
            return

        self.set(document, version)
        self.file.write_text(tomlkit.dumps(document))

    def is_dynamic(self, document: tomlkit.TOMLDocument) -> bool:
        project_meta = document.get("project", {})
        return "version" in project_meta.get("dynamic", []) or (
            "version" not in project_meta
        )

    def get(self, document: tomlkit.TOMLDocument) -> str:
        if self.is_dynamic(document):
            metadata = prepare_metadata(self.file.parent.as_posix())
            return metadata["Version"]

        return document["project"]["version"]  # type: ignore
