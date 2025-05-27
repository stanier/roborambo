#!/usr/bin/env python3
"""Simple validation for bot configuration files."""

import tomllib
from pathlib import Path
from typing import List, Tuple

class BotConfigValidator:
    """Simple validator for bot configurations."""
    
    def __init__(self):
        self.required_sections = ['instructions', 'cutoff', 'tunables', 'tools', 'interfaces']
        self.required_fields = {
            'instructions': ['team', 'site', 'instruction', 'persona'],
            'cutoff': ['enabled'],
            'tunables': ['model_file', 'model_library'],
            'tools': ['enabled'],
            'interfaces': ['enabled']
        }
        
        self.available_tools = ['web', 'inspector']
        self.available_interfaces = ['zulip']

    def validate_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate a bot configuration file."""
        errors = []
        
        # Check file exists
        if not Path(filepath).exists():
            return False, [f"File not found: {filepath}"]
        
        try:
            # Parse TOML
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)
            
            # Check basic structure
            if 'name' not in config:
                errors.append("Missing required field: name")
            if 'enabled' not in config:
                errors.append("Missing required field: enabled")
            
            # Check required sections
            for section in self.required_sections:
                if section not in config:
                    errors.append(f"Missing section: [{section}]")
                    continue
                
                # Check required fields in section
                if section in self.required_fields:
                    for field in self.required_fields[section]:
                        if field not in config[section]:
                            errors.append(f"Missing field: {section}.{field}")
            
            # Validate tools
            if 'tools' in config and 'enabled' in config['tools']:
                for tool in config['tools']['enabled']:
                    if tool not in self.available_tools:
                        errors.append(f"Unknown tool: {tool}")
            
            # Validate interfaces
            if 'interfaces' in config and 'enabled' in config['interfaces']:
                for interface in config['interfaces']['enabled']:
                    if interface not in self.available_interfaces:
                        errors.append(f"Unknown interface: {interface}")
                    
                    # Check interface configuration
                    if interface == 'zulip' and interface in config['interfaces']:
                        zulip_config = config['interfaces'][interface]
                        for field in ['key', 'email', 'site']:
                            if field not in zulip_config:
                                errors.append(f"Missing zulip field: {field}")
            
            # Basic tunables validation
            if 'tunables' in config and 'generation' in config['tunables']:
                gen = config['tunables']['generation']
                if 'temperature' in gen and not (0.0 <= gen['temperature'] <= 2.0):
                    errors.append("temperature must be between 0.0 and 2.0")
                if 'max_tokens' in gen and gen['max_tokens'] < 1:
                    errors.append("max_tokens must be positive")
                    
        except tomllib.TOMLDecodeError as e:
            errors.append(f"Invalid TOML: {e}")
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return len(errors) == 0, errors

    def test_loading(self, filepath: str) -> Tuple[bool, str]:
        """Test if the bot can be loaded."""
        try:
            from .config import Reader
            from .assistant import Assistant
            
            # Load bot config
            with open(filepath, 'rb') as f:
                bot_config = tomllib.load(f)
            
            # Try to create assistant
            assistant = Assistant(bot_config)
            return True, "Bot loaded successfully"
        except Exception as e:
            return False, str(e)

def main():
    """CLI for validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate bot configurations")
    parser.add_argument('config_file', help='Configuration file to validate')
    parser.add_argument('--test-loading', action='store_true', help='Test bot loading')
    
    args = parser.parse_args()
    
    validator = BotConfigValidator()
    is_valid, errors = validator.validate_file(args.config_file)
    
    print(f"Validating: {args.config_file}")
    
    if is_valid:
        print("✓ Configuration is valid")
        
        if args.test_loading:
            success, message = validator.test_loading(args.config_file)
            if success:
                print("✓ Bot loads successfully")
            else:
                print(f"✗ Bot loading failed: {message}")
                return 1
    else:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())