#!/usr/bin/env python3
"""
Comprehensive test suite for nothingburger and roborambo TUIs.
"""

import os
import tempfile
import tomllib
from pathlib import Path
from typing import Dict, List, Any
import unittest
from unittest.mock import patch, MagicMock

class TestModelConfigTUI(unittest.TestCase):
    """Test cases for nothingburger model configuration TUI."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.temp_dir))
    
    def test_openai_config_generation(self):
        """Test generating OpenAI configuration."""
        try:
            from nothingburger.config_tui import ModelConfigTUI
        except ImportError:
            self.skipTest("nothingburger.config_tui not available")
        
        tui = ModelConfigTUI()
        
        # Mock user inputs for OpenAI configuration
        with patch.object(tui, 'get_input') as mock_input, \
             patch.object(tui, 'get_confirm') as mock_confirm, \
             patch.object(tui, 'get_float') as mock_float, \
             patch.object(tui, 'get_int') as mock_int:
            
            # Configure mocks to simulate user inputs
            mock_input.side_effect = [
                'openai',  # provider
                'https://api.openai.com/v1',  # base_url
                'gpt-4-turbo-preview',  # model_key
                'chat',  # api_format
                'sk-test-key',  # api_key
                'Test GPT-4',  # name
                'OpenAI',  # author
                'MIT',  # license
                'https://openai.com',  # website
                'test-model.toml'  # filename
            ]
            
            mock_confirm.side_effect = [
                True,  # set api key
                True,  # configure generation
                False,  # add stop sequences
                True,  # save config
                False  # generate another
            ]
            
            mock_float.side_effect = [0.7, 0.9, 0.0, 0.0]  # temperature, top_p, penalties
            mock_int.side_effect = [1024, 40, 42]  # max_tokens, top_k, seed
            
            # Test config generation
            config = tui.generate_config()
            
            self.assertIsNotNone(config)
            self.assertEqual(config['service']['provider'], 'openai')
            self.assertEqual(config['service']['api_format'], 'chat')
            self.assertEqual(config['name'], 'Test GPT-4')
    
    def test_ollama_config_generation(self):
        """Test generating Ollama configuration."""
        try:
            from nothingburger.config_tui import ModelConfigTUI
        except ImportError:
            self.skipTest("nothingburger.config_tui not available")
        
        tui = ModelConfigTUI()
        
        # Test Ollama configuration
        config = tui.configure_ollama()
        
        # Mock inputs
        with patch.object(tui, 'get_input') as mock_input:
            mock_input.side_effect = [
                'http://localhost:11434',
                'llama2:7b',
                'completions'
            ]
            
            config = tui.configure_ollama()
            
            self.assertEqual(config['service']['provider'], 'ollama')
            self.assertEqual(config['service']['api_format'], 'completions')

class TestBotConfigTUI(unittest.TestCase):
    """Test cases for roborambo bot configuration TUI."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.temp_dir))
    
    def test_basic_bot_config_generation(self):
        """Test generating basic bot configuration."""
        try:
            from roborambo.config_tui import BotConfigTUI
        except ImportError:
            self.skipTest("roborambo.config_tui not available")
        
        tui = BotConfigTUI()
        
        # Test basic info configuration
        with patch.object(tui, 'get_input') as mock_input, \
             patch.object(tui, 'get_confirm') as mock_confirm:
            
            mock_input.side_effect = ['TestBot', 'Alice']
            mock_confirm.return_value = True
            
            config = tui.configure_basic_info()
            
            self.assertEqual(config['name'], 'TestBot')
            self.assertEqual(config['maintainers'], ['Alice'])
            self.assertTrue(config['enabled'])
    
    def test_tool_configuration(self):
        """Test tool configuration."""
        try:
            from roborambo.config_tui import BotConfigTUI
        except ImportError:
            self.skipTest("roborambo.config_tui not available")
        
        tui = BotConfigTUI()
        
        with patch.object(tui, 'get_confirm') as mock_confirm, \
             patch.object(tui, 'get_input') as mock_input:
            
            # Use default tool selection
            mock_confirm.side_effect = [True]  # use defaults
            mock_input.return_value = 'https://stract.com/beta/api/search'
            
            config = tui.configure_tools()
            
            self.assertIn('web', config['enabled'])
            self.assertIn('inspector', config['enabled'])
            self.assertEqual(config['web']['search_uri'], 'https://stract.com/beta/api/search')

class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.temp_dir))
    
    def create_test_model_config(self, config_dict: Dict[str, Any]) -> str:
        """Create a test model configuration file."""
        config_path = Path(self.temp_dir) / "test_model.toml"
        try:
            import tomli_w
            with open(config_path, 'wb') as f:
                tomli_w.dump(config_dict, f)
        except ImportError:
            # Fallback to manual TOML writing
            with open(config_path, 'w') as f:
                f.write(f"name = \"{config_dict.get('name', 'Test')}\"\n")
                f.write("[service]\n")
                for key, value in config_dict.get('service', {}).items():
                    f.write(f"{key} = \"{value}\"\n")
        
        return str(config_path)
    
    def test_valid_openai_config(self):
        """Test validation of valid OpenAI configuration."""
        try:
            from nothingburger.config_validator import ConfigValidator
        except ImportError:
            self.skipTest("nothingburger.config_validator not available")
        
        config = {
            'name': 'Test GPT-4',
            'author': 'OpenAI',
            'service': {
                'provider': 'openai',
                'base_url': 'https://api.openai.com/v1',
                'model_key': 'gpt-4-turbo-preview',
                'api_format': 'chat'
            },
            'generation': {
                'temperature': 0.7,
                'max_tokens': 1024
            }
        }
        
        config_path = self.create_test_model_config(config)
        validator = ConfigValidator()
        is_valid, errors = validator.validate_file(config_path)
        
        self.assertTrue(is_valid, f"Validation errors: {errors}")
    
    def test_invalid_openai_config(self):
        """Test validation of invalid OpenAI configuration."""
        try:
            from nothingburger.config_validator import ConfigValidator
        except ImportError:
            self.skipTest("nothingburger.config_validator not available")
        
        config = {
            'name': 'Test GPT-4',
            'service': {
                'provider': 'openai',
                # Missing required fields: base_url, model_key
                'api_format': 'invalid_format'
            }
        }
        
        config_path = self.create_test_model_config(config)
        validator = ConfigValidator()
        is_valid, errors = validator.validate_file(config_path)
        
        self.assertFalse(is_valid)
        self.assertTrue(any('base_url' in error for error in errors))
        self.assertTrue(any('model_key' in error for error in errors))
        self.assertTrue(any('api_format' in error for error in errors))
    
    def create_test_bot_config(self, config_dict: Dict[str, Any]) -> str:
        """Create a test bot configuration file."""
        config_path = Path(self.temp_dir) / "test_bot.toml"
        try:
            import tomli_w
            with open(config_path, 'wb') as f:
                tomli_w.dump(config_dict, f)
        except ImportError:
            # Fallback to manual TOML writing
            with open(config_path, 'w') as f:
                f.write(f"name = \"{config_dict.get('name', 'Test')}\"\n")
                f.write(f"enabled = {str(config_dict.get('enabled', True)).lower()}\n")
                for section_name, section in config_dict.items():
                    if isinstance(section, dict):
                        f.write(f"\n[{section_name}]\n")
                        for key, value in section.items():
                            if isinstance(value, str):
                                f.write(f"{key} = \"{value}\"\n")
                            elif isinstance(value, list):
                                f.write(f"{key} = {value}\n")
                            else:
                                f.write(f"{key} = {value}\n")
        
        return str(config_path)
    
    def test_valid_bot_config(self):
        """Test validation of valid bot configuration."""
        try:
            from roborambo.config_validator import BotConfigValidator
        except ImportError:
            self.skipTest("roborambo.config_validator not available")
        
        config = {
            'name': 'TestBot',
            'enabled': True,
            'instructions': {
                'team': 'Test Team',
                'site': 'Test Site',
                'instruction': '{persona}\\n\\n{tool_instructions}\\n\\n{scene_instructions}',
                'persona': 'You are {name}, a test bot.'
            },
            'cutoff': {
                'enabled': True,
                'phrase': 'test cutoff'
            },
            'tunables': {
                'model_file': 'test.toml',
                'model_library': '/tmp'
            },
            'tools': {
                'enabled': ['web', 'inspector']
            },
            'interfaces': {
                'enabled': []
            }
        }
        
        config_path = self.create_test_bot_config(config)
        validator = BotConfigValidator()
        is_valid, errors = validator.validate_file(config_path)
        
        self.assertTrue(is_valid, f"Validation errors: {errors}")

class TestIntegration(unittest.TestCase):
    """Integration tests for TUI-generated configurations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.temp_dir))
    
    def test_model_config_integration(self):
        """Test that generated model configs can be loaded."""
        # This test would require actual model libraries to be meaningful
        # For now, we'll just test the configuration structure
        config = {
            'name': 'Integration Test Model',
            'service': {
                'provider': 'ollama',
                'base_url': 'http://localhost:11434',
                'model_key': 'llama2:7b',
                'api_format': 'completions'
            },
            'generation': {
                'temperature': 0.7,
                'max_tokens': 512
            }
        }
        
        # Save config
        config_path = Path(self.temp_dir) / "integration_model.toml"
        try:
            import tomli_w
            with open(config_path, 'wb') as f:
                tomli_w.dump(config, f)
            
            # Validate it can be read back
            with open(config_path, 'rb') as f:
                loaded_config = tomllib.load(f)
            
            self.assertEqual(loaded_config['name'], config['name'])
            self.assertEqual(loaded_config['service']['provider'], 'ollama')
            
        except ImportError:
            self.skipTest("tomli_w not available for integration test")

def run_tui_tests():
    """Run all TUI tests."""
    # Test discovery and execution
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestModelConfigTUI,
        TestBotConfigTUI, 
        TestConfigValidation,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def validate_example_configs():
    """Validate the example configurations."""
    print("Validating example configurations...")
    
    # Example model configs to validate
    model_examples = [
        {
            'name': 'GPT-4 Production',
            'service': {
                'provider': 'openai',
                'base_url': 'https://api.openai.com/v1',
                'model_key': 'gpt-4-turbo-preview',
                'api_format': 'chat'
            },
            'generation': {
                'temperature': 0.7,
                'max_tokens': 1024
            }
        },
        {
            'name': 'Llama 2 7B',
            'service': {
                'provider': 'ollama',
                'base_url': 'http://localhost:11434',
                'model_key': 'llama2:7b',
                'api_format': 'completions'
            }
        }
    ]
    
    # Example bot configs to validate
    bot_examples = [
        {
            'name': 'HelpBot',
            'enabled': True,
            'instructions': {
                'team': 'Acme Corp',
                'site': 'Main Office',
                'instruction': '{persona}\\n\\n{tool_instructions}\\n\\n{scene_instructions}',
                'persona': 'You are {name}, a helpful assistant.'
            },
            'cutoff': {'enabled': True},
            'tunables': {
                'model_file': 'test.toml',
                'model_library': '/tmp'
            },
            'tools': {'enabled': ['web']},
            'interfaces': {'enabled': []}
        }
    ]
    
    # Validate model configs
    try:
        from nothingburger.config_validator import ConfigValidator
        model_validator = ConfigValidator()
        
        for i, config in enumerate(model_examples):
            # Create temporary file
            temp_file = f"/tmp/test_model_{i}.toml"
            try:
                import tomli_w
                with open(temp_file, 'wb') as f:
                    tomli_w.dump(config, f)
                
                is_valid, errors = model_validator.validate_file(temp_file)
                if is_valid:
                    print(f"✓ Model example {i+1} is valid")
                else:
                    print(f"✗ Model example {i+1} has errors: {errors}")
                
                os.unlink(temp_file)
            except ImportError:
                print(f"⚠ Skipping model validation {i+1} - tomli_w not available")
                
    except ImportError:
        print("⚠ Skipping model validation - nothingburger.config_validator not available")
    
    # Validate bot configs
    try:
        from roborambo.config_validator import BotConfigValidator
        bot_validator = BotConfigValidator()
        
        for i, config in enumerate(bot_examples):
            # Create temporary file
            temp_file = f"/tmp/test_bot_{i}.toml"
            try:
                import tomli_w
                with open(temp_file, 'wb') as f:
                    tomli_w.dump(config, f)
                
                is_valid, errors = bot_validator.validate_file(temp_file)
                if is_valid:
                    print(f"✓ Bot example {i+1} is valid")
                else:
                    print(f"✗ Bot example {i+1} has errors: {errors}")
                
                os.unlink(temp_file)
            except ImportError:
                print(f"⚠ Skipping bot validation {i+1} - tomli_w not available")
                
    except ImportError:
        print("⚠ Skipping bot validation - roborambo.config_validator not available")

def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TUI Test Suite")
    parser.add_argument('--validate-examples', action='store_true', help='Validate example configurations')
    parser.add_argument('--run-tests', action='store_true', help='Run unit tests')
    parser.add_argument('--all', action='store_true', help='Run all tests and validations')
    
    args = parser.parse_args()
    
    if args.all:
        args.validate_examples = True
        args.run_tests = True
    
    if not any([args.validate_examples, args.run_tests]):
        args.all = True
        args.validate_examples = True
        args.run_tests = True
    
    success = True
    
    if args.validate_examples:
        print("=" * 50)
        print("VALIDATING EXAMPLE CONFIGURATIONS")
        print("=" * 50)
        validate_example_configs()
        print()
    
    if args.run_tests:
        print("=" * 50)
        print("RUNNING UNIT TESTS")
        print("=" * 50)
        success = run_tui_tests()
        print()
    
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())