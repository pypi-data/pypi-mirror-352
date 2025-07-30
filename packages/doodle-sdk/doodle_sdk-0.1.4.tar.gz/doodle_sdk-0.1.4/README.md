# doodle-sdk

# Docs

Run the MkDocs development server to view your documentation locally:

``` bash
pip3 install requirements.txt
mkdocs serve
```

Merge "main" branch into "docs" branch to update documentation to main

# Legal
This project is not currently licensed for public or commercial use. Please contact me if you are interested in obtaining a license.
This software is proprietary and not open source. No rights are granted to use, copy, modify, or distribute this code without explicit written permission from the author.

# Development

Remove all the build files:
```bash
./clean.sh
```

Installing the pip package run:
```bash
pip3 install -e .
```

# Manually building the package
To manually build the package, follow these steps:

1. Ensure you have all the necessary dependencies installed:
    ```bash
    pip3 install -r requirements.txt
    ```

2. Clean any previous builds:
    ```bash
    ./clean.sh
    ```

3. Build the package:
    ```bash
    python3 setup.py sdist bdist_wheel
    ```

4. Verify the package:
    ```bash
    twine check dist/*
    ```

5. Optionally, upload the package to PyPI:
    ```bash
    twine upload dist/*
    ```
