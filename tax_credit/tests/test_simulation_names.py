#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2014--, tax-credit development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase

from tax_credit.simulation_names import (
    DIR_CROSS_VALIDATED,
    DIR_CROSS_VALIDATED_TRAD,
    DIR_NOVEL_TAXA_SIMULATIONS,
    DIR_REF_DBS,
    DIR_SELF_VALIDATED,
    cross_validated_root,
    cross_validated_trad_root,
    format_cv_fold_dirname,
    format_novel_fold_dirname,
    novel_taxa_simulations_root,
    parse_cv_dataset_id,
    parse_novel_dataset_id,
    parse_self_validated_dataset_id,
    ref_dbs_root,
    self_validated_root,
)


class SimulationNamesTests(TestCase):

    def test_roots(self):
        base = "/proj/data"
        self.assertEqual(
            cross_validated_root(base),
            "/proj/data/{}".format(DIR_CROSS_VALIDATED),
        )
        self.assertEqual(
            cross_validated_trad_root(base),
            "/proj/data/{}".format(DIR_CROSS_VALIDATED_TRAD),
        )
        self.assertEqual(
            novel_taxa_simulations_root(base),
            "/proj/data/{}".format(DIR_NOVEL_TAXA_SIMULATIONS),
        )
        self.assertEqual(
            self_validated_root(base),
            "/proj/data/{}".format(DIR_SELF_VALIDATED),
        )
        self.assertEqual(
            ref_dbs_root(base),
            "/proj/data/{}".format(DIR_REF_DBS),
        )

    def test_format_cv_fold_dirname(self):
        self.assertEqual(format_cv_fold_dirname("silva", 2), "silva-iter2")

    def test_parse_cv_dataset_id(self):
        p = parse_cv_dataset_id("silva-iter0")
        self.assertEqual(p.database, "silva")
        self.assertEqual(p.iteration, "0")

    def test_format_novel_fold_dirname(self):
        self.assertEqual(
            format_novel_fold_dirname("silva", 3, 1),
            "silva-order-iter1",
        )
        self.assertEqual(
            format_novel_fold_dirname("silva", 6, 0), "silva-species-iter0")

    def test_format_novel_fold_dirname_custom_rank_names(self):
        names = ["domain", "phylum", "class", "order", "family", "genus",
                 "sp"]
        self.assertEqual(
            format_novel_fold_dirname("pr2", 6, 2, names), "pr2-sp-iter2")
        with self.assertRaises(ValueError):
            format_novel_fold_dirname("pr2", 0, 0)      # first rank
        with self.assertRaises(ValueError):
            format_novel_fold_dirname("pr2", 7, 0)      # past species
        with self.assertRaises(ValueError):
            format_novel_fold_dirname(
                "pr2", 6, 0, names[:6] + ["sub-species"])  # hyphen

    def test_parse_novel_dataset_id(self):
        p = parse_novel_dataset_id("silva-order-iter0")
        self.assertEqual(p.database, "silva")
        self.assertEqual(p.rank, "order")
        self.assertEqual(p.level, 3)
        self.assertEqual(p.iteration, "0")

    def test_parse_novel_dataset_id_hyphenated_db(self):
        p = parse_novel_dataset_id("B1-REF-species-iter0")
        self.assertEqual(p.database, "B1-REF")
        self.assertEqual(p.rank, "species")
        self.assertEqual(p.level, 6)
        self.assertEqual(p.iteration, "0")

    def test_parse_novel_dataset_id_custom_rank_names(self):
        names = ["Domain", "Phylum", "Class", "Order", "Family", "Genus",
                 "Species"]
        p = parse_novel_dataset_id("pr2-Genus-iter1", names)
        self.assertEqual((p.database, p.rank, p.level), ("pr2", "Genus", 5))

    def test_parse_novel_dataset_id_rejects_other_names(self):
        # a cross-validated id, the first rank, and an old level-numbered name
        for dataset_id in ("addJ-test-iter0", "silva-kingdom-iter0",
                           "silva-L6-iter0"):
            with self.assertRaises(ValueError):
                parse_novel_dataset_id(dataset_id)
        with self.assertRaisesRegex(ValueError, "regenerate"):
            parse_novel_dataset_id("silva-L6-iter0")

    def test_format_parse_round_trip(self):
        for level in range(1, 7):
            name = format_novel_fold_dirname("B1-REF", level, 4)
            p = parse_novel_dataset_id(name)
            self.assertEqual((p.database, p.level, p.iteration),
                             ("B1-REF", level, "4"))

    def test_parse_self_validated_dataset_id(self):
        p = parse_self_validated_dataset_id("silva")
        self.assertEqual(p.database, "silva")
        self.assertEqual(p.iteration, "0")
