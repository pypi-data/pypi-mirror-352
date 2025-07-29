import re
import subprocess
from setuptools import Extension, setup
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable

from Cython.Build import cythonize

CBF_SOURCES = [
    "cbflib/src/cbf.c",
    "cbflib/src/cbf_airy_disk.c",
    "cbflib/src/cbf_alloc.c",
    "cbflib/src/cbf_ascii.c",
    "cbflib/src/cbf_binary.c",
    "cbflib/src/cbf_byte_offset.c",
    "cbflib/src/cbf_canonical.c",
    "cbflib/src/cbf_codes.c",
    "cbflib/src/cbf_compress.c",
    "cbflib/src/cbf_context.c",
    "cbflib/src/cbf_copy.c",
    "cbflib/src/cbf_file.c",
    "cbflib/src/cbf_getopt.c",
    "cbflib/src/cbf_lex.c",
    "cbflib/src/cbf_minicbf_header.c",
    "cbflib/src/cbf_nibble_offset.c",
    "cbflib/src/cbf_packed.c",
    "cbflib/src/cbf_predictor.c",
    "cbflib/src/cbf_read_binary.c",
    "cbflib/src/cbf_read_mime.c",
    "cbflib/src/cbf_simple.c",
    "cbflib/src/cbf_string.c",
    "cbflib/src/cbf_stx.c",
    "cbflib/src/cbf_tree.c",
    "cbflib/src/cbf_ulp.c",
    "cbflib/src/cbf_uncompressed.c",
    "cbflib/src/cbf_write.c",
    "cbflib/src/cbf_write_binary.c",
    "cbflib/src/cbf_ws.c",
    "cbflib/src/cbff.c",
    "cbflib/src/fgetln.c",
    "cbflib/src/img.c",
    "cbflib/src/md5c.c",
    # "cbflib/src/cbf_hdf5.c",
    # "cbflib/src/cbf_hdf5_filter.c",
]

PYCBF_ROOT = Path(__file__).parent
CBFLIB_INCLUDE = PYCBF_ROOT / "cbflib" / "include"

# Check we have checked out recursive
if not any(PYCBF_ROOT.joinpath(x).is_file() for x in CBF_SOURCES):
    raise RuntimeError(
        "Error: No CBF sources found. Did you check out --recursive? Run 'git submodule update --init'"
    )

extensions = [
    Extension(
        "pycbf._pycbf",
        sources=["pycbf_wrap.c", *CBF_SOURCES],
        include_dirs=[str(CBFLIB_INCLUDE)],
        define_macros=[
            ("CBF_NO_REGEX", None),
            ("SWIG_PYTHON_STRICT_BYTE_CHAR", None),
        ],
    ),
    *cythonize(
        [
            Extension(
                "pycbf.img",
                sources=["src/pycbf/img.pyx"],
                include_dirs=[
                    str(CBFLIB_INCLUDE),
                    str(PYCBF_ROOT),  # img.c includes from cbflib/include
                ],
            ),
        ]
    ),
]


def hash_files(*files, extra_data: Iterable[str] = None) -> str:
    """
    Generate a combined checksum for a list of files.

    For validating the the generated output file is the latest generated
    from the input sources. Equivalent to running the command:

        sha256sum <files> | sort | sha256sum

    If extra_data is provided - this is treated as though there was a
    file called "extra_contents" containing the iterable items,
    concatenated with newlines, and with a trailing newline.
    """
    hashes = []
    for filename in sorted(files):
        h = sha256()
        h.update(filename.read_bytes().replace(b"\r\n", b"\n"))
        hashes.append(h.hexdigest() + "  " + filename.name)
    if extra_data:
        h = sha256()
        h.update("\n".join(extra_data).encode() + b"\n")
        hashes.append(h.hexdigest() + "  " + "extra_data")
    hashes = sorted(hashes)
    print("\n".join(hashes))
    hashes.append("")
    # Make a combined checksum for this
    h = sha256()
    h.update("\n".join(hashes).encode())
    return h.hexdigest()


def generate_combined_checksum(root):
    # Calculate the combined hash so we know if the source have changed
    swigdir = root / "swig"
    gen_files = [
        swigdir / "make_pycbf.py",
        *swigdir.glob("*.i"),
    ]
    re_toml_hashlines = re.compile("^version ?=|Cython", re.I)
    # Find the pyproject.toml .... poetry might have moved it for editable install
    pyprojects = [root / "pyproject.toml", root / "pyproject.tmp"]
    pyproject = next(iter([x for x in pyprojects if x.is_file()] + [None]))
    if not pyproject:
        raise RuntimeError("Could not find pyproject.toml")
    extra_data = [
        x for x in pyproject.read_text().splitlines() if re_toml_hashlines.search(x)
    ]
    return hash_files(*gen_files, extra_data=extra_data)


def build(setup_kwargs: Dict[str, Any]) -> None:
    # Validate that the SWIG wrappers are generated from the latest
    # sources (if we have them)
    swigdir = PYCBF_ROOT / "SWIG"
    if swigdir.is_dir():
        combined_checksum = generate_combined_checksum(PYCBF_ROOT)
        if (
            combined_checksum not in (PYCBF_ROOT / "pycbf_wrap.c").read_text()
            or combined_checksum
            not in PYCBF_ROOT.joinpath("src", "pycbf", "_wrapper.py").read_text()
        ):
            raise RuntimeError("Error: The SWIG generated sources are out of date")

    # Apply Custom patches to the HDF5 sources - we want to build on upstream
    patches_paths = Path(__file__).parent.joinpath("patches").glob("*.patch")
    if not patches_paths:
        print("Warning: No patches found; assuming sources are pre-patched")
    for patch in sorted(patches_paths):
        print(f"Applying patch {patch}...")
        try:
            with patch.open("rb") as f:
                output = subprocess.check_output(
                    ["patch", "-p1", "-N"], stdin=f, encoding="utf-8"
                )
                print(output)
        except subprocess.CalledProcessError as e:
            print(e.output)
            # We want to ignore this if it was a case of already applied
            if (
                "Skipping patch" not in e.output
                and "Ignoring previously applied" not in e.output
            ):
                raise

    setup_kwargs.update({"ext_modules": extensions})


if __name__ == "__main__":
    setup_kwargs = {}
    build(setup_kwargs)
    setup(**setup_kwargs)
