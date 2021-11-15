#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from lab.environments import LocalEnvironment, BaselSlurmEnvironment
from downward.reports.compare import ComparativeReport
from downward.reports.scatter import ScatterPlotReport

import common_setup
from common_setup import IssueConfig, IssueExperiment
# from relativescatter import RelativeScatterPlotReport
from itertools import combinations

DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
# These revisions are all tag experimental branches off the same revision.
# we only need different tags so lab creates separate build directories in the build cache.
# We then manually recompile the code in the build cache with the correct settings.
OLD_REVISION = ["issue980v2"]
REVISIONS = ["shortest-optimal-cost-transformation"]
CONFIGS = [
    IssueConfig("wct-blind", ["--search", "astar(weight(blind(transform=transform_costs_back()),10000),verbosity=silent)"]),
    IssueConfig("wct-lmcut", ["--search", "astar(weight(lmcut(transform=transform_costs_back()),10000),verbosity=silent)"]),

    IssueConfig("wct-ms", ["--search", "astar(weight(merge_and_shrink(transform=transform_costs_back(), cache_estimates=true, merge_strategy=merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),shrink_strategy=shrink_strategy=shrink_bisimulation(greedy=false), prune_unreachable_states=true, prune_irrelevant_states=true, max_states=-1, max_states_before_merge=-1, threshold_before_merge=-1, verbosity=normal, main_loop_max_time=infinity),10000),verbosity=silent)"]),
    IssueConfig("wct-cegar", ["--search", "astar(weight(cegar(transform=transform_costs_back()),10000),verbosity=silent)"]),
    IssueConfig("wct-hmax", ["--search", "astar(weight(hmax(transform=transform_costs_back()),10000),verbosity=silent)"]),
    IssueConfig("wct-ipdb", ["--search", "astar(weight(ipdb(transform=transform_costs_back(), pdb_max_size=2000000, collection_max_size=20000000, num_samples=1000, min_improvement=10, max_time=infinity, random_seed=-1, max_time_dominance_pruning=infinity, cache_estimates=true),10000),verbosity=silent)"]),
]

SUITE = ["agricola-opt18-strips", "barman-opt11-strips", "data-network-opt18-strips", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "ged-opt14-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "organic-synthesis-split-opt18-strips", "parcprinter-08-strips", "parcprinter-opt11-strips", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "tetris-opt14-strips", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips"]
# SUITE = ["elevators-opt08-strips:p01.pddl"]

ENVIRONMENT = LocalEnvironment(processes=48)

exp = IssueExperiment(
    revisions=REVISIONS,
    configs=CONFIGS,
    environment=ENVIRONMENT)
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(exp.PLANNER_PARSER)
exp.add_parser("wct_parser.py")

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_fetcher(name='fetch')

exp.add_fetcher('data/issue980-v2-eval')
exp.add_fetcher('data/v3_2-eval')
exp.add_fetcher('data/v5-eval')

attributes = (
            IssueExperiment.DEFAULT_TABLE_ATTRIBUTES + ["plan_length", "fixed_cost", "fixed_initial_h_value"])
#exp.add_comparison_table_step(attributes=attributes)
# exp.add_absolute_report_step(attributes=attributes)

def rename_algorithms(run):
    run["algorithm"] = run["algorithm"].replace("issue980v2-","").replace("shortest-optimal-cost-transformation-","")
    return run
# nicks = ["shortest-blind", "shortest-lmcut", "shortest-ms", "shortest-cegar", "shortest-hmax", "shortest-ipdb"]
nicks = ["blind", "lmcut", "ms", "cegar", "hmax", "ipdb"]

# algs = ["%s-ct-%s" % (r, nick) for r in REVISIONS for nick in nicks ]
# algs.extend(["c292531fa6cdbeae95a0bf576fd50a65967ed5cc-shortest-%s" % nick for nick in nicks ])

NEW_SUITE = [x for x in SUITE if "parcprinter" not in x]

algs = []
for nick in nicks:
    algs.extend(["ct-%s" % nick, "wct-%s" % nick, "shortest-%s" % nick])
    

exp.add_absolute_report_step(attributes=attributes, filter=rename_algorithms, filter_algorithm=algs, filter_domain=NEW_SUITE)

def make_comparison_tables():
    compared_configs = [("wct-%s" % nick, "shortest-%s" % nick, "Diff (%s)" % nick) for nick in nicks]

    report = ComparativeReport(compared_configs, attributes=attributes, filter=rename_algorithms, filter_domain=NEW_SUITE)
    outfile = os.path.join(
                    exp.eval_dir,
                    "%s-compare-no-parcprinter-wct-deval.%s" % (
                        exp.name, report.output_format))
    report(exp.eval_dir, outfile)

    compared_configs = [("ct-%s" % nick, "wct-%s" % nick, "Diff (%s)" % nick) for nick in nicks]
    report = ComparativeReport(compared_configs, attributes=attributes, filter=rename_algorithms, filter_domain=NEW_SUITE)
    outfile = os.path.join(
                    exp.eval_dir,
                    "%s-compare-no-parcprinter-ct-wct.%s" % (
                        exp.name, report.output_format))
    report(exp.eval_dir, outfile)


exp.add_step("make-comparison-tables", make_comparison_tables)

def make_scatter():
    def add_evaluations_per_time(run):
        evaluations = run.get("evaluations")
        time = run.get("search_time")
        if evaluations is not None and evaluations >= 100 and time:
            run["evaluations_per_time"] = evaluations / time
        return run

    attributes = ["evaluations_per_time", "expansions"]
    pairs = [("ct-lmcut", "wct-lmcut")]
    for algo1, algo2 in pairs:
        for attr in attributes:
            report = ScatterPlotReport(
                    relative=True,
                    get_category=lambda run1, run2: run1["domain"],
                    attributes=[attr],
                    filter_algorithm=[algo1, algo2],
                    filter=[add_evaluations_per_time, rename_algorithms],
                    filter_domain=NEW_SUITE,
                    format="tex",
                )
            outfile = os.path.join(exp.eval_dir,f"{exp.name}-scatter-{algo1}-vs-{algo2}-{attr}.tex")
            report(exp.eval_dir, outfile)

exp.add_step("make-scatter", make_scatter)

exp.run_steps()
