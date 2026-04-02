#!/usr/bin/env python3
"""
Configuration Validator for Windows Crema Orchestrator
Validates the server_config.yaml and checks directory structure
"""

import yaml
import os
from pathlib import Path

def load_config():
    """Load the YAML configuration file"""
    config_path = Path(__file__).parent / "server_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def validate_directories(config):
    """Validate that all configured directories exist"""
    paths_to_check = []

    # Extract paths from config
    if 'test_path' in config:
        paths_to_check.append(config['test_path'])

    if 'processing' in config:
        for key, path in config['processing'].items():
            paths_to_check.append(path)

    if 'logging' in config and 'path' in config['logging']:
        paths_to_check.append(config['logging']['path'])

    # Check instance paths
    if 'instances' in config:
        for instance in config['instances']:
            for key, value in instance.items():
                if 'path' in key and isinstance(value, str) and ('E:/' in value or 'C:/' in value):
                    paths_to_check.append(value)

    # Validate paths
    results = {}
    for path in paths_to_check:
        path_obj = Path(path)
        results[path] = {
            'exists': path_obj.exists(),
            'is_directory': path_obj.is_dir() if path_obj.exists() else False
        }

    return results

def main():
    """Main validation function"""
    print("🔍 Validating Windows Server Configuration...")
    print("=" * 50)

    try:
        config = load_config()
        print("✅ Configuration file loaded successfully")

        # Validate directories
        print("\n📂 Directory Validation:")
        dir_results = validate_directories(config)

        for path, result in dir_results.items():
            status = "✅" if result['exists'] else "❌"
            print(f"{status} {path}")
            if not result['exists']:
                print(f"   ⚠️  Directory does not exist")

        print(f"\n📋 Summary:")
        print(f"   Environment: {config.get('environment', 'Not specified')}")
        print(f"   Server Port: {config.get('server', {}).get('port', 'Not specified')}")
        print(f"   Test Path: {config.get('test_path', 'Not specified')}")
        print(f"   Config Dir: {config.get('config_dir', 'Not specified')}")

    except Exception as e:
        print(f"❌ Error validating configuration: {e}")

if __name__ == "__main__":
    main()