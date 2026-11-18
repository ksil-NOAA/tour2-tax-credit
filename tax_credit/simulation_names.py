#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2014--, tax-credit development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

"""Directory names and string encodings for cross-validated and novel-taxa sims."""

from __future__ import annotations

import re
from os.path import join
from typing import NamedTuple

_NOVEL_DATASET_ID_RE = re.compile(r"^(.+)-([^-/\s]+)-iter(\d+)$")
_LEGACY_NOVEL_DATASET_ID_RE = re.compile(r"^.+-L\d+-iter\d+$")
_RANK_NAME_RE = re.compile(r"^[A-Za-z0-9_.]+$")

# The seven scored ranks when no other names are given. Novel-taxa folds are
# named by the held-out rank's name; its level is its index here (6 = species).
DEFAULT_RANK_NAMES = ("kingdom", "phylum", "class", "order", "family",
                      "genus", "species")

# --- Top-level folders under a *data_dir* ----------------------------------
DIR_CROSS_VALIDATED = "cross-validated"
DIR_CROSS_VALIDATED_TRAD = "cross-validated-trad"
DIR_NOVEL_TAXA_SIMULATIONS = "novel-taxa-simulations"
DIR_SELF_VALIDATED = "self-validated"
DIR_REF_DBS = "ref_dbs"

# --- Glob fragments for discovering fold directories -----------------------
GLOB_CV_FOLD_DIRS = "*-iter*"
GLOB_NOVEL_FOLD_DIRS = "*-iter*"


class NovelDatasetParts(NamedTuple):
    """Parsed ``<database>-<rank>-iter<n>`` fold / dataset id.

    *rank* is the held-out rank's name and *level* its index among the scored
    rank names (``species`` is 6 with the default names).
    """

    database: str
    rank: str
    level: int
    iteration: str


class CrossValidatedDatasetParts(NamedTuple):
    """Parsed ``<database>-iter<n>`` dataset id."""

    database: str
    iteration: str


class SelfValidatedDatasetParts(NamedTuple):
    """Parsed self-validated dataset id (reference database name only)."""

    database: str
    iteration: str


def cross_validated_root(data_dir: str) -> str:
    return join(data_dir, DIR_CROSS_VALIDATED)


def cross_validated_trad_root(data_dir: str) -> str:
    return join(data_dir, DIR_CROSS_VALIDATED_TRAD)


def novel_taxa_simulations_root(data_dir: str) -> str:
    return join(data_dir, DIR_NOVEL_TAXA_SIMULATIONS)


def self_validated_root(data_dir: str) -> str:
    return join(data_dir, DIR_SELF_VALIDATED)


def ref_dbs_root(data_dir: str) -> str:
    return join(data_dir, DIR_REF_DBS)


def format_cv_fold_dirname(database: str, iteration: int) -> str:
    """Build cross-validation fold directory name ``{db}-iter{n}``."""
    return "{0}-iter{1}".format(database, iteration)


def parse_cv_fold_dirname(basename: str) -> CrossValidatedDatasetParts:
    """Parse a CV fold directory basename into database and iteration string."""
    if "-iter" not in basename:
        raise ValueError(
            "CV fold basename must contain '-iter'; got {!r}".format(basename)
        )
    database, iteration = basename.split("-iter", 1)
    return CrossValidatedDatasetParts(database, iteration)


def _rank_names(rank_names=None):
    return tuple(DEFAULT_RANK_NAMES if rank_names is None else rank_names)


def check_rank_name(rank: str) -> str:
    """Return *rank* if it can be part of a fold name, else raise ``ValueError``.

    Novel-taxa fold names are ``<db>-<rank>-iter<n>``, so a rank name may hold
    only letters, digits, ``_`` and ``.`` -- no hyphen, slash or space.
    """
    rank = str(rank)
    if not _RANK_NAME_RE.match(rank):
        raise ValueError(
            "rank names used in novel-taxa fold names may contain only letters, "
            "digits, '_' and '.'; got {!r}".format(rank))
    return rank


def novel_level_rank(level: int, rank_names=None) -> str:
    """Name of the rank at *level* (index into *rank_names*; 6 = species)."""
    names = _rank_names(rank_names)
    level = int(level)
    if not 1 <= level < len(names):
        raise ValueError(
            "novel-taxa level must be 1..{0} ({1}); got {2}".format(
                len(names) - 1, ",".join(names), level))
    return check_rank_name(names[level])


def format_novel_fold_dirname(database: str, level: int, iteration: int,
                              rank_names=None) -> str:
    """Build novel-taxa fold name ``{db}-{rank}-iter{n}``.

    *level* indexes *rank_names* (default ``DEFAULT_RANK_NAMES``), so level 6
    gives ``<db>-species-iter<n>``.
    """
    rank = novel_level_rank(level, rank_names)
    return "{0}-{1}-iter{2}".format(database, rank, iteration)


def parse_novel_dataset_id(dataset_id: str, rank_names=None) -> NovelDatasetParts:
    """Parse ``dataset_id`` matching ``{database}-{rank}-iter{n}``.

    *database* may contain hyphens (e.g. ``B1-REF-species-iter0``); the rank
    is the segment before ``-iter<n>`` and must be one of *rank_names*
    (default ``DEFAULT_RANK_NAMES``) other than the first. Names written
    before folds were named by rank (``<db>-L6-iter0``) are rejected with a
    note to regenerate the datasets.
    """
    names = _rank_names(rank_names)
    m = _NOVEL_DATASET_ID_RE.match(dataset_id)
    level = None
    if m:
        lowered = [name.lower() for name in names]
        rank = m.group(2)
        if rank.lower() in lowered[1:]:
            level = lowered.index(rank.lower())
    if level is None:
        hint = ""
        if _LEGACY_NOVEL_DATASET_ID_RE.match(dataset_id):
            hint = (" Folds named by level number (-L6-) predate rank-named "
                    "folds; regenerate the novel-taxa datasets.")
        raise ValueError(
            "Novel-taxa dataset_id must match {{db}}-{{rank}}-iter{{n}} with a "
            "rank among {0}; got {1!r}.{2}".format(",".join(names[1:]),
                                                  dataset_id, hint))
    return NovelDatasetParts(m.group(1), names[level], level, m.group(3))


def parse_cv_dataset_id(dataset_id: str) -> CrossValidatedDatasetParts:
    """Parse a cross-validated *dataset_id* (``<db>-iter<n>``)."""
    return parse_cv_fold_dirname(dataset_id)


def parse_self_validated_dataset_id(dataset_id: str) -> SelfValidatedDatasetParts:
    """Parse a self-validated *dataset_id* (the reference database name)."""
    if "-iter" in dataset_id:
        raise ValueError(
            "Self-validated dataset_id must not contain '-iter'; got {!r}".format(
                dataset_id
            )
        )
    return SelfValidatedDatasetParts(dataset_id, "0")
