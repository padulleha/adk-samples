# Master Data Loader -- shared across inference and learning components.
"""
Master Data Loader — Shared module for loading and validating master_data.yaml

This module is consumed by eval, investigation agent, ALF, learning agent, and
the admin panel to read domain-specific configuration from a single YAML file.

When no master data file is provided, falls back to invoice-processing defaults
(backward compatible with the existing system).

Usage:
    from master_data_loader import load_master_data

    master = load_master_data("master_data.yaml")
    schema = master.get_extraction_schema("invoice")
    phases = master.get_validation_phases()
    eval_cfg = master.get_eval_schema()
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml

    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ============================================================================
# DEFAULT VALUES (invoice processing — backward compatibility)
# ============================================================================

_SCRIPT_DIR = Path(__file__).resolve().parent
_DEFAULT_MASTER_DATA_PATH = _SCRIPT_DIR / "invoice_master_data.yaml"


# ============================================================================
# MASTER DATA CLASS
# ============================================================================


class MasterData:
    """Typed accessor for master_data.yaml contents."""

    def __init__(self, data: Dict[str, Any], source_path: Optional[Path] = None):
        self._data = data
        self.source_path = source_path
        self.version = data.get("version", "0.0.0")
        self.domain = data.get("domain", "unknown")
        self.display_name = data.get("display_name", "Document Processing")

    # --- Top-level sections ---

    @property
    def raw(self) -> Dict[str, Any]:
        """Access the raw parsed dict."""
        return self._data

    # --- Document Types ---

    def get_document_types(self) -> Dict[str, Any]:
        return self._data.get("document_types", {})

    def get_primary_document_type(self) -> Dict[str, Any]:
        return self.get_document_types().get("primary", {})

    def get_supporting_document_types(self) -> List[Dict[str, Any]]:
        supporting = self.get_document_types().get("supporting", [])
        if isinstance(supporting, dict):
            return [supporting]
        return supporting

    # --- Extraction Schemas ---

    def get_extraction_schemas(self) -> Dict[str, Any]:
        return self._data.get("extraction_schemas", {})

    def get_extraction_schema(self, doc_type: str) -> Dict[str, Any]:
        return self.get_extraction_schemas().get(doc_type, {})

    def get_extraction_fields(self, doc_type: str) -> List[Dict[str, Any]]:
        return self.get_extraction_schema(doc_type).get("fields", [])

    def get_line_item_schema(self, doc_type: str) -> Dict[str, Any]:
        return self.get_extraction_schema(doc_type).get("line_item_schema", {})

    # --- Taxonomies ---

    def get_taxonomies(self) -> Dict[str, Any]:
        return self._data.get("taxonomies", {})

    def get_taxonomy(self, name: str) -> Dict[str, Any]:
        return self.get_taxonomies().get(name, {})

    def get_taxonomy_values(self, name: str) -> List[str]:
        return self.get_taxonomy(name).get("values", [])

    def get_tax_code_normalization(self) -> Dict[str, str]:
        return self.get_taxonomies().get("tax_code_normalization", {})

    def get_decision_status_mapping(self) -> Dict[str, str]:
        return self.get_taxonomies().get("decision_status_mapping", {})

    # --- Validation Pipeline ---

    def get_validation_pipeline(self) -> Dict[str, Any]:
        return self._data.get("validation_pipeline", {})

    def get_validation_phases(self) -> List[Dict[str, Any]]:
        return self.get_validation_pipeline().get("phases", [])

    def get_phase_config(self, phase_id: str) -> Optional[Dict[str, Any]]:
        for phase in self.get_validation_phases():
            if phase.get("id") == phase_id:
                return phase
        return None

    # --- Output Schema ---

    def get_output_schema(self) -> Dict[str, Any]:
        return self._data.get("output_schema", {})

    def get_output_sections(self) -> List[Dict[str, Any]]:
        return self.get_output_schema().get("sections", [])

    # --- Eval Schema ---

    def get_eval_schema(self) -> Dict[str, Any]:
        return self._data.get("eval_schema", {})

    def get_eval_decision_config(self) -> Dict[str, Any]:
        return self.get_eval_schema().get("decision", {})

    def get_eval_comparison_groups(self) -> List[Dict[str, Any]]:
        return self.get_eval_schema().get("comparison_groups", [])

    def get_eval_comparison_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        for group in self.get_eval_comparison_groups():
            if group.get("id") == group_id:
                return group
        return None

    def get_eval_status_to_decision(self) -> Dict[str, str]:
        return self.get_eval_decision_config().get("status_to_decision", {})

    def get_eval_decision_path(self) -> str:
        return self.get_eval_decision_config().get("path", "")

    # --- Investigation Config ---

    def get_investigation_config(self) -> Dict[str, Any]:
        return self._data.get("investigation", {})

    def get_agent_file_map(self) -> Dict[str, str]:
        return self.get_investigation_config().get("agent_file_map", {})

    def get_expected_extraction_fields(self) -> List[str]:
        return self.get_investigation_config().get("expected_extraction_fields", [])

    def get_phase_map(self) -> Dict[str, str]:
        """Build phase display name → phase id map from validation pipeline."""
        result = {}
        for phase in self.get_validation_phases():
            phase_id = phase.get("id", "")
            # Create display name like "Phase 1" from "phase1"
            display_name = phase.get("name", phase_id)
            # Also create "Phase N" style keys
            if phase_id.startswith("phase"):
                try:
                    num = phase_id.replace("phase", "")
                    result[f"Phase {num}"] = phase_id
                except ValueError:
                    pass
            result[display_name] = phase_id
        return result

    # --- Config Defaults ---

    def get_config_defaults(self) -> Dict[str, Any]:
        return self._data.get("config_defaults", {})

    # --- Labour Detection ---

    def get_labour_detection(self) -> Dict[str, Any]:
        return self._data.get("labour_detection", {})

    def get_labour_keywords(self) -> List[str]:
        return self.get_labour_detection().get("keywords", [])

    # --- Artifact Naming ---

    def get_artifacts(self) -> Dict[str, str]:
        return self._data.get("artifacts", {})

    # --- Rejection Templates ---

    def get_rejection_templates(self) -> List[Dict[str, Any]]:
        return self._data.get("rejection_templates", [])

    # --- Utility ---

    def resolve_dotpath(self, data: Dict[str, Any], path: str) -> Any:
        """Resolve a dot-separated path like 'Invoice Processing.Invoice Status'."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current


# ============================================================================
# LOADING FUNCTIONS
# ============================================================================


def load_master_data(path: Optional[str] = None) -> MasterData:
    """Load master data from a YAML or JSON file.

    Args:
        path: Path to master_data.yaml (or .json). If None, looks for
              the default invoice_master_data.yaml in the project root.

    Returns:
        MasterData instance with typed accessors.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file cannot be parsed.
    """
    if path is None:
        # Try default locations
        candidates = [
            _DEFAULT_MASTER_DATA_PATH,
            _SCRIPT_DIR / "master_data.yaml",
            _SCRIPT_DIR / "master_data.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                path = str(candidate)
                break

        if path is None:
            print("  Warning: No master data file found. Using empty defaults.")
            return MasterData({})

    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = _SCRIPT_DIR / file_path

    if not file_path.exists():
        raise FileNotFoundError(f"Master data file not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    if file_path.suffix in (".yaml", ".yml"):
        if not _YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required to load YAML master data files. "
                "Install with: pip install pyyaml"
            )
        data = yaml.safe_load(text)
    elif file_path.suffix == ".json":
        data = json.loads(text)
    else:
        # Try YAML first, fall back to JSON
        try:
            if _YAML_AVAILABLE:
                data = yaml.safe_load(text)
            else:
                data = json.loads(text)
        except Exception:
            raise ValueError(f"Cannot parse master data file: {file_path}")

    if not isinstance(data, dict):
        raise ValueError(
            f"Master data must be a YAML/JSON object, got: {type(data).__name__}"
        )

    master = MasterData(data, source_path=file_path)
    print(
        f"  Loaded master data: {master.display_name} v{master.version} ({file_path.name})"
    )
    return master


def validate_master_data(master: MasterData) -> List[str]:
    """Validate master data for completeness. Returns list of warnings."""
    warnings = []

    if not master.domain:
        warnings.append("Missing 'domain' field")
    if not master.display_name:
        warnings.append("Missing 'display_name' field")

    # Check extraction schemas
    if not master.get_extraction_schemas():
        warnings.append("No extraction_schemas defined")

    # Check validation pipeline
    phases = master.get_validation_phases()
    if not phases:
        warnings.append("No validation_pipeline.phases defined")
    else:
        for phase in phases:
            if not phase.get("id"):
                warnings.append(f"Phase missing 'id': {phase}")
            if not phase.get("steps"):
                warnings.append(f"Phase '{phase.get('id', '?')}' has no steps")

    # Check eval schema
    if not master.get_eval_schema():
        warnings.append("No eval_schema defined")
    elif not master.get_eval_decision_config():
        warnings.append("eval_schema missing 'decision' config")

    # Check investigation config
    if not master.get_agent_file_map():
        warnings.append("No investigation.agent_file_map defined")

    if warnings:
        print(f"  Master data validation: {len(warnings)} warning(s)")
        for w in warnings:
            print(f"    - {w}")

    return warnings
