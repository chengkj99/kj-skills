#!/usr/bin/env python3
"""Score research signals using the Industry Best Practices rubric.

Input JSON example:
{
  "product_fit": 85,
  "novelty": 70,
  "evidence_strength": 80,
  "source_diversity": 60,
  "architecture_transferability": 75,
  "evalability": 70,
  "implementation_efficiency": 80,
  "hype_penalty": 5,
  "material_type": "engineering_practice",
  "domain_velocity": "fast",
  "age_days": 420,
  "recently_revalidated": true
}
"""
from __future__ import annotations

import argparse
import json
import sys

WEIGHTS = {
    "product_fit": 0.25,
    "novelty": 0.18,
    "evidence_strength": 0.20,
    "source_diversity": 0.10,
    "architecture_transferability": 0.12,
    "evalability": 0.10,
    "implementation_efficiency": 0.05,
}

MATERIAL_HALF_LIFE_DAYS = {
    "breaking_change": 60,
    "product_practice": 120,
    "engineering_practice": 270,
    "benchmark_or_eval": 270,
    "academic_method": 365,
    "standard_or_framework": 1095,
    "classic_principle": 1460,
    "expert_talk": 120,
}

DOMAIN_VELOCITY_MULTIPLIER = {
    "fast": 0.65,
    "medium": 1.0,
    "slow": 1.5,
}


def clamp(value: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, value))


def truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "有", "是"}
    return bool(value)


def calculate_freshness_penalty(item: dict) -> tuple[float, dict]:
    """Estimate time decay without mechanically penalizing all old material."""
    if "freshness_penalty" in item:
        penalty = clamp(float(item["freshness_penalty"]), 0, 25)
        return penalty, {"source": "provided", "penalty": penalty}

    material_type = str(item.get("material_type", "product_practice"))
    domain_velocity = str(item.get("domain_velocity", "medium"))
    freshness_status = str(item.get("freshness_status", "")).lower()
    current_version_status = str(item.get("current_version_status", "")).lower()
    revalidated = truthy(item.get("recently_revalidated")) or bool(item.get("revalidation_evidence"))
    is_classic = truthy(item.get("is_classic")) or freshness_status == "classic"

    age_days_raw = item.get("age_days")
    if age_days_raw in (None, ""):
        return 0.0, {
            "source": "not_calculated",
            "reason": "age_days not provided",
            "material_type": material_type,
            "domain_velocity": domain_velocity,
        }

    age_days = max(0.0, float(age_days_raw))
    half_life = MATERIAL_HALF_LIFE_DAYS.get(material_type, 180)
    if material_type not in {"standard_or_framework", "classic_principle"}:
        half_life *= DOMAIN_VELOCITY_MULTIPLIER.get(domain_velocity, 1.0)

    ratio = age_days / max(half_life, 1)
    if ratio <= 1:
        penalty = ratio * 5
    elif ratio <= 2:
        penalty = 5 + (ratio - 1) * 7
    elif ratio <= 3:
        penalty = 12 + (ratio - 2) * 8
    else:
        penalty = 20 + min(5, (ratio - 3) * 2)

    if age_days > 365 and revalidated:
        if material_type in {"standard_or_framework", "classic_principle"} or is_classic:
            penalty = min(penalty, 8)
        else:
            penalty = min(penalty, 12)

    if age_days > 365 and not revalidated and material_type in {
        "breaking_change",
        "product_practice",
        "expert_talk",
    }:
        penalty = max(penalty, 18)

    if current_version_status in {"obsolete", "superseded", "deprecated", "replaced"}:
        penalty = max(penalty, 20)

    penalty = clamp(penalty, 0, 25)
    return penalty, {
        "source": "calculated",
        "material_type": material_type,
        "domain_velocity": domain_velocity,
        "age_days": age_days,
        "half_life_days": round(half_life, 1),
        "recently_revalidated": revalidated,
        "is_classic": is_classic,
        "current_version_status": current_version_status or None,
        "penalty": round(penalty, 1),
    }


def score(item: dict) -> dict:
    raw = 0.0
    details = {}
    for key, weight in WEIGHTS.items():
        value = clamp(float(item.get(key, 0)))
        contribution = value * weight
        details[key] = {"value": value, "weight": weight, "contribution": contribution}
        raw += contribution
    hype_penalty = clamp(float(item.get("hype_penalty", 0)), 0, 25)
    freshness_penalty, freshness_details = calculate_freshness_penalty(item)
    final = clamp(raw - hype_penalty - freshness_penalty)
    if final >= 80:
        bucket = "priority_opportunity"
    elif final >= 65:
        bucket = "watch_or_prototype"
    elif final >= 50:
        bucket = "record_only"
    else:
        bucket = "ignore_by_default"
    return {
        "score": round(final, 1),
        "raw_score": round(raw, 1),
        "hype_penalty": hype_penalty,
        "freshness_penalty": round(freshness_penalty, 1),
        "bucket": bucket,
        "details": details,
        "freshness_details": freshness_details,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", nargs="?", help="Path to JSON file. If omitted, read stdin.")
    args = parser.parse_args()
    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            item = json.load(f)
    else:
        item = json.load(sys.stdin)
    print(json.dumps(score(item), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
