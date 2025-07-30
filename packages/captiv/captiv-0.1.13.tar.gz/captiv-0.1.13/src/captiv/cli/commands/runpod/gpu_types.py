"""
GPU types command for RunPod management.

This module provides the command logic for listing available GPU types from RunPod.
"""

import typer
from loguru import logger

from captiv.cli.error_handling import handle_cli_errors
from captiv.cli.options import ConfigFileOption
from captiv.services.config_manager import ConfigManager
from captiv.services.exceptions import RunPodError
from captiv.services.runpod_service import RunPodService


@handle_cli_errors
def command(
    config_file: ConfigFileOption = None,
) -> None:
    """List available GPU types from RunPod."""
    config_manager = ConfigManager(config_file)

    # Get API key from config
    api_key = config_manager.get_config_value("runpod", "api_key")
    if not api_key:
        typer.echo("Error: RunPod API key not configured.")
        typer.echo("Set it with: captiv config set runpod api_key YOUR_API_KEY")
        raise typer.Exit(1)

    try:
        runpod_service = RunPodService(api_key, verbose=False)

        typer.echo("Fetching available GPU types...")
        gpu_types = runpod_service.get_gpu_types()

        if not gpu_types:
            typer.echo("No GPU types found.")
            return

        typer.echo(f"\nFound {len(gpu_types)} GPU types:")
        typer.echo("-" * 80)

        for gpu in gpu_types[:20]:  # Show first 20
            display_name = gpu.get("displayName", "N/A")
            gpu_id = gpu.get("id", "N/A")
            memory = gpu.get("memoryInGb", "N/A")
            secure_price = gpu.get("securePrice", "N/A")
            community_price = gpu.get("communityPrice", "N/A")

            typer.echo(f"ID: {gpu_id}")
            typer.echo(f"Name: {display_name}")
            typer.echo(f"Memory: {memory} GB")
            typer.echo(f"Secure Price: ${secure_price}/hr")
            typer.echo(f"Community Price: ${community_price}/hr")
            typer.echo("-" * 40)

    except RunPodError as e:
        typer.echo(f"❌ RunPod error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}")
        logger.exception("Failed to list GPU types")
        raise typer.Exit(1) from e
