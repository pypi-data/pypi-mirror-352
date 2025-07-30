"""Tests to verify package installation and functionality."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


def safe_subprocess_run(
    cmd: list[str],
    *,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Safely run a subprocess command with proper security settings.
    
    Args:
        cmd: List of command arguments
        capture_output: Whether to capture stdout and stderr
        text: Whether to return output as text
        check: Whether to check return code
        env: Environment variables to use
        
    Returns:
        CompletedProcess instance
        
    Raises:
        subprocess.CalledProcessError: If check=True and process returns non-zero
    """
    return subprocess.run(  # noqa: S603
        cmd,
        capture_output=capture_output,
        text=text,
        check=check,
        shell=False,  # Never use shell=True for security
        env=env,
    )


def test_package_installation():
    """Test that the package can be installed via pip."""
    # Create a temporary directory for the virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "venv"
        dist_dir = Path(temp_dir) / "dist"
        
        # Create a virtual environment
        safe_subprocess_run([sys.executable, "-m", "venv", str(venv_path)])
        
        # Get the python executable path
        if os.name == "nt":  # Windows
            python_path = venv_path / "Scripts" / "python"
        else:  # Unix-like
            python_path = venv_path / "bin" / "python"
        
        # Install build tools in the virtual environment
        # We need to download these wheels first and store them in the repo
        build_wheel = Path("tests/wheels/build-1.0.3-py3-none-any.whl")
        if not build_wheel.exists():
            pytest.skip("Build wheel not found. Please download it and place in tests/wheels/")
        
        safe_subprocess_run(
            [str(python_path), "-m", "pip", "install", "--no-index", str(build_wheel)]
        )
        
        # Build the distribution package
        safe_subprocess_run(
            [str(python_path), "-m", "build", "--outdir", str(dist_dir)]
        )
        
        # Find the wheel file
        wheel_files = list(dist_dir.glob("*.whl"))
        assert len(wheel_files) == 1, "Expected exactly one wheel file"
        wheel_file = wheel_files[0]
        
        # Install the package from the wheel without dependencies
        safe_subprocess_run(
            [str(python_path), "-m", "pip", "install", "--no-deps", str(wheel_file)]
        )
        
        # Install dependencies from local wheels
        wheels_dir = Path("tests/wheels")
        if not wheels_dir.exists():
            pytest.skip("Dependency wheels not found. Please download them and place in tests/wheels/")
        
        # Install each dependency wheel
        for wheel in wheels_dir.glob("*.whl"):
            if wheel.name != build_wheel.name:  # Skip the build wheel
                safe_subprocess_run(
                    [str(python_path), "-m", "pip", "install", "--no-index", str(wheel)]
                )
        
        # Verify the package is installed
        result = safe_subprocess_run(
            [str(python_path), "-m", "pip", "list"]
        )
        assert "trustwise" in result.stdout
        
        # Test importing the package with a clean Python environment
        env = os.environ.copy()
        env["PYTHONPATH"] = ""  # Clear PYTHONPATH to ensure isolation
        env["PYTHONHOME"] = ""  # Clear PYTHONHOME to ensure isolation
        
        # Test importing the package
        safe_subprocess_run(
            [str(python_path), "-c", "import trustwise"],
            env=env
        )
        
        # Test importing specific modules
        safe_subprocess_run(
            [str(python_path), "-c", "from trustwise.sdk import TrustwiseSDK"],
            env=env
        )
        
        # Verify no system packages are being used
        try:
            result = safe_subprocess_run(
                [str(python_path), "-c", "import sys; print('\\n'.join(sys.path))"],
                env=env
            )
            # Ensure no system paths are in sys.path
            paths = result.stdout.strip().split("\n")
            assert not any("site-packages" in path for path in paths), "Found system site-packages in sys.path"
            assert any(str(venv_path) in path for path in paths), "Virtual environment path not found in sys.path"
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to check sys.path: {e.stderr}")


def test_package_metadata():
    """Test that package metadata is correctly set."""
    import trustwise
    
    # Test version
    assert hasattr(trustwise, "__version__")
    assert isinstance(trustwise.__version__, str)
    
    # Test package name
    assert trustwise.__name__ == "trustwise"
    
    # Test that main classes are importable
    from trustwise.sdk import TrustwiseSDK
    from trustwise.sdk.config import TrustwiseConfig
    
    assert TrustwiseSDK is not None
    assert TrustwiseConfig is not None 