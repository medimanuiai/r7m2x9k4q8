"""Strict non-constructing YAML boundary for the Prompt-07 Rule DSL."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import unicodedata
from typing import Any

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, AnchorToken, DirectiveToken, TagToken

from systems.Parasara.engine.rules.dsl.models import (
    CanonicalDecimal,
    DslDiagnostic,
    MAX_DECIMAL_MAGNITUDE,
    MAX_DECIMAL_SCALE,
    MAX_DECIMAL_SIGNIFICANT_DIGITS,
    MAX_INTEGER,
    MAX_MAPPING_ENTRIES,
    MAX_YAML_DOCUMENTS,
    MIN_INTEGER,
    MAX_SEQUENCE_ELEMENTS,
    MAX_SOURCE_BYTES,
    MAX_STRING_LENGTH,
    SourceSpan,
)


_MESSAGES = {
    "P07E001_INVALID_ENCODING": "DSL source must be strict UTF-8 without BOM and use Unicode NFC.",
    "P07E002_SOURCE_SIZE_LIMIT": "DSL source exceeds the maximum byte size.",
    "P07E003_INVALID_YAML": "DSL source is not one valid YAML mapping document.",
    "P07E004_DUPLICATE_KEY": "A YAML mapping key is duplicated.",
    "P07E005_FORBIDDEN_YAML_FEATURE": "The YAML source uses a forbidden tag, anchor, alias, merge key, or directive.",
    "P07E006_MULTIPLE_DOCUMENTS": "DSL source must contain exactly one YAML document.",
    "P07E007_INVALID_SCALAR": "The YAML source contains a null or unsupported scalar form.",
    "P07E103_INVALID_FIELD_VALUE": "A DSL value violates its bounded field contract.",
    "P07E104_INVALID_NUMERIC_VALUE": "A numeric value violates the canonical numeric contract.",
}


@dataclass(frozen=True, slots=True)
class ParsedYaml:
    value: Mapping[str, Any]
    spans: tuple[tuple[str, SourceSpan], ...]

    def span_for(self, field_path: str) -> SourceSpan | None:
        lookup = dict(self.spans)
        current = field_path
        while current:
            found = lookup.get(current)
            if found is not None:
                return found
            if current.endswith("]"):
                current = current.rsplit("[", 1)[0]
            elif "." in current:
                current = current.rsplit(".", 1)[0]
            else:
                break
        return lookup.get("$")


@dataclass(frozen=True, slots=True)
class ParsedYamlSucceeded:
    document: ParsedYaml


@dataclass(frozen=True, slots=True)
class ParsedYamlFailed:
    diagnostic: DslDiagnostic


def _span(source_id: str, node_or_mark: Any, end_mark: Any | None = None) -> SourceSpan:
    start = getattr(node_or_mark, "start_mark", node_or_mark)
    end = end_mark if end_mark is not None else getattr(node_or_mark, "end_mark")
    return SourceSpan(
        source_id=source_id,
        start_line=start.line + 1,
        start_column=start.column + 1,
        end_line=end.line + 1,
        end_column=end.column + 1,
    )


def _diagnostic(
    code: str,
    source_id: str,
    *,
    span: SourceSpan | None = None,
    field_path: str = "$",
    details: Mapping[str, Any] | None = None,
) -> ParsedYamlFailed:
    return ParsedYamlFailed(DslDiagnostic(
        code=code,
        message=_MESSAGES[code],
        stage="parse",
        source_id=source_id,
        source_span=span,
        field_path=field_path,
        details={} if details is None else details,
    ))


def _numeric_like_invalid(value: str) -> bool:
    lower = value.casefold()
    if lower in {"null", "~", ".inf", "+.inf", "-.inf", ".nan"}:
        return True
    if value.startswith("+"):
        return True
    if lower.startswith(("0x", "-0x", "0o", "-0o")):
        return True
    if ":" in value and all(part.isdigit() for part in value.lstrip("-").split(":")):
        return True
    if "e" in lower:
        left, _, right = lower.partition("e")
        if left.replace("-", "", 1).replace(".", "", 1).isdigit() and right.replace("+", "", 1).replace("-", "", 1).isdigit():
            return True
    unsigned = value[1:] if value.startswith("-") else value
    if len(unsigned) > 1 and unsigned.startswith("0") and unsigned.isdigit():
        return True
    if len(unsigned) > 2 and unsigned.startswith("0") and "." in unsigned and unsigned.split(".", 1)[0] != "0":
        return True
    if len(value) >= 10 and value[4:5] == "-" and value[7:8] == "-" and value[:4].isdigit():
        return True
    return False


def _plain_scalar(node: ScalarNode) -> tuple[Any | None, str | None]:
    value = node.value
    if value == "" or _numeric_like_invalid(value):
        return None, "P07E007_INVALID_SCALAR"
    if value == "true":
        return True, None
    if value == "false":
        return False, None
    negative = value.startswith("-")
    unsigned = value[1:] if negative else value
    if unsigned == "0" or (unsigned and unsigned[0] in "123456789" and unsigned.isdigit()):
        if value == "-0":
            return None, "P07E007_INVALID_SCALAR"
        parsed = int(value)
        if not MIN_INTEGER <= parsed <= MAX_INTEGER:
            return None, "P07E104_INVALID_NUMERIC_VALUE"
        return parsed, None
    if "." in unsigned:
        whole, dot, fraction = unsigned.partition(".")
        if dot and fraction.isdigit() and (whole == "0" or (whole and whole[0] in "123456789" and whole.isdigit())):
            if negative and all(character == "0" for character in whole + fraction):
                return None, "P07E007_INVALID_SCALAR"
            significant = (whole.lstrip("0") + fraction).lstrip("0")
            if (
                len(significant or "0") > MAX_DECIMAL_SIGNIFICANT_DIGITS
                or len(fraction) > MAX_DECIMAL_SCALE
            ):
                return None, "P07E104_INVALID_NUMERIC_VALUE"
            try:
                decimal = Decimal(value)
            except InvalidOperation:
                return None, "P07E104_INVALID_NUMERIC_VALUE"
            if abs(decimal) > Decimal(MAX_DECIMAL_MAGNITUDE):
                return None, "P07E104_INVALID_NUMERIC_VALUE"
            normalized = format(decimal.normalize(), "f")
            if "." in normalized:
                normalized = normalized.rstrip("0").rstrip(".")
            if normalized in {"", "-0"}:
                normalized = "0"
            return CanonicalDecimal(value=normalized), None
    return value, None


def parse_yaml_source(*, source_id: str, payload: bytes | str) -> ParsedYamlSucceeded | ParsedYamlFailed:
    """Parse bounded YAML bytes without invoking any YAML object constructor."""

    if isinstance(payload, str):
        try:
            payload_bytes = payload.encode("utf-8", errors="strict")
        except UnicodeEncodeError:
            return _diagnostic("P07E001_INVALID_ENCODING", source_id)
        text = payload
    elif isinstance(payload, bytes):
        payload_bytes = payload
        try:
            text = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return _diagnostic("P07E001_INVALID_ENCODING", source_id)
    else:
        raise TypeError("payload must be bytes or str")
    if len(payload_bytes) > MAX_SOURCE_BYTES:
        return _diagnostic(
            "P07E002_SOURCE_SIZE_LIMIT", source_id,
            details={"limit": MAX_SOURCE_BYTES, "observed": len(payload_bytes)},
        )
    if payload_bytes.startswith(b"\xef\xbb\xbf") or text.startswith("\ufeff") or unicodedata.normalize("NFC", text) != text:
        return _diagnostic("P07E001_INVALID_ENCODING", source_id)

    try:
        for token in yaml.scan(text):
            if isinstance(token, (AliasToken, AnchorToken, DirectiveToken, TagToken)):
                return _diagnostic(
                    "P07E005_FORBIDDEN_YAML_FEATURE",
                    source_id,
                    span=_span(source_id, token),
                )
        documents = list(yaml.compose_all(text, Loader=yaml.SafeLoader))
    except (yaml.YAMLError, RecursionError):
        return _diagnostic("P07E003_INVALID_YAML", source_id)
    if len(documents) != MAX_YAML_DOCUMENTS:
        return _diagnostic("P07E006_MULTIPLE_DOCUMENTS", source_id)
    root = documents[0]
    if root is None or not isinstance(root, MappingNode):
        return _diagnostic(
            "P07E003_INVALID_YAML", source_id,
            span=None if root is None else _span(source_id, root),
        )

    spans: list[tuple[str, SourceSpan]] = []

    def convert(node: Any, path: str, depth: int = 0) -> tuple[Any | None, ParsedYamlFailed | None]:
        # This is a parser-safety ceiling, not the DSL AST limit. The compiler
        # owns and diagnoses the exact 64-level expression contract.
        if depth > 512:
            return None, _diagnostic("P07E003_INVALID_YAML", source_id, span=_span(source_id, node), field_path=path)
        spans.append((path, _span(source_id, node)))
        if isinstance(node, ScalarNode):
            if node.style is not None:
                value: Any = node.value
            else:
                value, code = _plain_scalar(node)
                if code is not None:
                    return None, _diagnostic(code, source_id, span=_span(source_id, node), field_path=path)
            if isinstance(value, str) and len(value) > MAX_STRING_LENGTH:
                return None, _diagnostic("P07E103_INVALID_FIELD_VALUE", source_id, span=_span(source_id, node), field_path=path)
            return value, None
        if isinstance(node, SequenceNode):
            if len(node.value) > MAX_SEQUENCE_ELEMENTS:
                return None, _diagnostic(
                    "P07E103_INVALID_FIELD_VALUE", source_id,
                    span=_span(source_id, node), field_path=path,
                    details={"limit": MAX_SEQUENCE_ELEMENTS, "observed": len(node.value)},
                )
            output = []
            for index, child in enumerate(node.value):
                value, failure = convert(child, f"{path}[{index}]", depth + 1)
                if failure is not None:
                    return None, failure
                output.append(value)
            return output, None
        if isinstance(node, MappingNode):
            if len(node.value) > MAX_MAPPING_ENTRIES:
                return None, _diagnostic(
                    "P07E103_INVALID_FIELD_VALUE", source_id,
                    span=_span(source_id, node), field_path=path,
                    details={"limit": MAX_MAPPING_ENTRIES, "observed": len(node.value)},
                )
            output: dict[str, Any] = {}
            for key_node, value_node in node.value:
                if not isinstance(key_node, ScalarNode) or key_node.style is None and _numeric_like_invalid(key_node.value):
                    return None, _diagnostic("P07E003_INVALID_YAML", source_id, span=_span(source_id, key_node), field_path=path)
                key = key_node.value
                if key == "<<":
                    return None, _diagnostic("P07E005_FORBIDDEN_YAML_FEATURE", source_id, span=_span(source_id, key_node), field_path=path)
                if key in output:
                    return None, _diagnostic("P07E004_DUPLICATE_KEY", source_id, span=_span(source_id, key_node), field_path=f"{path}.{key}")
                child_path = f"{path}.{key}"
                spans.append((child_path, _span(source_id, key_node, value_node.end_mark)))
                value, failure = convert(value_node, child_path, depth + 1)
                if failure is not None:
                    return None, failure
                output[key] = value
            return output, None
        return None, _diagnostic("P07E003_INVALID_YAML", source_id, span=_span(source_id, node), field_path=path)

    try:
        converted, failure = convert(root, "$")
    except RecursionError:
        return _diagnostic("P07E003_INVALID_YAML", source_id)
    if failure is not None:
        return failure
    assert isinstance(converted, Mapping)
    return ParsedYamlSucceeded(ParsedYaml(value=converted, spans=tuple(spans)))


__all__ = ("ParsedYaml", "ParsedYamlFailed", "ParsedYamlSucceeded", "parse_yaml_source")
