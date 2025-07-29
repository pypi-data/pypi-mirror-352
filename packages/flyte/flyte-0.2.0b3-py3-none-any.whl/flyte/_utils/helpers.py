import os
import string
import typing
from pathlib import Path


def load_proto_from_file(pb2_type, path):
    with open(path, "rb") as reader:
        out = pb2_type()
        out.ParseFromString(reader.read())
        return out


def write_proto_to_file(proto, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as writer:
        writer.write(proto.SerializeToString())


def str2bool(value: typing.Optional[str]) -> bool:
    """
    Convert a string to a boolean. This is useful for parsing environment variables.
    :param value: The string to convert to a boolean
    :return: the boolean value
    """
    if value is None:
        return False
    return value.lower() in ("true", "t", "1")


BASE36_ALPHABET = string.digits + string.ascii_lowercase  # 0-9 + a-z (36 characters)


def base36_encode(byte_data: bytes) -> str:
    """
    This function expects to encode bytes coming from an hd5 hash function into a base36 encoded string.
    md5 shas are limited to 128 bits, so the maximum byte value should easily fit into a 30 character long string.
    If the input is too large howeer
    """
    # Convert bytes to a big integer
    num = int.from_bytes(byte_data, byteorder="big")

    # Convert integer to base36 string
    if num == 0:
        return BASE36_ALPHABET[0]

    base36 = []
    while num:
        num, rem = divmod(num, 36)
        base36.append(BASE36_ALPHABET[rem])
    return "".join(reversed(base36))


# does not work at all in the setuptools case. see old flytekit editable installs
def get_cwd_editable_install() -> typing.Optional[Path]:
    """
    This helper function is incomplete since it hasn't been tested with all the package managers out there,
    but the intention is that it returns the source folder for an editable install if the current working directory
    is inside the editable install project - if the code is inside an src/ folder, and the cwd is a level above,
    it should still work, returning the src/ folder. If cwd is the src/ folder, this should return the same.

    The idea is that the return path will be used to determine the relative path for imported modules when building
    the code bundle.

    :return:
    """
    import site

    from flyte._logging import logger

    egg_links = [Path(p) for p in Path(site.getsitepackages()[0]).glob("*.egg-link")]
    pth_files = [Path(p) for p in Path(site.getsitepackages()[0]).glob("*.pth")]

    if not egg_links and not pth_files:
        logger.debug("No editable installs found.")
        return None

    editable_installs = []
    egg_links.extend(pth_files)
    for file in egg_links:
        with open(file, "r") as f:
            line = f.readline()
            if line:
                # Check if the first line is a directory
                p = Path(line)
                if p.is_dir():
                    editable_installs.append(p)
    logger.debug(f"Editable installs: {editable_installs}")

    # check to see if the current working directory is in any of the editable installs
    # including if the current folder is the root folder, one level up from the src and contains
    # the pyproject.toml file.
    # Two scenarios to consider
    #   - if cwd is nested inside the editable install folder.
    #   - if the cwd is exactly one level above the editable install folder.
    cwd = Path.cwd()
    for install in editable_installs:
        # child.is_relative_to(parent) is True if child is inside parent
        if cwd.is_relative_to(install):
            return install
        else:
            # check if the cwd is one level above the install folder
            if install.parent == cwd:
                # check if the install folder contains a pyproject.toml file
                if (cwd / "pyproject.toml").exists() or (cwd / "setup.py").exists():
                    return install  # note we want the install folder, not the parent

    return None
