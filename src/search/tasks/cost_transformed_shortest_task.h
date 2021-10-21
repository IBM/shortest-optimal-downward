#ifndef TASKS_COST_TRANSFORMED_SHORTEST_TASK_H
#define TASKS_COST_TRANSFORMED_SHORTEST_TASK_H

#include "delegating_task.h"

#include "../operator_cost.h"

namespace options {
class Options;
}

namespace tasks {
/*
  Task transformation that changes transformed operator costs back.
  The transformation in the input is 
  c -> c*N + 1

  The transformation back is 
  c -> (c-1)/N

  Regardless of the cost_type value, axioms will always keep their original
  cost, which is 0 by default.
*/
class CostTransformedShortestTask : public DelegatingTask {
    const bool parent_is_unit_cost;
public:
    CostTransformedShortestTask(
        const std::shared_ptr<AbstractTask> &parent);
    virtual ~CostTransformedShortestTask() override = default;

    virtual int get_operator_cost(int index, bool is_axiom) const override;
};
}

#endif
