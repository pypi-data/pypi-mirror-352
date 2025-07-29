"""
Custom Actions Example

This example demonstrates:
1. Creating custom action types
2. Advanced action configuration
3. Custom validation logic
4. Action metadata handling
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from zuma import (
    ZumaActionStep,
    ZumaExecutionError,
    ZumaParallelAction,
    ZumaRunner,
    ZumaWorkflow,
)


class MetricsAction(ZumaActionStep):
    """Custom action that collects and reports metrics"""

    def __init__(
        self,
        name: str,
        metrics_to_collect: List[str],
        threshold: Optional[float] = None,
    ):
        super().__init__(
            name=name,
            description="Collects and validates metrics",
            metadata={
                "metrics": metrics_to_collect,
                "threshold": threshold,
                "collection_time": datetime.now().isoformat(),
            },
        )
        self.metrics = metrics_to_collect
        self.threshold = threshold

    def validate(self) -> List[str]:
        """Custom validation logic"""
        errors = []
        if not self.metrics:
            errors.append("No metrics specified for collection")
        if self.threshold is not None and self.threshold <= 0:
            errors.append("Threshold must be positive")
        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Collecting metrics: {', '.join(self.metrics)}")
        await asyncio.sleep(0.5)  # Simulate metric collection

        # Simulate collecting metrics
        metric_values = {metric: round(random.random() * 100, 2) for metric in self.metrics}

        # Check threshold if specified
        if self.threshold is not None:
            violations = [
                f"{metric}: {value}"
                for metric, value in metric_values.items()
                if value > self.threshold
            ]
            if violations:
                raise ZumaExecutionError(f"Metrics exceeded threshold: {', '.join(violations)}")

        return {"metrics": metric_values, "collection_time": self.metadata["collection_time"]}


class JSONConfigAction(ZumaActionStep):
    """Action that loads and validates JSON configuration"""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(
            name=name,
            description="Processes JSON configuration",
            metadata={"config_schema": list(config.keys())},
        )
        self.config = config

    def validate(self) -> List[str]:
        """Validate JSON configuration"""
        errors = []
        required_fields = ["name", "version", "settings"]

        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required field: {field}")

        if "version" in self.config:
            try:
                major, minor, patch = str(self.config["version"]).split(".")
                if not all(x.isdigit() for x in [major, minor, patch]):
                    errors.append("Invalid version format")
            except ValueError:
                errors.append("Version must be in format: major.minor.patch")

        return errors

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Processing configuration...")
        await asyncio.sleep(0.3)  # Simulate processing

        # Add processed flag to all settings
        processed_config = self.config.copy()
        if "settings" in processed_config:
            processed_config["settings"] = {
                k: {"value": v, "processed": True} for k, v in processed_config["settings"].items()
            }

        return {"processed_config": processed_config}


class AuditAction(ZumaActionStep):
    """Action that maintains an audit trail of workflow execution"""

    def __init__(self, name: str):
        super().__init__(
            name=name,
            description="Records workflow execution details",
            metadata={"audit_start_time": datetime.now().isoformat()},
        )
        self.events = []

    def record_event(self, event_type: str, details: Dict[str, Any]):
        """Record an audit event"""
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": event_type,
                "details": details,
            }
        )

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        print(f"[{self.name}] Recording audit trail...")

        # Record workflow context
        self.record_event("CONTEXT", {"workflow_context": context})

        # Record step execution
        for key, value in context.items():
            if isinstance(value, dict) and "execution_time" in value:
                self.record_event(
                    "STEP_EXECUTION",
                    {
                        "step": key,
                        "execution_time": value["execution_time"],
                    },
                )

        return {
            "audit_trail": self.events,
            "audit_summary": {
                "total_events": len(self.events),
                "start_time": self.metadata["audit_start_time"],
                "end_time": datetime.now().isoformat(),
            },
        }


async def run_custom_actions():
    """Demonstrates the use of custom actions"""

    # Create test configuration
    config = {
        "name": "TestConfig",
        "version": "1.0.0",
        "settings": {
            "timeout": 30,
            "retry_count": 3,
            "log_level": "INFO",
        },
    }

    # Create workflow with custom actions
    workflow = ZumaWorkflow(
        "Custom Actions Demo",
        steps=[
            # Collect system metrics
            MetricsAction(
                "System Metrics",
                metrics_to_collect=["cpu_usage", "memory_usage", "disk_usage"],
                threshold=90.0,
            ),
            # Process configuration
            JSONConfigAction("Config Processor", config),
            # Run parallel metric collection
            ZumaParallelAction(
                "Parallel Metrics",
                steps=[
                    MetricsAction(
                        "Network Metrics",
                        metrics_to_collect=["bandwidth", "latency"],
                        threshold=75.0,
                    ),
                    MetricsAction(
                        "Application Metrics",
                        metrics_to_collect=["requests_per_second", "error_rate"],
                        threshold=50.0,
                    ),
                ],
            ),
            # Record audit trail
            AuditAction("Workflow Audit"),
        ],
    )

    # Run workflow
    runner = ZumaRunner()
    result = await runner.run_workflow(workflow, diagram_output="custom_actions")
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    import random  # Required for metric simulation

    asyncio.run(run_custom_actions())
