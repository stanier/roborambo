# src/roborambo/config_tui.py
"""
Interactive TUI for creating bot/assistant configuration files for roborambo.
"""

import os
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm, FloatPrompt, IntPrompt
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

class BotConfigTUI:
    def __init__(self):
        if HAS_RICH:
            self.console = Console()
        else:
            self.console = None
        
        self.available_tools = {
            'web': {
                'name': 'Web Engine',
                'description': 'Search and navigate the web',
                'default_enabled': True
            },
            'inspector': {
                'name': 'Tool Inspector',
                'description': 'Inspect and analyze available tools',
                'default_enabled': True
            },
            'file': {
                'name': 'File Browser',
                'description': 'Search, read and write local files',
                'default_enabled': False
            },
            'chat': {
                'name': 'Chat Interface',
                'description': 'Interact with messaging systems',
                'default_enabled': False
            },
            'knowledgebase': {
                'name': 'Knowledgebase Explorer',
                'description': 'Search internal knowledge bases',
                'default_enabled': False
            },
            'graphql': {
                'name': 'GraphQL',
                'description': 'Query GraphQL endpoints',
                'default_enabled': False
            },
            'vectorstore': {
                'name': 'Vector Store',
                'description': 'Semantic search and storage',
                'default_enabled': False
            },
            'expert': {
                'name': 'Ask An Expert',
                'description': 'Get expert input on topics',
                'default_enabled': False
            },
            'schedule': {
                'name': 'Schedule Tool',
                'description': 'Manage schedules and appointments',
                'default_enabled': False
            }
        }
        
        self.available_interfaces = {
            'zulip': {
                'name': 'Zulip',
                'description': 'Zulip team chat platform',
                'required_fields': ['key', 'email', 'site'],
                'optional_fields': ['privileged_users']
            },
            'discord': {
                'name': 'Discord',
                'description': 'Discord chat platform',
                'required_fields': ['token'],
                'optional_fields': ['privileged_users']
            },
            'mattermost': {
                'name': 'Mattermost',
                'description': 'Mattermost team collaboration',
                'required_fields': ['url', 'token'],
                'optional_fields': ['privileged_users']
            },
            'matrix': {
                'name': 'Matrix',
                'description': 'Matrix/Element chat protocol',
                'required_fields': ['homeserver', 'username', 'password'],
                'optional_fields': ['privileged_users']
            }
        }

    def print_header(self):
        if self.console:
            self.console.print(Panel.fit(
                "[bold magenta]Roborambo Bot Configuration Generator[/bold magenta]\n"
                "Create assistant configuration files for chatbots",
                border_style="magenta"
            ))
        else:
            print("=" * 60)
            print("Roborambo Bot Configuration Generator")
            print("Create assistant configuration files for chatbots")
            print("=" * 60)

    def get_input(self, prompt, default=None, choices=None):
        if HAS_RICH and choices:
            return Prompt.ask(prompt, choices=choices, default=default)
        elif HAS_RICH:
            return Prompt.ask(prompt, default=default)
        else:
            if choices:
                prompt += f" ({'/'.join(choices)})"
            if default:
                prompt += f" [{default}]"
            result = input(f"{prompt}: ").strip()
            return result if result else default

    def get_float(self, prompt, default=None):
        if HAS_RICH:
            return FloatPrompt.ask(prompt, default=default)
        else:
            if default is not None:
                prompt += f" [{default}]"
            while True:
                try:
                    result = input(f"{prompt}: ").strip()
                    return float(result) if result else default
                except ValueError:
                    print("Please enter a valid number.")

    def get_int(self, prompt, default=None):
        if HAS_RICH:
            return IntPrompt.ask(prompt, default=default)
        else:
            if default is not None:
                prompt += f" [{default}]"
            while True:
                try:
                    result = input(f"{prompt}: ").strip()
                    return int(result) if result else default
                except ValueError:
                    print("Please enter a valid integer.")

    def get_confirm(self, prompt, default=True):
        if HAS_RICH:
            return Confirm.ask(prompt, default=default)
        else:
            default_str = "Y/n" if default else "y/N"
            result = input(f"{prompt} ({default_str}): ").strip().lower()
            if not result:
                return default
            return result.startswith('y')

    def get_multiline_input(self, prompt, default=""):
        if self.console:
            self.console.print(f"[bold]{prompt}[/bold]")
            self.console.print("(Press Ctrl+D or enter empty line to finish)")
        else:
            print(f"{prompt}")
            print("(Press Ctrl+D or enter empty line to finish)")
        
        lines = []
        try:
            while True:
                line = input("> ").strip()
                if not line:
                    break
                lines.append(line)
        except EOFError:
            pass
        
        return "\n".join(lines) if lines else default

    def configure_basic_info(self):
        if self.console:
            self.console.print("\n[bold blue]Basic Information[/bold blue]")
        else:
            print("\nBasic Information:")
        
        config = {}
        config['name'] = self.get_input("Bot name", "RoboRambo")
        config['maintainers'] = [self.get_input("Maintainer name", "You")]
        config['enabled'] = self.get_confirm("Enable this bot?", True)
        
        return config

    def configure_instructions(self):
        if self.console:
            self.console.print("\n[bold blue]Instructions & Personality[/bold blue]")
        else:
            print("\nInstructions & Personality:")
        
        instructions = {}
        instructions['team'] = self.get_input("Team/Organization name", "Your Team")
        instructions['site'] = self.get_input("Site/Location", "Your Site")
        
        # Core instruction template
        instructions['instruction'] = "{persona}\\n\\n{tool_instructions}\\n\\n{scene_instructions}"
        
        # Persona
        default_persona = "You are {name}, an AI assistant powered by an LLM ran on-premises by {team} at {site}."
        if self.get_confirm("Customize bot personality?", False):
            custom_persona = self.get_multiline_input(
                "Bot personality/persona:", 
                default_persona
            )
            instructions['persona'] = custom_persona if custom_persona else default_persona
        else:
            instructions['persona'] = default_persona
        
        # Scene instructions
        default_scene = "You have access to an instant messaging service that enables communication between members of {team}. Continue the conversation history provided in Input"
        if self.get_confirm("Customize scene/context instructions?", False):
            custom_scene = self.get_multiline_input(
                "Scene/context instructions:",
                default_scene
            )
            instructions['scene_instructions'] = custom_scene if custom_scene else default_scene
        else:
            instructions['scene_instructions'] = default_scene
        
        # Timestamp instructions
        instructions['timestamp_instructions'] = "A timestamp will accompany each message, surrounded by brackets. When referring to the time, do so in a natural human-readable way"
        
        # Tool instructions template
        instructions['tool_instructions'] = "You have access to the following tools:\\n{tools}To use a tool, respond with `invoke tool.function(arg_foo = \\\"lorem\\\", arg_bar = 42)` where the tool, function and arguments appropriately complement the tool you wish to use"
        
        # Template formats
        instructions['tool_entry_template'] = "{tool_name}: {tool_desc}\\n{func_entries}\\n"
        instructions['func_entry_template'] = "  - `{tool_slug}.{func_slug}`: {func_desc}\\n    Args:{arg_entries}\\n"
        instructions['args_entry_template'] = "      - `{arg_slug}` (`{arg_type}`): {arg_desc}"
        
        return instructions

    def configure_cutoff(self):
        if self.console:
            self.console.print("\n[bold blue]Emergency Cutoff[/bold blue]")
        else:
            print("\nEmergency Cutoff:")
        
        cutoff = {}
        cutoff['enabled'] = self.get_confirm("Enable emergency cutoff phrase?", True)
        
        if cutoff['enabled']:
            cutoff['phrase'] = self.get_input("Cutoff phrase", "bicycle built for two")
            cutoff['hint'] = self.get_input(
                "Cutoff hint (for operators)", 
                "It won't be a stylish marriage, I can't afford a carriage, But you'll look sweet upon the seat Of a [cutoff phrase]!"
            )
            cutoff['message'] = "Emergency cutoff activated. {name} is now halted."
        
        return cutoff

    def configure_model_settings(self):
        if self.console:
            self.console.print("\n[bold blue]Model Settings[/bold blue]")
        else:
            print("\nModel Settings:")
        
        tunables = {}
        
        # Model file configuration
        tunables['model_file'] = self.get_input("Model config file", "ollama/neural-chat.toml")
        default_model_library = str(Path.home() / ".config" / "nothingburger" / "model_library")
        tunables['model_library'] = self.get_input("Model library path", default_model_library)
        
        # API format
        api_format = self.get_input("Preferred API format", "chat", ["chat", "completions"])
        tunables['api_format'] = api_format
        
        template_style = self.get_input("Template style", "chat", ["chat", "completion"])
        tunables['template_style'] = template_style
        
        # Generation parameters
        if self.get_confirm("Configure generation parameters?", True):
            generation = {}
            generation['frequency_penalty'] = self.get_float("Frequency penalty", 1.07)
            generation['max_tokens'] = self.get_int("Max tokens", 1024)
            generation['presence_penalty'] = self.get_float("Presence penalty", 0.0)
            generation['seed'] = self.get_int("Seed", 42)
            generation['temperature'] = self.get_float("Temperature", 0.0)
            generation['top_p'] = self.get_float("Top P", 1.0)
            generation['top_k'] = self.get_int("Top K", -1)
            
            tunables['generation'] = generation
            
            # Mirostat settings
            if self.get_confirm("Configure Mirostat sampling?", False):
                mirostat = {}
                mirostat['mode'] = self.get_int("Mirostat mode", 0)
                mirostat['eta'] = self.get_float("Mirostat eta", 0.1)
                mirostat['tau'] = self.get_float("Mirostat tau", 5.0)
                tunables['generation']['mirostat'] = mirostat
        
        return tunables

    def show_tools(self):
        if self.console:
            table = Table(title="Available Tools", box=box.ROUNDED)
            table.add_column("Key", style="cyan")
            table.add_column("Name", style="magenta") 
            table.add_column("Description", style="green")
            table.add_column("Default", style="yellow")
            
            for key, tool in self.available_tools.items():
                default = "✓" if tool['default_enabled'] else "✗"
                table.add_row(key, tool['name'], tool['description'], default)
            
            self.console.print(table)
        else:
            print("\nAvailable Tools:")
            for key, tool in self.available_tools.items():
                default = "Yes" if tool['default_enabled'] else "No"
                print(f"  {key}: {tool['name']} - {tool['description']} (Default: {default})")

    def configure_tools(self):
        if self.console:
            self.console.print("\n[bold blue]Tools Configuration[/bold blue]")
        else:
            print("\nTools Configuration:")
        
        self.show_tools()
        
        tools_config = {}
        enabled_tools = []
        
        if self.get_confirm("Use default tool selection?", True):
            enabled_tools = [key for key, tool in self.available_tools.items() if tool['default_enabled']]
        else:
            for key, tool in self.available_tools.items():
                if self.get_confirm(f"Enable {tool['name']}?", tool['default_enabled']):
                    enabled_tools.append(key)
        
        tools_config['enabled'] = enabled_tools
        
        # Tool-specific configuration
        if 'web' in enabled_tools:
            search_uri = self.get_input("Web search URI", "https://stract.com/beta/api/search")
            tools_config['web'] = {'search_uri': search_uri}
        
        return tools_config

    def show_interfaces(self):
        if self.console:
            table = Table(title="Available Interfaces", box=box.ROUNDED)
            table.add_column("Key", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Description", style="green")
            table.add_column("Required Fields", style="yellow")
            
            for key, interface in self.available_interfaces.items():
                required = ", ".join(interface['required_fields'])
                table.add_row(key, interface['name'], interface['description'], required)
            
            self.console.print(table)
        else:
            print("\nAvailable Interfaces:")
            for key, interface in self.available_interfaces.items():
                required = ", ".join(interface['required_fields'])
                print(f"  {key}: {interface['name']} - {interface['description']} (Requires: {required})")

    def configure_interfaces(self):
        if self.console:
            self.console.print("\n[bold blue]Messaging Interfaces[/bold blue]")
        else:
            print("\nMessaging Interfaces:")
        
        self.show_interfaces()
        
        interfaces_config = {}
        enabled_interfaces = []
        
        for key, interface in self.available_interfaces.items():
            if self.get_confirm(f"Configure {interface['name']}?", False):
                enabled_interfaces.append(key)
                
                # Configure interface-specific settings
                interface_config = {}
                
                if key == 'zulip':
                    interface_config['key'] = self.get_input("Bot API key", "<bot api key here>")
                    interface_config['email'] = self.get_input("Bot email", "<bot email here>")
                    interface_config['site'] = self.get_input("Zulip domain", "<zulip domain here>")
                elif key == 'discord':
                    interface_config['token'] = self.get_input("Bot token", "<discord bot token>")
                elif key == 'mattermost':
                    interface_config['url'] = self.get_input("Mattermost URL", "https://your-mattermost.com")
                    interface_config['token'] = self.get_input("Bot token", "<mattermost bot token>")
                elif key == 'matrix':
                    interface_config['homeserver'] = self.get_input("Homeserver URL", "https://matrix.org")
                    interface_config['username'] = self.get_input("Bot username", "@bot:matrix.org")
                    interface_config['password'] = self.get_input("Bot password", "<bot password>")
                
                # Privileged users
                if self.get_confirm("Add privileged users?", False):
                    privileged_users = []
                    while True:
                        user = self.get_input("Privileged user email/ID (empty to finish)")
                        if not user:
                            break
                        privileged_users.append(user)
                    if privileged_users:
                        interface_config['privileged_users'] = privileged_users
                    else:
                        interface_config['privileged_users'] = []
                else:
                    interface_config['privileged_users'] = []
                
                interfaces_config[key] = interface_config
        
        return {
            'enabled': enabled_interfaces,
            **interfaces_config
        }

    def generate_config(self):
        self.print_header()
        
        config = {}
        
        # Basic information
        basic_info = self.configure_basic_info()
        config.update(basic_info)
        
        # Instructions
        config['instructions'] = self.configure_instructions()
        
        # Cutoff
        config['cutoff'] = self.configure_cutoff()
        
        # Model settings
        config['tunables'] = self.configure_model_settings()
        
        # Tools
        config['tools'] = self.configure_tools()
        
        # Interfaces
        config['interfaces'] = self.configure_interfaces()
        
        return config

    def save_config(self, config):
        if self.console:
            self.console.print("\n[bold]Save Configuration[/bold]")
        else:
            print("\nSave Configuration")
        
        # Default save location
        default_base_dir = Path.home() / ".config" / "roborambo" / "bot_library"
        bot_name = config.get('name', 'bot').lower().replace(' ', '').replace('-', '')
        default_filename = default_base_dir / bot_name / "config.toml"
        
        filename = self.get_input("Filename", str(default_filename))
        
        # Ensure .toml extension
        if not filename.endswith('.toml'):
            filename += '.toml'
        
        # Create directory if needed
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to TOML format
        try:
            import tomli_w
            with open(filepath, 'wb') as f:
                tomli_w.dump(config, f)
            
            if self.console:
                self.console.print(f"[green]✓ Bot configuration saved to {filepath}[/green]")
                self.console.print(f"[cyan]Remember to:[/cyan]")
                self.console.print("  • Add the bot to your daemon config (bot_library/config.toml)")
                self.console.print("  • Configure your model files in the model library")
                self.console.print("  • Set up interface credentials before enabling")
            else:
                print(f"✓ Bot configuration saved to {filepath}")
                print("Remember to:")
                print("  • Add the bot to your daemon config (bot_library/config.toml)")
                print("  • Configure your model files in the model library") 
                print("  • Set up interface credentials before enabling")
            
            return str(filepath)
        except ImportError:
            print("Error: tomli-w is required for generating TOML files.")
            print("Install with: pip install tomli-w")
            return None
        except Exception as e:
            if self.console:
                self.console.print(f"[red]✗ Error saving configuration: {e}[/red]")
            else:
                print(f"✗ Error saving configuration: {e}")
            return None

    def run(self):
        try:
            config = self.generate_config()
            if config:
                # Preview config
                if self.console:
                    self.console.print("\n[bold]Configuration Preview:[/bold]")
                    try:
                        import tomli_w
                        toml_str = tomli_w.dumps(config)
                        self.console.print(Panel(toml_str, title="Generated Bot Config", border_style="green"))
                    except ImportError:
                        self.console.print("[yellow]Install tomli-w to see preview[/yellow]")
                else:
                    print("\nConfiguration Preview:")
                    try:
                        import tomli_w
                        print(tomli_w.dumps(config))
                    except ImportError:
                        print("Install tomli-w to see preview")
                
                if self.get_confirm("Save this configuration?", True):
                    self.save_config(config)
                    
                if self.get_confirm("Generate another bot configuration?", False):
                    self.run()
        except KeyboardInterrupt:
            if self.console:
                self.console.print("\n[yellow]Configuration cancelled.[/yellow]")
            else:
                print("\nConfiguration cancelled.")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
            else:
                print(f"Error: {e}")

def main():
    """Entry point for bot config TUI."""
    tui = BotConfigTUI()
    tui.run()

if __name__ == "__main__":
    main()