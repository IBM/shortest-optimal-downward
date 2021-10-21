#include "cost_transformed_shortest_task.h"

#include "../operator_cost.h"
#include "../option_parser.h"
#include "../plugin.h"

#include "../task_utils/task_properties.h"
#include "../tasks/root_task.h"
#include "../utils/system.h"

#include <iostream>
#include <memory>

using namespace std;
using utils::ExitCode;

namespace tasks {
CostTransformedShortestTask::CostTransformedShortestTask(
    const shared_ptr<AbstractTask> &parent)
    : DelegatingTask(parent),
      parent_is_unit_cost(task_properties::is_unit_cost(TaskProxy(*parent))) {
}

int CostTransformedShortestTask::get_operator_cost(int index, bool is_axiom) const {
    int cost = parent->get_operator_cost(index, is_axiom);
    if (parent_is_unit_cost || is_axiom) {
        return cost;
    }
    return (cost - 1) / COST_MULTIPLIER;     
}


static shared_ptr<AbstractTask> _parse(OptionParser &parser) {
    parser.document_synopsis(
        "Cost-transformed task",
        "A cost transformation of the root task back to the original cost.");
    Options opts = parser.parse();
    if (parser.dry_run()) {
        return nullptr;
    } else {
        return make_shared<CostTransformedShortestTask>(g_root_task);
    }
}

static Plugin<AbstractTask> _plugin("transform_costs_back", _parse);
}
