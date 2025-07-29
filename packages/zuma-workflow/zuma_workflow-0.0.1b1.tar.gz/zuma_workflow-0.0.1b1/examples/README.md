# Zuma Examples

This directory contains various examples demonstrating the features and capabilities of the Zuma workflow framework.

## Examples Overview

1. `simple.py` - Basic sequential workflow demonstration
   - Sequential step execution
   - Context passing
   - Basic workflow patterns

2. `retry_mechanism.py` - Advanced retry handling with visualization
   - Configurable retry attempts
   - Exponential backoff
   - Error handling
   - Retry visualization

3. `parallel_processing.py` - Concurrent task execution
   - Parallel step execution
   - Concurrency control
   - Resource management
   - Result aggregation

4. `workflow_in_workflow.py` - Nested workflow composition
   - Workflow nesting
   - Complex dependencies
   - State management

5. `conditional_workflow.py` - Dynamic branching based on conditions
   - Conditional execution
   - Dynamic routing
   - Context-based decisions

6. `error_handling.py` - Comprehensive error handling patterns
   - Exception handling
   - Error recovery
   - Failure management

7. `dynamic_workflow.py` - Runtime workflow modification
   - Dynamic step creation
   - Runtime configuration
   - Adaptive workflows

8. `custom_actions.py` - Creating custom action steps
   - Custom step implementation
   - Action step inheritance
   - Extended functionality

9. `workflow_composition.py` - Complex workflow composition
   - Multiple workflow types
   - Advanced patterns
   - Component reuse

10. `workflow_visualization.py` - Workflow visualization examples
    - Basic workflow visualization
    - Retry mechanism visualization
    - Parallel processing visualization
    - Nested workflow visualization

## Running the Examples

Each example can be run directly:

```bash
python examples/simple.py
python examples/retry_mechanism.py
# etc...
```

## Generated Diagrams

When running examples with visualization enabled, diagram files will be generated in the current directory:

- `parallel_processing.mermaid` - Shows parallel task execution
- `retry_mechanism.mermaid` - Shows retry attempts and paths
- `combined_workflow.mermaid` - Shows nested workflow structure

The generated .mermaid files can be:
- Rendered directly in many Markdown viewers
- Converted to various image formats (PNG, SVG)
- Used in documentation and presentations

## Example Dependencies

All examples use core Zuma functionality and don't require additional dependencies beyond what's specified in the main project's requirements.

## Additional Resources

- [Zuma Documentation](../docs.html)
- [API Reference](../docs.html#api-reference)
- [Best Practices Guide](../docs.html#best-practices) 