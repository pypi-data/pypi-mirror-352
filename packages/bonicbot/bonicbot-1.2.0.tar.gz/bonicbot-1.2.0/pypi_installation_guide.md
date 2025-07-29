# Complete Instructions for Creating and Uploading BonicBot Library to PyPI

## Step 1: Create the Project Structure

Create the following directory structure:

```
bonicbot/
├── bonicbot/
│   ├── __init__.py
│   ├── controller.py
│   ├── gui.py
│   └── test_installation.py
├── examples/
│   ├── basic_control.py
│   ├── head_movements.py
│   ├── hand_gestures.py
│   └── base_movement.py
├── docs/
│   └── API.md
├── tests/
│   ├── __init__.py
│   └── test_controller.py
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── MANIFEST.in
└── requirements.txt
```

## Step 2: Set Up Your Development Environment

1. **Install required tools:**
```bash
pip install --upgrade pip setuptools wheel twine build
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip setuptools wheel twine build
```

## Step 3: Prepare Your Package Files

1. **Update personal information** in the following files:
   - `setup.py`: Replace "Your Name" and email
   - `pyproject.toml`: Replace author information and GitHub URLs
   - `README.md`: Update GitHub URLs
   - `LICENSE`: Replace "Your Name" with your actual name

2. **Test your package locally:**
```bash
cd bonicbot
pip install -e .
```

3. **Test the installation:**
```bash
python -c "from bonicbot import BonicBotController; print('Import successful!')"
```

## Step 4: Create PyPI Accounts

1. **Create accounts on:**
   - [PyPI](https://pypi.org/account/register/) (production)
   - [Test PyPI](https://test.pypi.org/account/register/) (testing)

2. **Enable 2FA** (Two-Factor Authentication) on both accounts

3. **Create API tokens:**
   - Go to Account Settings → API tokens
   - Create a token for the entire account
   - Save the token securely (you'll need it for uploading)

## Step 5: Configure Authentication

1. **Create a `.pypirc` file** in your home directory:

**Linux/Mac:** `~/.pypirc`
**Windows:** `%USERPROFILE%\.pypirc`

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_ACTUAL_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_ACTUAL_TESTPYPI_TOKEN_HERE
```

**⚠️ Important:** Replace `YOUR_ACTUAL_PYPI_TOKEN_HERE` with your actual API tokens!

## Step 6: Build Your Package

```bash
cd bonicbot
python -m build
```

This creates:
- `dist/bonicbot-1.0.0.tar.gz` (source distribution)
- `dist/bonicbot-1.0.0-py3-none-any.whl` (wheel distribution)

## Step 7: Test Upload (Recommended)

1. **Upload to Test PyPI first:**
```bash
python -m twine upload --repository testpypi dist/*
```

2. **Test installation from Test PyPI:**
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ bonicbot
```

3. **Test your package:**
```bash
python -c "from bonicbot import BonicBotController; print('Test installation successful!')"
```

## Step 8: Upload to Production PyPI

1. **Upload to PyPI:**
```bash
python -m twine upload dist/*
```

2. **Verify upload:**
   - Go to https://pypi.org/project/bonicbot/
   - Check that your package appears correctly

3. **Test installation:**
```bash
pip install bonicbot
```

## Step 9: Verify Installation

Test that everything works:

```bash
# Test basic import
python -c "from bonicbot import BonicBotController, ServoID; print('✓ Import successful')"

# Test GUI command (if tkinter available)
bonicbot-gui --help

# Run an example (adjust port as needed)
python examples/basic_control.py
```

## Step 10: Post-Upload Tasks

1. **Create a GitHub repository** (if you haven't already)
2. **Update GitHub URLs** in your package metadata
3. **Add badges** to your README
4. **Create releases** on GitHub matching your PyPI versions
5. **Write documentation** or wiki pages

## Troubleshooting

### Common Issues and Solutions

1. **Permission denied on serial port:**
```bash
sudo usermod -a -G dialout $USER  # Linux
# Then log out and back in
```

2. **Package name already exists:**
   - Choose a different name (e.g., `bonicbot-controller`)
   - Update all references in setup.py, pyproject.toml, etc.

3. **Build failures:**
```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info/
python -m build
```

4. **Import errors after installation:**
   - Check that all required dependencies are listed in requirements.txt
   - Verify package structure and __init__.py files

5. **Upload failures:**
   - Check your API token is correct
   - Ensure you're not uploading the same version twice
   - Verify your .pypirc file format

### Version Updates

When updating your package:

1. **Update version number** in:
   - `bonicbot/__init__.py` (`__version__`)
   - `setup.py` (if using dynamic versioning from __init__.py)

2. **Build and upload new version:**
```bash
rm -rf dist/
python -m build
python -m twine upload dist/*
```

## Security Best Practices

1. **Never commit API tokens** to version control
2. **Use environment variables** for sensitive data:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
twine upload dist/*
```

3. **Consider using keyring** for token storage:
```bash
pip install keyring
python -m keyring set https://upload.pypi.org/legacy/ __token__
```

## Continuous Integration (Optional)

For automated publishing, you can set up GitHub Actions:

`.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Success Verification

Your package is successfully published when:

1. ✅ It appears on https://pypi.org/project/bonicbot/
2. ✅ `pip install bonicbot` works
3. ✅ `from bonicbot import BonicBotController` works
4. ✅ `bonicbot-gui` command is available
5. ✅ Examples run without import errors

Congratulations! Your BonicBot library is now available for the Python community! 🎉