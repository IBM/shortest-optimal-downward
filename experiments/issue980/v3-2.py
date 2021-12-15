#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from lab.environments import LocalEnvironment, BaselSlurmEnvironment

import common_setup
from common_setup import IssueConfig, IssueExperiment
#from relativescatter import RelativeScatterPlotReport
from itertools import combinations

DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
# These revisions are all tag experimental branches off the same revision.
# we only need different tags so lab creates separate build directories in the build cache.
# We then manually recompile the code in the build cache with the correct settings.
REVISIONS = ["issue980v3"]
CONFIGS = [
    IssueConfig("shortesthd-ms", ["--search", "shortest_astar(merge_and_shrink(transform=no_transform(), cache_estimates=true, merge_strategy=merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),shrink_strategy=shrink_strategy=shrink_bisimulation(greedy=false), prune_unreachable_states=true, prune_irrelevant_states=true, max_states=-1, max_states_before_merge=-1, threshold_before_merge=-1, verbosity=normal, main_loop_max_time=infinity), d_eval=merge_and_shrink(transform=adapt_costs(cost_type=ONE), cache_estimates=true, merge_strategy=merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),shrink_strategy=shrink_strategy=shrink_bisimulation(greedy=false), prune_unreachable_states=true, prune_irrelevant_states=true, max_states=-1, max_states_before_merge=-1, threshold_before_merge=-1, verbosity=normal, main_loop_max_time=infinity), verbosity=silent)"]),
    IssueConfig("shortesthd-cegar", ["--search", "shortest_astar(cegar(), d_eval=cegar(transform=adapt_costs(cost_type=ONE)),verbosity=silent)"]),
    IssueConfig("shortesthd-hmax", ["--search", "shortest_astar(hmax(), d_eval=hmax(transform=adapt_costs(cost_type=ONE)),verbosity=silent)"]),
    IssueConfig("shortesthd-ipdb", ["--search", "shortest_astar(ipdb(pdb_max_size=2000000, collection_max_size=20000000, num_samples=1000, min_improvement=10, max_time=infinity, random_seed=-1, max_time_dominance_pruning=infinity, transform=no_transform(), cache_estimates=true), d_eval=ipdb(pdb_max_size=2000000, collection_max_size=20000000, num_samples=1000, min_improvement=10, max_time=infinity, random_seed=-1, max_time_dominance_pruning=infinity, transform=adapt_costs(cost_type=ONE), cache_estimates=true),verbosity=silent)"]),
]

# SUITE = ["agricola-opt18-strips", "barman-opt11-strips", "data-network-opt18-strips", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "ged-opt14-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "organic-synthesis-split-opt18-strips", "parcprinter-08-strips", "parcprinter-opt11-strips", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "tetris-opt14-strips", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips"]
SUITE = ["agricola-opt18-strips", "barman-opt11-strips", "data-network-opt18-strips", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "ged-opt14-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "organic-synthesis-split-opt18-strips", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "tetris-opt14-strips", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips"]
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
exp.add_parser("parser.py")

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_fetcher(name='fetch')

exp.add_fetcher('data/issue980-v3-eval')
exp.add_fetcher('/data/software/shortest-optimal-v2/experiments/issue980/data/issue980-v2-eval')


attributes = (
            IssueExperiment.DEFAULT_TABLE_ATTRIBUTES + ["plan_length", "fixed_cost", "fixed_initial_h_value"])
#exp.add_absolute_report_step(attributes=attributes)
#exp.add_comparison_table_step(attributes=attributes)




algs = []
nicks = ['lmcut', 'ms', 'cegar', 'hmax', 'ipdb']
for nick in nicks:
    algs.extend(["issue980v2-shortest-%s" % nick, "issue980v3-shortesthd-%s" % nick])

exp.add_absolute_report_step(attributes=attributes,filter_algorithm=algs, filter_domain=SUITE)

def make_scatter():

    attributes = ["expansions", "total_time"]
    pairs = [("issue980v2-shortest-%s" % nick, "issue980v3-shortesthd-%s" % nick) for nick in nicks]
    for algo1, algo2 in pairs:
        for attr in attributes:
            for rel in [True, False]:
                rel_str = "rel" if rel else "abs"
                report = ScatterPlotReport(
                        relative=rel,
                        get_category=lambda run1, run2: run1["domain"],
                        attributes=[attr],
                        filter_algorithm=[algo1, algo2],
                        filter=[add_evaluations_per_time, rename_algorithms],
                        filter_domain=NEW_SUITE,
                        format="tex",
                    )
                outfile = os.path.join(exp.eval_dir,f"{exp.name}-scatter-{rel_str}-{algo1}-vs-{algo2}-{attr}.tex")
                report(exp.eval_dir, outfile)

exp.add_step("make-scatter", make_scatter)

exp.run_steps()
