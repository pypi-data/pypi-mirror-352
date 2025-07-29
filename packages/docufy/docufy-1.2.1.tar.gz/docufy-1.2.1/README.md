# Docufy: Automated README Generation with Gemini Pro

Docufy is a command-line tool designed to automatically generate comprehensive README files for your software projects using the power of Google's Gemini Pro model. It analyzes your project's source code and creates a well-structured README, saving you time and effort in documenting your work.

Project's GitHub: https://github.com/AnozieChibuike/docufy

## Installation

1.  **Install the package:**

    ```bash
    pip install docufy
    ```

2.  **Set up your Gemini API key:**

    You'll need a Google Gemini API key to use Docufy. You can provide it in one of two ways:

    *   Using the `--apikey` flag when running Docufy.
    *   Setting the `GEMINI_API_KEY` environment variable.

## Usage

To generate a README for your project, run the following command:

```bash
docufy --path <project_path> --out <output_path> --apikey <your_api_key>
```

*   `<project_path>`: The path to your project's root directory.
*   `<output_path>`: The desired path for the generated README file (e.g., `README.md`). Defaults to `README.md` in the current directory if not provided.
*   `<your_api_key>`: Your Google Gemini API key.

**Example:**

```bash
docufy --path my_project --out README.md --apikey AIzaSy...
```

**Optional Arguments:**

*   `--include <extensions>`: Specify file extensions to include in the analysis (e.g., `.py`, `.js`). Defaults to `.py`.  Use multiple `--include` flags to include multiple extensions. currently supports only python and javascript files... except you explicitly set other file types
*   `--exclude <files/folders>`:  Specify files or folders to exclude from the analysis (e.g., `__init__.py`, `tests/`).  Use multiple `--exclude` flags to exclude multiple files or folders.
*   `--model <model_name>`: Specify the Gemini model to use. Defaults to `gemini-2.0-flash`.

## Features Overview

*   **Automated README Generation:** Generates a comprehensive README file based on your project's source code.
*   **Gemini Pro Integration:** Leverages the power of Google's Gemini Pro model for intelligent summarization and documentation.
*   **Customizable Inclusion/Exclusion:**  Control which files and folders are included or excluded from the analysis.
*   **.readmeignore Support:**  Uses a `.readmeignore` file (similar to `.gitignore`) to specify files and folders to exclude.
*   **Clear and Concise Output:**  Generates a well-structured README in Markdown format.

## File Structure Summary

*   `docufy/generate_readme.py`: Contains the core logic for generating the README file.  This file handles file processing, summarization using Gemini Pro, and output formatting.
*   `docufy/__init__.py`:  Defines the command-line interface using `argparse` and orchestrates the README generation process.

## Configuration

### The `.readmeignore` File

Docufy uses a `.readmeignore` file in your project's root directory to specify files and folders that should be excluded from the README generation process.  The `.readmeignore` file follows the same syntax as `.gitignore`.

**Example `.readmeignore`:**

```
# Ignore dependency directories
node_modules/
.venv/

# Ignore log files
*.log

# Ignore test files
tests/
```

Docufy automatically creates a default `.readmeignore` file in your project's root directory if one doesn't exist.  This file includes common exclusions like dependency directories, build outputs, and log files. You can customize this file to refine your exclusions.

## Important Notes

*   Ensure your Gemini API key is properly configured.
*   The quality of the generated README depends on the clarity and structure of your source code.
*   Consider reviewing and editing the generated README to ensure accuracy and completeness.