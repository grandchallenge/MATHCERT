from __future__ import annotations

import unittest

from otp_finalize_family_replay_evidence import FAMILIES, same_unique_string_set


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


if __name__ == "__main__":
    unittest.main()
