#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from lab.environments import LocalEnvironment, BaselSlurmEnvironment

import common_setup
from common_setup import IssueConfig, IssueExperiment
from downward.reports.scatter import ScatterPlotReport

# from relativescatter import RelativeScatterPlotReport
# from itertools import combinations

DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
# These revisions are all tag experimental branches off the same revision.
# we only need different tags so lab creates separate build directories in the build cache.
# We then manually recompile the code in the build cache with the correct settings.
REVISIONS = ["7a9dc9fd2f6ab01112f8f0b8c8bca26d371b1a1c"]
CONFIGS = [
    # IssueConfig("blind", ["--search", "astar(blind())"]),
    IssueConfig("blind", ["--search", "astar(blind())"]),
    IssueConfig("lmcut", ["--search", "astar(lmcut())"]),

    IssueConfig("ms", ["--search", "astar(merge_and_shrink(transform=no_transform(), cache_estimates=true, merge_strategy=merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),shrink_strategy=shrink_strategy=shrink_bisimulation(greedy=false), prune_unreachable_states=true, prune_irrelevant_states=true, max_states=-1, max_states_before_merge=-1, threshold_before_merge=-1, verbosity=normal, main_loop_max_time=infinity))"]),
    IssueConfig("cegar", ["--search", "astar(cegar())"]),
    IssueConfig("hmax", ["--search", "astar(hmax())"]),
    IssueConfig("ipdb", ["--search", "astar(ipdb(pdb_max_size=2000000, collection_max_size=20000000, num_samples=1000, min_improvement=10, max_time=infinity, random_seed=-1, max_time_dominance_pruning=infinity, transform=no_transform(), cache_estimates=true))"]),
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
exp.add_fetcher('data/issue980-v1-eval')
attributes = (
            IssueExperiment.DEFAULT_TABLE_ATTRIBUTES + ["plan_length", "reopened"])
exp.add_absolute_report_step(attributes=attributes)
#exp.add_comparison_table_step(attributes=attributes)


def make_comparison_table():
    alg_names = ["blind", "cegar", "hmax", "ipdb", "lmcut", "ms"]
    rev1 = "7a9dc9fd2f6ab01112f8f0b8c8bca26d371b1a1c"
    rev2 = "issue980v2-shortest"
    pairs = [ ("%s-%s" % (rev1, nick), "%s-%s" % (rev2, nick)) for nick in alg_names]
    print(pairs)

    report = common_setup.ComparativeReport(
        algorithm_pairs=pairs, attributes=attributes,
    )
    outfile = os.path.join(
        exp.eval_dir, "%s-compare.%s" % (exp.name, report.output_format)
    )
    report(exp.eval_dir, outfile)

    exp.add_report(report)

exp.add_step("comparison table", make_comparison_table)

#exp.add_comparison_table_step()

#exp.add_scatter_plot_step(attributes=['search_time'])
#exp.add_scatter_plot_step(attributes=['search_time'], relative=True)



def make_scatter():
    alg_names = ["blind", "cegar", "hmax", "ipdb", "lmcut", "ms"]
    attributes = ['search_time', "plan_length"]
    rev1 = "7a9dc9fd2f6ab01112f8f0b8c8bca26d371b1a1c"
    rev2 = "issue980v2-shortest"
    for nick in alg_names:

        algo1 = "%s-%s" % (rev1, nick)
        algo2 = "%s-%s" % (rev2, nick)

        for attr in attributes:        
            report = ScatterPlotReport(
                    filter_algorithm=[algo1, algo2],
                    attributes=[attr],
                    relative=True,
                    get_category=lambda run1, run2: run1["domain"])

            outfile = os.path.join(
                exp.eval_dir, "%s-scatter-%s.%s" % (exp.name, attr, report.output_format)
            )
            report(exp.eval_dir, outfile)
            exp.add_report(report)

exp.add_step("Scatter plots", make_scatter)

# attrs = ["total_time", "reopened", "memory", "expansions", "expansions_until_last_jump"]
# for attr in attrs:
#     for nick in alg_names:
#         exp.add_report(RelativeScatterPlotReport(
#                     attributes=attr,
#                                 filter_algorithm=["%s-%s" % (r, nick) for r in [rev1, rev2]],
#                                             get_category=lambda run1, run2: run1["domain"]),
#                                                         outfile="issue980-base-%s-%s-%s-%s.png" % (attr, r1, r2, nick))

exp.run_steps()
