import logging
import pathlib
import shutil
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_venv_python_executable(venv_dir_path: pathlib.Path) -> str:
    """Gets the path to the Python executable in the virtual environment.
    Args:
        venv_dir_path (pathlib.Path): Path to the virtual environment directory.
    Returns:
        str: Path to the Python executable in the virtual environment.
    """
    if sys.platform == "win32":
        return str(venv_dir_path / "Scripts" / "python.exe")
    else:
        return str(venv_dir_path / "bin" / "python")


def setup_uv_pip(
    venv_dir_path: pathlib.Path = None,
    packages_to_install: list[str] = None,
    python_version: str = None,
    overwrite_existing: bool = True,
) -> str:  # Return type is str, not None
    """
    Creates a virtual environment and installs a list of packages if not already set up.
    Uses 'uv' for environment and package management.
    Args:
        venv_dir_path (pathlib.Path): Path to the virtual environment directory.
        packages_to_install (list[str]): List of packages to install in the virtual environment.
        python_version (str): Python version to use for the virtual environment.
        overwrite_existing (bool): Whether to overwrite an existing virtual environment.
    Returns:
        str: Path to the Python executable in the virtual environment.
    Raises:
        RuntimeError: If setting up the environment or installing packages fails.
        FileNotFoundError: If 'uv' command is not found.
    """

    if venv_dir_path is None:
        raise ValueError("venv_dir_path must be provided")
    if packages_to_install is None:
        raise ValueError("packages_to_install must be provided")
    if python_version is None:
        raise ValueError("python_version must be provided")

    venv_python_executable = get_venv_python_executable(venv_dir_path)
    needs_venv_creation = False

    if venv_dir_path.exists():
        if overwrite_existing:
            logger.info(f"Virtual environment '{venv_dir_path}' exists. Overwriting as requested.")
            try:
                shutil.rmtree(str(venv_dir_path))
            except OSError as e:
                logger.error(f"Error removing existing venv '{venv_dir_path}': {e}")
                raise RuntimeError(f"Failed to remove existing venv '{venv_dir_path}'.") from e
            needs_venv_creation = True
        elif not pathlib.Path(venv_python_executable).exists():
            logger.warning(
                f"Virtual environment '{venv_dir_path}' exists but is incomplete (Python executable missing). "
                f"Recreating."
            )
            try:
                shutil.rmtree(str(venv_dir_path))  # Clean up potentially corrupted venv
            except OSError as e:
                logger.error(f"Error removing incomplete venv '{venv_dir_path}': {e}")
                raise RuntimeError(f"Failed to remove incomplete venv '{venv_dir_path}'.") from e
            needs_venv_creation = True
        else:
            logger.info(
                f"Virtual environment '{venv_dir_path}' already exists and Python executable found. "
                f"Skipping venv creation step."
            )
            # venv exists and is complete, and not overwriting
    else:
        logger.info(f"Virtual environment '{venv_dir_path}' not found. Will create.")
        needs_venv_creation = True

    try:
        if needs_venv_creation:
            logger.info(f"Creating virtual environment at '{venv_dir_path}' using Python {python_version}.")
            # Create venv
            subprocess.run(
                ["uv", "venv", str(venv_dir_path), f"--python={python_version}"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"Virtual environment '{venv_dir_path}' created successfully with Python {python_version}.")
        else:
            logger.info(f"Using existing virtual environment at '{venv_dir_path}'.")

        # Install packages in the venv
        # 'uv pip install' is generally idempotent, so it's okay to run this even if packages might exist.
        # It will ensure they are present.
        for package in packages_to_install:
            # Ensure venv_python_executable is valid before using it for install
            if not pathlib.Path(venv_python_executable).exists():
                # This case should ideally be caught by the venv creation logic if needs_venv_creation was true
                # or by the initial check if needs_venv_creation was false.
                # Adding a safeguard here.
                logger.error(
                    f"Python executable '{venv_python_executable}' not found before package installation. "
                    f"Venv setup might have failed unexpectedly."
                )
                raise RuntimeError(f"Venv Python executable not found at '{venv_python_executable}'.")

            install_command = ["uv", "pip", "install", "--python", venv_python_executable, package]
            logger.info(f"Installing/verifying {package} using command: {' '.join(install_command)}")
            result = subprocess.run(install_command, check=True, capture_output=True, text=True)
            # uv might not produce much stdout for already satisfied requirements, which is fine.
            if result.stdout.strip():
                logger.info(f"Output for {package} installation:\n{result.stdout.strip()}")
            else:
                logger.info(f"{package} is up to date or installed successfully in '{venv_dir_path}'.")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during virtual environment operation for '{venv_dir_path}':")
        logger.error(f"Command: {' '.join(e.cmd)}")
        logger.error(f"Return code: {e.returncode}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr.strip()}")
        raise RuntimeError(f"Failed to set up or update virtual environment '{venv_dir_path}'.") from e
    except FileNotFoundError:
        logger.error("`uv` command not found. Please ensure `uv` is installed and in your PATH.")
        # Re-raise the FileNotFoundError to be handled by the caller if needed,
        # or to clearly indicate 'uv' is the issue.
        raise

    return venv_python_executable
