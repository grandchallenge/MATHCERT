from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "governance/result_family_adjudication_contracts"
REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_WP07_ADJUDICATION_CONTRACTS.json"
CONTRACT_SCHEMA = ROOT / "schemas/openai_ten_proofs_adjudication_contract.schema.json"
REGISTRY_SCHEMA = ROOT / "schemas/openai_ten_proofs_adjudication_contract_registry.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP06_ROUTE_REGISTRATIONS.json"
ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-CERT-ROUTE-REGISTRATION-001.v1.json"
ATTESTATION_DOCUMENT = ROOT / "governance/post_merge_attestations/OTP-CERT-ROUTE-REGISTRATION-001.v1.md"
FAMILIES = ["OTP-F-EHRHART", "OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"]
CONTRACT_BLOBS = {"OTP-F-EHRHART": "6e1c210d82440210da71fd661daffe986df81f03", "OTP-J1-COMPACTNESS": "4288cf2199603ffc90d897062a575a5865326d70", "OTP-J2-TWO-DEGENERATE": "2bb9d70b931ea0a07487664c112644f990527760"}
REGISTRY_BLOB = "7a4aa7ca4f016020fccd0b9d4e73e1c5af12d03f"
ROUTE_REGISTRY_BLOB = "b5541045591f8589130b1577c50d51d70c3b4337"
RECEIPT_BLOB = "38b1c03a6506f877ad9aed74e92cb6d202b444a5"
ATTESTATION_BLOB = "01c963fe22acec8073086038b78601b2128fea27"
ATTESTATION_DOCUMENT_BLOB = "afe8b4241fe5c8cc99626f713f9ac76f48f7b805"
COMMON = {
    "official_subject": {"repository": "openai/ten-proofs", "commit": "e62211d28e3a9131950c89caa6542cfe5eff3bca", "tree": "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365", "archive_sha256": "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f"},
    "provider_manifest": ("grandchallenge/MATHFORGE", "0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15", "provider_manifests/OPENAI-TEN-PROOFS-001.json", "fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472"),
    "source_revision_audit": ("grandchallenge/MATHFORGE", "a498ef40b7652b55bf121b5682604e259b8d3073", "sources/OPENAI-TEN-PROOFS-001/source_revision_audits/OTP-TRANCHE-001.json", "80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05"),
}
EXPECTED = {
    "OTP-F-EHRHART": {"contract_id": "MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART", "route_id": "MC-ROUTE-OTP-F-EHRHART", "targets": ["Ehrhart.Volume.ehrhart_volume_inequality_for_sets", "Ehrhart.SimplexVolume.exists_centeredBody_sharp", "Ehrhart.SimplexVolume.barycenter_centeredSimplex", "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex"], "semantic": "a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb", "packet": "4653985d4980113514266c3c421804437bacb019", "intake": "1c6a5f349803bba09b000ceb3f8a53ee3038ca48", "wp": "056149e7a659fb6b24b7d7389a3dcd68bb581bcd", "replay": "d17d36d02f6505060f5a9e5f1f71f3c323fa1af8", "bundle": "346eebb415609e6e66a9cb04510b7ba4994cf309", "bundle_sha256": "22fcaad533db94c03569439bb41fcda68618386826abd3aa624bbf90e9345adb", "proposal": "7b069a003c84ef285259108076a55338fab0bc7f", "source_tokens": ["Chapter 8", "Theorem 1.1"], "boundary_tokens": ["encoded Ehrhart", "classification of all equality cases"], "exclusion_tokens": ["classification", "proof body", "encoded theorem targets"], "competence": "convex and discrete geometry"},
    "OTP-J1-COMPACTNESS": {"contract_id": "MC-OTP-ADJUDICATION-CONTRACT-J1-COMPACTNESS", "route_id": "MC-ROUTE-OTP-J1-COMPACTNESS", "targets": ["CompactnessConjecture.quantitativeCompactnessCounterexample", "CompactnessConjecture.compactnessCounterexample_bigO", "CompactnessConjecture.not_erdos_180"], "semantic": "659396358d0d999c00011645f72602f30ccf6b0e", "packet": "2d9c6e555a03b71eb33c476321e7f2d311ed168f", "intake": "d08eec02d7ee44f3bc2692cf7949c70d8e0f2bbf", "wp": "d80cade6d99c7ca54f4384a68e178b2f4335a8b2", "replay": "5fe635510a0d2aa05da641e342078cf8b2b34aa6", "bundle": "0f2a8918e669734ab89ece34b3f6dc60774552e2", "bundle_sha256": "852d0fa51a328199e6aeaf67a51fdd384ab30ec62ef6a7e28c5e22e597b3a99b", "proposal": "2e541ca5882873ee1c756814642994361b10c78c", "source_tokens": ["Chapter 10", "Theorem 1.1"], "boundary_tokens": ["checker acceptance", "construction", "asymptotic interpretation"], "exclusion_tokens": ["construction", "historical compactness", "proof body"], "competence": "extremal graph theory"},
    "OTP-J2-TWO-DEGENERATE": {"contract_id": "MC-OTP-ADJUDICATION-CONTRACT-J2-TWO-DEGENERATE", "route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE", "targets": ["TwoDegenerateGraphs.twoDegenerateExtremalCounterexample", "TwoDegenerateGraphs.not_erdos_146"], "semantic": "7bd168c46921f64364b20021b6315d68f0fde7d0", "packet": "0d226492bf13e13bc1a437be01104db3d4c96f79", "intake": "6e9cfee8f988e357aabdd53e2883220d170b7e60", "wp": "dbbc4ab59f21b3f5cb2f313c51f754b9b306389c", "replay": "215ce18b4139159c89d167ab11cab6c35d5a38ff", "bundle": "14d050b03ccc9891f8c3e5ec4f522aa5aa00b8aa", "bundle_sha256": "b3efb532152677dd84c0872071a9d2aa061ea56b9a8a7d9175c6382766f27ed4", "proposal": "0692ac15c19328532bdcd3e73b3c8c4371647ac6", "source_tokens": ["Chapter 10", "Theorem 1.2"], "boundary_tokens": ["checker acceptance", "construction", "extremal interpretation"], "exclusion_tokens": ["construction", "coloring-side", "proof body"], "competence": "extremal graph theory"},
}
TOP_KEYS = {"schema_version", "record_type", "contract_id", "candidate_id", "result_family", "route_id", "contract_state", "tracker_issue", "authority", "route_scope", "decision_contract", "reviewer_requirements", "execution_gate", "state", "preserved_limitations", "claim_boundary"}
AUTH_KEYS = {"official_subject", "provider_manifest", "source_revision_audit", "semantic_record", "producer_packet", "cert_intake", "cert_work_package", "replay_evidence", "repository_bundle", "route_proposal", "route_registration", "post_merge_attestation", "implementation_authorization"}
STATE = {"may_adjudicate": False, "adjudication": None, "cert_output": None, "mathematical_target_proved": False, "may_promote_claim": False, "aggregate_adjudication": False}
LIMITS = {"whole_document_byte_equivalence": "not_established", "whole_document_semantic_equivalence": "not_established", "proof_body_compared_in_full": False, "unexamined_result_family_count": 9, "blocked_repair_lanes": ["OTP-C-PERMANENT", "OTP-H-GAPCVP"], "all_lean_state": "failed_namespace_collision"}
REGISTRY_LIMITS = {"whole_document_byte_equivalence": "not_established", "whole_document_semantic_equivalence": "not_established", "proof_bodies_compared_in_full": False, "unexamined_result_family_count": 9, "blocked_repair_lanes": ["OTP-C-PERMANENT", "OTP-H-GAPCVP"], "all_lean_state": "failed_namespace_collision"}
EVIDENCE_IDS = ["authority_integrity", "isolated_checker_replay", "source_statement_concordance", "nonvacuity", "construction_and_interpretation", "independent_specialist_review", "human_steward_execution_authorization"]
DISPOSITIONS = ["adjudication_clear_encoded_targets_only", "adjudication_not_clear", "defer_insufficient_evidence"]
EXECUTED_PATHS = [ROOT / f"governance/result_family_adjudications/{fam}.json" for fam in FAMILIES] + [ROOT / f"certificates/openai_ten_proofs/{fam}.json" for fam in FAMILIES]

def artifact(repo: str, commit: str, path: str, digest: str) -> dict[str, Any]:
    return {"repository": repo, "commit_sha": commit, "path": path, "digest_algorithm": "git_blob_sha1", "digest": digest}

def expected_authority(fam: str) -> dict[str, Any]:
    x = EXPECTED[fam]
    stem = "ehrhart" if fam.endswith("EHRHART") else "compactness" if fam.endswith("COMPACTNESS") else "two-degenerate"
    return {
        "official_subject": COMMON["official_subject"],
        "provider_manifest": artifact(*COMMON["provider_manifest"]),
        "source_revision_audit": artifact(*COMMON["source_revision_audit"]),
        "semantic_record": artifact("grandchallenge/MATHFORGE", "cb0a203c36a9ef33270d62ab369df7bc27d3b242", f"sources/OPENAI-TEN-PROOFS-001/semantic_audits/{fam}.json", x["semantic"]),
        "producer_packet": artifact("grandchallenge/MATHSOLVE", "443daf537dc7e4ee34ab43aeb01508d9177816ab", f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{fam}.json", x["packet"]),
        "cert_intake": artifact("grandchallenge/MATHCERT", "d99d2625ee838945087a91a50923cddc2dcc8d85", f"governance/result_family_intakes/{fam}.json", x["intake"]),
        "cert_work_package": artifact("grandchallenge/MATHCERT", "677a58a126145977581050bcb5d12d5b6a99fb51", f"governance/result_family_work_packages/{fam}-CERT-WP01.json", x["wp"]),
        "replay_evidence": artifact("grandchallenge/MATHCERT", "563c29c9687aad1bd06330436e3056cce7745c93", f"governance/result_family_replay_evidence/{fam}.json", x["replay"]),
        "repository_bundle": {**artifact("grandchallenge/MATHCERT", "563c29c9687aad1bd06330436e3056cce7745c93", f"evidence/openai_ten_proofs/{stem}.zip.b64", x["bundle"]), "decoded_sha256": x["bundle_sha256"]},
        "route_proposal": artifact("grandchallenge/MATHCERT", "e8d1e34509e640d82902ad0195560740b52bec0e", f"governance/result_family_route_proposals/{fam}.json", x["proposal"]),
    }
