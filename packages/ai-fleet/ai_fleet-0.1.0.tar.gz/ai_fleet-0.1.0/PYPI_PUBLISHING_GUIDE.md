# Publishing AI Fleet to PyPI with uv

## Prerequisites

1. **Update pyproject.toml metadata** (✅ Done)
   - Replace "Your Name" and "your.email@example.com" with your actual details
   - Update GitHub URLs to your repository

2. **Create a LICENSE file** (Required)
   ```bash
   # Create MIT LICENSE file (adjust based on your preference)
   cat > LICENSE << 'EOF'
   MIT License

   Copyright (c) 2025 Your Name

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
   EOF
   ```

3. **Create PyPI accounts**
   - Register at https://pypi.org/account/register/
   - Register at https://test.pypi.org/account/register/
   - Generate API tokens for both

## Step 1: Build the Package

```bash
# Build both source distribution and wheel
uv build --no-sources

# This creates files in dist/ directory:
# - ai_fleet-0.1.0-py3-none-any.whl
# - ai_fleet-0.1.0.tar.gz
```

## Step 2: Test on TestPyPI First

```bash
# Set your TestPyPI token
export UV_PUBLISH_TOKEN="your-test-pypi-token"

# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Test installation from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ai-fleet
```

## Step 3: Publish to PyPI

```bash
# Set your PyPI token
export UV_PUBLISH_TOKEN="your-pypi-token"

# Publish to PyPI
uv publish
```

## Step 4: Verify Installation

```bash
# Test that it can be installed
uv run --with ai-fleet --no-project -- fleet --version

# Or with pipx (recommended for CLI tools)
pipx install ai-fleet
fleet --version
```

## Alternative: Using GitHub Actions

For automated publishing, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Build package
        run: uv build --no-sources
      - name: Publish to PyPI
        run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

## Tips

1. **Version Management**: Update version in pyproject.toml before each release
2. **Testing**: Always test on TestPyPI first
3. **Tokens**: Use project-specific tokens, not account-wide tokens
4. **Retry**: If upload fails midway, run the same command again (PyPI ignores existing files)

## Troubleshooting

- **Token Issues**: Ensure token starts with `pypi-` and has correct permissions
- **Build Errors**: Run `uv build` without `--no-sources` to debug
- **Import Errors**: Check that all dependencies are listed in pyproject.toml