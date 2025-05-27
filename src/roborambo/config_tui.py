#!/usr/bin/env python3
"""Simple TUI for creating bot configuration files."""

import os
from pathlib import Path

class BotConfigTUI:
    def __init__(self):
        self.tools = {
            'web': {'name': 'Web Engine', 'default': True},
            'inspector': {'name': 'Tool Inspector', 'default': True},
        }
        
        self.interfaces = {
            'zulip': {
                'name': 'Zulip',
                'fields': ['key', 'email', 'site']
            }
        }

    def get_input(self, prompt, default=None):
        if default:
            prompt += f" [{default}]"
        result = input(f"{prompt}: ").strip()
        return result if result else default

    def get_confirm(self, prompt, default=True):
        default_str = "Y/n" if default else "y/N"
        result = input(f"{prompt} ({default_str}): ").strip().lower()
        if not result:
            return default
        return result.startswith('y')

    def get_float(self, prompt, default):
        while True:
            try:
                result = input(f"{prompt} [{default}]: ").strip()
                return float(result) if result else default
            except ValueError:
                print("Please enter a valid number.")

    def get_int(self, prompt, default):
        while True:
            try:
                result = input(f"{prompt} [{default}]: ").strip()
                return int(result) if result else default
            except ValueError:
                print("Please enter a valid integer.")

    def configure_basic(self):
        print("\nBasic Information:")
        config = {}
        config['name'] = self.get_input("Bot name", "MyBot")
        config['maintainers'] = [self.get_input("Maintainer name", "You")]
        config['enabled'] = self.get_confirm("Enable this bot?", True)
        return config

    def configure_instructions(self):
        print("\nInstructions:")
        instructions = {}
        instructions['team'] = self.get_input("Team/Organization", "Your Team")
        instructions['site'] = self.get_input("Site/Location", "Your Site")
        
        # Use simple defaults
        instructions['instruction'] = "{persona}\\n\\n{tool_instructions}\\n\\n{scene_instructions}"
        instructions['persona'] = "You are {name}, an AI assistant powered by an LLM ran on-premises by {team} at {site}."
        instructions['scene_instructions'] = "You have access to an instant messaging service that enables communication between members of {team}. Continue the conversation history provided in Input"
        instructions['timestamp_instructions'] = "A timestamp will accompany each message, surrounded by brackets. When referring to the time, do so in a natural human-readable way"
        instructions['tool_instructions'] = "You have access to the following tools:\\n{tools}To use a tool, respond with `invoke tool.function(arg_foo = \\\"lorem\\\", arg_bar = 42)` where the tool, function and arguments appropriately complement the tool you wish to use"
        instructions['tool_entry_template'] = "{tool_name}: {tool_desc}\\n{func_entries}\\n"
        instructions['func_entry_template'] = "  - `{tool_slug}.{func_slug}`: {func_desc}\\n    Args:{arg_entries}\\n"
        instructions['args_entry_template'] = "      - `{arg_slug}` (`{arg_type}`): {arg_desc}"
        
        return instructions

    def configure_cutoff(self):
        print("\nEmergency Cutoff:")
        cutoff = {}
        cutoff['enabled'] = self.get_confirm("Enable emergency cutoff?", True)
        if cutoff['enabled']:
            cutoff['phrase'] = self.get_input("Cutoff phrase", "bicycle built for two")
            cutoff['hint'] = "Emergency cutoff hint"
            cutoff['message'] = "Emergency cutoff activated. {name} is now halted."
        return cutoff

    def configure_model(self):
        print("\nModel Settings:")
        tunables = {}
        tunables['model_file'] = self.get_input("Model config file", "ollama/neural-chat.toml")
        default_path = str(Path.home() / ".config" / "nothingburger" / "model_library")
        tunables['model_library'] = self.get_input("Model library path", default_path)
        tunables['api_format'] = self.get_input("API format", "chat")
        tunables['template_style'] = self.get_input("Template style", "chat")
        
        if self.get_confirm("Configure generation parameters?", False):
            generation = {}
            generation['temperature'] = self.get_float("Temperature", 0.0)
            generation['max_tokens'] = self.get_int("Max tokens", 1024)
            generation['frequency_penalty'] = self.get_float("Frequency penalty", 1.07)
            tunables['generation'] = generation
        
        return tunables

    def configure_tools(self):
        print("\nTools:")
        enabled = []
        
        if self.get_confirm("Use default tools (web, inspector)?", True):
            enabled = ['web', 'inspector']
        else:
            for key, tool in self.tools.items():
                if self.get_confirm(f"Enable {tool['name']}?", tool['default']):
                    enabled.append(key)
        
        config = {'enabled': enabled}
        
        if 'web' in enabled:
            config['web'] = {
                'search_uri': self.get_input("Web search URI", "https://stract.com/beta/api/search")
            }
        
        return config

    def configure_interfaces(self):
        print("\nMessaging Interfaces:")
        enabled = []
        config = {'enabled': enabled}
        
        for key, interface in self.interfaces.items():
            if self.get_confirm(f"Configure {interface['name']}?", False):
                enabled.append(key)
                
                interface_config = {}
                for field in interface['fields']:
                    interface_config[field] = self.get_input(f"{field.title()}", f"<{field}>")
                
                interface_config['privileged_users'] = []
                config[key] = interface_config
        
        return config

    def save_config(self, config):
        # Default save location
        bot_name = config.get('name', 'bot').lower().replace(' ', '')
        default_dir = Path.home() / ".config" / "roborambo" / "bot_library" / bot_name
        default_filename = default_dir / "config.toml"
        
        filename = self.get_input("Save as", str(default_filename))
        if not filename.endswith('.toml'):
            filename += '.toml'
        
        # Create directory
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate TOML
        toml_content = self._to_toml(config)
        
        with open(filepath, 'w') as f:
            f.write(toml_content)
        
        print(f"✓ Bot configuration saved to {filepath}")
        print("Remember to add the bot to your daemon config!")

    def _to_toml(self, config):
        """Simple TOML generator."""
        lines = []
        
        # Top-level fields
        for key, value in config.items():
            if not isinstance(value, dict):
                if isinstance(value, str):
                    lines.append(f'{key} = "{value}"')
                elif isinstance(value, list):
                    if all(isinstance(x, str) for x in value):
                        items = ', '.join(f'"{x}"' for x in value)
                        lines.append(f'{key} = [{items}]')
                    else:
                        lines.append(f'{key} = {value}')
                else:
                    lines.append(f'{key} = {str(value).lower()}')
        
        # Sections
        for section, values in config.items():
            if isinstance(values, dict):
                lines.append(f'\n[{section}]')
                for key, value in values.items():
                    if isinstance(value, dict):
                        # Subsection
                        lines.append(f'\n[{section}.{key}]')
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, str):
                                lines.append(f'{subkey} = "{subvalue}"')
                            elif isinstance(subvalue, list):
                                if all(isinstance(x, str) for x in subvalue):
                                    items = ', '.join(f'"{x}"' for x in subvalue)
                                    lines.append(f'{subkey} = [{items}]')
                                else:
                                    lines.append(f'{subkey} = {subvalue}')
                            else:
                                lines.append(f'{subkey} = {subvalue}')
                    elif isinstance(value, str):
                        lines.append(f'{key} = "{value}"')
                    elif isinstance(value, list):
                        if all(isinstance(x, str) for x in value):
                            items = ', '.join(f'"{x}"' for x in value)
                            lines.append(f'{key} = [{items}]')
                        else:
                            lines.append(f'{key} = {value}')
                    else:
                        lines.append(f'{key} = {str(value).lower()}')
        
        return '\n'.join(lines) + '\n'

    def run(self):
        print("Bot Configuration Generator")
        print("=" * 40)
        
        config = {}
        config.update(self.configure_basic())
        config['instructions'] = self.configure_instructions()
        config['cutoff'] = self.configure_cutoff()
        config['tunables'] = self.configure_model()
        config['tools'] = self.configure_tools()
        config['interfaces'] = self.configure_interfaces()
        
        # Preview
        print(f"\nGenerated configuration:")
        print("-" * 30)
        print(self._to_toml(config))
        
        # Save
        if self.get_confirm("Save this configuration?", True):
            self.save_config(config)

def main():
    tui = BotConfigTUI()
    tui.run()

if __name__ == "__main__":
    main()