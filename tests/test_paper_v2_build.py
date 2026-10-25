"""Offline regressions for stale PDF publication and appendix preservation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ccc_paper_builder", ROOT / "paper/v2/make_v2.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PaperBuildTests(unittest.TestCase):
    def test_editorial_cleanup_keeps_science_on_both_sides(self):
        source = "## G. Related work\nkeep G\n## H. Figure plan\nremove me\n## I. Tables\nkeep I\n"
        cleaned = builder.clean_source(source)
        self.assertNotIn("remove me", cleaned)
        self.assertIn("keep G", cleaned)
        self.assertIn("keep I", cleaned)

    def test_heldout_figure_targets_heldout_section(self):
        source = "### 5.1 Controls\nDEV\n### 5.4 Original study\nOC\n## 6. Discussion\n"
        where = next(x[1] for x in builder.FIGS if x[2].startswith("Figure 3."))
        at = builder.section_end(source, where)
        self.assertEqual(source[at:][:5], "## 6.")

    def test_archive_invalidates_old_candidate_without_losing_original(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(builder, "BUILD", Path(directory)):
            old = Path(directory) / "submission_v2.pdf"
            old.write_bytes(b"old PDF must not remain candidate")
            sha = builder.digest(old)
            builder.archive_previous()
            self.assertFalse(old.exists())
            self.assertEqual((Path(directory) / "history" / sha / old.name).read_bytes(), b"old PDF must not remain candidate")

    def test_hash_check_rejects_changed_source_or_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "paper/v2/build").mkdir(parents=True)
            build = root / "paper/v2/build"
            source, pdf = root / "source.md", build / "submission_v2.pdf"
            source.write_text("current source")
            pdf.write_bytes(b"%PDF-test")
            report = {"pdf_current": True, "inputs": {"source.md": builder.digest(source)},
                      "outputs": {"paper/v2/build/submission_v2.pdf": builder.digest(pdf)}}
            (build / "build_report.json").write_text(json.dumps(report))
            with patch.object(builder, "ROOT", root), patch.object(builder, "BUILD", build):
                self.assertTrue(builder.check_freshness())
                source.write_text("changed after build")
                self.assertFalse(builder.check_freshness())
                source.write_text("current source")
                pdf.write_bytes(b"old or tampered PDF")
                self.assertFalse(builder.check_freshness())

    def test_renderer_failure_never_publishes_output(self):
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)
            html, pdf = build / "candidate.html", build / "candidate.pdf"
            html.write_text("<p>offline</p>")
            with patch.object(builder, "BUILD", build), patch.object(builder.subprocess, "run", side_effect=OSError("renderer blocked")):
                with self.assertRaises(OSError):
                    builder.render_pdf(html, pdf, "unavailable-browser")
            self.assertFalse(pdf.exists())


if __name__ == "__main__":
    unittest.main()
