#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from lab.environments import LocalEnvironment, BaselSlurmEnvironment
from downward.reports.compare import ComparativeReport

import common_setup
from common_setup import IssueConfig, IssueExperiment
#from relativescatter import RelativeScatterPlotReport
from itertools import combinations

DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
# These revisions are all tag experimental branches off the same revision.
# we only need different tags so lab creates separate build directories in the build cache.
# We then manually recompile the code in the build cache with the correct settings.
REVISIONS = ["shortest-optimal-cost-transformation"]
CONFIGS = [
    # IssueConfig("blind", ["--search", "astar(blind())"]),
    IssueConfig("ct-blind", ["--search", "astar(blind())"]),
    IssueConfig("ct-lmcut", ["--search", "astar(lmcut())"]),

    IssueConfig("ct-ms", ["--search", "astar(merge_and_shrink(transform=no_transform(), cache_estimates=true, merge_strategy=merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),shrink_strategy=shrink_strategy=shrink_bisimulation(greedy=false), prune_unreachable_states=true, prune_irrelevant_states=true, max_states=-1, max_states_before_merge=-1, threshold_before_merge=-1, verbosity=normal, main_loop_max_time=infinity))"]),
    IssueConfig("ct-cegar", ["--search", "astar(cegar())"]),
    IssueConfig("ct-hmax", ["--search", "astar(hmax())"]),
    IssueConfig("ct-ipdb", ["--search", "astar(ipdb(pdb_max_size=2000000, collection_max_size=20000000, num_samples=1000, min_improvement=10, max_time=infinity, random_seed=-1, max_time_dominance_pruning=infinity, transform=no_transform(), cache_estimates=true))"]),
]

SUITE = ["agricola-opt18-strips", "barman-opt11-strips", "data-network-opt18-strips", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "ged-opt14-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "organic-synthesis-split-opt18-strips", "parcprinter-08-strips", "parcprinter-opt11-strips", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "tetris-opt14-strips", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips"]
# SUITE = ["elevators-opt08-strips:p01.pddl"]

ENVIRONMENT = LocalEnvironment(processes=48)

exp = IssueExperiment(
    revisions=REVISIONS,
    configs=CONFIGS,
    environment=ENVIRONMENT,
)
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(exp.PLANNER_PARSER)

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_fetcher(name='fetch')

exp.add_fetcher('/data/software/shortest-structural-symmetries-pruning/experiments/issue980/data/issue980-v5-DEval-all-eval')

attributes = (
            IssueExperiment.DEFAULT_TABLE_ATTRIBUTES + ["plan_length"])
#exp.add_comparison_table_step(attributes=attributes)
# exp.add_absolute_report_step(attributes=attributes)

def rename_algorithms(run):
    run["algorithm"] = run["algorithm"].replace("c292531fa6cdbeae95a0bf576fd50a65967ed5cc-","").replace("shortest-optimal-cost-transformation-","")
    return run
# nicks = ["shortest-blind", "shortest-lmcut", "shortest-ms", "shortest-cegar", "shortest-hmax", "shortest-ipdb"]
nicks = ["blind", "lmcut", "ms", "cegar", "hmax", "ipdb"]

# algs = ["%s-ct-%s" % (r, nick) for r in REVISIONS for nick in nicks ]
# algs.extend(["c292531fa6cdbeae95a0bf576fd50a65967ed5cc-shortest-%s" % nick for nick in nicks ])

algs = []
for nick in nicks:
    algs.extend(["ct-%s" % nick, "shortest-%s" % nick])



exp.add_absolute_report_step(attributes=attributes, filter=rename_algorithms, filter_algorithm=algs)

def make_comparison_tables():
    compared_configs = [("ct-%s" % nick, "shortest-%s" % nick, "Diff (%s)" % nick) for nick in nicks]

    report = ComparativeReport(compared_configs, attributes=attributes, filter=rename_algorithms)
    outfile = os.path.join(
                    exp.eval_dir,
                    "%s-compare.%s" % (
                        exp.name, report.output_format))
    report(exp.eval_dir, outfile)

exp.add_step("make-comparison-tables", make_comparison_tables)

# exp.add_comparison_table_step(attributes=attributes, filter=rename_algorithms, algorithm_pairs=pairs, revisions=["ct", "shortest"])


#exp.add_comparison_table_step()
"""
for r1, r2 in combinations(REVISIONS, 2):
    for nick in ["opcount-seq-lmcut", "diverse-potentials", "optimal-lmcount"]:
        exp.add_report(RelativeScatterPlotReport(
            attributes=["total_time"],
            filter_algorithm=["%s-%s" % (r, nick) for r in [r1, r2]],
            get_category=lambda run1, run2: run1["domain"]),
            outfile="issue925-v1-total-time-%s-%s-%s.png" % (r1, r2, nick))
"""
exp.run_steps()
