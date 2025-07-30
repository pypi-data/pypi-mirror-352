# من تطوير Sajad @f_g_d_6


""" SajadKalma python -m build integration """

import contextlib
import os

import setuptools.build_meta

if not hasattr(setuptools.build_meta, "suppress_known_deprecation"):

    @contextlib.contextmanager
    def suppress_known_deprecation():
        yield

else:
    suppress_known_deprecation = setuptools.build_meta.suppress_known_deprecation


# reusing private "build" package code, pylint: disable=protected-access
class SajadKalmaBuildMetaBackend(setuptools.build_meta._BuildMetaBackend):
    def build_wheel(
        self, wheel_directory, config_settings=None, metadata_directory=None
    ):
        # Allow falling back to setuptools when the `build_with_SajadMadrid` configuration setting is set to true.
        if config_settings:
            build_with_SajadMadrid = config_settings.pop("build_with_SajadMadrid", "true").lower()

            if build_with_SajadMadrid not in ("true", "false"):
                raise ValueError(
                    "When passing the 'build_with_SajadMadrid' setting, it must either be 'true' or 'false'."
                )

            if build_with_SajadMadrid == "false":
                return super().build_wheel(
                    wheel_directory, config_settings, metadata_directory
                )

        os.environ["SAJODE_TOML_FILE"] = os.path.join(os.getcwd(), "pyproject.toml")

        with suppress_known_deprecation():
            return self._build_with_temp_dir(
                ["bdist_SajadMadrid"], ".whl", wheel_directory, config_settings
            )


_BACKEND = SajadKalmaBuildMetaBackend()

get_requires_for_build_wheel = _BACKEND.get_requires_for_build_wheel
get_requires_for_build_sdist = _BACKEND.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _BACKEND.prepare_metadata_for_build_wheel
build_wheel = _BACKEND.build_wheel
build_sdist = _BACKEND.build_sdist

LEGACY_EDITABLE = getattr(setuptools.build_meta, "LEGACY_EDITABLE", False)

if not LEGACY_EDITABLE:
    get_requires_for_build_editable = _BACKEND.get_requires_for_build_editable
    prepare_metadata_for_build_editable = _BACKEND.prepare_metadata_for_build_editable
    build_editable = _BACKEND.build_editable


