"""Valida la base canónica sin regenerar ni alterar sus datos."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "sources" / "knowledge"
PLACEHOLDERS = (
    "source_text",
    "ver source",
    "source_preserved",
    "conservadas dentro",
    "characteristics_and_rules",
)
CHARACTERISTICS = {"M", "WS", "BS", "S", "T", "W", "I", "A", "Ld"}
SOURCE_FIELDS = {"manual", "printed_page", "section"}


def load_yaml(path: Path, errors: list[str]):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # El nombre del fichero importa más que veinte líneas de traceback.
        errors.append(f"YAML inválido en {path.relative_to(ROOT)}: {exc}")
        return None


def valid_source(source) -> bool:
    return isinstance(source, dict) and SOURCE_FIELDS <= set(source) and all(
        source.get(field) not in (None, "") for field in SOURCE_FIELDS
    )


def validate_band(path: Path, band_ids: set[str], errors: list[str]) -> int:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    for marker in PLACEHOLDERS:
        if marker in lowered:
            errors.append(f"Marcador obsoleto '{marker}' en {path.name}")

    band = load_yaml(path, errors)
    if not isinstance(band, dict):
        return 0

    band_id = band.get("id")
    if not band_id or band_id in band_ids:
        errors.append(f"ID de banda ausente o duplicado en {path.name}: {band_id!r}")
    band_ids.add(band_id)
    if not valid_source(band.get("source")):
        errors.append(f"Banda sin fuente estructurada en {path.name}")

    profiles = band.get("profiles", [])
    local_profiles = {profile.get("id") for profile in profiles}
    if None in local_profiles or len(local_profiles) != len(profiles):
        errors.append(f"Perfiles sin ID o duplicados en {path.name}")
    equipment_lists = band.get("equipment_lists", [])
    list_ids = {entry.get("id") for entry in equipment_lists}
    if None in list_ids or len(list_ids) != len(equipment_lists):
        errors.append(f"Listas de equipo sin ID o duplicadas en {path.name}")
    for equipment_list in equipment_lists:
        if not valid_source(equipment_list.get("source")):
            errors.append(f"Lista de equipo sin fuente en {path.name}: {equipment_list.get('id')}")

    for member in band.get("roster", {}).get("members", []):
        if member.get("profile_id") not in local_profiles:
            errors.append(f"Perfil de roster inexistente en {path.name}: {member.get('profile_id')}")
        maximum = member.get("maximum")
        if maximum is not None and member.get("minimum", 0) > maximum:
            errors.append(f"Cupo imposible en {path.name}: {member.get('profile_id')}")

    for profile in profiles:
        stats = profile.get("characteristics", {})
        if set(stats) != CHARACTERISTICS:
            errors.append(f"Perfil incompleto en {path.name}: {profile.get('id')}")
        for list_id in profile.get("equipment_lists", []):
            if list_id not in list_ids:
                errors.append(f"Lista de equipo inexistente en {path.name}: {list_id}")
        if not valid_source(profile.get("source")):
            errors.append(f"Perfil sin fuente estructurada en {path.name}: {profile.get('id')}")
        for rule in profile.get("rules", []):
            if not valid_source(rule.get("source")):
                errors.append(f"Regla de perfil sin fuente en {path.name}: {rule.get('id')}")

    for rule in band.get("band_rules", []):
        if not valid_source(rule.get("source")):
            errors.append(f"Regla de banda sin fuente en {path.name}: {rule.get('id')}")

    return len(profiles)


def validate_catalogs(errors: list[str]) -> int:
    record_ids: set[str] = set()
    records = 0
    for path in sorted((KB / "catalog").glob("*.yaml")):
        data = load_yaml(path, errors)
        if not isinstance(data, dict):
            continue
        if "records" not in data:
            continue
        for record in data["records"]:
            record_id = record.get("id")
            if not record_id or record_id in record_ids:
                errors.append(f"ID de catálogo ausente o duplicado: {record_id!r} ({path.name})")
            record_ids.add(record_id)
            if not record.get("source"):
                errors.append(f"Registro sin fuente: {record_id} ({path.name})")
            if not record.get("rule_summary"):
                errors.append(f"Registro sin regla: {record_id} ({path.name})")
            records += 1
    return records


def validate_manifest(errors: list[str]) -> int:
    manifest = json.loads((KB / "index" / "manifest.json").read_text(encoding="utf-8"))
    manuals = manifest.get("manuals", [])
    if len(manuals) != 4:
        errors.append(f"Número de manuales en el manifiesto: {len(manuals)}; se esperaban 4")
    return sum(manual.get("pages", 0) for manual in manuals)


def main() -> None:
    errors: list[str] = []
    band_ids: set[str] = set()
    profile_count = 0
    band_paths = sorted((KB / "bands").glob("*.yaml"))

    for path in band_paths:
        profile_count += validate_band(path, band_ids, errors)

    if len(band_paths) != 34:
        errors.append(f"Número de bandas: {len(band_paths)}; se esperaban 34")

    catalog_count = validate_catalogs(errors)
    page_count = validate_manifest(errors)

    if errors:
        raise SystemExit("\n".join(f"- {error}" for error in errors))

    print(
        f"OK: {len(band_paths)} bandas, {profile_count} perfiles, "
        f"{catalog_count} reglas de catálogo y {page_count} páginas documentadas"
    )


if __name__ == "__main__":
    main()
