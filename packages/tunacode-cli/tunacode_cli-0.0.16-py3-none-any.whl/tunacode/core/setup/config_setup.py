"""Module: tinyagent.core.setup.config_setup

Configuration system initialization for the Sidekick CLI.
Handles user configuration loading, validation, and first-time setup onboarding.
"""

import json
from pathlib import Path

from tunacode.configuration.defaults import DEFAULT_USER_CONFIG
from tunacode.configuration.models import ModelRegistry
from tunacode.constants import APP_NAME, CONFIG_FILE_NAME, UI_COLORS
from tunacode.core.setup.base import BaseSetup
from tunacode.core.state import StateManager
from tunacode.exceptions import ConfigurationError
from tunacode.types import ConfigFile, ConfigPath, UserConfig
from tunacode.ui import console as ui
from tunacode.utils import system, user_configuration
from tunacode.utils.text_utils import key_to_title


class ConfigSetup(BaseSetup):
    """Setup step for configuration and onboarding."""

    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.config_dir: ConfigPath = Path.home() / ".config"
        self.config_file: ConfigFile = self.config_dir / CONFIG_FILE_NAME
        self.model_registry = ModelRegistry()
        self.cli_config = None  # Will be set if CLI args are provided

    @property
    def name(self) -> str:
        return "Configuration"

    async def should_run(self, force_setup: bool = False) -> bool:
        """Config setup should always run to load and merge configuration."""
        return True

    async def execute(self, force_setup: bool = False) -> None:
        """Setup configuration and run onboarding if needed."""
        self.state_manager.session.device_id = system.get_device_id()
        loaded_config = user_configuration.load_config()

        # Handle CLI configuration if provided
        if self.cli_config and any(self.cli_config.values()):
            await self._handle_cli_config(loaded_config)
            return

        if loaded_config and not force_setup:
            # Silent loading
            # Merge loaded config with defaults to ensure all required keys exist
            self.state_manager.session.user_config = self._merge_with_defaults(
                loaded_config
            )
        else:
            if force_setup:
                await ui.muted("Running setup process, resetting config")
                self.state_manager.session.user_config = DEFAULT_USER_CONFIG.copy()
                user_configuration.save_config(
                    self.state_manager
                )  # Save the default config initially
                await self._onboarding()
            else:
                # No config found - show CLI usage instead of onboarding
                from tunacode.ui.console import console
                console.print("\n[bold red]No configuration found![/bold red]")
                console.print("\n[bold]Quick Setup:[/bold]")
                console.print("Configure TunaCode using CLI flags:")
                console.print("\n[blue]Examples:[/blue]")
                console.print("  [green]tunacode --model 'openai:gpt-4' --key 'your-key'[/green]")
                console.print("  [green]tunacode --model 'anthropic:claude-3-opus' --key 'your-key'[/green]")
                console.print("  [green]tunacode --model 'openrouter:anthropic/claude-3.5-sonnet' --key 'your-key' --baseurl 'https://openrouter.ai/api/v1'[/green]")
                console.print("\n[yellow]Run 'tunacode --help' for more options[/yellow]\n")
                raise SystemExit(0)

        if not self.state_manager.session.user_config.get("default_model"):
            raise ConfigurationError(
                (
                    f"No default model found in config at [bold]{self.config_file}[/bold]\n\n"
                    "Run [code]sidekick --setup[/code] to rerun the setup process."
                )
            )

        # No model validation - trust user's model choice

        self.state_manager.session.current_model = (
            self.state_manager.session.user_config["default_model"]
        )

    async def validate(self) -> bool:
        """Validate that configuration is properly set up."""
        # Check that we have a user config
        if not self.state_manager.session.user_config:
            return False

        # Check that we have a default model
        if not self.state_manager.session.user_config.get("default_model"):
            return False

        # No model validation - trust user input

        return True

    def _merge_with_defaults(self, loaded_config: UserConfig) -> UserConfig:
        """Merge loaded config with defaults to ensure all required keys exist."""
        # Start with loaded config if available, otherwise use defaults
        if loaded_config:
            merged = loaded_config.copy()

            # Add missing top-level keys from defaults
            for key, default_value in DEFAULT_USER_CONFIG.items():
                if key not in merged:
                    merged[key] = default_value

            return merged
        else:
            return DEFAULT_USER_CONFIG.copy()

    async def _onboarding(self):
        """Run the onboarding process for new users."""
        initial_config = json.dumps(
            self.state_manager.session.user_config, sort_keys=True
        )

        await self._step1_api_keys()

        # Only continue if at least one API key was provided
        env = self.state_manager.session.user_config.get("env", {})
        has_api_key = any(key.endswith("_API_KEY") and env.get(key) for key in env)

        if has_api_key:
            if not self.state_manager.session.user_config.get("default_model"):
                await self._step2_default_model()

            # Compare configs to see if anything changed
            current_config = json.dumps(
                self.state_manager.session.user_config, sort_keys=True
            )
            if initial_config != current_config:
                if user_configuration.save_config(self.state_manager):
                    message = f"Config saved to: [bold]{self.config_file}[/bold]"
                    await ui.panel(
                        "Finished", message, top=0, border_style=UI_COLORS["success"]
                    )
                else:
                    await ui.error("Failed to save configuration.")
        else:
            await ui.panel(
                "Setup canceled",
                "At least one API key is required.",
                border_style=UI_COLORS["warning"],
            )

    async def _step1_api_keys(self):
        """Onboarding step 1: Collect API keys."""
        message = (
            f"Welcome to {APP_NAME}!\n"
            "Let's get you setup. First, we'll need to set some environment variables.\n"
            "Skip the ones you don't need."
        )
        await ui.panel("Setup", message, border_style=UI_COLORS["primary"])
        env_keys = self.state_manager.session.user_config["env"].copy()
        for key in env_keys:
            provider = key_to_title(key)
            val = await ui.input(
                "step1",
                pretext=f"  {provider}: ",
                is_password=True,
                state_manager=self.state_manager,
            )
            val = val.strip()
            if val:
                self.state_manager.session.user_config["env"][key] = val

    async def _step2_default_model(self):
        """Onboarding step 2: Select default model."""
        message = "Which model would you like to use by default?\n\n"

        model_ids = self.model_registry.list_model_ids()
        for index, model_id in enumerate(model_ids):
            message += f"  {index} - {model_id}\n"
        message = message.strip()

        await ui.panel("Default Model", message, border_style=UI_COLORS["primary"])
        choice = await ui.input(
            "step2",
            pretext="  Default model (#): ",
            validator=ui.ModelValidator(len(model_ids)),
            state_manager=self.state_manager,
        )
        self.state_manager.session.user_config["default_model"] = model_ids[int(choice)]

    async def _step2_default_model_simple(self):
        """Simple model selection - just enter model name."""
        await ui.muted("Format: provider:model-name")
        await ui.muted("Examples: openai:gpt-4.1, anthropic:claude-3-opus, google-gla:gemini-2.0-flash")
        
        while True:
            model_name = await ui.input(
                "step2",
                pretext="  Model (provider:name): ",
                state_manager=self.state_manager,
            )
            model_name = model_name.strip()
            
            # Check if provider prefix is present
            if ":" not in model_name:
                await ui.error("Model name must include provider prefix")
                await ui.muted("Format: provider:model-name")
                await ui.muted("You can always change it later with /model")
                continue
            
            # No validation - user is responsible for correct model names
            self.state_manager.session.user_config["default_model"] = model_name
            await ui.warning("Model set without validation - verify the model name is correct")
            await ui.success(f"Selected model: {model_name}")
            break

    async def _handle_cli_config(self, loaded_config: UserConfig) -> None:
        """Handle configuration provided via CLI arguments."""
        # Start with existing config or defaults
        if loaded_config:
            self.state_manager.session.user_config = self._merge_with_defaults(loaded_config)
        else:
            self.state_manager.session.user_config = DEFAULT_USER_CONFIG.copy()
        
        # Apply CLI overrides
        if self.cli_config.get("key"):
            # Determine which API key to set based on the model or baseurl
            if self.cli_config.get("baseurl") and "openrouter" in self.cli_config["baseurl"]:
                self.state_manager.session.user_config["env"]["OPENROUTER_API_KEY"] = self.cli_config["key"]
            elif self.cli_config.get("model"):
                if "claude" in self.cli_config["model"] or "anthropic" in self.cli_config["model"]:
                    self.state_manager.session.user_config["env"]["ANTHROPIC_API_KEY"] = self.cli_config["key"]
                elif "gpt" in self.cli_config["model"] or "openai" in self.cli_config["model"]:
                    self.state_manager.session.user_config["env"]["OPENAI_API_KEY"] = self.cli_config["key"]
                elif "gemini" in self.cli_config["model"]:
                    self.state_manager.session.user_config["env"]["GEMINI_API_KEY"] = self.cli_config["key"]
                else:
                    # Default to OpenRouter for unknown models
                    self.state_manager.session.user_config["env"]["OPENROUTER_API_KEY"] = self.cli_config["key"]
        
        if self.cli_config.get("baseurl"):
            self.state_manager.session.user_config["env"]["OPENAI_BASE_URL"] = self.cli_config["baseurl"]
        
        if self.cli_config.get("model"):
            model = self.cli_config["model"]
            # Require provider prefix
            if ":" not in model:
                raise ConfigurationError(
                    f"Model '{model}' must include provider prefix\n"
                    "Format: provider:model-name\n"
                    "Examples: openai:gpt-4.1, anthropic:claude-3-opus"
                )
            
            self.state_manager.session.user_config["default_model"] = model
        
        # Set current model
        self.state_manager.session.current_model = self.state_manager.session.user_config["default_model"]
        
        # Save the configuration
        if user_configuration.save_config(self.state_manager):
            await ui.warning("Model set without validation - verify the model name is correct")
            await ui.success(f"Configuration saved to: {self.config_file}")
        else:
            await ui.error("Failed to save configuration.")
