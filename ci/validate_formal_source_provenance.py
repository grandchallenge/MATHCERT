#!/usr/bin/env python3
"""Validate the immutable MC-FC-GOV-001 expanded-source provenance record."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance" / "formal_sources" / "MC-FC-GOV-001.json"
ROUTES_PATH = ROOT / "governance" / "certification_routes.json"

SOLVE = "90b3ee6eb12e9224737f09a56dd4578f6baed750"
PROGRAMME = "aafd5d5d18989d4ac246de8f6dd2455f02614307"
FORGE = "0faee396ffa56c568ee0ae6a348bdb43ca80ac4d"
UPSTREAM = "85f863718beeec7b58a3a1926ee92e3472bc2020"
READY = {"UC-001", "NS-CI-001", "HC-001"}
PENDING = {"BSD-001", "PNP-001", "RH-001", "YM-001", "OZ-001"}
MANIFESTS = {
    "UC-001": "55629c3004b8bffc35fc0fa6f5fbc711ff48aa3c",
    "NS-CI-001": "35f7cd6ccf0e27f199571189fcb34a3f8adc31d7",
    "HC-001": "48e3a0c22299147fe48cb4288cda813d7cffdcb4",
    "BSD-001": "3fb3b07400915d90047a06a353537cf2e1593b9e",
    "PNP-001": "6ecdfa0714828518878ccaf2cdc65756a5955186",
    "RH-001": "0b58fa0ed35907eddf89062069793987b3b03f2e",
    "YM-001": "733d11811d0226fa2b2467965c3655a7d0fad963",
    "OZ-001": "8b3164ab88a35ec9fba69013b44056573e846bfe",
}
PACKETS = {
    "UC-001": "8369bc21e45be6af71d2a0cdb0c5ab3cb5313bfb",
    "NS-CI-001": "58b10636bd614e91e6c35900b9f5fb68e7f88afb",
    "HC-001": "0c154af2e577e4367f9f5d0aeac5e15f9420172c",
    "BSD-001": "20f8dbf016ab179cbf910d0510ad26b2bd9a24cb",
    "PNP-001": "c9d419c43293d533de8858099d26672f1b8d9dbe",
    "RH-001": "525ca580e3b29ed7fcc690f2ce810a26a17a9df2",
    "YM-001": "54b7ad8156532e3dceba439356848dfa65a4d1ac",
    "OZ-001": "b244c30b1b3aa4590a8b9ff9d63c5b66dab87663",
}
COMMON = {
    "governance/external_formal_sources.json": "4680bee8e6b641956a5db2b453c94aab7cabb37b",
    "formal_sources/formal_conjectures/source_locks/FC-GDM-002.json": "9acd4a94538592a235bb302c1f31e5da11662643",
    "formal_sources/formal_conjectures/snapshots/FC-GDM-002-ACTIVE-CAMPAIGN-EXPANSION.replay.json": "1ad4250df912bf2c7cfcc7342fb0ad75e8d667e7",
    "formal_sources/formal_conjectures/update_ledgers/FC-GDM-001-TO-FC-GDM-002.json": "ff2590e2a91b7d5ea5ea5a42c23c67c9745608a0",
    "formal_sources/formal_conjectures/replays/FC-GDM-002/REPLAY_MANIFEST.json": "d91c8ae08262791d248c9ba87837c4624c0b4cda",
    "formal_sources/formal_conjectures/replays/FC-GDM-002/FC-GDM-002-INVENTORY-SCREEN.json": "8dbe8d6769e842be72eb8be1e22cc605278c7561",
    "formal_sources/formal_conjectures/replays/FC-GDM-002/FC-GDM-002-TAG-RESOLUTION.json": "7dd39a995a789da583f8f2f0b15da2c30207f0f1",
}
CAMPAIGN_BLOBS = {
    "UC-001": {"formal_sources/formal_conjectures/concordance/UC-001.json": "8bba56b13978b36471e1cbafe358b82b571c2b95"},
    "PNP-001": {"formal_sources/formal_conjectures/concordance/PNP-001.json": "c88ac8ee7493a551670ca2a37385a9157b43c658"},
    "OZ-001": {
        "formal_sources/formal_conjectures/concordance/OZ-001-ZETA3.json": "a7ca853bd5638814078228b40e78283ae0e29b76",
        "formal_sources/formal_conjectures/concordance/OZ-001-ZETA5.json": "b4f5ef332025669c7202b83ea3a3cb13f2c8009e",
        "formal_sources/formal_conjectures/concordance/OZ-001-ZETA7.json": "34e28294097b1519b18c40a770e3cd3d8e81a15c",
        "formal_sources/formal_conjectures/concordance/OZ-001-ZETA9.json": "a6ba362e0160d92f7b609bcc12eea09b66810606",
        "formal_sources/formal_conjectures/concordance/OZ-001-ZETA11.json": "5cdda19da72b5411b67bf378b9c83df2da28dfb5",
        "formal_sources/formal_conjectures/concordance/OZ-001-ODD-UNIVERSAL.json": "06931337e40f3f7644b99470aca7939a5cd89a4f",
        "formal_sources/formal_conjectures/concordance/OZ-001-ODD-INFINITUDE.json": "2e1dd5320a6c19bd4b1515c2f7abdf9843050f48",
        "formal_sources/formal_conjectures/concordance/OZ-001-ZUDILIN-5-11.json": "a17def6ccd96d4cdea6602336f2a09c5f66d188c",
    },
    "BSD-001": {"formal_sources/formal_conjectures/coverage/BSD-001.json": "82166625115162817551c9a6c6ce377e9e049c7e"},
    "HC-001": {"formal_sources/formal_conjectures/coverage/HC-001.json": "dc9dcdd8313c86298d9b4a15a712f0b9c7928a62"},
    "YM-001": {"formal_sources/formal_conjectures/coverage/YM-001.json": "84c25fe523e854cc0e64862fd3eb0bd866a2eac7"},
}
SCOPES = [
    "zeta3", "zeta5", "zeta7", "zeta9", "zeta11",
    "universal-odd-irrationality", "odd-value-infinitude",
    "finite-zudilin-disjunction",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def provenance_errors(
    record_path: Path = RECORD_PATH,
    routes_path: Path = ROUTES_PATH,
) -> list[str]:
    del routes_path  # Current route state is governed by validate_certification_routes.py.
    record = load_json(record_path)
    errors: list[str] = []
    if record.get("schema_version") != "1.0.0" or record.get("verification_id") != "MC-FC-GOV-001":
        errors.append("record identity drift")
    expected_lineage = {
        "mathsolve_commit": SOLVE,
        "mathsolve_contract_path": "contracts/formal_conjectures_expanded_evidence.json",
        "mathsolve_contract_blob": "a6ac51cfe3374c892f7f307d4c7ccff3faa038d1",
        "programme_commit": PROGRAMME,
        "programme_admission_path": "governance/mathforge_provider_imports.json",
        "programme_admission_blob": "3b796157324eeb925051efee78795a2ad1bcb2b5",
        "mathforge_commit": FORGE,
        "upstream_repository": "google-deepmind/formal-conjectures",
        "upstream_commit": UPSTREAM,
    }
    if record.get("lineage") != expected_lineage:
        errors.append("lineage drift")
    replay = record.get("independent_replay", {})
    expected_replay = {
        "workflow_run_id": 30544600547,
        "artifact_id": 8761186970,
        "artifact_downloaded": True,
        "archive_byte_length": 73686,
        "archive_sha256": "1c74747519c17f873f323198a92104538667092f3274a667a09e1a6b219a7bcb",
        "zip_valid": True,
        "canonical_snapshot_sha256": "2b6bda841d15b022ec8c66bc332177d1283ca791f5d5f6e82323c304d1e6fdf6",
        "lean_toolchain": "leanprover/lean4:v4.27.0",
        "mathlib_revision": "v4.27.0",
    }
    for key, value in expected_replay.items():
        if replay.get(key) != value:
            errors.append(f"replay {key} drift")
    members = {m.get("name"): m for m in replay.get("members", []) if isinstance(m, dict)}
    expected_members = {
        "FC-GDM-002-ACTIVE-CAMPAIGN-EXPANSION.json": (52589, "e7534f913160cc9cef4eb80a735c44b7b1a8ea4273f0f5236d82cc7b9dab042b", 43, 0),
        "FC-GDM-002-FULL-INVENTORY.json": (1255363, "2693de3b83c0990b0e7c62ab5032698c6dde6de0942441ba7d6cdb035625e687", 0, 3232),
        "FC-GDM-002-INVENTORY-SCREEN.json": (2926, "42924e2d64af4a521d2eb7d8f6ace257bc985a833315995746f168a49fb4c587", 0, 0),
        "FC-GDM-002-TAG-RESOLUTION.json": (430, "cb36d1abb7a08984220f9b2c4fc7fe51a2341368bc6f7945497caadba5ae36b6", 0, 0),
        "REPLAY_MANIFEST.json": (1208, "de8786668ecbe8fbd087a3ef5d1ca2fea384f43ed1c388a5c80f498e3408d1ad", 0, 0),
    }
    if set(members) != set(expected_members):
        errors.append("replay member set drift")
    for name, expected in expected_members.items():
        member = members.get(name, {})
        actual = (
            member.get("byte_length"), member.get("sha256"),
            member.get("statement_count"), member.get("problem_count"),
        )
        if actual != expected:
            errors.append(f"replay member drift: {name}")
    if record.get("common_provider_blobs") != COMMON:
        errors.append("common provider artifacts drift")
    campaigns = record.get("campaign_provider_blobs", {})
    if campaigns != CAMPAIGN_BLOBS:
        errors.append("campaign provider artifacts drift")
    if len(campaigns.get("OZ-001", {})) != 8:
        errors.append("odd-zeta theorem lattice incomplete")
    if record.get("solve_manifest_blobs") != MANIFESTS:
        errors.append("Solve manifest identities drift")
    packet_map = record.get("solve_handoff_packets", {})
    if set(packet_map) != set(PACKETS):
        errors.append("Solve packet coverage drift")
    for campaign, digest in PACKETS.items():
        state = "ready" if campaign in READY else "pending"
        if packet_map.get(campaign) != {"blob": digest, "state": state}:
            errors.append(f"{campaign} packet drift")
    controls = record.get("scope_controls", {})
    if controls.get("required_odd_zeta_scopes") != SCOPES:
        errors.append("odd-zeta scope drift")
    if controls.get("explicit_non_routes") != {
        "BSD-001": "adjacency-only",
        "HC-001": "bounded-negative-source-screen",
        "YM-001": "lexical-false-positive",
    }:
        errors.append("non-route drift")
    if controls.get("pilot_lane") != {
        "source_id": "FC-GDM-001",
        "campaigns": ["RH-001", "NS-CI-001"],
        "status": "unchanged",
    }:
        errors.append("RH/NS pilot drift")
    if record.get("certification_result") != {
        "source_identity_verified": True,
        "extraction_archive_replayed": True,
        "route_manifest_identity_verified": True,
        "handoff_packet_identity_verified": True,
        "target_declaration_elaborated": False,
        "concordance_theorem_kernel_checked": False,
        "mathematical_target_proved": False,
        "adjudicated_outputs": 0,
    }:
        errors.append("certification boundary drift")
    return errors


def main() -> int:
    errors = provenance_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("verified immutable MC-FC-GOV-001 expanded-source provenance; current route adjudications are validated separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
