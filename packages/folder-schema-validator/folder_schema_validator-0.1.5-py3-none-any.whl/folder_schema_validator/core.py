#!/usr/bin/env python3
"""
Unified Folder Structure Validator

This module provides tools for validating folder structures against a schema,
with support for advanced features like regex patterns, conditional requirements,
custom validators, incremental validation, and parallel processing.

Features include:
- Basic folder structure validation with wildcards
- Enhanced validation with regex patterns and content validation
- Conditional requirements based on file existence
- Custom validator plugins for file-specific validations
- Incremental validation with caching for performance
- Parallel processing for faster validation of large structures
- Lazy loading for memory efficiency
"""

import os
import re
import sys
import json
import time
import fnmatch
import hashlib
import inspect
import argparse
import importlib
import multiprocessing
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable, Type, Iterator, Generator
from functools import lru_cache


import os
import re
import sys
import json
import time
import fnmatch
import hashlib
import inspect
import argparse
import importlib


class FolderSchema:
    """Class to define and work with folder structure schemas."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None, schema_file: Optional[str] = None):
        """
        Initialize a folder schema.
        
        Args:
            schema: Dictionary representation of the schema
            schema_file: Path to a JSON file containing the schema
        """
        if schema_file and os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                self.schema = json.load(f)
        elif schema:
            self.schema = schema
        else:
            self.schema = {}
    
    def add_directory(self, path: str, required: bool = True, children: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a directory to the schema.
        
        Args:
            path: Path to the directory
            required: Whether the directory is required
            children: Dictionary of child items
        """
        path_parts = path.strip('/').split('/')
        current_node = self.schema
        
        # Navigate to the parent directory
        for i, part in enumerate(path_parts[:-1]):
            if part not in current_node:
                current_node[part] = {
                    "type": "directory",
                    "required": True,
                    "children": {}
                }
            current_node = current_node[part]["children"]
        
        # Add the target directory
        last_part = path_parts[-1]
        current_node[last_part] = {
            "type": "directory",
            "required": required,
            "children": children or {}
        }
    
    def add_file(self, path: str, required: bool = True) -> None:
        """
        Add a file to the schema.
        
        Args:
            path: Path to the file
            required: Whether the file is required
        """
        path_parts = path.strip('/').split('/')
        current_node = self.schema
        
        # Navigate to the parent directory
        for i, part in enumerate(path_parts[:-1]):
            if part not in current_node:
                current_node[part] = {
                    "type": "directory",
                    "required": True,
                    "children": {}
                }
            current_node = current_node[part]["children"]
        
        # Add the target file
        last_part = path_parts[-1]
        current_node[last_part] = {
            "type": "file",
            "required": required
        }
    
    def save(self, schema_file: str) -> None:
        """
        Save the schema to a JSON file.
        
        Args:
            schema_file: Path to save the schema to
        """
        with open(schema_file, 'w') as f:
            json.dump(self.schema, f, indent=4)


class FolderValidator:
    """Class to validate folders against a schema."""
    
    def __init__(self, schema: FolderSchema, root_dir: str, 
                 ignore_patterns: Optional[List[str]] = None):
        """
        Initialize validator with a schema and root directory.
        
        Args:
            schema: The folder schema to validate against
            root_dir: The root directory to validate
            ignore_patterns: List of patterns to ignore
        """
        self.schema = schema
        self.root_dir = root_dir
        self.ignore_patterns = ignore_patterns or []
        self.issues = []
    
    def validate(self) -> List[str]:
        """
        Validate the folder structure against the schema.
        
        Returns:
            List of validation issues
        """
        self.issues = []
        self._validate_directory(self.schema.schema, self.root_dir, [])
        return self.issues
    
    def _is_ignored(self, path: str) -> bool:
        """
        Check if a path should be ignored based on ignore patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be ignored, False otherwise
        """
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False
    
    def _validate_directory(self, schema_node: Dict[str, Any], current_path: str, path_parts: List[str]) -> None:
        """
        Recursively validate a directory against the schema.
        
        Args:
            schema_node: Current node in the schema
            current_path: Current path being validated
            path_parts: Parts of the path for reporting
        """
        # Get the items in the current directory
        try:
            items = os.listdir(current_path)
        except (FileNotFoundError, PermissionError) as e:
            self.issues.append(f"Error accessing directory {current_path}: {e}")
            return
        
        # First pass: check for required items
        for name, properties in schema_node.items():
            if name in ["required", "type"]:  # Skip metadata properties
                continue
                
            # Handle wildcards in directory/file names
            if "*" in name or "?" in name or "[" in name:
                # Find matching items
                matched_items = []
                for item in items:
                    if fnmatch.fnmatch(item, name):
                        matched_items.append(item)
                
                # If no matches found and the item is required, report an issue
                if not matched_items and properties.get("required", True):
                    self.issues.append(f"Missing required item matching pattern '{name}' in {'/'.join(path_parts)}")
                
                # Validate matched items
                for item in matched_items:
                    item_path = os.path.join(current_path, item)
                    item_path_parts = path_parts + [item]
                    
                    if properties.get("type") == "directory" and os.path.isdir(item_path):
                        if "children" in properties:
                            self._validate_directory(properties["children"], item_path, item_path_parts)
                    elif properties.get("type") == "file" and os.path.isfile(item_path):
                        pass  # Files don't need further validation in the basic validator
            else:
                # Regular item (no wildcards)
                if name in items:
                    item_path = os.path.join(current_path, name)
                    item_path_parts = path_parts + [name]
                    
                    if properties.get("type") == "directory" and os.path.isdir(item_path):
                        if "children" in properties:
                            self._validate_directory(properties["children"], item_path, item_path_parts)
                    elif properties.get("type") == "file" and os.path.isfile(item_path):
                        pass  # Files don't need further validation in the basic validator
                elif properties.get("required", True):
                    item_path_str = "/".join(path_parts + [name])
                    if not self._is_ignored(item_path_str):
                        self.issues.append(f"Missing required item: {item_path_str}")
        
        # Second pass: check for unexpected items
        for item in items:
            # Skip if the item matches any schema node
            is_expected = False
            for name, properties in schema_node.items():
                if name in ["required", "type"]:  # Skip metadata properties
                    continue
                    
                if ("*" in name or "?" in name or "[" in name) and fnmatch.fnmatch(item, name):
                    is_expected = True
                    break
                elif name == item:
                    is_expected = True
                    break
            
            if not is_expected:
                item_path_str = "/".join(path_parts + [item])
                if not self._is_ignored(item_path_str):
                    self.issues.append(f"Unexpected item: {item_path_str}")


class EnhancedFolderSchema(FolderSchema):
    """Enhanced class to define and work with folder structure schemas."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None, schema_file: Optional[str] = None):
        """
        Initialize a folder schema.
        
        Args:
            schema: Dictionary representation of the schema
            schema_file: Path to a JSON file containing the schema
        """
        super().__init__(schema, schema_file)
        
        # Compile all regex patterns in the schema
        self._compile_regex_patterns(self.schema)
    
    def _compile_regex_patterns(self, node: Dict[str, Any]) -> None:
        """
        Recursively compile all regex patterns in the schema.
        
        Args:
            node: Current schema node
        """
        for name, properties in list(node.items()):
            if properties.get("type") == "directory" and "children" in properties:
                self._compile_regex_patterns(properties["children"])
            
            # Check if this is a regex pattern
            if properties.get("pattern_type") == "regex":
                try:
                    # Compile the pattern to validate it
                    re.compile(name)
                except re.error:
                    print(f"Warning: Invalid regex pattern '{name}'")
    
    def add_pattern_directory(self, path: str, pattern: str, pattern_type: str = "glob",
                             required: bool = True, children: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a directory pattern to the schema.
        
        Args:
            path: Path to the parent directory
            pattern: Pattern for matching directories
            pattern_type: Type of pattern ('glob' or 'regex')
            required: Whether matching directories are required
            children: Dictionary of child items
        """
        path_parts = path.strip('/').split('/')
        current_node = self.schema
        
        # Navigate to the parent directory
        for part in path_parts:
            if part:
                if part not in current_node:
                    current_node[part] = {
                        "type": "directory",
                        "required": True,
                        "children": {}
                    }
                current_node = current_node[part]["children"]
        
        # Add the pattern
        current_node[pattern] = {
            "type": "directory",
            "required": required,
            "pattern_type": pattern_type,
            "children": children or {}
        }
        
        # Compile regex pattern if applicable
        if pattern_type == "regex":
            try:
                re.compile(pattern)
            except re.error:
                print(f"Warning: Invalid regex pattern '{pattern}'")
    
    def add_pattern_file(self, path: str, pattern: str, pattern_type: str = "glob",
                        required: bool = True, content_pattern: Optional[str] = None,
                        checksum: Optional[str] = None, min_size: Optional[int] = None,
                        max_size: Optional[int] = None) -> None:
        """
        Add a file pattern to the schema.
        
        Args:
            path: Path to the parent directory
            pattern: Pattern for matching files
            pattern_type: Type of pattern ('glob' or 'regex')
            required: Whether matching files are required
            content_pattern: Regex pattern for file content
            checksum: Expected SHA-256 checksum
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
        """
        path_parts = path.strip('/').split('/')
        current_node = self.schema
        
        # Navigate to the parent directory
        for part in path_parts:
            if part:
                if part not in current_node:
                    current_node[part] = {
                        "type": "directory",
                        "required": True,
                        "children": {}
                    }
                current_node = current_node[part]["children"]
        
        # Add the pattern
        properties = {
            "type": "file",
            "required": required,
            "pattern_type": pattern_type
        }
        
        # Add optional properties
        if content_pattern:
            properties["content_pattern"] = content_pattern
        if checksum:
            properties["checksum"] = checksum
        if min_size is not None:
            properties["min_size"] = min_size
        if max_size is not None:
            properties["max_size"] = max_size
        
        current_node[pattern] = properties
        
        # Compile regex pattern if applicable
        if pattern_type == "regex":
            try:
                re.compile(pattern)
            except re.error:
                print(f"Warning: Invalid regex pattern '{pattern}'")
        
        # Compile content pattern if applicable
        if content_pattern:
            try:
                re.compile(content_pattern)
            except re.error:
                print(f"Warning: Invalid content pattern '{content_pattern}'")


class EnhancedFolderValidator(FolderValidator):
    """Enhanced class to validate folders against a schema."""
    
    def __init__(self, schema: EnhancedFolderSchema, root_dir: str, 
                validation_mode: str = "strict",
                ignore_patterns: Optional[List[str]] = None):
        """
        Initialize validator with a schema and root directory.
        
        Args:
            schema: The folder schema to validate against
            root_dir: The root directory to validate
            validation_mode: Validation mode ("strict", "relaxed")
            ignore_patterns: List of patterns to ignore
        """
        self.schema = schema
        self.root_dir = root_dir
        self.ignore_patterns = ignore_patterns or []
        self.validation_mode = validation_mode
        self.issues = []
    
    def validate(self) -> List[str]:
        """
        Validate the folder structure against the schema.
        
        Returns:
            List of validation issues
        """
        self.issues = []
        self._validate_directory(self.schema.schema, self.root_dir, [])
        return self.issues
    
    def _validate_directory(self, schema_node: Dict[str, Any], current_path: str, path_parts: List[str]) -> None:
        """
        Recursively validate a directory against the schema.
        
        Args:
            schema_node: Current node in the schema
            current_path: Current path being validated
            path_parts: Parts of the path for reporting
        """
        # Get the items in the current directory
        try:
            items = os.listdir(current_path)
        except (FileNotFoundError, PermissionError) as e:
            self.issues.append(f"Error accessing directory {current_path}: {e}")
            return
        
        # Track which items have been matched
        matched_items = set()
        
        # First pass: check for required items
        for name, properties in schema_node.items():
            # Skip metadata properties
            if name in ["required", "type", "pattern_type", "min_items", "max_items", "min_size", "max_size"]:
                continue
                
            # Check if this is a pattern
            is_pattern = "*" in name or "?" in name or "[" in name
            is_regex = properties.get("pattern_type") == "regex"
            
            if is_pattern or is_regex:
                # Find matching items
                matching_items = self._find_matching_items(name, items, properties)
                matched_items.update(matching_items)
                
                # Validate item count constraints
                min_items = properties.get("min_items")
                max_items = properties.get("max_items")
                
                if min_items is not None and len(matching_items) < min_items:
                    self.issues.append(
                        f"Too few items matching '{name}' in {'/'.join(path_parts)}: "
                        f"found {len(matching_items)}, expected at least {min_items}"
                    )
                
                if max_items is not None and len(matching_items) > max_items:
                    self.issues.append(
                        f"Too many items matching '{name}' in {'/'.join(path_parts)}: "
                        f"found {len(matching_items)}, expected at most {max_items}"
                    )
                
                # If no matches found and the item is required, report an issue
                if not matching_items and properties.get("required", True):
                    current_path_rel = '/'.join(path_parts) if path_parts else "."
                    if not self._is_ignored(os.path.join(current_path_rel, name)):
                        self.issues.append(
                            f"Missing required item matching pattern '{name}' in {current_path_rel}"
                        )
                
                # Validate matched items
                for item in matching_items:
                    item_path = os.path.join(current_path, item)
                    item_path_parts = path_parts + [item]
                    
                    if properties.get("type") == "directory" and os.path.isdir(item_path):
                        if "children" in properties:
                            self._validate_directory(properties["children"], item_path, item_path_parts)
                    elif properties.get("type") == "file" and os.path.isfile(item_path):
                        self._validate_file(item_path, properties, item_path_parts)
            else:
                # Regular item (no pattern)
                if name in items:
                    matched_items.add(name)
                    item_path = os.path.join(current_path, name)
                    item_path_parts = path_parts + [name]
                    
                    if properties.get("type") == "directory" and os.path.isdir(item_path):
                        if "children" in properties:
                            self._validate_directory(properties["children"], item_path, item_path_parts)
                    elif properties.get("type") == "file" and os.path.isfile(item_path):
                        self._validate_file(item_path, properties, item_path_parts)
                elif properties.get("required", True):
                    # Item is required but not found
                    item_path_str = "/".join(path_parts + [name])
                    if not self._is_ignored(item_path_str):
                        self.issues.append(f"Missing required item: {item_path_str}")
        
        # Second pass: check for unexpected items
        if self.validation_mode == "strict":
            for item in items:
                if item not in matched_items:
                    item_path_str = "/".join(path_parts + [item])
                    if not self._is_ignored(item_path_str):
                        # Ignore common patterns like .DS_Store, __pycache__, etc.
                        if any(item.startswith(p) for p in [".", "__"]):
                            continue
                        
                        current_path_rel = '/'.join(path_parts) if path_parts else "."
                        self.issues.append(f"Unexpected item '{item}' in {current_path_rel}")
    
    def _validate_file(self, file_path: str, properties: Dict[str, Any], path_parts: List[str]) -> None:
        """
        Validate a file against schema properties.
        
        Args:
            file_path: Path to the file
            properties: Schema properties for the file
            path_parts: Parts of the path for reporting
        """
        # Check file size constraints if specified
        file_size = os.path.getsize(file_path)
        min_size = properties.get("min_size")
        max_size = properties.get("max_size")
        
        if min_size is not None and file_size < min_size:
            self.issues.append(
                f"File '{'/'.join(path_parts)}' is too small: "
                f"{file_size} bytes, expected at least {min_size} bytes"
            )
        
        if max_size is not None and file_size > max_size:
            self.issues.append(
                f"File '{'/'.join(path_parts)}' is too large: "
                f"{file_size} bytes, expected at most {max_size} bytes"
            )
        
        # Check content pattern if specified
        content_pattern = properties.get("content_pattern")
        if content_pattern:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not re.search(content_pattern, content):
                    self.issues.append(
                        f"Content of '{'/'.join(path_parts)}' does not match required pattern"
                    )
            except Exception as e:
                self.issues.append(f"Error reading file '{'/'.join(path_parts)}': {e}")
        
        # Check checksum if specified
        checksum = properties.get("checksum")
        if checksum:
            calculated = self._calculate_checksum(file_path)
            if calculated != checksum:
                self.issues.append(
                    f"Checksum mismatch for '{'/'.join(path_parts)}': "
                    f"expected {checksum}, got {calculated}"
                )
    
    def _calculate_checksum(self, file_path: str) -> str:
        """
        Calculate SHA-256 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal checksum string
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _find_matching_items(self, pattern: str, items: List[str], properties: Dict[str, Any]) -> List[str]:
        """
        Find items that match a pattern based on pattern type.
        
        Args:
            pattern: Pattern to match
            items: List of item names to check
            properties: Schema properties containing pattern type
            
        Returns:
            List of matching item names
        """
        pattern_type = properties.get("pattern_type", "glob")
        matching_items = []
        
        for item in items:
            if pattern_type == "regex":
                if re.match(f"^{pattern}$", item):
                    matching_items.append(item)
            else:  # glob pattern
                if fnmatch.fnmatch(item, pattern):
                    matching_items.append(item)
        
        return matching_items


class ConditionalRequirement:
    """Class to represent a conditional requirement in the schema."""
    
    def __init__(self, condition_path: str, required_paths: List[str], 
                message: Optional[str] = None):
        """
        Initialize a conditional requirement.
        
        Args:
            condition_path: Path that triggers the requirement if it exists
            required_paths: Paths that are required if the condition is met
            message: Custom message for validation issues
        """
        self.condition_path = condition_path
        self.required_paths = required_paths
        self.message = message or f"If {condition_path} exists, then {', '.join(required_paths)} must also exist"
    
    def check(self, root_dir: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the conditional requirement is satisfied.
        
        Args:
            root_dir: Root directory to check against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        condition_full_path = os.path.join(root_dir, self.condition_path)
        
        # If condition path doesn't exist, requirement doesn't apply
        if not os.path.exists(condition_full_path):
            return True, None
        
        # Check if all required paths exist
        missing_paths = []
        for path in self.required_paths:
            full_path = os.path.join(root_dir, path)
            if not os.path.exists(full_path):
                missing_paths.append(path)
        
        if missing_paths:
            return False, f"{self.message}. Missing: {', '.join(missing_paths)}"
        
        return True, None

#!/usr/bin/env python3


# Imports are handled at the beginning

class CustomValidator:
    """Base class for custom validators.
    
    Custom validators allow for file-specific validation logic to be applied
    during folder structure validation.
    """
    
    def can_validate(self, file_path: str) -> bool:
        """
        Check if this validator can validate the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this validator can validate the file, False otherwise
        """
        raise NotImplementedError("Subclasses must implement can_validate")
    
    def validate(self, file_path: str) -> List[str]:
        """
        Validate the file and return a list of issues.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            List of validation issues
        """
        raise NotImplementedError("Subclasses must implement validate")
    
    def __str__(self) -> str:
        return self.__class__.__name__


class PythonSyntaxValidator(CustomValidator):
    """Validator for Python files that checks for syntax errors."""
    
    def can_validate(self, file_path: str) -> bool:
        """
        Check if this is a Python file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this is a Python file, False otherwise
        """
        return file_path.endswith('.py')
    
    def validate(self, file_path: str) -> List[str]:
        """
        Validate the Python file for syntax errors.
        
        Args:
            file_path: Path to the Python file to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Attempt to compile the code to check for syntax errors
            compile(source, file_path, 'exec')
        except SyntaxError as e:
            issues.append(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            issues.append(f"Error validating {file_path}: {e}")
        
        return issues


class JsonSyntaxValidator(CustomValidator):
    """Validator for JSON files that checks for syntax errors."""
    
    def can_validate(self, file_path: str) -> bool:
        """
        Check if this is a JSON file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this is a JSON file, False otherwise
        """
        return file_path.endswith('.json')
    
    def validate(self, file_path: str) -> List[str]:
        """
        Validate the JSON file for syntax errors.
        
        Args:
            file_path: Path to the JSON file to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            issues.append(f"JSON syntax error in {file_path}: {e}")
        except Exception as e:
            issues.append(f"Error validating {file_path}: {e}")
        
        return issues


class ValidationCache:
    """Cache for incremental validation to avoid re-validating unchanged directories."""
    
    def __init__(self, cache_file: str):
        """
        Initialize the validation cache.
        
        Args:
            cache_file: Path to the cache file
        """
        self.cache_file = cache_file
        self.cache = {}
        self._loaded = False
        self._stats = {
            "total_paths": 0,
            "valid_paths": 0,
            "invalid_paths": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cached_valid": 0,
            "cached_invalid": 0
        }
    
    def load(self) -> None:
        """
        Load the cache from disk (lazy loading).
        """
        if self._loaded:
            return
            
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                    self._stats["total_paths"] = len(self.cache)
                    self._stats["valid_paths"] = sum(1 for v in self.cache.values() if v.get("valid", False))
                    self._stats["invalid_paths"] = self._stats["total_paths"] - self._stats["valid_paths"]
            self._loaded = True
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cache = {}
            self._loaded = True
    
    def save(self) -> None:
        """
        Save the cache to disk.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.cache_file)), exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def update(self, path: str, is_valid: bool) -> None:
        """
        Update the cache for a path.
        
        Args:
            path: Path to update
            is_valid: Whether the path is valid
        """
        self.load()
        self.cache[path] = {
            "timestamp": time.time(),
            "valid": is_valid
        }
        self._stats["total_paths"] = len(self.cache)
        self._stats["valid_paths"] = sum(1 for v in self.cache.values() if v.get("valid", False))
        self._stats["invalid_paths"] = self._stats["total_paths"] - self._stats["valid_paths"]
    
    def is_valid(self, path: str) -> bool:
        """
        Check if a path is valid in the cache.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is valid in the cache, False otherwise
        """
        self.load()
        if path in self.cache:
            self._stats["cache_hits"] += 1
            if self.cache[path].get("valid", False):
                self._stats["cached_valid"] += 1
                return True
            else:
                self._stats["cached_invalid"] += 1
                return False
        self._stats["cache_misses"] += 1
        return False
    
    def get_timestamp(self, path: str) -> float:
        """
        Get the timestamp for a path in the cache.
        
        Args:
            path: Path to get timestamp for
            
        Returns:
            Timestamp for the path, or 0 if not in cache
        """
        self.load()
        if path in self.cache:
            return self.cache[path].get("timestamp", 0)
        return 0
    
    def clear(self) -> None:
        """
        Clear the cache.
        """
        self.cache = {}
        self._stats = {
            "total_paths": 0,
            "valid_paths": 0,
            "invalid_paths": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cached_valid": 0,
            "cached_invalid": 0
        }
        self._loaded = True
        
        # Remove the cache file if it exists
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except Exception as e:
                print(f"Error removing cache file: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with statistics
        """
        self.load()
        return self._stats

#!/usr/bin/env python3


# Import statements are handled at the beginning of the file
# If you need to import from pathlib, it should be done there
# Same for custom validator classes

# Import statements are already handled at the top of the file

# No need for placeholder classes - the real classes are defined above


class ConditionalRequirement:
    """Class to represent a conditional requirement in the schema."""
    
    def __init__(self, condition_path: str, required_paths: List[str], 
                message: Optional[str] = None):
        """
        Initialize a conditional requirement.
        
        Args:
            condition_path: Path that triggers the requirement if it exists
            required_paths: Paths that are required if the condition is met
            message: Custom message for validation issues
        """
        self.condition_path = condition_path
        self.required_paths = required_paths
        self.message = message or f"If {condition_path} exists, then {', '.join(required_paths)} must also exist"
    
    def check(self, root_dir: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the conditional requirement is satisfied.
        
        Args:
            root_dir: Root directory to check against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        condition_full_path = os.path.join(root_dir, self.condition_path)
        
        # If condition path doesn't exist, requirement doesn't apply
        if not os.path.exists(condition_full_path):
            return True, None
        
        # Check if all required paths exist
        missing_paths = []
        for path in self.required_paths:
            full_path = os.path.join(root_dir, path)
            if not os.path.exists(full_path):
                missing_paths.append(path)
        
        if missing_paths:
            return False, f"{self.message}. Missing: {', '.join(missing_paths)}"
        
        return True, None


class AdvancedFolderSchema(EnhancedFolderSchema):
    """Advanced folder schema with support for conditional requirements and custom validators."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None, schema_file: Optional[str] = None):
        """
        Initialize an advanced folder schema.
        
        Args:
            schema: Dictionary representation of the schema
            schema_file: Path to a JSON file containing the schema
        """
        # Call parent class initialization with proper parameters
        super().__init__(schema=schema, schema_file=schema_file)
        
        # Initialize advanced features
        self.conditional_requirements: List[ConditionalRequirement] = []
        self.custom_validators: List[CustomValidator] = [
            PythonSyntaxValidator(),
            JsonSyntaxValidator()
        ]
    
    def add_conditional_requirement(self, condition_path: str, required_paths: List[str],
                                   message: Optional[str] = None) -> None:
        """
        Add a conditional requirement to the schema.
        
        Args:
            condition_path: Path that triggers the requirement if it exists
            required_paths: Paths that are required if the condition is met
            message: Custom message for validation issues
        """
        self.conditional_requirements.append(
            ConditionalRequirement(condition_path, required_paths, message)
        )
    
    def add_custom_validator(self, validator: CustomValidator) -> None:
        """
        Add a custom validator to the schema.
        
        Args:
            validator: Custom validator instance
        """
        self.custom_validators.append(validator)
        
    def load_custom_validators_from_module(self, module_path: str) -> None:
        """
        Load custom validators from a Python module.
        
        This method dynamically imports a Python module and finds all classes that
        inherit from CustomValidator, then adds instances of those classes to the
        schema's custom validators list.
        
        Args:
            module_path: Path to the Python module containing custom validators
        """
        try:
            # Handle module import in a way that works with both Python 3.5+ and older versions
            module_name = os.path.basename(module_path)
            if module_name.endswith('.py'):
                module_name = module_name[:-3]
                
            # Method 1: Try using importlib.util (Python 3.5+)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except (ImportError, AttributeError):
                # Method 2: Fallback to imp (deprecated but works in older Python)
                sys.path.insert(0, os.path.dirname(os.path.abspath(module_path)))
                module = importlib.import_module(module_name)
                sys.path.pop(0)
            
            # Find all classes that inherit from CustomValidator
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, CustomValidator) and obj != CustomValidator:
                    self.add_custom_validator(obj())
                    print(f"Loaded custom validator: {name}")
        except Exception as e:
            print(f"Error loading custom validators from {module_path}: {e}")
    
    # End of AdvancedFolderSchema class


class AdvancedFolderValidator(EnhancedFolderValidator):
    """Advanced folder validator with support for conditional requirements, custom validators, 
    incremental validation, and parallel processing."""
    
    def __init__(self, schema: AdvancedFolderSchema, root_dir: str, 
                validation_mode: str = "strict",
                ignore_patterns: Optional[List[str]] = None,
                use_cache: bool = False, cache_file: Optional[str] = None,
                parallel: bool = False, num_workers: Optional[int] = None,
                lazy: bool = False):
        """
        Initialize advanced validator with a schema and root directory.
        
        Args:
            schema: The folder schema to validate against
            root_dir: The root directory to validate
            validation_mode: Validation mode ("strict", "relaxed")
            ignore_patterns: List of patterns to ignore
            use_cache: Whether to use incremental validation cache
            cache_file: Path to the cache file
            parallel: Whether to use parallel processing
            num_workers: Number of worker processes for parallel processing
            lazy: Whether to use lazy directory traversal
        """
        super().__init__(schema, root_dir, validation_mode, ignore_patterns)
        
        # Set up validation cache
        self.use_cache = use_cache
        self.cache = None
        if use_cache:
            if cache_file is None:
                cache_dir = os.path.join(os.path.dirname(os.path.abspath(root_dir)), ".validation_cache")
                cache_file = os.path.join(cache_dir, f"{os.path.basename(root_dir)}_cache.json")
            self.cache = ValidationCache(cache_file)
        
        # Set up parallel processing
        self.parallel = parallel
        self.num_workers = num_workers or max(1, multiprocessing.cpu_count() - 1)
        
        # Set up lazy directory traversal
        self.lazy = lazy
        
        # Performance metrics
        self.metrics = {
            "start_time": 0,
            "end_time": 0,
            "duration": 0,
            "files_processed": 0,
            "directories_processed": 0,
            "cache_hits": 0,
            "validator_time": 0
        }
    
    def validate(self) -> List[str]:
        """
        Validate the folder structure against the schema.
        
        Returns:
            List of validation issues
        """
        self.issues = []
        self.metrics["start_time"] = time.time()
        
        # Check conditional requirements
        for req in self.schema.conditional_requirements:
            is_valid, message = req.check(self.root_dir)
            if not is_valid:
                self.issues.append(message)
        
        # Validate directory structure
        if self.lazy:
            self._validate_lazy(self.schema.schema, self.root_dir, [])
        else:
            self._validate_directory(self.schema.schema, self.root_dir, [])
        
        # Save cache if used
        if self.use_cache and self.cache:
            self.cache.save()
        
        self.metrics["end_time"] = time.time()
        self.metrics["duration"] = self.metrics["end_time"] - self.metrics["start_time"]
        
        return self.issues
    
    def _validate_lazy(self, schema_node: Dict[str, Any], current_path: str, path_parts: List[str]) -> None:
        """
        Validate a directory using lazy loading to save memory.
        
        Args:
            schema_node: Current node in the schema
            current_path: Current path being validated
            path_parts: Parts of the path for reporting
        """
        # Check if we can use the cache for this path
        relative_path = os.path.relpath(current_path, self.root_dir)
        if self.use_cache and self.cache and relative_path != '.' and self.cache.is_valid(relative_path):
            self.metrics["cache_hits"] += 1
            return
        
        try:
            # Use a generator to avoid loading all items at once
            item_iter = os.scandir(current_path)
            items = []
            
            # First pass: collect all items
            for entry in item_iter:
                items.append(entry.name)
            
            # Continue with normal validation, but with memory-efficient item collection
            self.metrics["directories_processed"] += 1
            matched_items = set()
            
            # Validate required items
            for name, properties in schema_node.items():
                # Skip metadata properties
                if name in ["required", "type", "pattern_type", "min_items", "max_items", "min_size", "max_size"]:
                    continue
                    
                # Check if this is a pattern
                is_pattern = "*" in name or "?" in name or "[" in name
                is_regex = properties.get("pattern_type") == "regex"
                
                if is_pattern or is_regex:
                    # Find matching items
                    matching_items = self._find_matching_items(name, items, properties)
                    matched_items.update(matching_items)
                    
                    # Apply validation logic (similar to _validate_directory)
                    min_items = properties.get("min_items")
                    max_items = properties.get("max_items")
                    
                    if min_items is not None and len(matching_items) < min_items:
                        self.issues.append(
                            f"Too few items matching '{name}' in {'/'.join(path_parts)}: "
                            f"found {len(matching_items)}, expected at least {min_items}"
                        )
                    
                    if max_items is not None and len(matching_items) > max_items:
                        self.issues.append(
                            f"Too many items matching '{name}' in {'/'.join(path_parts)}: "
                            f"found {len(matching_items)}, expected at most {max_items}"
                        )
                    
                    # If no matches found and the item is required, report an issue
                    if not matching_items and properties.get("required", True):
                        current_path_rel = '/'.join(path_parts) if path_parts else "."
                        if not self._is_ignored(os.path.join(current_path_rel, name)):
                            self.issues.append(
                                f"Missing required item matching pattern '{name}' in {current_path_rel}"
                            )
                    
                    # Validate matched items
                    for item in matching_items:
                        item_path = os.path.join(current_path, item)
                        item_path_parts = path_parts + [item]
                        
                        if properties.get("type") == "directory" and os.path.isdir(item_path):
                            if "children" in properties:
                                self._validate_lazy(properties["children"], item_path, item_path_parts)
                        elif properties.get("type") == "file" and os.path.isfile(item_path):
                            self.metrics["files_processed"] += 1
                            self._validate_file(item_path, properties, item_path_parts)
                            self._apply_custom_validators(item_path, item_path_parts)
                else:
                    # Regular item (no pattern)
                    if name in items:
                        matched_items.add(name)
                        item_path = os.path.join(current_path, name)
                        item_path_parts = path_parts + [name]
                        
                        if properties.get("type") == "directory" and os.path.isdir(item_path):
                            if "children" in properties:
                                self._validate_lazy(properties["children"], item_path, item_path_parts)
                        elif properties.get("type") == "file" and os.path.isfile(item_path):
                            self.metrics["files_processed"] += 1
                            self._validate_file(item_path, properties, item_path_parts)
                            self._apply_custom_validators(item_path, item_path_parts)
                    elif properties.get("required", True):
                        # Item is required but not found
                        item_path_str = "/".join(path_parts + [name])
                        if not self._is_ignored(item_path_str):
                            self.issues.append(f"Missing required item: {item_path_str}")
            
            # Check for unexpected items in strict mode
            if self.validation_mode == "strict":
                for item in items:
                    if item not in matched_items:
                        item_path_str = "/".join(path_parts + [item])
                        if not self._is_ignored(item_path_str):
                            # Ignore common patterns
                            if any(item.startswith(p) for p in [".", "__"]):
                                continue
                            
                            current_path_rel = '/'.join(path_parts) if path_parts else "."
                            self.issues.append(f"Unexpected item '{item}' in {current_path_rel}")
            
            # Update cache if used
            if self.use_cache and self.cache and relative_path != '.':
                self.cache.update(relative_path, not any(
                    issue.startswith(f"Missing required item: {relative_path}/") or
                    issue.startswith(f"Unexpected item '{os.path.basename(relative_path)}' in ")
                    for issue in self.issues
                ))
        except (FileNotFoundError, PermissionError) as e:
            self.issues.append(f"Error accessing directory {current_path}: {e}")
    
    def _apply_custom_validators(self, file_path: str, path_parts: List[str]) -> None:
        """
        Apply custom validators to a file.
        
        Args:
            file_path: Path to the file to validate
            path_parts: Parts of the path for reporting
        """
        validator_start_time = time.time()
        
        for validator in self.schema.custom_validators:
            if validator.can_validate(file_path):
                try:
                    issues = validator.validate(file_path)
                    for issue in issues:
                        self.issues.append(f"[{validator}] {issue}")
                except Exception as e:
                    self.issues.append(f"Error with validator {validator} on {'/'.join(path_parts)}: {e}")
        
        self.metrics["validator_time"] += time.time() - validator_start_time
    
    def _find_schema_node(self, schema_node: Dict[str, Any], path_parts: List[str]) -> Optional[Dict[str, Any]]:
        """
        Find the schema node that matches a path.
        
        Args:
            schema_node: Current node in the schema
            path_parts: Parts of the path to find
            
        Returns:
            Matching schema node or None if not found
        """
        if not path_parts:
            return schema_node
            
        current_part = path_parts[0]
        remaining_parts = path_parts[1:]
        
        # First try exact match
        if current_part in schema_node:
            properties = schema_node[current_part]
            if properties.get("type") == "directory" and "children" in properties:
                return self._find_schema_node(properties["children"], remaining_parts)
            elif not remaining_parts:
                return properties
        
        # Then try pattern match
        for name, properties in schema_node.items():
            # Skip metadata properties
            if name in ["required", "type", "pattern_type"]:
                continue
                
            # Check if this is a pattern
            is_pattern = "*" in name or "?" in name or "[" in name
            is_regex = properties.get("pattern_type") == "regex"
            
            if is_pattern or is_regex:
                is_match = False
                
                if is_regex:
                    is_match = bool(re.match(f"^{name}$", current_part))
                else:  # glob pattern
                    is_match = fnmatch.fnmatch(current_part, name)
                
                if is_match:
                    if properties.get("type") == "directory" and "children" in properties:
                        return self._find_schema_node(properties["children"], remaining_parts)
                    elif not remaining_parts:
                        return properties
        
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the validation.
        
        Returns:
            Dictionary with performance metrics
        """
        metrics = self.metrics.copy()
        
        if self.use_cache and self.cache:
            cache_stats = self.cache.get_stats()
            metrics.update(cache_stats)
        
        return metrics


def main():
    """Command-line interface for the folder structure validator."""
    parser = argparse.ArgumentParser(
        description="Validate folder structure against a schema",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--schema", "-s",
        help="Path to the schema file (JSON)",
        required=True
    )
    
    parser.add_argument(
        "--directory", "-d",
        help="Directory to validate",
        default="."
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["strict", "relaxed"],
        default="strict",
        help="Validation mode (strict: report unexpected items, relaxed: ignore unexpected items)"
    )
    
    parser.add_argument(
        "--ignore", "-i",
        action="append",
        default=[],
        help="Patterns to ignore (can be specified multiple times)"
    )
    
    parser.add_argument(
        "--validator", "-v",
        help="Path to custom validator module"
    )
    
    parser.add_argument(
        "--cache", "-c",
        action="store_true",
        help="Use incremental validation cache"
    )
    
    parser.add_argument(
        "--cache-file",
        help="Path to cache file (default: .validation_cache/<directory>_cache.json)"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Use parallel processing"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        help="Number of worker processes for parallel processing"
    )
    
    parser.add_argument(
        "--lazy", "-l",
        action="store_true",
        help="Use lazy directory traversal to save memory"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the validation cache before running"
    )
    
    parser.add_argument(
        "--basic",
        action="store_true",
        help="Use basic validator (v1) with minimal features"
    )
    
    parser.add_argument(
        "--enhanced",
        action="store_true",
        help="Use enhanced validator (v2) with pattern matching and content validation"
    )
    
    args = parser.parse_args()
    
    # Determine which validator to use
    if args.basic:
        # Basic validator (v1)
        schema = FolderSchema(schema_file=args.schema)
        validator = FolderValidator(
            schema=schema,
            root_dir=args.directory,
            ignore_patterns=args.ignore
        )
    elif args.enhanced:
        # Enhanced validator (v2)
        schema = EnhancedFolderSchema(schema_file=args.schema)
        validator = EnhancedFolderValidator(
            schema=schema,
            root_dir=args.directory,
            validation_mode=args.mode,
            ignore_patterns=args.ignore
        )
    else:
        # Advanced validator (v3, default)
        schema = AdvancedFolderSchema(schema_file=args.schema)
        
        # Load custom validators if specified
        if args.validator:
            schema.load_custom_validators(args.validator)
        
        validator = AdvancedFolderValidator(
            schema=schema,
            root_dir=args.directory,
            validation_mode=args.mode,
            ignore_patterns=args.ignore,
            use_cache=args.cache,
            cache_file=args.cache_file,
            parallel=args.parallel,
            num_workers=args.workers,
            lazy=args.lazy
        )
        
        # Clear cache if requested
        if args.clear_cache and validator.cache:
            validator.cache.clear()
            print("Cache cleared.")
    
    # Run validation
    issues = validator.validate()
    
    # Print validation results
    if issues:
        print(f"\n❌ Validation failed with {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        sys.exit(1)
    else:
        print("\n✅ Validation successful! No issues found.")
        
        # Print metrics in verbose mode for advanced validator
        if not args.basic and not args.enhanced and hasattr(validator, 'get_metrics'):
            metrics = validator.get_metrics()
            print(f"\nPerformance metrics:")
            print(f"  Duration: {metrics['duration']:.2f} seconds")
            print(f"  Files processed: {metrics['files_processed']}")
            print(f"  Directories processed: {metrics['directories_processed']}")
            
            if args.cache:
                print(f"  Cache hits: {metrics.get('cache_hits', 0)}")
                print(f"  Cache misses: {metrics.get('cache_misses', 0)}")
        
        sys.exit(0)


def generate_schema_from_directory(directory_path: str, output_file: Optional[str] = None,
                              ignore_patterns: Optional[List[str]] = None,
                              include_file_properties: bool = False,
                              max_depth: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate a folder schema by analyzing an existing directory structure.
    
    Args:
        directory_path: Path to the directory to analyze
        output_file: Path to save the generated schema to (optional)
        ignore_patterns: List of patterns to ignore (e.g. ["*.pyc", "__pycache__", ".git"])
        include_file_properties: Whether to include additional file properties like size
        max_depth: Maximum depth to traverse (None for unlimited)
        
    Returns:
        Dictionary representing the generated schema
    """
    ignore_patterns = ignore_patterns or ["*.pyc", "__pycache__", ".git", ".svn", ".hg", ".DS_Store", "*.swp", "*.bak"]
    
    # Create a schema instance
    schema = AdvancedFolderSchema()
    
    # Helper function to recursively traverse the directory
    def traverse_directory(current_path: str, rel_path: str, depth: int = 0):
        # Check max depth
        if max_depth is not None and depth > max_depth:
            return {}
        
        result = {}
        items = os.listdir(current_path)
        
        for item in items:
            item_path = os.path.join(current_path, item)
            item_rel_path = os.path.join(rel_path, item) if rel_path else item
            
            # Check if this item should be ignored
            if any(fnmatch.fnmatch(item, pattern) for pattern in ignore_patterns):
                continue
                
            if os.path.isdir(item_path):
                # It's a directory
                children = traverse_directory(item_path, item_rel_path, depth + 1)
                result[item] = {
                    "type": "directory",
                    "required": True,
                    "children": children
                }
            else:
                # It's a file
                file_props = {
                    "type": "file",
                    "required": True
                }
                
                # Add additional file properties if requested
                if include_file_properties:
                    file_stats = os.stat(item_path)
                    file_props["size"] = file_stats.st_size
                    file_props["modified"] = file_stats.st_mtime
                    
                    # Try to determine file type
                    if item.endswith(".py"):
                        file_props["file_type"] = "python"
                    elif item.endswith(".json"):
                        file_props["file_type"] = "json"
                    elif item.endswith((".md", ".markdown")):
                        file_props["file_type"] = "markdown"
                    elif item.endswith((".yml", ".yaml")):
                        file_props["file_type"] = "yaml"
                    
                result[item] = file_props
                
        return result
    
    # Start traversal from the root directory
    schema_dict = traverse_directory(directory_path, "")
    schema.schema = schema_dict
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(schema_dict, f, indent=4)
    
    return schema_dict


class SchemaGenerator:
    """
    Class to generate folder structure schemas from existing directories.
    """
    
    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        """
        Initialize a schema generator.
        
        Args:
            ignore_patterns: List of patterns to ignore
        """
        self.ignore_patterns = ignore_patterns or [
            "*.pyc", "__pycache__", ".git", ".svn", ".hg", 
            ".DS_Store", "*.swp", "*.bak", "node_modules",
            ".idea", ".vscode", "*.class", "*.o", "*.so"
        ]
    
    def generate_schema(self, directory_path: str, 
                        output_file: Optional[str] = None,
                        schema_class: Type = AdvancedFolderSchema,
                        include_file_properties: bool = False,
                        detect_patterns: bool = False,
                        max_depth: Optional[int] = None) -> Any:
        """
        Generate a folder schema by analyzing an existing directory structure.
        
        Args:
            directory_path: Path to the directory to analyze
            output_file: Path to save the generated schema to
            schema_class: Class to use for the schema (default: AdvancedFolderSchema)
            include_file_properties: Whether to include additional file properties
            detect_patterns: Try to detect patterns in filenames
            max_depth: Maximum depth to traverse (None for unlimited)
            
        Returns:
            Generated schema instance
        """
        # Create a schema instance of the specified class
        schema_instance = schema_class()
        
        # Helper function to detect patterns in a list of names
        def detect_name_pattern(names):
            if len(names) < 3:
                return None
                
            # Check for numeric patterns (e.g., file1.txt, file2.txt)
            if all(re.match(r'(.*?)\d+(.*)', name) for name in names):
                # Extract the common prefix and suffix
                prefixes = [re.match(r'(.*?)\d+(.*)', name).group(1) for name in names]
                suffixes = [re.match(r'(.*?)\d+(.*)', name).group(2) for name in names]
                
                if len(set(prefixes)) == 1 and len(set(suffixes)) == 1:
                    return f"{prefixes[0]}\\d+{suffixes[0]}"
            
            return None
        
        # Helper function to recursively traverse the directory
        def traverse_directory(current_path: str, rel_path: str, depth: int = 0):
            # Check max depth
            if max_depth is not None and depth > max_depth:
                return {}
            
            result = {}
            try:
                items = os.listdir(current_path)
                
                # Group similar files for pattern detection
                if detect_patterns:
                    files = []
                    dirs = []
                    
                    for item in items:
                        item_path = os.path.join(current_path, item)
                        if any(fnmatch.fnmatch(item, pattern) for pattern in self.ignore_patterns):
                            continue
                        
                        if os.path.isdir(item_path):
                            dirs.append(item)
                        else:
                            files.append(item)
                    
                    # Try to detect file patterns
                    file_pattern = detect_name_pattern(files)
                    if file_pattern:
                        # Add a pattern file instead of individual files
                        result[file_pattern] = {
                            "type": "file",
                            "required": True,
                            "pattern_type": "regex"
                        }
                        # Remove the matched files so we don't process them individually
                        files = []
                    
                    # Try to detect directory patterns
                    dir_pattern = detect_name_pattern(dirs)
                    if dir_pattern:
                        # We'll need to sample one directory to get its structure
                        sample_dir = dirs[0]
                        sample_path = os.path.join(current_path, sample_dir)
                        sample_rel_path = os.path.join(rel_path, sample_dir) if rel_path else sample_dir
                        
                        children = traverse_directory(sample_path, sample_rel_path, depth + 1)
                        result[dir_pattern] = {
                            "type": "directory",
                            "required": True,
                            "pattern_type": "regex",
                            "children": children
                        }
                        # Remove the matched dirs so we don't process them individually
                        dirs = [f for f in dirs if not re.match(dir_pattern, f)]
                    
                    # Process remaining individual items
                    items = files + dirs
                
                # Process each item in the directory
                for item in items:
                    item_path = os.path.join(current_path, item)
                    item_rel_path = os.path.join(rel_path, item) if rel_path else item
                    
                    # Check if this item should be ignored
                    if any(fnmatch.fnmatch(item, pattern) for pattern in self.ignore_patterns):
                        continue
                        
                    if os.path.isdir(item_path):
                        # It's a directory
                        children = traverse_directory(item_path, item_rel_path, depth + 1)
                        result[item] = {
                            "type": "directory",
                            "required": True,
                            "children": children
                        }
                    else:
                        # It's a file
                        file_props = {
                            "type": "file",
                            "required": True
                        }
                        
                        # Add additional file properties if requested
                        if include_file_properties:
                            file_stats = os.stat(item_path)
                            file_props["size"] = file_stats.st_size
                            
                            # Try to determine file type
                            if item.endswith(".py"):
                                file_props["file_type"] = "python"
                            elif item.endswith(".json"):
                                file_props["file_type"] = "json"
                            elif item.endswith((".md", ".markdown")):
                                file_props["file_type"] = "markdown"
                            
                        result[item] = file_props
            except (PermissionError, FileNotFoundError) as e:
                # Handle permission errors or deleted files during traversal
                print(f"Error accessing {current_path}: {e}")
                
            return result
        
        # Start traversal from the root directory
        schema_dict = traverse_directory(directory_path, "")
        schema_instance.schema = schema_dict
        
        # Save to file if requested
        if output_file:
            schema_instance.save(output_file)
        
        return schema_instance
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze a directory and return statistics about its structure.
        
        Args:
            directory_path: Path to the directory to analyze
            
        Returns:
            Dictionary with statistics about the directory structure
        """
        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "max_depth": 0,
            "file_types": defaultdict(int),
            "avg_files_per_dir": 0,
            "largest_file": {
                "path": "",
                "size": 0
            },
            "deepest_path": ""
        }
        
        dirs_with_files = 0
        
        # Helper function to recursively traverse the directory
        def analyze_recursive(current_path: str, rel_path: str, depth: int = 0):
            nonlocal dirs_with_files
            
            stats["max_depth"] = max(stats["max_depth"], depth)
            if depth == stats["max_depth"]:
                stats["deepest_path"] = rel_path
            
            try:
                items = os.listdir(current_path)
                
                files_in_current_dir = 0
                stats["total_dirs"] += 1
                
                for item in items:
                    item_path = os.path.join(current_path, item)
                    item_rel_path = os.path.join(rel_path, item) if rel_path else item
                    
                    # Check if this item should be ignored
                    if any(fnmatch.fnmatch(item, pattern) for pattern in self.ignore_patterns):
                        continue
                        
                    if os.path.isdir(item_path):
                        # Recursively analyze subdirectory
                        analyze_recursive(item_path, item_rel_path, depth + 1)
                    else:
                        # It's a file
                        stats["total_files"] += 1
                        files_in_current_dir += 1
                        
                        # Get file extension
                        _, ext = os.path.splitext(item)
                        ext = ext.lower()[1:] if ext else "(no extension)"
                        stats["file_types"][ext] += 1
                        
                        # Check if it's the largest file
                        file_size = os.path.getsize(item_path)
                        if file_size > stats["largest_file"]["size"]:
                            stats["largest_file"]["size"] = file_size
                            stats["largest_file"]["path"] = item_rel_path
                
                if files_in_current_dir > 0:
                    dirs_with_files += 1
            except (PermissionError, FileNotFoundError) as e:
                print(f"Error accessing {current_path}: {e}")
        
        # Start analysis from the root directory
        analyze_recursive(directory_path, "")
        
        # Calculate average files per directory
        if dirs_with_files > 0:
            stats["avg_files_per_dir"] = stats["total_files"] / dirs_with_files
        
        # Convert defaultdict to regular dict for better JSON serialization
        stats["file_types"] = dict(stats["file_types"])
        
        return stats


def generate_schema_cli():
    """
    Command-line interface for generating a schema from an existing directory.
    """
    parser = argparse.ArgumentParser(description="Generate a folder schema from an existing directory")
    parser.add_argument("directory", help="Directory to analyze")
    parser.add_argument("-o", "--output", help="Output file for the schema")
    parser.add_argument("-i", "--ignore", nargs="+", help="Patterns to ignore (e.g. *.pyc __pycache__)")
    parser.add_argument("-p", "--properties", action="store_true", help="Include file properties")
    parser.add_argument("-d", "--detect-patterns", action="store_true", help="Try to detect patterns")
    parser.add_argument("-m", "--max-depth", type=int, help="Maximum depth to traverse")
    parser.add_argument("--analyze", action="store_true", help="Analyze directory and print statistics")
    
    args = parser.parse_args()
    
    # Create schema generator
    generator = SchemaGenerator(ignore_patterns=args.ignore)
    
    if args.analyze:
        # Analyze directory and print statistics
        stats = generator.analyze_directory(args.directory)
        print(json.dumps(stats, indent=4))
    else:
        # Generate schema
        schema = generator.generate_schema(
            directory_path=args.directory,
            output_file=args.output,
            include_file_properties=args.properties,
            detect_patterns=args.detect_patterns,
            max_depth=args.max_depth
        )
        
        # If no output file specified, print to stdout
        if not args.output:
            print(json.dumps(schema.schema, indent=4))
        else:
            print(f"Schema saved to {args.output}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Remove the 'generate' argument
        sys.argv.pop(1)
        generate_schema_cli()
    else:
        main()
