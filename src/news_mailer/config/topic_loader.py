"""Utility helpers for loading topic configuration from YAML.
"""
from __future__ import annotations

import importlib.resources as pkg_resources
from typing import Dict, List, Any

import yaml


def _read_topics_yaml() -> dict[str, Any]:
    """Load and parse ``topics.yaml`` shipped inside the ``news_mailer.config`` package."""
    with pkg_resources.files(__package__).joinpath("topics.yaml").open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def load_config() -> dict[str, Any]:
    """Return the full topics YAML structure, cached at module level."""
    # Simple module-level cache to avoid re-reading the file in the same process
    global _CONFIG_CACHE  # type: ignore
    try:
        return _CONFIG_CACHE  # type: ignore
    except NameError:
        _CONFIG_CACHE = _read_topics_yaml()  # type: ignore
        return _CONFIG_CACHE  # type: ignore


def get_topics_for_run(run_id: str) -> Dict[str, str]:
    """Return the topic-to-query mapping for a specific ``run_id``.

    Raises
    ------
    KeyError
        If the requested ``run_id`` is not defined in the YAML file.
    """
    cfg = load_config()
    runs = cfg.get("runs", {})
    run_cfg = runs.get(run_id)
    # run_cfg should contain 'region' and 'topics' list
    if run_cfg is None:
        raise KeyError(f"Run id '{run_id}' is not defined in topics.yaml")

    topics_map: Dict[str, str] = cfg.get("topics", {})
    region: str | None = run_cfg.get("region")
    requested_topic_keys: List[str] = (
        run_cfg.get("topics")
        or run_cfg.get("global_topics", []) + run_cfg.get("regional_topics", [])
    )

    global_only_keys: set[str] = set(run_cfg.get("global_topics", []))

    resolved: Dict[str, str] = {}
    for key in requested_topic_keys:
        topic_entry = topics_map.get(key)
        if topic_entry is None:
            continue
        if isinstance(topic_entry, str):
            # Simple string (no per-region split)
            resolved[key] = topic_entry
        else:
            # Dict of regional queries available
            if key in global_only_keys and "global" in topic_entry:
                resolved[key] = topic_entry["global"]
            elif region and region in topic_entry:
                resolved[key] = topic_entry[region]
            elif "global" in topic_entry:
                resolved[key] = topic_entry["global"]
            else:
                resolved[key] = next(iter(topic_entry.values()))
    return resolved


def all_topic_queries() -> Dict[str, str]:
    """Return mapping for *all* topics in the YAML file."""
    all_map: Dict[str, Any] = load_config().get("topics", {})
    flat: Dict[str, str] = {}
    for key, val in all_map.items():
        if isinstance(val, str):
            flat[key] = val
        elif isinstance(val, dict):
            flat[key] = val.get("global") or next(iter(val.values()))
    return flat
