"""Patch / Evidence / Review Flow layer.

Módulos migrados:
- evidence_bundle.py : criação e gerenciamento de bundles de evidência para revisão de patches (inclui risk summary, decisão).
- patch_review_flow.py : lifecycle de patches, linking a queue/inbox, fluxo de revisão (get_patch_review_flow).

Estes suportam o processo de validação, review gate e decisão manual/automática antes de apply.
Compat com legado via thin delegates.

Terminologia:
- Evidence Bundle: pacote de evidências (testes, cobertura, gate) para decisão sobre patch.
- Patch Review Flow / Fluxo de Revisão de Patch.
"""

def create_evidence_bundle(*a, **k):
    from .evidence_bundle import create_evidence_bundle as fn
    return fn(*a, **k)

def list_evidence_bundles(*a, **k):
    from .evidence_bundle import list_evidence_bundles as fn
    return fn(*a, **k)

def read_evidence_bundle(*a, **k):
    from .evidence_bundle import read_evidence_bundle as fn
    return fn(*a, **k)

def record_patch_decision(*a, **k):
    from .evidence_bundle import record_patch_decision as fn
    return fn(*a, **k)

def compute_risk_summary(*a, **k):
    from .evidence_bundle import compute_risk_summary as fn
    return fn(*a, **k)


def get_patch_lifecycle(*a, **k):
    from .patch_review_flow import get_patch_lifecycle as fn
    return fn(*a, **k)

def save_patch_lifecycle(*a, **k):
    from .patch_review_flow import save_patch_lifecycle as fn
    return fn(*a, **k)

def discover_workspace_patches(*a, **k):
    from .patch_review_flow import discover_workspace_patches as fn
    return fn(*a, **k)

def link_patch_to_queue_item(*a, **k):
    from .patch_review_flow import link_patch_to_queue_item as fn
    return fn(*a, **k)

def update_patch_lifecycle(*a, **k):
    from .patch_review_flow import update_patch_lifecycle as fn
    return fn(*a, **k)

def get_patch_review_flow(*a, **k):
    from .patch_review_flow import get_patch_review_flow as fn
    return fn(*a, **k)

# aiw/patch now sources patch_gate + validation_plan + coverage_report (step 2 migration) + changed_lines_coverage.
# Prefer local aiw/ for migrated: patch_gate, validation_plan, coverage_report, changed_lines.
# Other bridges still to aiw_workspace during staged (test_runner etc).
def review_gate_for_patch(*a, **k):
    from .patch_gate import review_gate_for_patch as fn
    return fn(*a, **k)

def list_review_gates(*a, **k):
    from .patch_gate import list_review_gates as fn
    return fn(*a, **k)

def apply_reviewed_patch(*a, **k):
    from .patch_gate import apply_reviewed_patch as fn
    return fn(*a, **k)

def rollback_reviewed_patch(*a, **k):
    from .patch_gate import rollback_reviewed_patch as fn
    return fn(*a, **k)

# Now aiw-first: validation_plan logic in aiw/patch/validation_plan.py (thin in aiw_workspace)
def validation_plan_for_patch(*a, **k):
    from .validation_plan import validation_plan_for_patch as fn
    return fn(*a, **k)

def ensure_validation_plan_snapshot(*a, **k):
    from .validation_plan import ensure_validation_plan_snapshot as fn
    return fn(*a, **k)

def list_validation_plan_snapshots(*a, **k):
    from .validation_plan import list_validation_plan_snapshots as fn
    return fn(*a, **k)

def get_validation_plan_snapshot(*a, **k):
    from .validation_plan import get_validation_plan_snapshot as fn
    return fn(*a, **k)

def compare_validation_plan_snapshots(*a, **k):
    from .validation_plan import compare_validation_plan_snapshots as fn
    return fn(*a, **k)

def validation_reliability(*a, **k):
    from .validation_plan import validation_reliability as fn
    return fn(*a, **k)

def preview_validation_plan_command(*a, **k):
    from .validation_plan import preview_validation_plan_command as fn
    return fn(*a, **k)

def run_validation_plan_commands(*a, **k):
    from .validation_plan import run_validation_plan_commands as fn
    return fn(*a, **k)

# coverage_report now aiw-first in aiw/patch/coverage_report.py
def analyze_patch_coverage(*a, **k):
    from .coverage_report import analyze_patch_coverage as fn
    return fn(*a, **k)

def load_coverage_reports(*a, **k):
    from .coverage_report import load_coverage_reports as fn
    return fn(*a, **k)

def capture_test_run_coverage(*a, **k):
    from .coverage_report import capture_test_run_coverage as fn
    return fn(*a, **k)

def load_patch_preview(*a, **k):
    from aiw_workspace.patch_review_flow import load_patch_preview as fn
    return fn(*a, **k)

def suggest_tests_for_patch(*a, **k):
    from aiw_workspace.patch_review_flow import suggest_tests_for_patch as fn
    return fn(*a, **k)

def preview_patch_suggested_test(*a, **k):
    from aiw_workspace.patch_review_flow import preview_patch_suggested_test as fn
    return fn(*a, **k)

def run_patch_suggested_test(*a, **k):
    from aiw_workspace.patch_review_flow import run_patch_suggested_test as fn
    return fn(*a, **k)

# aiw-first (step 1): test_runner now in aiw/patch/
def preview_test_command(*a, **k):
    from .test_runner import preview_test_command as fn
    return fn(*a, **k)

def run_test_command(*a, **k):
    from .test_runner import run_test_command as fn
    return fn(*a, **k)

def analyze_changed_lines_coverage(*a, **k):
    from .changed_lines_coverage import analyze_changed_lines_coverage as fn
    return fn(*a, **k)

# aiw-first step 1: coverage_baseline now in aiw/patch/
def get_current_coverage_baseline(*a, **k):
    from .coverage_baseline import get_current_coverage_baseline as fn
    return fn(*a, **k)

def promote_coverage_baseline(*a, **k):
    from .coverage_baseline import promote_coverage_baseline as fn
    return fn(*a, **k)

def list_coverage_baselines(*a, **k):
    from .coverage_baseline import list_coverage_baselines as fn
    return fn(*a, **k)

def coverage_diff(*a, **k):
    from .coverage_baseline import coverage_diff as fn
    return fn(*a, **k)

__all__ = [
    "create_evidence_bundle", "list_evidence_bundles", "read_evidence_bundle",
    "record_patch_decision", "compute_risk_summary",
    "get_patch_lifecycle", "save_patch_lifecycle",
    "discover_workspace_patches", "link_patch_to_queue_item", "update_patch_lifecycle",
    "get_patch_review_flow",
    # step 2 migrated: validation_plan + coverage_report to aiw/patch/ (aiw-first, with thin delegates)
    # + prior: patch_gate + changed_lines_coverage
    "review_gate_for_patch", "list_review_gates", "apply_reviewed_patch", "rollback_reviewed_patch",
    "validation_plan_for_patch", "ensure_validation_plan_snapshot", "list_validation_plan_snapshots",
    "get_validation_plan_snapshot", "compare_validation_plan_snapshots",
    "validation_reliability", "preview_validation_plan_command", "run_validation_plan_commands",
    "load_patch_preview", "suggest_tests_for_patch", "preview_patch_suggested_test", "run_patch_suggested_test",
    "preview_test_command", "run_test_command",
    "analyze_changed_lines_coverage",
    # coverage migrated
    "analyze_patch_coverage", "load_coverage_reports", "capture_test_run_coverage",
    # step 1: coverage_baseline + test_runner more
    "get_current_coverage_baseline", "promote_coverage_baseline", "list_coverage_baselines", "coverage_diff",
]
