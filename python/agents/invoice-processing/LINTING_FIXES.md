# Linting Fixes Summary

All 209 remaining `ruff` errors (after auto-fix) were resolved across the invoice processing agent codebase. This document shows before/after examples for each major category of change.

---

## 1. pyproject.toml Structure (RUF200)

`dependencies` was accidentally placed under `[project.urls]` (where values must be strings), causing a parse error.

```toml
# BEFORE — dependencies fell under [project.urls]
[project.urls]
Repository = "https://github.com/GoogleCloudPlatform/adk-samples"

dependencies = [          # <-- ruff sees this as a url value, expects string
    "google-adk>=1.0.0",
    ...
]
```

```toml
# AFTER — dependencies under [project] where it belongs
[project]
name = "invoice-processing"
...
dependencies = [
    "google-adk>=1.0.0",
    ...
]

[project.urls]
Repository = "https://github.com/GoogleCloudPlatform/adk-samples"
```

---

## 2. Implicit Optional Type Annotations (RUF013) — ~30 instances

PEP 484 requires `None` defaults to be explicitly typed as `X | None`. Without it, the type checker assumes the parameter cannot be `None` even though it defaults to `None`.

```python
# BEFORE
def call_gemini(prompt: str, model_name: str = None, response_schema: type[BaseModel] = None):
    ...

def build_case_context(self, output_folder: Path, extraction: dict = None,
                       phase1: dict = None, phase2: dict = None):
    ...
```

```python
# AFTER
def call_gemini(prompt: str, model_name: str | None = None, response_schema: type[BaseModel] | None = None):
    ...

def build_case_context(self, output_folder: Path, extraction: dict | None = None,
                       phase1: dict | None = None, phase2: dict | None = None):
    ...
```

**Files affected:** `session_logger.py`, `general_invoice_agent.py`, `alf_engine.py`, `investigate_agent_reconst.py`

---

## 3. Mutable Class Attribute Defaults (RUF012) — ~15 instances

Mutable defaults on class attributes are shared across all instances. `ClassVar` marks them as class-level (not per-instance), making the intent explicit and preventing accidental mutation bugs.

```python
# BEFORE
class TransformerAgent:
    VALID_ITEM_CODES = ["LABOUR", "PARTS", "FREIGHT", ...]
    TAX_CODE_MAP = {"GST": "TAX", "gst": "TAX", ...}
```

```python
# AFTER
from typing import ClassVar

class TransformerAgent:
    VALID_ITEM_CODES: ClassVar[list[str]] = ["LABOUR", "PARTS", "FREIGHT", ...]
    TAX_CODE_MAP: ClassVar[dict[str, str]] = {"GST": "TAX", "gst": "TAX", ...}
```

**Files affected:** `general_invoice_agent.py`, `alf_engine.py`, `investigate_agent_reconst.py`, `test_condition_evaluator.py`

---

## 4. Global Statement Refactoring (PLW0603) — 3 files

`global` statements make code harder to reason about and test. Replaced with structured containers (dataclasses or dicts) that hold the same mutable state behind a single module-level instance.

### agent.py — 7 globals → dataclass

```python
# BEFORE — 7 separate globals, updated via `global` keyword
_investigation_initialized = False
_llm_validator = None
_data_source_validator = None
_bypass_detector = None
_tolerance_extractor = None
_per_group_validator = None
_rule_discovery = None

def _ensure_investigation_initialized():
    global _investigation_initialized, _llm_validator, _data_source_validator
    global _bypass_detector, _tolerance_extractor, _per_group_validator
    global _rule_discovery
    if _investigation_initialized:
        return
    _llm_validator = LLMRulesValidatorReconstructed(...)
    ...
    _investigation_initialized = True
```

```python
# AFTER — single dataclass instance, attributes accessed via dot notation
@dataclass
class _InvestigationState:
    initialized: bool = False
    llm_validator: Any = None
    data_source_validator: Any = None
    bypass_detector: Any = None
    tolerance_extractor: Any = None
    per_group_validator: Any = None
    rule_discovery: Any = None

_investigation_state = _InvestigationState()

def _ensure_investigation_initialized():
    if _investigation_state.initialized:
        return
    _investigation_state.llm_validator = LLMRulesValidatorReconstructed(...)
    ...
    _investigation_state.initialized = True
```

### general_invoice_agent.py — GCP config globals → dataclass

```python
# BEFORE
PROJECT_ID = None
LOCATION = None
GEMINI_FLASH_MODEL = None
_gcp_initialized = False

def _ensure_gcp_initialized():
    global PROJECT_ID, LOCATION, GEMINI_FLASH_MODEL, _gcp_initialized
    if _gcp_initialized:
        return
    PROJECT_ID = os.environ.get("PROJECT_ID", "")
    ...
```

```python
# AFTER
@dataclass
class _GCPConfig:
    project_id: str = ""
    location: str = ""
    gemini_flash_model: str = ""
    initialized: bool = False

_gcp_config = _GCPConfig()

def _ensure_gcp_initialized():
    if _gcp_config.initialized:
        return
    _gcp_config.project_id = os.environ.get("PROJECT_ID", "")
    ...
```

---

## 5. Operator Dispatch Refactoring (C901 in alf_engine.py)

The biggest single-function refactoring. `_apply_operator` was a 45-branch if/elif chain (complexity score 45 vs limit of 10). Replaced with a dispatch dictionary mapping operator names to small handler functions.

```python
# BEFORE — 45-branch monolith
@staticmethod
def _apply_operator(operator: str, actual: Any, expected: Any) -> bool:
    if operator == "is_null":
        return actual is None
    elif operator == "is_not_null":
        return actual is not None
    elif operator == "equals":
        if actual is None:
            return False
        return str(actual).strip().lower() == str(expected).strip().lower()
    elif operator == "not_equals":
        ...
    elif operator == "contains":
        ...
    elif operator == "greater_than":
        ...
    elif operator == "regex_match":
        ...
    elif operator == "any_item_contains":
        ...
    # ... 35+ more elif branches
```

```python
# AFTER — small focused handlers + dispatch dict
def _op_is_null(actual: Any, expected: Any) -> bool:
    return actual is None

def _op_equals(actual: Any, expected: Any) -> bool:
    if actual is None:
        return False
    return str(actual).strip().lower() == str(expected).strip().lower()

def _op_contains(actual: Any, expected: Any) -> bool:
    if actual is None:
        return False
    return str(expected).lower() in str(actual).lower()

# ... one function per operator

_OPERATOR_DISPATCH = {
    "is_null": _op_is_null,
    "equals": _op_equals,
    "contains": _op_contains,
    "greater_than": _op_greater_than,
    "regex_match": _op_regex_match,
    # ... all 21 operators
}

@staticmethod
def _apply_operator(operator: str, actual: Any, expected: Any) -> bool:
    handler = _OPERATOR_DISPATCH.get(operator)
    if handler is None:
        logger.warning(f"Unknown operator: {operator}")
        return False
    return handler(actual, expected)
```

---

## 6. Large Function Decomposition (C901/PLR0912/PLR0915)

Complex functions were broken into focused helpers. The pattern is the same across all files: extract logical blocks into private helper functions, keeping the original function as a thin orchestrator.

### Example: `run_inference` in agent.py (97 statements → ~30)

```python
# BEFORE — one massive function doing everything
def run_inference(case_id: str, skip_investigation: str = "false") -> dict:
    # 1. Set up paths and clean old outputs (15 lines)
    # 2. Run acting agent (20 lines)
    # 3. Check for errors in acting result (15 lines)
    # 4. Run investigation stage (25 lines)
    # 5. Run ALF engine (20 lines)
    # 6. Save outputs and return (10 lines)
    ...  # 97 statements total, 13 branches, 7 returns
```

```python
# AFTER — orchestrator delegates to focused helpers
def _run_acting_stage(case_id, source_folder):
    """Handle source folder validation, cleanup, and process_invoice call."""
    ...

def _build_acting_stage_result(acting_result, stages):
    """Process acting result dict, detect errors."""
    ...

def _run_investigation_stage(case_id, case_data, ...):
    """Run investigation pipeline including MAJOR_VIOLATION gate."""
    ...

def _run_alf_stage(case_id, output_folder, ...):
    """Run ALF engine and produce final pipeline result."""
    ...

def run_inference(case_id: str, skip_investigation: str = "false") -> dict:
    acting_result = _run_acting_stage(case_id, source_folder)
    error = _build_acting_stage_result(acting_result, stages)
    if error:
        return error
    investigation = _run_investigation_stage(case_id, ...)
    return _run_alf_stage(case_id, ...)
```

### Example: `evaluate_case` in eval.py (61 statements → ~20)

```python
# BEFORE — mixed schema-driven and legacy paths in one function
def evaluate_case(case_id, gt_file, agent_file, master, tolerance):
    # Load files (10 lines)
    # Schema-driven path (25 lines of comparisons + mismatch collection)
    # Legacy fallback path (20 lines)
    # Return result dict (6 lines)
```

```python
# AFTER — each path is its own helper
def _evaluate_schema_driven(case_id, gt, agent, master, tolerance):
    """Full schema-driven evaluation using master data groups."""
    ...

def _evaluate_legacy(case_id, gt, agent, tolerance):
    """Legacy fallback evaluation for repos without master data."""
    ...

def evaluate_case(case_id, gt_file, agent_file, master, tolerance):
    gt, agent = _load_case_files(gt_file, agent_file)
    if master:
        return _evaluate_schema_driven(case_id, gt, agent, master, tolerance)
    return _evaluate_legacy(case_id, gt, agent, tolerance)
```

### Example: `main` in eval.py (102 statements → ~15)

```python
# BEFORE
def main():
    parser = argparse.ArgumentParser(...)   # arg setup (15 lines)
    args = parser.parse_args()
    master = load_master_data(...)          # master loading (10 lines)
    gt_dir, agent_dir = ...                # path resolution (15 lines)
    case_ids = [...]                       # case discovery (10 lines)
    for case_id in case_ids:               # eval loop (20 lines)
        ...
    stats = compute_aggregate_stats(...)
    print_report(stats, results)
    with open(...) as f:                   # save results (15 lines)
        json.dump(...)
```

```python
# AFTER
def _parse_args(): ...
def _load_master(args): ...
def _resolve_directories(args): ...
def _collect_case_ids(gt_dir, agent_dir): ...
def _run_evaluation_loop(case_ids, gt_dir, agent_dir, master, tolerance): ...
def _save_results(results, stats, output_path): ...

def main():
    args = _parse_args()
    master = _load_master(args)
    gt_dir, agent_dir = _resolve_directories(args)
    case_ids = _collect_case_ids(gt_dir, agent_dir)
    results = _run_evaluation_loop(case_ids, gt_dir, agent_dir, master, args.tolerance)
    stats = compute_aggregate_stats(results, master)
    print_report(stats, results)
    if args.output:
        _save_results(results, stats, args.output)
```

---

## 7. Magic Values → Named Constants (PLR2004)

Bare numbers in comparisons are hard to understand. Named constants explain _what_ the number means.

```python
# BEFORE
if len(abn_clean) != 11:
    return False, f"Invalid length: {len(abn_clean)} (must be 11)"

if content and len(content.strip()) > 50:
    return content, "gemini"

if compliance_score == 100:
    overall_compliance = "FULLY_COMPLIANT"
elif compliance_score >= 60:
    overall_compliance = "PARTIAL_VIOLATION"
```

```python
# AFTER
_ABN_EXPECTED_LENGTH = 11
_MIN_PDF_CONTENT_LENGTH = 50
_FULL_COMPLIANCE_SCORE = 100
_PARTIAL_COMPLIANCE_THRESHOLD = 60

if len(abn_clean) != _ABN_EXPECTED_LENGTH:
    return False, f"Invalid length: {len(abn_clean)} (must be {_ABN_EXPECTED_LENGTH})"

if content and len(content.strip()) > _MIN_PDF_CONTENT_LENGTH:
    return content, "gemini"

if compliance_score == _FULL_COMPLIANCE_SCORE:
    overall_compliance = "FULLY_COMPLIANT"
elif compliance_score >= _PARTIAL_COMPLIANCE_THRESHOLD:
    overall_compliance = "PARTIAL_VIOLATION"
```

---

## 8. Exception Chaining (B904)

When re-raising a different exception inside an `except` block, Python loses the original traceback unless you chain with `from`. Using `from None` explicitly suppresses the original (when the new error fully replaces it).

```python
# BEFORE
except ImportError:
    raise ImportError(
        "Vertex AI SDK required for LLM actions. Install with: "
        "pip install google-cloud-aiplatform"
    )

except Exception:
    raise ValueError(f"Cannot parse master data file: {file_path}")
```

```python
# AFTER
except ImportError:
    raise ImportError(
        "Vertex AI SDK required for LLM actions. Install with: "
        "pip install google-cloud-aiplatform"
    ) from None

except Exception:
    raise ValueError(f"Cannot parse master data file: {file_path}") from None
```

---

## 9. zip() Safety (B905)

`zip()` silently truncates when iterables have different lengths. Adding `strict=False` makes the intent explicit (we know lengths may differ and that's OK).

```python
# BEFORE
for gt_line, agent_line in zip(gt_sorted, agent_sorted):
    ...
```

```python
# AFTER
for gt_line, agent_line in zip(gt_sorted, agent_sorted, strict=False):
    ...
```

---

## 10. Other Small Fixes

### Unused loop variables (B007) — prefix with `_`

```python
# BEFORE                                    # AFTER
for group_id, result in results.items():     for _group_id, result in results.items():
for i, desc in enumerate(descriptions):      for i, _desc in enumerate(descriptions):
```

### Self-assignment removal (PLW0127)

```python
# BEFORE                     # AFTER
if condition:                 if condition:
    stripped = "...".strip()      stripped = "...".strip()
else:                         # else branch removed entirely
    stripped = stripped
```

### Loop variable overwrite (PLW2901)

```python
# BEFORE — `pattern` loop var overwritten
for pattern in search_patterns:
    pattern = pattern.strip().lower()   # overwrites loop variable
    if pattern in text:
        ...
```

```python
# AFTER — separate variable name
for raw_pattern in search_patterns:
    normalized = raw_pattern.strip().lower()
    if normalized in text:
        ...
```

### Dict iteration (PLC0206)

```python
# BEFORE — repeated dict lookups
for key in output:
    if isinstance(output[key], dict) and "validations" in output[key]:
        validations = output[key]["validations"]
```

```python
# AFTER — single lookup via .items()
for _key, value in output.items():
    if isinstance(value, dict) and "validations" in value:
        validations = value["validations"]
```

### List concatenation (RUF005)

```python
# BEFORE                                          # AFTER
eval_case_ids = [target_case_id] + sampled_others  eval_case_ids = [target_case_id, *sampled_others]
```

### Unnecessary list() in sorted() (C414)

```python
# BEFORE                                   # AFTER
rule_reference=sorted(list(details["rules"]))  rule_reference=sorted(details["rules"])
```
