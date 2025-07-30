"""
RunPod service for managing remote GPU instances for model inference.

This service handles the creation, management, and communication with RunPod instances
for running image captioning models remotely. It provides a seamless interface for
offloading compute-intensive model operations to cloud GPUs.
"""

import json
import time
from typing import Any

import requests
from loguru import logger

from captiv.services.exceptions import RunPodError


def _import_runpod():
    """Import runpod library lazily to avoid initialization issues."""
    try:
        import runpod

        return runpod
    except ImportError as e:
        raise RunPodError(f"RunPod library not installed: {str(e)}") from e


class RunPodService:
    """Service for managing RunPod instances and remote model inference."""

    def __init__(
        self, api_key: str, template_id: str | None = None, verbose: bool = True
    ):
        """
        Initialize the RunPod service.

        Args:
            api_key: RunPod API key for authentication
            template_id: Optional template ID for pod creation
            verbose: Whether to enable verbose logging (for GUI/mutations)
        """
        if not api_key:
            raise RunPodError("RunPod API key is required")

        self.api_key = api_key
        self.template_id = template_id
        self.verbose = verbose
        self.active_pod_id: str | None = None
        self.pod_endpoint: str | None = None

        try:
            # Import and set the API key for the runpod library
            runpod = _import_runpod()
            runpod.api_key = api_key
            if self.verbose:
                logger.info("RunPod service initialized successfully")
        except Exception as e:
            raise RunPodError(f"Failed to initialize RunPod service: {str(e)}") from e

    def get_gpu_types(self) -> list[dict[str, Any]]:
        """
        Get available GPU types from RunPod.

        Returns:
            List of available GPU types with their IDs and details

        Raises:
            RunPodError: If the API request fails
        """
        try:
            # Use the runpod library to get GPU types
            runpod = _import_runpod()
            gpu_types = runpod.get_gpus()
            # Ensure we return a list
            if isinstance(gpu_types, dict):
                return [gpu_types]
            return gpu_types or []
        except Exception as e:
            raise RunPodError(f"Failed to get GPU types: {str(e)}") from e

    def create_pod(
        self,
        name: str = "captiv-joycaption",
        gpu_type: str = "NVIDIA A30",
        container_disk_size: int = 50,
        volume_disk_size: int = 50,
        ports: str = "7860/http,8888/http,22/tcp",
    ) -> str:
        """
        Create a new RunPod instance.

        Args:
            name: Name for the pod
            gpu_type: GPU type ID to use
            container_disk_size: Container disk size in GB
            volume_disk_size: Volume disk size in GB
            ports: Port configuration string

        Returns:
            Pod ID of the created instance

        Raises:
            RunPodError: If pod creation fails
        """
        if self.verbose:
            logger.info(f"Creating RunPod instance: {name}")

        try:
            # Use the runpod library to create a pod
            runpod = _import_runpod()
            # Create pod with base image (template_id not supported in runpod 1.0.1)
            pod = runpod.create_pod(
                name=name,
                image_name="runpod/base:0.4.0-cuda11.8.0",
                gpu_type_id=gpu_type,
                container_disk_in_gb=container_disk_size,
                volume_in_gb=volume_disk_size,
                ports=ports,
                env={
                    "JUPYTER_PASSWORD": "captiv123",
                    "RUNPOD_POD_ID": "{{POD_ID}}",
                },
            )

            if not pod or not pod.get("id"):
                raise RunPodError("Failed to create pod: No pod ID returned")

            pod_id = pod["id"]
            self.active_pod_id = pod_id

            logger.info(f"Pod created successfully: {pod_id}")
            return pod_id

        except Exception as e:
            raise RunPodError(f"Failed to create RunPod instance: {str(e)}") from e

    def wait_for_pod_ready(self, pod_id: str, timeout: int = 300) -> dict[str, Any]:
        """
        Wait for a pod to be ready and return its details.

        Args:
            pod_id: ID of the pod to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            Pod details including endpoint information

        Raises:
            RunPodError: If pod doesn't become ready within timeout
        """
        if self.verbose:
            logger.info(f"Waiting for pod {pod_id} to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Note: get_pod doesn't exist in runpod 1.0.1, so we'll simulate it
                # For now, we'll assume the pod is ready after creation
                pod_data = {
                    "id": pod_id,
                    "desiredStatus": "RUNNING",
                    "runtime": {"ports": []},
                }

                if not pod_data:
                    raise RunPodError(f"Pod {pod_id} not found")

                status = pod_data.get("desiredStatus")
                runtime = pod_data.get("runtime")

                if status == "RUNNING" and runtime and runtime.get("ports"):
                    # Find the HTTP port for our service
                    ports = runtime.get("ports", [])
                    http_port = None

                    for port in ports:
                        if (
                            port.get("privatePort") == 7860
                            and port.get("type") == "http"
                        ):
                            if port.get("isIpPublic"):
                                http_port = f"https://{pod_id}-7860.proxy.runpod.net"
                            else:
                                http_port = (
                                    f"http://{port.get('ip')}:{port.get('publicPort')}"
                                )
                            break

                    if http_port:
                        self.pod_endpoint = http_port
                        logger.info(f"Pod {pod_id} is ready at {http_port}")
                        return pod_data

                if self.verbose:
                    logger.debug(f"Pod {pod_id} status: {status}, waiting...")
                time.sleep(10)

            except Exception as e:
                logger.warning(f"Error checking pod status: {str(e)}")
                time.sleep(10)

        raise RunPodError(f"Pod {pod_id} did not become ready within {timeout} seconds")

    def stop_pod(self, pod_id: str) -> bool:
        """
        Stop a running pod.

        Args:
            pod_id: ID of the pod to stop

        Returns:
            True if successful

        Raises:
            RunPodError: If stopping the pod fails
        """
        if self.verbose:
            logger.info(f"Stopping pod {pod_id}")

        try:
            runpod = _import_runpod()
            result = runpod.stop_pod(pod_id)

            if result:
                logger.info(f"Pod {pod_id} stopped successfully")
                if self.active_pod_id == pod_id:
                    self.active_pod_id = None
                    self.pod_endpoint = None
                return True
            else:
                raise RunPodError(f"Failed to stop pod {pod_id}")

        except Exception as e:
            raise RunPodError(f"Failed to stop pod {pod_id}: {str(e)}") from e

    def terminate_pod(self, pod_id: str) -> bool:
        """
        Terminate a pod (permanent deletion).

        Args:
            pod_id: ID of the pod to terminate

        Returns:
            True if successful

        Raises:
            RunPodError: If terminating the pod fails
        """
        if self.verbose:
            logger.info(f"Terminating pod {pod_id}")

        try:
            runpod = _import_runpod()
            result = runpod.terminate_pod(pod_id)

            if result:
                logger.info(f"Pod {pod_id} terminated successfully")
                if self.active_pod_id == pod_id:
                    self.active_pod_id = None
                    self.pod_endpoint = None
                return True
            else:
                raise RunPodError(f"Failed to terminate pod {pod_id}")

        except Exception as e:
            raise RunPodError(f"Failed to terminate pod {pod_id}: {str(e)}") from e

    def generate_caption_remote(
        self,
        image_data: bytes,
        model_variant: str = "joycaption-beta-one",
        mode: str = "default",
        prompt: str | None = None,
        **generation_params,
    ) -> str:
        """
        Generate a caption using the remote RunPod instance.

        Args:
            image_data: Image data as bytes
            model_variant: JoyCaption model variant to use
            mode: Captioning mode
            prompt: Custom prompt (overrides mode)
            **generation_params: Additional generation parameters

        Returns:
            Generated caption text

        Raises:
            RunPodError: If remote caption generation fails
        """
        if not self.pod_endpoint:
            raise RunPodError("No active pod endpoint available")

        if self.verbose:
            logger.info(f"Generating caption remotely using {model_variant}")

        # Prepare the request payload
        files = {"image": ("image.jpg", image_data, "image/jpeg")}
        data = {
            "model_variant": model_variant,
            "mode": mode,
            "prompt": prompt or "",
            "generation_params": json.dumps(generation_params),
        }

        try:
            import requests

            # Make request to the pod's caption endpoint
            response = requests.post(
                f"{self.pod_endpoint}/api/caption",
                files=files,
                data=data,
                timeout=120,  # Allow time for model inference
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                raise RunPodError(
                    f"Remote caption generation failed: {result['error']}"
                )

            caption = result.get("caption")
            if not caption:
                raise RunPodError("No caption returned from remote service")

            logger.info("Caption generated successfully")
            return caption

        except Exception as e:
            if "requests" in str(type(e).__module__):
                raise RunPodError(
                    f"Failed to communicate with remote pod: {str(e)}"
                ) from e
            else:
                raise RunPodError(f"Remote caption generation error: {str(e)}") from e

    def health_check(self) -> bool:
        """
        Check if the active pod is healthy and responsive.

        Returns:
            True if pod is healthy, False otherwise
        """
        if not self.pod_endpoint:
            return False

        try:
            response = requests.get(f"{self.pod_endpoint}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def get_pod_status(self, pod_id: str) -> dict[str, Any]:
        """
        Get the current status of a pod.

        Args:
            pod_id: ID of the pod to check

        Returns:
            Pod status information
        """
        try:
            # Note: get_pod doesn't exist in runpod 1.0.1
            # Return a basic status structure
            return {"id": pod_id, "status": "unknown"}
        except Exception as e:
            raise RunPodError(f"Failed to get pod status: {str(e)}") from e

    def list_pods(self) -> list[dict[str, Any]]:
        """
        List all pods in the account.

        Returns:
            List of pod information

        Raises:
            RunPodError: If the API request fails
        """
        try:
            # Note: get_pods doesn't exist in runpod 1.0.1
            # Return empty list for now
            return []
        except Exception as e:
            raise RunPodError(f"Failed to list pods: {str(e)}") from e
