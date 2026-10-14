# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jsonschema[format-nongpl]>=4.23",
#     "openapi-spec-validator>=0.7",
#     "pyyaml>=6.0",
# ]
# ///
"""Check that the contracts are valid and consistent with each other (Lesson L1.3, step 6).

Run from the repository root:
    uv run tools/check_contracts.py

Exits with code 1 if any check fails, so CI can use it (L2.3).
"""

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate as validate_openapi
from referencing import Registry, Resource

CONTRACTS = Path("contracts")
SCHEMA_SQL = CONTRACTS / "schema.sql"
OPENAPI = CONTRACTS / "openapi" / "platform-api.yaml"
EVENTS = CONTRACTS / "events"
SAMPLES = CONTRACTS / "sample-data" / "events"

# Enums shared between the database, the API and the events.
# Name used in OpenAPI and events -> (table, column) in schema.sql.
SHARED_ENUMS = {
    "SlideStatus": ("slides", "status"),
    "Stain": ("slides", "stain"),
    "SpecimenType": ("cases", "specimen_type"),
    "QcVerdict": ("qc_results", "verdict"),
    "ModelTask": ("model_versions", "task"),
    "ModelStatus": ("model_versions", "status"),
    "RunStatus": ("inference_runs", "status"),
    "DecisionValue": ("pathologist_decisions", "decision"),
    "ReportSource": ("reports", "source"),
}

failures: list[str] = []


def ok(message: str) -> None:
    print(f"  ok    {message}")


def fail(message: str) -> None:
    print(f"  FAIL  {message}")
    failures.append(message)


def sql_check_enums(sql: str) -> dict[tuple[str, str], set[str]]:
    """Find every `CHECK (column IN ('a', 'b'))` and return {(table, column): {'a', 'b'}}."""
    enums: dict[tuple[str, str], set[str]] = {}
    for table, body in re.findall(r"CREATE TABLE (\w+) \((.*?)\n\);", sql, re.DOTALL):
        for column, values in re.findall(r"CHECK \((\w+) IN \(([^)]*)\)\)", body):
            enums[(table, column)] = set(re.findall(r"'([^']*)'", values))
    return enums


def load_event_schemas() -> dict[str, dict]:
    return {
        path.name.removesuffix(".schema.json"): json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(EVENTS.glob("*.schema.json"))
    }


def check_openapi() -> dict:
    print("OpenAPI")
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    try:
        validate_openapi(spec)
        ok(f"{OPENAPI} is valid OpenAPI {spec['openapi']} ({len(spec['paths'])} paths)")
    except Exception as error:  # the validator raises several exception types
        fail(f"{OPENAPI} is invalid: {error}")
    return spec


def check_events(schemas: dict[str, dict]) -> None:
    print("Event schemas and samples")

    # A registry lets "$ref": "common.schema.json#/..." resolve to the file on disk.
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
    )

    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as error:
            fail(f"{name}: not a valid JSON Schema: {error}")
            continue

        if name == "common":
            ok("common: valid")
            continue

        if schema.get("unevaluatedProperties") is not False:
            fail(f"{name}: must set \"unevaluatedProperties\": false (no unknown fields)")

        sample_path = SAMPLES / f"{name}.json"
        if not sample_path.exists():
            fail(f"{name}: no sample at {sample_path}")
            continue

        validator = Draft202012Validator(
            schema, registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER
        )
        sample = json.loads(sample_path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(sample), key=lambda e: list(e.path))
        if errors:
            for error in errors:
                location = "/".join(str(p) for p in error.path) or "(root)"
                fail(f"{name}: sample invalid at {location}: {error.message}")
        else:
            ok(f"{name}: schema valid, sample valid")

    for sample_path in sorted(SAMPLES.glob("*.json")):
        if sample_path.stem not in schemas:
            fail(f"sample {sample_path.name} has no schema in {EVENTS}")


def check_shared_enums(spec: dict, schemas: dict[str, dict]) -> None:
    print("Shared enums (schema.sql vs OpenAPI vs events)")
    sql_enums = sql_check_enums(SCHEMA_SQL.read_text(encoding="utf-8"))
    api_schemas = spec.get("components", {}).get("schemas", {})
    event_defs = schemas.get("common", {}).get("$defs", {})

    for name, (table, column) in SHARED_ENUMS.items():
        sql_values = sql_enums.get((table, column))
        if sql_values is None:
            fail(f"{name}: no CHECK constraint on {table}.{column} in schema.sql")
            continue

        others = {
            "OpenAPI": api_schemas.get(name, {}).get("enum"),
            "events": event_defs.get(name, {}).get("enum"),
        }
        present = {source: set(values) for source, values in others.items() if values}
        if not present:
            fail(f"{name}: only in schema.sql; expected in OpenAPI or events too")
            continue

        mismatches = [
            f"{source} {sorted(values)} != schema.sql {sorted(sql_values)}"
            for source, values in present.items()
            if values != sql_values
        ]
        if mismatches:
            fail(f"{name}: " + "; ".join(mismatches))
        else:
            ok(f"{name}: schema.sql and {' and '.join(present)} agree")


def main() -> None:
    if not CONTRACTS.is_dir():
        sys.exit("Run this from the repository root (no contracts/ folder here).")

    spec = check_openapi()
    schemas = load_event_schemas()
    check_events(schemas)
    check_shared_enums(spec, schemas)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed.")
        sys.exit(1)
    print("All contract checks passed.")


if __name__ == "__main__":
    main()
