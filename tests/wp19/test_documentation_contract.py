from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = (
    "systems/Parasara/Documentation/README.md",
    "systems/Parasara/Documentation/architecture/current-state.md",
    "systems/Parasara/Documentation/specifications/README.md",
    "systems/Parasara/Documentation/specifications/predicates.md",
    "systems/Parasara/Documentation/specifications/rules.md",
    "systems/Parasara/Documentation/specifications/astrostate.md",
    "systems/Parasara/Documentation/specifications/output.md",
    "systems/Parasara/Documentation/prompts/prompt-01/README.md",
    "systems/Parasara/Documentation/guides/README.md",
    "systems/Parasara/Documentation/guides/testing.md",
    "systems/Parasara/Documentation/guides/vertical-slice.md",
    "systems/Parasara/Documentation/guides/predicate-authoring.md",
    "systems/Parasara/Documentation/guides/conditions-yoga-career.md",
    "systems/Parasara/Documentation/governance/guardrails.md",
    "systems/Parasara/Documentation/implementation/status.md",
    "systems/Parasara/Documentation/implementation/roadmap.md",
    "systems/Parasara/Documentation/implementation/tasks.md",
    "systems/Parasara/Documentation/implementation/gaps.md",
    "systems/Parasara/Documentation/CHANGELOG.md",
    "systems/Parasara/rules/parashara/v1/README.md",
    "tests/testing_framework/README.md",
    "tests/COMPLETION_MATRIX.md",
)


def _local_links(path: Path):
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = target.split("#", 1)[0]
        if target and "://" not in target and not target.startswith("mailto:"):
            yield target


def test_changed_document_links_resolve():
    checked = 0
    for relative in DOCUMENTS:
        path = ROOT / relative
        assert path.is_file(), relative
        for target in _local_links(path):
            checked += 1
            assert (path.parent / target).resolve().exists(), (relative, target)
    assert checked >= 20


def test_completion_claims_keep_release_and_publication_separate():
    prompt = (
        ROOT
        / "systems/Parasara/Documentation/prompts/prompt-01/README.md"
    ).read_text(encoding="utf-8")
    report = (
        ROOT
        / "systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP19/WP19.md"
    ).read_text(encoding="utf-8")
    assert "PROMPT_01_IMPLEMENTATION: COMPLETE" in prompt
    assert "RELEASE_READINESS: NOT ASSESSED" in prompt
    assert "PUBLICATION_APPROVAL: NOT GRANTED" in prompt
    for statement in (
        "Windows is the supported Stage-01 backend/runtime platform.",
        "Linux is not currently supported or validated.",
        "Linux portability may be considered in a separately authorized future package.",
        "Web and future iPhone clients remain platform-independent API consumers.",
    ):
        assert statement in prompt
        assert statement in report
    assert "actions/runs/29598198223" in report
    assert "out-of-scope platform incompatibility" in report
    assert "Audit-25 release/publication approval" in report
