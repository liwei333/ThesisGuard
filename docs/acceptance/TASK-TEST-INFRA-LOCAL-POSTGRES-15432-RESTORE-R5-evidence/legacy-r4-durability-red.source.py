#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path


class LegacyR4DurabilityRedTest(unittest.TestCase):
    def test_r4_observer_persists_each_sample_before_waiting(self) -> None:
        source = Path(sys.argv[1]).read_text(encoding="utf-8")
        required_primitives = ("flush()", "os.fsync", "stability-timeline.jsonl")
        missing = [primitive for primitive in required_primitives if primitive not in source]
        self.assertEqual(
            missing,
            [],
            "R4 stdout-only/in-memory observer lacks per-sample durable primitives: "
            + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
