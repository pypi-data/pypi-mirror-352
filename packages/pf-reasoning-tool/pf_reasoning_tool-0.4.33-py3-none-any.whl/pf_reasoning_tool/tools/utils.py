# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/utils.py
# Loads all tool YAML definitions found in pf_reasoning_tool/yamls

from pathlib import Path
from ruamel.yaml import YAML

yaml_loader = YAML(typ='safe')  # Safe YAML loader


def collect_tools_from_directory(base_dir: Path) -> dict:
    """
    Scan *base_dir* for *.yaml files and return a dict
    {tool_id: yaml_dict} for every valid PromptFlow tool definition.

    Supports both formats:
    1) flat style  : name:, function:, module:, …
    2) nested style: <tool-id>:\n   name:, function:, module:, …
    """
    tools: dict = {}

    if not base_dir.is_dir():
        print(f'Warning: tool YAML directory not found: {base_dir}')
        return tools

    for f_path in base_dir.glob('*.yaml'):
        try:
            with f_path.open(encoding='utf-8') as fh:
                data = yaml_loader.load(fh)
        except Exception as err:
            print(f'  > Error parsing {f_path.name}: {err}')
            continue

        # ------------ flat YAML (old style) -------------------------------
        if isinstance(data, dict) and data.get('function'):
            tool_id = f_path.stem                      # filename stem
            tools[tool_id] = data
            print(f'  > Loaded tool: {tool_id} (flat style)')
            continue

        # ------------ nested YAML (new style) -----------------------------
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, dict) and val.get('function'):
                    tools[key] = val                  # key is the explicit ID
                    print(f'  > Loaded tool: {key} (nested style)')
        else:
            print(f'  > Warning: {f_path.name} does not look like a tool YAML.')

    if not tools:
        print(f'Warning: no valid tool YAML files found in {base_dir}')

    return tools


def list_package_tools() -> dict:
    """
    Entry point used by PromptFlow.  Returns a map of tool metadata
    discovered under pf_reasoning_tool/yamls.
    """
    yaml_dir = Path(__file__).resolve().parents[1] / 'yamls'
    print(f'Listing package tools in: {yaml_dir}')
    return collect_tools_from_directory(yaml_dir)
