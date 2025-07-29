import json
import re
from typing import Any, List, Dict


def parse_json(text: str) -> Dict[str, Any] | None:
    try:
        if text.find("```json") == -1:
            return json.loads(text)
    except json.JSONDecodeError:
        pass
    results = extract_json_from_markdown(text)
    return results[0] if results else None


def extract_json_from_markdown(markdown_content: str) -> List[Any]:
    # Matches:
    # 1. ```json\n...\n```
    # 2. ```\n{...}\n``` (generic code block with JSON)
    # 3. Single-line ```{...}```
    pattern = r"```(?:json)?\n?(.*?)\n?```"
    json_blocks = re.findall(pattern, markdown_content, re.DOTALL)

    results: List[Any] = []
    for block in json_blocks:
        block = block.strip()  # Remove leading/trailing whitespace
        if not block:
            continue
        try:
            results.append(json.loads(block))
        except json.JSONDecodeError:
            continue  # Skip invalid JSON

    return results
