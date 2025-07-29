"""
Parallel Processing Example

This example demonstrates:
1. Parallel execution of multiple steps
2. Concurrency control
3. Dependency management
4. Result aggregation
"""

import asyncio
from typing import Any, Dict

from zuma import ZumaActionStep, ZumaParallelAction, ZumaRunner, ZumaWorkflow


class DataValidationStep(ZumaActionStep):
    """Validates input files before processing"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        files = context.get("files", [])
        print(f"[{self.name}] Validating {len(files)} files...")

        valid_files = []
        for file in files:
            if self.validate_file(file):
                valid_files.append(file)

        return {"valid_files": valid_files}

    def validate_file(self, file: str) -> bool:
        # Simple validation based on file extension
        return file.endswith((".csv", ".json", ".xml"))


class DataProcessStep(ZumaActionStep):
    """Processes a single file type"""

    def __init__(self, name: str, file_type: str):
        super().__init__(name)
        self.file_type = file_type

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        # Get files of our type from the valid files list
        valid_files = context.get("valid_files", [])
        our_files = [f for f in valid_files if f.endswith(self.file_type)]

        results = []
        for file in our_files:
            print(f"[{self.name}] Processing {file}...")
            await asyncio.sleep(0.5)  # Simulate processing
            results.append({"file": file, "processor": self.name, "status": "completed"})

        return {"processed_files": len(results), "results": results}


class DataAggregationStep(ZumaActionStep):
    """Aggregates results from all parallel processing steps"""

    async def execute(
        self, context: Dict[str, Any], dependencies: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        # Collect all results from parallel processing
        all_results = []
        for key, value in context.items():
            if isinstance(value, dict) and "results" in value:
                all_results.extend(value["results"])

        print(f"[{self.name}] Aggregated {len(all_results)} results")
        return {"total_processed": len(all_results), "aggregated_results": all_results}


async def run_parallel_workflow():
    """Run the parallel processing workflow"""
    # Initial data validation
    validation = DataValidationStep("Validate Files")

    # Parallel processing of different file types
    parallel_processing = ZumaParallelAction(
        "Parallel Processing",
        steps=[
            DataProcessStep("Process CSV", ".csv"),
            DataProcessStep("Process JSON", ".json"),
            DataProcessStep("Process XML", ".xml"),
        ],
        max_concurrency=2,  # Process 2 file types at a time
    )

    # Final aggregation
    aggregation = DataAggregationStep("Aggregate Results")

    # Create workflow
    workflow = ZumaWorkflow(
        "Parallel Processing Workflow",
        steps=[validation, parallel_processing, aggregation],
    )

    # Run workflow with sample data
    initial_context = {
        "files": [
            "data1.csv",
            "data2.json",
            "data3.xml",
            "data4.csv",
            "data5.json",
            "invalid.txt",
        ]
    }

    runner = ZumaRunner()
    result = await runner.run_workflow(
        workflow, context=initial_context, diagram_output="parallel_processing"
    )
    runner.print_execution_summary(result)
    return result


if __name__ == "__main__":
    asyncio.run(run_parallel_workflow())
