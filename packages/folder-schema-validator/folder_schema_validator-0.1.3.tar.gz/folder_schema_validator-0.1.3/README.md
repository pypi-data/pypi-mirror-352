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
- [Real-World Examples](#real-world-examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Folder Schema Validator is designed to ensure that directory structures conform to predefined patterns. It allows you to define expected folder hierarchies and validate if existing directories match these expectations. This is particularly useful for maintaining consistency across multiple projects, validating user-submitted content, or ensuring deployment structures are correct.

## Features

### Basic Features
- **Flexible schema definition**: Define folder structure schemas with required and optional elements
- **Wildcard pattern support**: Handle variable folder names with wildcards (*, ?, [chars])
- **Schema persistence**: Save and load schemas from JSON files
- **Detailed validation**: Get comprehensive reports identifying specific validation issues
- **Easy integration**: Simple API that can be integrated into any Python application

### Enhanced Features
- **Regular expression support**: Use powerful regex patterns for more flexible matching
- **File content validation**: Validate file contents against patterns or requirements
- **Nested wildcards**: Support complex patterns like `project_*/data_*/raw`
- **Cross-platform compatibility**: Works on Windows, macOS, and Linux

### Advanced Features
- **Conditional requirements**: Define folder/file requirements based on the existence of other items
- **Custom validators**: Create and use custom validator plugins for specialized file validation
- **Incremental validation**: Use caching to avoid re-validating unchanged directories
- **Parallel processing**: Leverage multiple CPU cores for faster validation
- **Lazy directory traversal**: Save memory when working with large folder structures
- **Validation hooks**: Execute custom code before/after validation of specific paths

## When to Use

This tool is ideal for:

- **Project templates**: Ensure new projects follow organizational standards
- **Data pipeline validation**: Verify data folder structures before processing
- **Deployment validation**: Check that deployment artifacts are correctly structured
- **Content management**: Validate user-uploaded content structures
- **Quality assurance**: Enforce structural conventions across repositories
- **Automated testing**: Include structural validation in CI/CD pipelines

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

Schemas are defined as nested structures that mirror the expected directory layout.

### Basic Schema

A basic schema is a JSON object with `required` and `optional` keys:

```json
{
  "required": {
    "src": {},
    "README.md": {}
  },
  "optional": {
    "docs": {},
    "examples": {}
  }
}
```

### Advanced Schema

Advanced schemas can include additional properties for more specific validation:

```json
{
  "required": {
    "src": {
      "required": {
        "main.py": {
          "content_validator": "python_syntax",
          "min_size": 10,
          "max_size": 10000
        },
        "utils": {
          "required": {
            "helpers.py": {}
          }
        }
      }
    },
    "data": {
      "min_items": 1,
      "max_items": 100
    },
    "README.md": {
      "content_pattern": "# Project Title"
    }
  },
  "optional": {
    "docs": {
      "required": {
        "index.md": {}
      }
    },
    "tests": {
      "required": {
        "test_*.py": {"pattern": true}
      }
    }
  },
  "conditional": [
    {
      "if_exists": "config/production.env",
      "then_required": "deploy.sh"
    }
  ]
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
    "clients/*/config.json": {"pattern": true},
    "logs/????-??.log": {"pattern": true},
    "src/[abc]*.py": {"pattern": true},
    "data/[!test]*/raw": {"pattern": true}
  }
}
```

This schema requires:
- A `config.json` file in any subfolder of `clients/`
- Log files in the `logs/` folder matching the pattern (e.g., `2023-01.log`)
- Python files in `src/` starting with 'a', 'b', or 'c'
- A `raw` folder inside any subfolder of `data/` not starting with 'test'

## Validation Modes

The validator supports different validation modes:

- **Strict**: Validates that all required items exist and no unexpected items are present
- **Relaxed**: Only checks that required items exist, ignoring unexpected items
- **Content-only**: Only validates file contents without checking structure
- **Structure-only**: Only validates folder structure without checking file contents

```python
# Set the validation mode
validator = FolderValidator(schema, "/path/to/project", validation_mode="relaxed")
```

## Custom Validators

You can create custom validators to check specific file types or contents:

```python
from folder_schema_validator import CustomValidator

class JsonSchemaValidator(CustomValidator):
    """Validates JSON files against a JSON schema."""
    
    def __init__(self, schema_path):
        self.schema_path = schema_path
        # Load the JSON schema
        import json
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def can_validate(self, file_path: str) -> bool:
        return file_path.endswith('.json')
    
    def validate(self, file_path: str) -> tuple[bool, str]:
        import json
        import jsonschema
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            jsonschema.validate(data, self.schema)
            return True, "JSON schema validation passed"
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except jsonschema.exceptions.ValidationError as e:
            return False, f"JSON schema validation failed: {str(e)}"

# Using the custom validator
schema = AdvancedFolderSchema()
schema.add_custom_validator("config.json", JsonSchemaValidator("config_schema.json"))
```

## Performance Optimization

For large directory structures, several performance optimizations are available:

### Incremental Validation

The validator can cache validation results and only re-validate changed directories:

```python
validator = AdvancedFolderValidator(
    schema,
    "/path/to/large/project",
    use_cache=True,
    cache_file=".validation_cache"
)
```

### Parallel Processing

Leverage multiple CPU cores for faster validation:

```python
validator = AdvancedFolderValidator(
    schema,
    "/path/to/large/project",
    parallel=True,
    workers=8  # Number of worker processes
)
```

### Lazy Directory Traversal

Save memory when working with large folder structures:

```python
validator = AdvancedFolderValidator(
    schema,
    "/path/to/large/project",
    lazy=True
)
```

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
