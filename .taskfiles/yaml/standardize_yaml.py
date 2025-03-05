#!/usr/bin/env python3
"""
Standardize YAML files by ordering keys according to Kubernetes conventions.
Preserves comments and document structure while reordering keys.
"""

import argparse
import os
import sys
import difflib
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple
import subprocess
import tempfile

try:
    from ruamel.yaml import YAML
except ImportError:
    print("Error: ruamel.yaml package is required. Install with 'pip install ruamel.yaml'")
    sys.exit(1)

# Define the standard order for top-level Kubernetes resource keys
K8S_TOP_LEVEL_ORDER = [
    "apiVersion",
    "kind",
    "metadata",
    "spec",
    "status",
]

# Define the standard order for metadata fields
METADATA_ORDER = [
    "name",
    "namespace",
    "labels",
    "annotations",
]

# Define the standard order for spec fields in common Kubernetes resources
SPEC_ORDER = {
    "HelmRelease": [
        "interval",
        "chart",
        "values",
        "valuesFrom",
        "install",
        "upgrade",
        "rollback",
        "uninstall",
        "dependsOn",
        "timeout",
        "suspend",
    ],
    "Kustomization": [
        "interval",
        "path",
        "prune",
        "sourceRef",
        "dependsOn",
        "timeout",
        "suspend",
    ],
}

# Define the standard order for common nested structures
CHART_SPEC_ORDER = [
    "chart",
    "version",
    "sourceRef",
    "interval",
]

HELM_VALUES_ORDER = [
    "controllers",
    "defaultPodOptions",
    "service",
    "ingress",
    "persistence",
]

def order_dict_by_key_order(d: Dict, key_order: List[str]) -> Dict:
    """Order a dictionary by the specified key order, with remaining keys in alphabetical order."""
    # Create a new ordered dict with keys in the specified order
    result = {}

    # First, add keys that are in the key_order list
    for key in key_order:
        if key in d:
            result[key] = d[key]

    # Then, add any remaining keys in alphabetical order
    for key in sorted(k for k in d.keys() if k not in key_order):
        result[key] = d[key]

    return result

def standardize_yaml_dict(data: Dict, resource_kind: Optional[str] = None) -> Dict:
    """
    Recursively standardize a YAML dictionary by ordering keys according to conventions.

    Args:
        data: The YAML data to standardize
        resource_kind: The Kubernetes resource kind, if known

    Returns:
        The standardized YAML data
    """
    if not isinstance(data, dict):
        return data

    # Handle top-level Kubernetes resource
    if "apiVersion" in data and "kind" in data:
        resource_kind = data.get("kind")
        return order_dict_by_key_order(data, K8S_TOP_LEVEL_ORDER)

    # Handle metadata
    if resource_kind and "metadata" in data:
        data["metadata"] = order_dict_by_key_order(data["metadata"], METADATA_ORDER)

    # Handle spec based on resource kind
    if resource_kind and "spec" in data and resource_kind in SPEC_ORDER:
        data["spec"] = order_dict_by_key_order(data["spec"], SPEC_ORDER[resource_kind])

    # Handle chart spec in HelmReleases
    if resource_kind == "HelmRelease" and "spec" in data and "chart" in data["spec"] and "spec" in data["spec"]["chart"]:
        data["spec"]["chart"]["spec"] = order_dict_by_key_order(data["spec"]["chart"]["spec"], CHART_SPEC_ORDER)

    # Handle values in HelmReleases
    if resource_kind == "HelmRelease" and "spec" in data and "values" in data["spec"]:
        data["spec"]["values"] = order_dict_by_key_order(data["spec"]["values"], HELM_VALUES_ORDER)

    # Recursively standardize all dictionary values
    for key, value in list(data.items()):
        if isinstance(value, dict):
            data[key] = standardize_yaml_dict(value, resource_kind)
        elif isinstance(value, list):
            data[key] = [
                standardize_yaml_dict(item, resource_kind) if isinstance(item, dict) else item
                for item in value
            ]

    return data

def standardize_yaml_file(file_path: str, show_diff: bool = False, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Standardize a YAML file by ordering keys according to conventions.

    Args:
        file_path: Path to the YAML file
        show_diff: Whether to print the diff
        dry_run: Whether to perform a dry run (don't write changes)

    Returns:
        Tuple of (success, message)
    """
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)

        with open(file_path, 'r') as f:
            original_content = f.read()

        # Split the content by document separators
        lines = original_content.splitlines()
        document_blocks = []
        current_block = []
        header_lines = []

        # Check for header lines (before first ---)
        for i, line in enumerate(lines):
            if line.strip() == '---':
                header_lines = current_block
                current_block = []
                document_blocks.append({'headers': [line], 'content': []})
            elif document_blocks:
                if line.strip().startswith('# yaml-language-server:') or line.strip().startswith('yaml-language-server:'):
                    document_blocks[-1]['headers'].append(line)
                else:
                    document_blocks[-1]['content'].append(line)
            else:
                current_block.append(line)

        # If we never encountered a ---, everything is part of a single document
        if not document_blocks:
            document_blocks.append({'headers': [], 'content': current_block})

        # Process each document
        documents = []
        yaml_loader = YAML()
        yaml_loader.preserve_quotes = True

        for block in document_blocks:
            content = '\n'.join(block['content'])
            if not content.strip():
                continue  # Skip empty documents

            data = yaml_loader.load(content)
            if data is not None:
                documents.append({
                    'headers': block['headers'],
                    'data': standardize_yaml_dict(data)
                })

        # Write the standardized YAML to a string
        yaml_dumper = YAML()
        yaml_dumper.preserve_quotes = True
        yaml_dumper.indent(mapping=2, sequence=4, offset=2)
        yaml_dumper.explicit_start = False  # Don't auto-add '---' at start of documents
        yaml_dumper.width = 4096  # Set a very large line width to prevent wrapping

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            # First write any header content if it exists
            if header_lines:
                for line in header_lines:
                    f.write(f"{line}\n")

            # Write each document with its headers
            for doc in documents:
                # Write document headers (includes ---)
                for header in doc['headers']:
                    f.write(f"{header}\n")

                # Write the document content
                yaml_dumper.dump(doc['data'], f)
            temp_filename = f.name

        with open(temp_filename, 'r') as f:
            standardized_content = f.read()

        os.unlink(temp_filename)

        # If content hasn't changed, we're done
        if original_content == standardized_content:
            return True, f"File {file_path} is already standardized."

        # Show diff if requested
        if show_diff:
            diff = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                standardized_content.splitlines(keepends=True),
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (standardized)"
            )
            diff_text = ''.join(diff)
            print(diff_text)

        # Write the standardized YAML back to the file (unless dry run)
        if not dry_run:
            with open(file_path, 'w') as f:
                f.write(standardized_content)
            return True, f"Standardized {file_path}"

        return True, f"Would standardize {file_path} (dry run)"

    except Exception as e:
        return False, f"Error standardizing {file_path}: {e}"

def validate_yaml_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate a YAML file using kubeconform or kubectl.

    Args:
        file_path: Path to the YAML file

    Returns:
        Tuple of (success, message)
    """
    # First try kubeconform if available
    try:
        result = subprocess.run(
            ["kubeconform", file_path],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return True, f"File {file_path} is valid (kubeconform)."
        else:
            return False, f"File {file_path} failed validation:\n{result.stderr}"
    except FileNotFoundError:
        pass  # kubeconform not found, try kubectl instead

    # Fall back to kubectl if kubeconform isn't available
    try:
        result = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", file_path],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return True, f"File {file_path} is valid (kubectl)."
        else:
            return False, f"File {file_path} failed validation:\n{result.stderr}"
    except FileNotFoundError:
        return False, f"Neither kubeconform nor kubectl found. Cannot validate {file_path}."

def find_yaml_files(directory: str, exclude_patterns: List[str] = None) -> List[str]:
    """Find all YAML files in a directory and its subdirectories."""
    if exclude_patterns is None:
        exclude_patterns = []

    yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                file_path = os.path.join(root, file)

                # Check if the file matches any exclude pattern
                exclude = False
                for pattern in exclude_patterns:
                    if pattern in file_path:
                        exclude = True
                        break

                if not exclude:
                    yaml_files.append(file_path)

    return sorted(yaml_files)

def main():
    parser = argparse.ArgumentParser(description='Standardize YAML files by ordering keys according to conventions.')
    parser.add_argument('--file', help='Path to a specific YAML file to standardize')
    parser.add_argument('--dir', help='Directory to search for YAML files', default='kubernetes')
    parser.add_argument('--exclude', action='append', help='Patterns to exclude from processing', default=[])
    parser.add_argument('--validate', action='store_true', help='Validate the YAML files after standardizing')
    parser.add_argument('--diff', action='store_true', help='Show diff of changes')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run (don\'t write changes)')

    args = parser.parse_args()

    # Process a single file
    if args.file:
        if not os.path.isfile(args.file):
            print(f"Error: File {args.file} does not exist.")
            sys.exit(1)

        success, message = standardize_yaml_file(args.file, args.diff, args.dry_run)
        print(message)

        if args.validate and success and not args.dry_run:
            success, message = validate_yaml_file(args.file)
            print(message)

        sys.exit(0 if success else 1)

    # Process all YAML files in a directory
    if not os.path.isdir(args.dir):
        print(f"Error: Directory {args.dir} does not exist.")
        sys.exit(1)

    yaml_files = find_yaml_files(args.dir, args.exclude)
    print(f"Found {len(yaml_files)} YAML files to process.")

    success_count = 0
    failure_count = 0

    for file_path in yaml_files:
        success, message = standardize_yaml_file(file_path, args.diff, args.dry_run)
        print(message)

        if success:
            success_count += 1

            if args.validate and not args.dry_run:
                validate_success, validate_message = validate_yaml_file(file_path)
                print(validate_message)

                if not validate_success:
                    failure_count += 1
        else:
            failure_count += 1

    print(f"Processed {len(yaml_files)} files: {success_count} succeeded, {failure_count} failed.")
    sys.exit(0 if failure_count == 0 else 1)

if __name__ == "__main__":
    main()
