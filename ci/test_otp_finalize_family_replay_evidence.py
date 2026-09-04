from __future__ import annotations

import unittest

from otp_finalize_family_replay_evidence import (
    FAMILIES,
    helper_digest_reference_status,
    same_unique_string_set,
)


class SharedFamilyReplayFinalizerTests(unittest.TestCase):
    def test_supported_family_set_is_exact(self) -> None:
        self.assertEqual(
            set(FAMILIES),
            {
                "OTP-H-GAPCVP",
                "OTP-B1-BINARY-CODES",
                "OTP-B2-SPHERICAL-CODES",
            },
        )

    def test_permitted_axiom_order_is_not_semantic(self) -> None:
        self.assertTrue(
            same_unique_string_set(
                ["propext", "Classical.choice", "Quot.sound"],
                ["Quot.sound", "propext", "Classical.choice"],
            )
        )

    def test_permitted_axiom_membership_drift_is_rejected(self) -> None:
        self.assertFalse(
            same_unique_string_set(
                ["propext", "Classical.choice"],
                ["propext", "Quot.sound"],
            )
        )

    def test_duplicate_axiom_entries_are_rejected(self) -> None:
        self.assertFalse(
            same_unique_string_set(
                ["propext", "propext"],
                ["propext"],
            )
        )

    def test_non_string_axiom_entries_are_rejected(self) -> None:
        self.assertFalse(same_unique_string_set(["propext", 1], ["propext", "1"]))

    def test_helper_digest_drift_is_retained_as_observation_not_rejected(self) -> None:
        status = helper_digest_reference_status(
            {"nanoda_bin": "60cc", "landrun": "a4ba"},
            {"nanoda_bin": "2827", "landrun": "a4ba"},
        )
        self.assertFalse(status["nanoda_bin"]["matches_reference_observation"])
        self.assertEqual(status["nanoda_bin"]["reference_observation"], "60cc")
        self.assertEqual(status["nanoda_bin"]["current_observation"], "2827")
        self.assertTrue(status["landrun"]["matches_reference_observation"])

    def test_helper_digest_reference_must_cover_exact_helper_set(self) -> None:
        with self.assertRaisesRegex(ValueError, "coverage drift"):
            helper_digest_reference_status(
                {"nanoda_bin": "60cc"},
                {"nanoda_bin": "2827", "landrun": "a4ba"},
            )

    def test_helper_digest_reference_must_be_string_map(self) -> None:
        with self.assertRaisesRegex(ValueError, "string map"):
            helper_digest_reference_status(
                {"nanoda_bin": 60},
                {"nanoda_bin": "2827"},
            )


if __name__ == "__main__":
    unittest.main()
