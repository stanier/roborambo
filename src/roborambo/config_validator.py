# src/roborambo/config_validator.py
"""
Validation utilities for roborambo bot configurations.
"""

import os
import tomllib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class BotConfigValidator:
    """Validates roborambo bot configuration files."""
    
    def __init__(self):
        self.required_sections = ['instructions', 'cutoff', 'tunables', 'tools', 'interfaces']
        self.required_fields = {
            'instructions': ['team', 'site', 'instruction', 'persona'],
            'cutoff': ['enabled'],
            'tunables': ['model_file', 'model_library'],
            'tools': ['enabled'],
            'interfaces': ['enabled']
        }
        
        self.available_tools = [
            'web', 'inspector', 'file', 'chat', 'knowledgebase', 
            'graphql', 'vectorstore', 'expert', 'schedule'
        ]
        
        self.available_interfaces = ['zulip', 'discord', 'mattermost', 'matrix']
        
        self.interface_requirements = {
            'zulip': ['key', 'email', 'site'],
            'discord': ['token'],
            'mattermost': ['url', 'token'],
            'matrix': ['homeserver', 'username', 'password']
        }

    def validate_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate a bot configuration file. Returns (is_valid, errors)."""
        errors = []
        
        try:
            # Check file exists and is readable
            if not Path(filepath).exists():
                errors.append(f"Configuration file not found: {filepath}")
                return False, errors
            
            # Parse TOML
            with open(filepath, 'rb') as f:
                config = tomllib.load(f)
            
            # Validate basic structure
            structure_errors = self._validate_structure(config)
            errors.extend(structure_errors)
            
            # Validate instructions
            instruction_errors = self._validate_instructions(config)
            errors.extend(instruction_errors)
            
            # Validate tools
            tool_errors = self._validate_tools(config)
            errors.extend(tool_errors)
            
            # Validate interfaces
            interface_errors = self._validate_interfaces(config)
            errors.extend(interface_errors)
            
            # Validate tunables
            tunable_errors = self._validate_tunables(config)
            errors.extend(tunable_errors)
            
        except tomllib.TOMLDecodeError as e:
            errors.append(f"Invalid TOML syntax: {e}")
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return len(errors) == 0, errors

    def _validate_structure(self, config: Dict) -> List[str]:
        """Validate basic configuration structure."""
        errors = []
        
        # Check required top-level fields
        if 'name' not in config:
            errors.append("Missing required field: name")
        if 'enabled' not in config:
            errors.append("Missing required field: enabled")
        
        # Check required sections
        for section in self.required_sections:
            if section not in config:
                errors.append(f"Missing required section: [{section}]")
                continue
            
            # Check required fields in each section
            if section in self.required_fields:
                section_config = config[section]
                for field in self.required_fields[section]:
                    if field not in section_config:
                        errors.append(f"Missing required field: {section}.{field}")
        
        return errors

    def _validate_instructions(self, config: Dict) -> List[str]:
        """Validate instruction configuration."""
        errors = []
        
        if 'instructions' not in config:
            return errors
        
        instructions = config['instructions']
        
        # Validate template strings contain expected placeholders
        templates_to_check = {
            'instruction': ['{persona}', '{tool_instructions}', '{scene_instructions}'],
            'persona': ['{name}'],
            'scene_instructions': ['{team}'],
            'tool_instructions': ['{tools}']
        }
        
        for template_name, expected_placeholders in templates_to_check.items():
            if template_name in instructions:
                template = instructions[template_name]
                for placeholder in expected_placeholders:
                    if placeholder not in template:
                        errors.append(f"instructions.{template_name} missing placeholder: {placeholder}")
        
        return errors

    def _validate_tools(self, config: Dict) -> List[str]:
        """Validate tool configuration."""
        errors = []
        
        if 'tools' not in config:
            return errors
        
        tools = config['tools']
        
        # Validate enabled tools
        if 'enabled' in tools:
            for tool in tools['enabled']:
                if tool not in self.available_tools:
                    errors.append(f"Unknown tool: {tool}")
        
        # Validate tool-specific configurations
        if 'web' in tools and 'web' in tools['enabled']:
            web_config = tools['web']
            if 'search_uri' in web_config:
                if not web_config['search_uri'].startswith(('http://', 'https://')):
                    errors.append("tools.web.search_uri must be a valid HTTP/HTTPS URL")
        
        return errors

    def _validate_interfaces(self, config: Dict) -> List[str]:
        """Validate interface configuration."""
        errors = []
        
        if 'interfaces' not in config:
            return errors
        
        interfaces = config['interfaces']
        
        # Validate enabled interfaces
        if 'enabled' in interfaces:
            for interface in interfaces['enabled']:
                if interface not in self.available_interfaces:
                    errors.append(f"Unknown interface: {interface}")
                
                # Check interface-specific configuration
                if interface in interfaces:
                    interface_config = interfaces[interface]
                    required_fields = self.interface_requirements.get(interface, [])
                    
                    for field in required_fields:
                        if field not in interface_config:
                            errors.append(f"Missing required field for {interface}: interfaces.{interface}.{field}")
                    
                    # Validate URLs for interfaces that need them
                    if interface in ['mattermost'] and 'url' in interface_config:
                        if not interface_config['url'].startswith(('http://', 'https://')):
                            errors.append(f"interfaces.{interface}.url must be a valid HTTP/HTTPS URL")
                    
                    if interface == 'matrix' and 'homeserver' in interface_config:
                        if not interface_config['homeserver'].startswith(('http://', 'https://')):
                            errors.append(f"interfaces.{interface}.homeserver must be a valid HTTP/HTTPS URL")
        
        return errors

    def _validate_tunables(self, config: Dict) -> List[str]:
        """Validate tunables configuration."""
        errors = []
        
        if 'tunables' not in config:
            return errors
        
        tunables = config['tunables']
        
        # Validate API format
        if 'api_format' in tunables:
            if tunables['api_format'] not in ['chat', 'completions']:
                errors.append("tunables.api_format must be 'chat' or 'completions'")
        
        if 'template_style' in tunables:
            if tunables['template_style'] not in ['chat', 'completion']:
                errors.append("tunables.template_style must be 'chat' or 'completion'")
        
        # Validate generation parameters if present
        if 'generation' in tunables:
            generation = tunables['generation']
            
            # Validate numeric ranges
            numeric_validations = {
                'temperature': (0.0, 2.0),
                'top_p': (0.0, 1.0),
                'top_k': (-1, None),
                'max_tokens': (1, None),
                'presence_penalty': (-2.0, 2.0),
                'frequency_penalty': (-2.0, 2.0),
                'seed': (-1, None)
            }
            
            for field, (min_val, max_val) in numeric_validations.items():
                if field in generation:
                    value = generation[field]
                    if not isinstance(value, (int, float)):
                        errors.append(f"tunables.generation.{field} must be a number")
                        continue
                    
                    if min_val is not None and value < min_val:
                        errors.append(f"tunables.generation.{field} must be >= {min_val}")
                    if max_val is not None and value > max_val:
                        errors.append(f"tunables.generation.{field} must be <= {max_val}")
        
        return errors

    def test_bot_loading(self, filepath: str) -> Tuple[bool, Optional[str]]:
        """Test if the bot configuration can be loaded. Returns (success, error)."""
        try:
            from .config import Reader
            from .assistant import Assistant
            
            # Mock a simple config structure for testing
            config_reader = Reader()
            
            # Load the specific bot config
            with open(filepath, 'rb') as f:
                bot_config = tomllib.load(f)
            
            # Try to create an assistant instance
            assistant = Assistant(bot_config)
            
            return True, None
        except Exception as e:
            return False, str(e)

    def validate_model_reference(self, bot_config_path: str) -> Tuple[bool, Optional[str]]:
        """Validate that the referenced model configuration exists and is valid."""
        try:
            with open(bot_config_path, 'rb') as f:
                bot_config = tomllib.load(f)
            
            if 'tunables' not in bot_config:
                return False, "No tunables section found"
            
            model_library = bot_config['tunables'].get('model_library', '')
            model_file = bot_config['tunables'].get('model_file', '')
            
            if not model_library or not model_file:
                return False, "model_library or model_file not specified"
            
            # Expand environment variables
            model_library = os.path.expandvars(model_library)
            model_path = Path(model_library) / model_file
            
            if not model_path.exists():
                return False, f"Model configuration not found: {model_path}"
            
            # Validate the model config
            try:
                from nothingburger.config_validator import ConfigValidator
                validator = ConfigValidator()
                is_valid, errors = validator.validate_file(str(model_path))
                if not is_valid:
                    return False, f"Invalid model configuration: {'; '.join(errors)}"
            except ImportError:
                # If nothingburger validator not available, just check file exists
                pass
            
            return True, None
            
        except Exception as e:
            return False, str(e)

def validate_config_cli():
    """Command-line interface for bot config validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate roborambo bot configurations")
    parser.add_argument('config_file', help='Path to configuration file')
    parser.add_argument('--test-loading', action='store_true', help='Test bot loading')
    parser.add_argument('--check-model', action='store_true', help='Validate referenced model config')
    parser.add_argument('--quiet', action='store_true', help='Only output errors')
    
    args = parser.parse_args()
    
    validator = BotConfigValidator()
    is_valid, errors = validator.validate_file(args.config_file)
    
    if not args.quiet:
        print(f"Validating: {args.config_file}")
    
    exit_code = 0
    
    if is_valid:
        if not args.quiet:
            print("✓ Configuration is valid")
        
        if args.check_model:
            success, error = validator.validate_model_reference(args.config_file)
            if success:
                if not args.quiet:
                    print("✓ Model reference is valid")
            else:
                print(f"✗ Model reference validation failed: {error}")
                exit_code = 1
        
        if args.test_loading:
            success, error = validator.test_bot_loading(args.config_file)
            if success:
                if not args.quiet:
                    print("✓ Bot loads successfully")
            else:
                print(f"✗ Bot loading failed: {error}")
                exit_code = 1
    else:
        print("✗ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        exit_code = 1
    
    return exit_code

if __name__ == "__main__":
    exit(validate_config_cli())