import sys

from mcpf_core.core import runtime

if len(sys.argv) < 2:
    print(
        """Usage: python -m mcpf_core.run [extension_pipeline_config.yaml...] pipeline_config.yaml
    
extension_pipeline_config.yaml: Path to the extension pipeline configuration file.
          Note that extension pipeline files are processed from right to left.
pipeline_config.yaml: Path to the pipeline configuration file.
"""
    )
    sys.exit(1)

runtime.run(*sys.argv[1:])
