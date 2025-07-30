import platform
from pathlib import Path

import pytest
from cmake_coverage import cmake_script

base_dir = Path(__file__).parent
scripts_dir = base_dir / "cmake_scripts"

lookup_env = {
    "CMAKE_PREFIX_PATH": str(base_dir / "data" / "projects"),
    "CMTPROJECTPATH": str(base_dir / "data" / "projects_cmt"),
    "BINARY_TAG": "x86_64-slc0-gcc99-opt",
}
toolchain_env = {
    "CMAKE_PREFIX_PATH": str(base_dir / "data" / "toolchain"),
    "BINARY_TAG": "x86_64-slc0-gcc99-opt",
}

all_tests = {
    "binary_tag_utils": {},
    "functional_utils": {},
    "heptools_parsing": {
        "CMAKE_PREFIX_PATH": str(base_dir / "data" / "heptools"),
        "BINARY_TAG": "x86_64-slc0-gcc99-opt",
        "CMTPROJECTPATH": None,
    },
    "no_use": lookup_env,
    "simple_use": lookup_env,
    "chain": lookup_env,
    "diamond": lookup_env,
    "with_tools": lookup_env,
    "with_chained_tools": lookup_env,
    "version_selection": lookup_env,
    "atlas_convention": lookup_env,
    "special_conventions": lookup_env,
    "guess_toolchain": lookup_env,
    "toolchain_extensions_min": toolchain_env,
    "toolchain_extensions": toolchain_env,
    "toolchain_extensions_multi": toolchain_env,
}


@pytest.mark.parametrize("name", all_tests)
def test_cmake(name, monkeypatch):
    """
    Test the binary tag utilities in CMake.
    This test checks if the binary tag utilities work correctly.
    """
    # Set up environment variables for the test
    for key, value in all_tests[name].items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)

    if name == "heptools_parsing":
        if Path("/cvmfs/projects.cern.ch/intelsw/psxe").exists():
            pytest.skip(
                "Can't run heptools_parsing test when /cvmfs/projects.cern.ch is mounted"
            )
    elif name in {
        "guess_toolchain",
        "special_conventions",
        "toolchain_extensions",
        "toolchain_extensions_min",
        "toolchain_extensions_multi",
    }:
        pytest.xfail("Unknown but expected failure.")
    elif platform.system() == "Darwin" and name == "binary_tag_utils":
        pytest.xfail("Known issue on macOS for binary_tag_utils.")

    out, err, returncode = cmake_script(
        scripts_dir / f"test_{name}.cmake", cwd=base_dir
    )

    print("---------- stdout ----------")
    print(out)
    print("---------- stderr ----------")
    print(err)

    assert returncode == 0
