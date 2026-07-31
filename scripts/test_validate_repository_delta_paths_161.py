#!/usr/bin/env python3
"""Focused regression tests for ERR-LAB-008 path normalization."""

from __future__ import annotations

import unittest

from validate_repository import normalize_registry_paths


EXISTING = {"registry/a.json", "registry/b.json", "registry/c.json"}


class RegistryDeltaPathTests(unittest.TestCase):
    def normalize(self, value):
        return normalize_registry_paths(value, EXISTING.__contains__)

    def test_scalar_path_is_preserved(self):
        scalar, issues = self.normalize({"projects": "registry/a.json"})
        self.assertEqual(scalar, {"projects": "registry/a.json"})
        self.assertEqual(issues, [])

    def test_valid_path_list_is_checked_and_not_loaded_as_registry(self):
        scalar, issues = self.normalize(
            {"projects": "registry/a.json", "decision_deltas": ["registry/b.json", "registry/c.json"]}
        )
        self.assertEqual(scalar, {"projects": "registry/a.json"})
        self.assertEqual(issues, [])

    def test_empty_list_is_valid(self):
        scalar, issues = self.normalize({"decision_deltas": []})
        self.assertEqual(scalar, {})
        self.assertEqual(issues, [])

    def test_duplicate_paths_are_rejected(self):
        _, issues = self.normalize(
            {"decision_deltas": ["registry/b.json", "registry/b.json"]}
        )
        self.assertEqual(len(issues), 1)
        self.assertIn("duplicate path", issues[0])

    def test_invalid_container_type_is_rejected(self):
        _, issues = self.normalize({"decision_deltas": {"path": "registry/b.json"}})
        self.assertEqual(len(issues), 1)
        self.assertIn("path string or path array", issues[0])

    def test_invalid_array_item_type_is_rejected(self):
        _, issues = self.normalize({"decision_deltas": ["registry/b.json", 7]})
        self.assertEqual(len(issues), 1)
        self.assertIn("must be a path string", issues[0])

    def test_nonexistent_paths_are_rejected(self):
        _, issues = self.normalize({"decision_deltas": ["registry/missing.json"]})
        self.assertEqual(len(issues), 1)
        self.assertIn("missing path", issues[0])

    def test_mixed_scalar_and_array_records(self):
        scalar, issues = self.normalize(
            {
                "projects": "registry/a.json",
                "decision_deltas": ["registry/b.json"],
                "evidence": "registry/c.json",
            }
        )
        self.assertEqual(
            scalar,
            {"projects": "registry/a.json", "evidence": "registry/c.json"},
        )
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
