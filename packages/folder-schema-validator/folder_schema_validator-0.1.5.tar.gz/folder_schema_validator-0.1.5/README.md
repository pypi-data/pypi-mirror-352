# Advanced Folder Schema Validator

A comprehensive Python tool for defining folder structure blueprints and validating existing folder structures against those blueprints. This unified validator supports advanced features including wildcards, regex patterns, conditional requirements, custom validators, and performance optimizations.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [When to Use](#when-to-use)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [Schema Format](#schema-format)
  - [Basic Schema](#basic-schema)
  - [Advanced Schema](#advanced-schema)
  - [Wildcard Patterns](#wildcard-patterns)
- [Validation Modes](#validation-modes)
- [Custom Validators](#custom-validators)
- [Performance Optimization](#performance-optimization)
- [Schema Generation](#schema-generation)
- [Real-World Examples](#real-world-examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Folder Schema Validator is a powerful and flexible tool designed to ensure directory structures conform to predefined patterns. It implements a "schema-first" approach to folder validation, allowing you to define expected folder hierarchies as JSON schemas and validate if existing directories match these expectations.

### Why Folder Structure Validation Matters

Consistent folder structures are crucial for:

- **Maintainability**: Makes codebases more navigable and understandable
- **Automation**: Enables reliable automated processing of file trees
- **Standardization**: Enforces organizational best practices across teams
- **Integration**: Ensures compatibility with tools expecting specific structures
- **Quality Assurance**: Prevents structural issues before deployment

With Folder Schema Validator, you can codify these structural requirements as schemas, run validations as part of CI/CD pipelines, and ensure that project structures remain compliant throughout their lifecycle. The validator supports three tiers of functionality (Basic, Enhanced, and Advanced) to meet various complexity needs.

## Features

The Folder Schema Validator offers three tiers of validation capabilities to match different use cases and complexity requirements:

### Basic Features

- **Flexible schema definition**: Create schemas that precisely define your folder structure requirements
  ```python
  schema = FolderSchema()
  schema.add_directory("src", required=True)
  schema.add_file("README.md", required=True)
  schema.add_directory("docs", required=False)  # Optional directory
  ```

- **Wildcard pattern support**: Handle variable folder names with powerful glob patterns
  ```json
  {
    "required": {
      "src/modules/*.py": {},
      "config/settings_?.json": {},
      "data/client_[0-9][0-9]/": {}
    }
  }
  ```

- **Schema persistence**: Save and load schemas from JSON files for reuse
  ```python
  # Save schema for later use
  schema.save("project_schema.json")
  
  # Load an existing schema
  schema = FolderSchema(schema_file="project_schema.json")
  ```

- **Detailed validation**: Get comprehensive reports identifying specific validation issues
  ```
  ❌ Validation failed with 3 issues:
    1. Missing required item: src/main.py
    2. Missing required item matching pattern 'test_*.py' in tests
    3. Unexpected item 'temp.log' in data
  ```

- **Easy integration**: Simple API that can be integrated into any Python application or CI/CD pipeline

### Enhanced Features

- **Regular expression support**: Use powerful regex patterns for even more flexible matching
  ```python
  schema.add_pattern_file(
      path="src",
      pattern=r"model_\d+\.py$", 
      pattern_type="regex"
  )
  ```

- **File content validation**: Validate file contents against regex patterns
  ```python
  schema.add_file("setup.py", required=True, content_pattern=r"name=['\"]project_name['\"]")
  ```

- **File size constraints**: Validate file sizes to ensure they meet requirements
  ```python
  # Ensure README is not empty and not too large
  schema.add_file("README.md", min_size=100, max_size=1024*50)  # 50KB max
  ```

- **Item count validation**: Control how many items should match a pattern
  ```python
  # Ensure we have between 1-5 configuration files
  schema.add_pattern_file("config/*.yml", min_items=1, max_items=5)
  ```

- **Cross-platform compatibility**: Works consistently on Windows, macOS, and Linux

### Advanced Features

- **Conditional requirements**: Define folder/file requirements based on the existence of other items
  ```python
  # If Dockerfile exists, docker-compose.yml must also exist
  schema.add_conditional_requirement(
      condition_path="Dockerfile",
      required_paths=["docker-compose.yml"],
      message="Docker Compose file is required when using Docker"
  )
  ```

- **Custom validators**: Create and use custom validator plugins for specialized file validation
  ```python
  class YamlValidator(CustomValidator):
      def can_validate(self, file_path):
          return file_path.endswith('.yml') or file_path.endswith('.yaml')
          
      def validate(self, file_path):
          # Custom validation logic here
          return ["Issue found: invalid YAML format"]
          
  # Load custom validators
  schema.add_custom_validator(YamlValidator())
  # Or load from a module
  schema.load_custom_validators_from_module("custom_validators.py")
  ```

- **Incremental validation**: Use caching to avoid re-validating unchanged directories
  ```python
  validator = AdvancedFolderValidator(
      schema, 
      "/path/to/project",
      use_cache=True,
      cache_file=".validation_cache"
  )
  ```

- **Parallel processing**: Leverage multiple CPU cores for faster validation of large structures
  ```python
  validator = AdvancedFolderValidator(
      schema, 
      "/path/to/project",
      parallel=True,
      num_workers=4  # Use 4 worker processes
  )
  ```

- **Lazy directory traversal**: Save memory when working with large folder structures
  ```python
  validator = AdvancedFolderValidator(
      schema, 
      "/path/to/project",
      lazy=True  # Use memory-efficient traversal
  )
  ```

- **Validation metrics**: Get detailed performance statistics about validation runs
  ```python
  metrics = validator.get_metrics()
  print(f"Validation took {metrics['duration']:.2f} seconds")
  print(f"Processed {metrics['files_processed']} files")
  print(f"Processed {metrics['directories_processed']} directories")
  ```

## When to Use

Folder Schema Validator solves real-world problems across various development and operational scenarios:

### Software Development

- **Project Template Conformance**: Ensure new projects adhere to organizational standards
  ```bash
  # Validate a new project against your team's template
  python -m folder_schema_validator -s team_standards.json -d ./new_project
  ```

- **Monorepo Structure Validation**: Maintain consistent structure in large repositories with multiple packages
  ```python
  # In your CI pipeline
  validator = AdvancedFolderValidator(schema, "./monorepo")
  results = validator.validate()
  if not results.is_valid:
      raise Exception("Monorepo structure validation failed!")
  ```

- **Library Distribution Checks**: Ensure all required files are included before package publishing
  ```bash
  # Pre-publish check
  python -m folder_schema_validator -s python_package.json -d ./dist --mode strict
  ```

### Data Engineering & Science

- **Data Pipeline Validation**: Verify data folder structures match expected format before processing
  ```python
  # Validate data structure before running pipeline
  schema = AdvancedFolderSchema(schema_file="data_pipeline_schema.json")
  validator = AdvancedFolderValidator(schema, "./data")
  if validator.validate():
      run_data_pipeline()
  ```

- **Machine Learning Project Structure**: Enforce consistent organization of ML experiment assets
  ```bash
  # Validate ML project structure
  python -m folder_schema_validator -s ml_project.json -d ./experiment_123 --ignore "__pycache__"
  ```

- **Dataset Preparation**: Validate dataset directories meet requirements before training
  ```python
  # Check that a dataset has the required structure
  schema.add_pattern_directory("dataset/*/images", min_items=100)  # Each class needs at least 100 images
  schema.add_pattern_directory("dataset/*/annotations", required=True)
  ```

### DevOps & Deployment

- **Infrastructure as Code Validation**: Ensure terraform modules follow best practices
  ```bash
  # Validate terraform project structure
  python -m folder_schema_validator -s terraform_module.json -d ./infrastructure
  ```

- **Deployment Artifact Checks**: Verify build artifacts are properly structured before deployment
  ```python
  # Pre-deployment validation
  schema = EnhancedFolderSchema(schema_file="webapp_release.json")
  validator = EnhancedFolderValidator(schema, "./build")
  validator.validate()
  ```

- **Serverless Function Packaging**: Ensure Lambda/Cloud Function deployments include all required files
  ```bash
  # Validate serverless function structure
  python -m folder_schema_validator -s lambda_function.json -d ./function --mode strict
  ```

### Content Management & Documentation

- **Documentation Structure**: Enforce documentation organization standards
  ```python
  # Check docs structure with custom validators
  schema = AdvancedFolderSchema(schema_file="docs_schema.json")
  schema.load_custom_validators_from_module("markdown_validators.py")
  validator = AdvancedFolderValidator(schema, "./docs")
  ```

- **CMS Content Validation**: Validate user-uploaded content structures before processing
  ```python
  # Process each upload with validation
  for upload_dir in uploads:
      validator = FolderValidator(schema, upload_dir)
      if validator.validate():
          process_upload(upload_dir)
      else:
          flag_invalid_upload(upload_dir)
  ```

### Continuous Integration

- **Pre-commit Hooks**: Validate project structure before allowing commits
  ```bash
  # In .pre-commit-config.yaml
  - repo: local
    hooks:
      - id: validate-structure
        name: Validate Project Structure
        entry: python -m folder_schema_validator -s project_schema.json -d .
        language: system
        pass_filenames: false
  ```

- **CI/CD Pipeline Integration**: Include structure validation as a pipeline step
  ```yaml
  # In GitHub Actions workflow
  jobs:
    validate-structure:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - name: Validate project structure
          run: python -m folder_schema_validator -s ci_schema.json -d .
  ```

## Getting Started

### Quick Start Example

Let's walk through a simple example to validate a typical Python project structure:

1. Create a schema file `python_project_schema.json`:

```json
{
  "required": {
    "src": {
      "required": {
        "__init__.py": {},
        "main.py": {}
      }
    },
    "tests": {
      "required": {
        "__init__.py": {},
        "test_*.py": {"pattern": true}
      }
    },
    "README.md": {},
    "requirements.txt": {}
  },
  "optional": {
    "docs": {},
    ".gitignore": {},
    "setup.py": {}
  }
}
```

2. Run the validator:

```bash
python folder_schema_validator.py --schema python_project_schema.json --directory /path/to/your/project
```

3. Review the validation results showing any missing required files or other issues.

## Installation

### PyPI Installation

The easiest way to install the Folder Schema Validator is via pip:

```bash
pip install folder-schema-validator
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/folder-schema-validator.git
cd folder-schema-validator

# Install dependencies
pip install -r requirements.txt

# Optional: Install as a package for system-wide use
pip install -e .
```

## Usage

### Command Line Interface

The validator provides a comprehensive command-line interface:

```bash
python folder_schema_validator.py --schema example_schema.json --directory /path/to/validate
```

#### Available Options

```
--schema SCHEMA, -s SCHEMA       Path to the schema file (JSON) (required)
--directory DIRECTORY, -d DIR    Directory to validate (default: current directory)
--mode {strict,relaxed}, -m MODE Validation mode (default: strict)
--ignore IGNORE, -i IGNORE       Patterns to ignore (can be specified multiple times)
--validator VALIDATOR, -v VAL    Path to custom validator module
--cache, -c                      Use incremental validation cache
--cache-file CACHE_FILE          Path to cache file
--parallel, -p                   Use parallel processing
--workers WORKERS, -w WORKERS    Number of worker processes for parallel processing
--lazy, -l                       Use lazy directory traversal to save memory
--clear-cache                    Clear the validation cache before running
--basic                          Use basic validator with minimal features
--enhanced                       Use enhanced validator with pattern matching
--output {text,json,xml}, -o     Output format for validation results
--verbose, -vv                   Show detailed validation information
--quiet, -q                      Suppress all output except errors
```

#### Examples

**Basic validation with default options:**
```bash
python folder_schema_validator.py -s project_schema.json -d ./my_project
```

**Advanced validation with custom options:**
```bash
python folder_schema_validator.py -s data_schema.json -d ./datasets --mode relaxed --ignore "*.tmp" --ignore "*.log" --parallel --workers 4 --cache --output json
```

**Using custom validators:**
```bash
python folder_schema_validator.py -s web_project.json -d ./website --validator ./custom_validators/web_validators.py
```

### Python API

The Python API gives you more flexibility and integration options:

#### Basic Usage

```python
from folder_schema_validator import FolderSchema, FolderValidator

# Create a schema programmatically
schema = FolderSchema()
schema.add_required_folder("src")
schema.add_required_file("README.md")
schema.add_optional_folder("docs")

# Alternatively, load from a JSON file
# schema = FolderSchema.from_json("my_schema.json")

# Create validator and run validation
validator = FolderValidator(schema, "/path/to/project")
results = validator.validate()

# Process results
if results.is_valid:
    print("Validation successful!")
else:
    print(f"Found {len(results.issues)} issues:")
    for issue in results.issues:
        print(f" - {issue}")
```

#### Advanced Usage

```python
from folder_schema_validator import AdvancedFolderSchema, AdvancedFolderValidator

# Create an advanced schema
schema = AdvancedFolderSchema()

# Add various requirements
schema.add_required_folder("src")
schema.add_required_file("README.md")
schema.add_required_pattern("logs/*.log", min_matches=1)
schema.add_optional_folder("docs")

# Add wildcard patterns
schema.add_required_folder("clients/*/data")
schema.add_required_file("clients/*/config.json")

# Add a conditional requirement
schema.add_conditional_requirement(
    condition_path="config/dev.env",
    required_path="config/dev.example.env",
    message="When dev.env exists, dev.example.env must also exist as a template"
)

# Add regex pattern validation
schema.add_required_pattern(
    "src/models/model_*.py", 
    regex=True,
    content_pattern=r"class\s+Model\w+\(BaseModel\)"
)

# Load custom validators
schema.load_custom_validators_from_module("custom_validators.py")

# Save schema for later use
schema.save_to_json("advanced_project_schema.json")

# Create validator with advanced options
validator = AdvancedFolderValidator(
    schema, 
    "/path/to/project",
    validation_mode="strict",
    ignore_patterns=[".git", "__pycache__", "*.pyc"],
    use_cache=True,
    cache_file=".validation_cache",
    parallel=True,
    workers=4,
    lazy=True
)

# Run validation
results = validator.validate()

# Get detailed validation report
report = results.generate_report(format="markdown")
print(report)

# Export results
results.export_to_json("validation_results.json")
```

## Schema Format

Schemas are defined in JSON format, with powerful options to express a variety of requirements. Below are examples demonstrating the full range of schema capabilities from basic to advanced.

### Basic Schema Structure

```json
{
  "required": {
    "src/": {},
    "README.md": {},
    "requirements.txt": {}
  },
  "optional": {
    "docs/": {},
    "tests/": {},
    "examples/": {}
  }
}
```

Key elements of the schema format:
- `required`: Items that must be present for validation to pass
- `optional`: Items that may be present but are not required
- Directories are denoted by a trailing slash (`/`)
- Files have no trailing slash

### Pattern Matching

You can use glob patterns to match multiple files or directories:

```json
{
  "required": {
    "src/*.py": {},                 # All Python files in src/
    "config/*_settings.json": {},   # Files ending with _settings.json in config/
    "docs/api/v[0-9]/": {},         # Directories matching v0, v1, v2, etc.
    "data/client_??/": {}           # Directories like client_01, client_02, etc.
  }
}
```

### Enhanced Schema Options

The Enhanced and Advanced validators support additional options:

```json
{
  "required": {
    "README.md": {
      "min_size": 100,                 # Minimum file size in bytes
      "max_size": 51200,               # Maximum file size in bytes
      "content_pattern": "# Project"    # Content must contain this pattern
    },
    "src/": {
      "children": {                    # Define children requirements
        "main.py": {
          "required": true,
          "content_pattern": "if __name__ == '__main__':"
        },
        "*.py": {
          "min_items": 3,              # At least 3 Python files required
          "max_items": 20              # No more than 20 Python files allowed
        }
      }
    },
    "src/utils/": {
      "pattern_files": {               # Define pattern-based file requirements
        "helper_*.py": {
          "required": true,
          "min_items": 1
        } 
      }
    }
  }
}
```

### Advanced Schema with Regex Patterns

Regular expressions provide even more powerful pattern matching:

```json
{
  "required": {
    "src/": {
      "pattern_files": {
        "model_\\d+\\.py": {            # Matches model_1.py, model_2.py, etc.
          "pattern_type": "regex",     # Specify regex pattern type
          "required": true
        }
      }
    },
    "data/": {
      "pattern_directories": {
        "dataset_[a-z]+_v\\d+": {       # Matches dataset_name_v1, dataset_test_v2, etc.
          "pattern_type": "regex",
          "required": true,
          "min_items": 1
        }
      }
    }
  }
}
```

### Conditional Requirements

Advanced schemas can define dependencies between files and directories:

```json
{
  "required": {
    "Dockerfile": {},
    "requirements.txt": {}
  },
  "conditional_requirements": [
    {
      "condition_path": "Dockerfile",            # If Dockerfile exists
      "required_paths": [                        # Then these must also exist
        "docker-compose.yml",
        ".dockerignore"
      ],
      "message": "Docker Compose and .dockerignore files are required when using Docker"
    },
    {
      "condition_path": "tests/",               # If tests/ directory exists 
      "required_paths": [                        # Then these must also exist
        "pytest.ini",
        "requirements-dev.txt"
      ]
    }
  ]
}
```

### Custom Validators in Schema

Advanced schemas can reference custom validators:

```json
{
  "required": {
    "src/": {},
    "*.py": {
      "validators": ["python_syntax"]           # Apply python_syntax validator to all .py files
    },
    "config/*.json": {
      "validators": ["json_syntax", "json_schema"] # Apply multiple validators
    }
  },
  "custom_validators": {
    "python_syntax": {
      "class": "PythonSyntaxValidator",          # Built-in validator
      "ignore_comments": true                    # Configuration options
    },
    "json_syntax": {
      "class": "JsonSyntaxValidator"             # Built-in validator
    },
    "json_schema": {
      "module": "custom_validators",              # External module
      "class": "JsonSchemaValidator",             # Class from module
      "schema_path": "schemas/config_schema.json" # Configuration options
    }
  }
}
```

### Wildcard Patterns

Wildcards allow for flexible matching of file and folder names:

- `*` - Matches any sequence of characters (except path separators)
- `?` - Matches any single character
- `[abc]` - Matches any character within the brackets
- `[!abc]` - Matches any character not in the brackets

#### Examples

```json
{
  "required": {
    "clients/*/config.json": {},
    "logs/????-??.log": {},
    "src/[abc]*.py": {},
    "data/[!test]*/raw/": {}
  }
}
```

This schema requires:
- A `config.json` file in any subfolder of `clients/`
- Log files in the `logs/` folder matching the pattern (e.g., `2023-01.log`)
- Python files in `src/` starting with 'a', 'b', or 'c'
- A `raw` folder inside any subfolder of `data/` not starting with 'test'

## Validation Modes

The folder validator supports different validation modes to adapt to various usage scenarios:

### Mode Types

- **Strict Mode** (default): Validates that all required items exist AND reports unexpected items as errors
  - Best for enforcing exact folder structures
  - Ideal for templates, standardized projects, and deployments
  - Helps catch misplaced files or directories

- **Relaxed Mode**: Only checks that required items exist, ignoring unexpected items
  - Better for projects with varying additional content
  - Useful for validating minimum requirements without being restrictive
  - Avoids overwhelming reports when validating existing projects

```python
# Using relaxed mode
validator = AdvancedFolderValidator(
    schema=schema,
    root_dir="/path/to/project",
    validation_mode="relaxed"  # Only validate required items
)
```

### Combining Modes with Ignore Patterns

You can use ignore patterns with both strict and relaxed modes to fine-tune validation:

```python
# Strict mode with ignored patterns
validator = AdvancedFolderValidator(
    schema=schema,
    root_dir="/path/to/project",
    validation_mode="strict",
    ignore_patterns=[
        "__pycache__",      # Ignore all __pycache__ directories
        "*.pyc",           # Ignore all Python cache files
        ".git/",           # Ignore git directory
        "**/.DS_Store"     # Ignore macOS metadata files
    ]
)
```

### CLI Usage with Validation Modes

```bash
# Run in relaxed mode
python -m folder_schema_validator -s schema.json -d /path/to/project --mode relaxed

# Run in strict mode with ignore patterns
python -m folder_schema_validator -s schema.json -d /path/to/project \
    --mode strict --ignore "__pycache__" --ignore "*.pyc"
```

## Custom Validators

The Advanced validator tier supports custom validator plugins for specialized file validation. Custom validators allow you to validate file contents, syntax, format, or any other aspect of files in your folder structure.

### Creating Custom Validators

Custom validators must implement the `CustomValidator` interface:

```python
from folder_schema_validator import CustomValidator

class YamlFormatValidator(CustomValidator):
    """Validates YAML files for correct formatting."""
    
    def __init__(self, strict=False):
        self.strict = strict
        
    def can_validate(self, file_path: str) -> bool:
        """Determine if this validator can validate the given file."""
        return file_path.endswith(('.yaml', '.yml'))
    
    def validate(self, file_path: str) -> list[str]:
        """Validate the file and return a list of issues (empty if valid)."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                if self.strict:
                    yaml.safe_load(f)
                else:
                    yaml.load(f, Loader=yaml.SafeLoader)
            return []  # No issues found
        except yaml.YAMLError as e:
            return [f"YAML validation error: {str(e)}"]
        except Exception as e:
            return [f"Unexpected error validating YAML: {str(e)}"]
            
    def __str__(self) -> str:
        """Return a string representation of this validator."""
        return f"YamlFormatValidator(strict={self.strict})"
```

### Using Built-in Validators

The library includes several built-in validators:

```python
# Python syntax validator
from folder_schema_validator import PythonSyntaxValidator

# JSON syntax validator
from folder_schema_validator import JsonSyntaxValidator

# Create a schema with built-in validators
schema = AdvancedFolderSchema()

# Add validators to specific files or patterns
schema.add_custom_validator("src/*.py", PythonSyntaxValidator())
schema.add_custom_validator("config/*.json", JsonSyntaxValidator())
```

### Applying Custom Validators Programmatically

```python
# Create your custom validators
markdown_validator = MarkdownValidator()
json_schema_validator = JsonSchemaValidator("schemas/config_schema.json")

# Create schema and add validators
schema = AdvancedFolderSchema(schema_file="project_schema.json")
schema.add_custom_validator("**/*.md", markdown_validator)
schema.add_custom_validator("config.json", json_schema_validator)

# Use the schema with validators
validator = AdvancedFolderValidator(schema, "/path/to/project")
results = validator.validate()
```

### Loading Validators from External Modules

You can also define validators in separate Python modules and load them dynamically:

```python
# File: custom_validators.py
from folder_schema_validator import CustomValidator

class XmlValidator(CustomValidator):
    def can_validate(self, file_path):
        return file_path.endswith('.xml')
        
    def validate(self, file_path):
        # XML validation logic here
        return []  # No issues

# Main script
schema = AdvancedFolderSchema()
schema.load_custom_validators("custom_validators.py")

# Or use in CLI
# python -m folder_schema_validator -s schema.json -d . --validator custom_validators.py
```

### Validator Results

Validators return a list of issue strings, which are included in the validation report:

```
❌ Validation failed with 2 issues:
  1. Missing required file: config.json
  2. [PythonSyntaxValidator] Syntax error in src/main.py: invalid syntax (line 23)
```

## Performance Optimization

The Advanced validator tier includes several performance optimizations for working with large directory structures:

### Incremental Validation with Caching

Avoid re-validating unchanged directories by using the validation cache:

```python
# Enable caching for incremental validation
validator = AdvancedFolderValidator(
    schema=schema,
    root_dir="/path/to/large/project",
    use_cache=True,                         # Enable cache
    cache_file=".validation_cache/cache.json"  # Custom cache location
)

# Run validation (only changed files will be reprocessed)
issues = validator.validate()

# Get cache statistics
metrics = validator.get_metrics()
print(f"Cache hits: {metrics['cache_hits']}")
print(f"Cache misses: {metrics['cache_misses']}")
```

CLI usage:
```bash
# Enable cache
python -m folder_schema_validator -s schema.json -d /path/to/project --cache

# Specify custom cache file
python -m folder_schema_validator -s schema.json -d /path/to/project \
    --cache --cache-file ".validation_cache/custom_cache.json"
    
# Clear the cache before running
python -m folder_schema_validator -s schema.json -d /path/to/project \
    --cache --clear-cache
```

### Parallel Processing

Leverage multiple CPU cores for faster validation of large folder structures:

```python
# Enable parallel processing
validator = AdvancedFolderValidator(
    schema=schema,
    root_dir="/path/to/large/project",
    parallel=True,                 # Enable parallelism
    num_workers=4                  # Use 4 worker processes (default: CPU count)
)

# Get performance metrics
metrics = validator.get_metrics()
print(f"Validation took {metrics['duration']:.2f} seconds")
print(f"Files processed: {metrics['files_processed']}")
```

CLI usage:
```bash
# Enable parallel processing
python -m folder_schema_validator -s schema.json -d /path/to/project --parallel

# Specify worker count
python -m folder_schema_validator -s schema.json -d /path/to/project \
    --parallel --workers 8
```

### Lazy Directory Traversal

Use memory-efficient traversal for extremely large folder structures:

```python
# Enable lazy traversal to reduce memory usage
validator = AdvancedFolderValidator(
    schema=schema,
    root_dir="/path/to/large/project",
    lazy=True  # Use memory-efficient lazy traversal
)
```

CLI usage:
```bash
# Enable lazy traversal
python -m folder_schema_validator -s schema.json -d /path/to/project --lazy
```

### Combining Optimizations

You can combine all optimizations for maximum performance with large directories:

```python
# Full optimization for large directories
validator = AdvancedFolderValidator(
    schema=schema,
    root_dir="/path/to/large/project",
    use_cache=True,       # Use incremental validation
    parallel=True,        # Use parallel processing
    num_workers=8,        # 8 worker processes
    lazy=True,            # Memory-efficient traversal
    ignore_patterns=["**/__pycache__", "**/.git"]  # Skip irrelevant files
)
```

CLI usage:
```bash
# Combine all optimizations
python -m folder_schema_validator -s schema.json -d /path/to/project \
    --cache --parallel --workers 8 --lazy \
    --ignore "**/__pycache__" --ignore "**/.git"
```

## Schema Generation

The Folder Schema Validator includes powerful tools to automatically generate schemas from existing directory structures, saving you time when starting with validation for an existing project.

### Command Line Schema Generation

```bash
# Generate a schema from an existing directory structure
python -m folder_schema_validator generate-schema --directory /path/to/your/project --output schema.json

# Advanced options
python -m folder_schema_validator generate-schema --directory /path/to/your/project \
    --output schema.json \
    --ignore "*.pyc" --ignore "__pycache__" --ignore ".git" \
    --include-properties --detect-patterns --max-depth 5
```

### Python API for Schema Generation

```python
from folder_schema_validator import SchemaGenerator

# Create a generator with custom ignore patterns
generator = SchemaGenerator(ignore_patterns=["*.pyc", "__pycache__", ".git"])

# Generate a schema from an existing directory
schema = generator.generate_schema(
    directory_path="/path/to/your/project",
    output_file="schema.json",  # Optional: save to file
    include_file_properties=True,  # Include size info, etc.
    detect_patterns=True,  # Try to detect patterns in filenames
    max_depth=5  # Limit traversal depth
)

# Analyze directory statistics
stats = generator.analyze_directory("/path/to/your/project")
print(f"Total files: {stats['total_files']}")
print(f"Total directories: {stats['total_directories']}")
print(f"Max depth: {stats['max_depth']}")
```

### Using Generated Schemas

Generated schemas provide a starting point based on your existing directory structure:

1. **Generate** a schema from your existing project
2. **Customize** the generated schema to add or remove requirements
3. **Validate** other directories against this schema

This workflow is especially useful when:
- Documenting an existing project's structure
- Creating a template based on a reference implementation
- Setting up validation for similar projects
- Analyzing differences between directory structures

## Real-World Examples

### Data Science Project

```json
{
  "required": {
    "data": {
      "required": {
        "raw": {},
        "processed": {},
        "external": {}
      }
    },
    "notebooks": {
      "required": {
        "exploratory": {},
        "report": {}
      }
    },
    "src": {
      "required": {
        "__init__.py": {},
        "data": {
          "required": {
            "__init__.py": {},
            "make_dataset.py": {}
          }
        },
        "features": {
          "required": {
            "__init__.py": {},
            "build_features.py": {}
          }
        },
        "models": {
          "required": {
            "__init__.py": {},
            "train_model.py": {},
            "predict_model.py": {}
          }
        }
      }
    },
    "README.md": {},
    "requirements.txt": {},
    ".gitignore": {}
  },
  "optional": {
    "models": {},
    "references": {},
    "reports": {
      "required": {
        "figures": {}
      }
    },
    "setup.py": {},
    "Makefile": {}
  }
}
```

### Web Application Project

```json
{
  "required": {
    "src": {
      "required": {
        "components": {},
        "pages": {},
        "utils": {},
        "App.js": {},
        "index.js": {}
      }
    },
    "public": {
      "required": {
        "index.html": {},
        "favicon.ico": {}
      }
    },
    "package.json": {},
    "README.md": {}
  },
  "optional": {
    "tests": {},
    "docs": {},
    ".github": {
      "required": {
        "workflows": {
          "required": {
            "ci.yml": {}
          }
        }
      }
    },
    ".eslintrc.js": {},
    ".prettierrc": {},
    "Dockerfile": {}
  },
  "conditional": [
    {
      "if_exists": "Dockerfile",
      "then_required": "docker-compose.yml"
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### "Pattern matching failed for wildcard"

**Problem**: Wildcard patterns aren't matching as expected.
**Solution**: Check your wildcard syntax and ensure the paths are relative to the validation root. Use the `--verbose` flag to see detailed matching information.

#### "Validation is extremely slow"

**Problem**: Validation takes too long for large directories.
**Solution**: 
- Enable parallel processing: `--parallel --workers 4`
- Use lazy directory traversal: `--lazy`
- Enable caching: `--cache`
- Add specific ignore patterns for large, irrelevant directories: `--ignore "node_modules" --ignore ".git"`

#### "Custom validator not being applied"

**Problem**: Custom validators aren't being used during validation.
**Solution**: Ensure your custom validator class implements both `can_validate` and `validate` methods correctly. Use the `--verbose` flag to see which validators are being applied to which files.

### Debugging Tips

- Use `--verbose` for detailed logging of the validation process
- Check that file paths in your schema are using the correct separator for your OS
- For custom validators, add print statements or logging to debug the validation logic
- Validate smaller subdirectories first to isolate issues in large projects

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. When a new release is created on GitHub, the package is automatically published to PyPI.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
