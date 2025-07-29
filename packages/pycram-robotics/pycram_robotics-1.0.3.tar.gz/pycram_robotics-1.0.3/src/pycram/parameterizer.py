import copy
import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Type, List

import numpy as np
from probabilistic_model.probabilistic_circuit.nx.helper import fully_factorized
from probabilistic_model.probabilistic_circuit.nx.probabilistic_circuit import ProbabilisticCircuit
from probabilistic_model.probabilistic_model import ProbabilisticModel
from random_events.product_algebra import Event, SimpleEvent
from random_events.set import Set
from random_events.variable import Symbolic, Integer, Variable, Continuous

from .datastructures.partial_designator import PartialDesignator
from .language import SequentialPlan
from .plan import Plan, DesignatorNode, ActionNode


@dataclass
class Parameterizer:
    """
    Class that generates possible parameters for a plan.

    This class can be used to generate possible parameters for a plan from probability distributions.
    """

    plan: Plan
    """
    The plan to generate the parameters for.
    """

    parameters: Dict[DesignatorNode, Any] = field(default_factory=dict, init=False)
    """
    A dictionary that maps all nodes in the plan that hold actions to their parameters.
    """

    variables_of_node: Dict[DesignatorNode, List[Variable]] = field(default_factory=dict, init=False)
    """
    A dictionary that maps all nodes in the plan that hold actions to the variables that describe that nodes parameters.
    """

    def __post_init__(self):
        self.make_parameters()
        self.make_variables()

    @property
    def variables(self) -> List[Variable]:
        """
        :return: The variables for all parameters in the plan.
        """
        return list(itertools.chain.from_iterable(self.variables_of_node.values()))

    def get_variable(self, name: str) -> Variable:
        """
        :param name: The name of the variable.
        :return: The variable.
        """
        return [v for v  in self.variables if v.name == name][0]

    def make_parameters(self):
        """
        Create the parameters for all relevant nodes in the plan.
        """
        for node in self.plan.nodes:
            if isinstance(node, DesignatorNode):
                self.parameters[node] = node.action._parameters

    def make_variables(self):
        """
        Create the variables for all relevant parameters in the plan.
        """
        for index, (node, params) in enumerate(self.parameters.items()):
            variables = []
            for name, leaf_type in node.flattened_parameters().items():
                full_name = f"{node.action.__name__}_{index}.{name}"
                variable = leaf_type_to_variable(full_name, leaf_type)
                variables.append(variable)
            self.variables_of_node[node] = variables


    def plan_from_sample(self, model: ProbabilisticModel, sample: np.array) -> Plan:
        """
        Create a sequential plan from a sample of all parameters.

        :param model: The model that generated the sample.
        :param sample: The sample to generate the plan from.
        :return: The executable, sequential plan
        """
        sub_plans = []

        for node in self.variables_of_node:
            flattened_parameters = []
            for variable in self.variables_of_node[node]:
                flattened_parameters.append(sample[model.variables.index(variable)])
            resolved = node.action.reconstruct(flattened_parameters)

            kwargs = {key: getattr(resolved, key) for key in resolved._parameters}
            sub_plans.append(Plan(ActionNode(designator_ref=PartialDesignator(node.action, **kwargs),
                       action = node.action, kwargs=kwargs)))

        return SequentialPlan(*sub_plans)

    def create_fully_factorized_distribution(self) -> ProbabilisticCircuit:
        """
        :return: a fully factorized distribution for the plan.
        """
        distribution = fully_factorized(self.variables, means={v: 0 for v in self.variables},
                                        variances={v: 1 for v in self.variables})
        return distribution

    def create_restrictions(self) -> SimpleEvent:
        """
        :return: The restrictions present in the plan as random event.
        """
        restrictions = {}
        for index, (node, variables) in enumerate(self.variables_of_node.items()):
            for variable in variables:
                parameter_name = variable.name.split(".", 1)[1]
                restriction = node.kwargs.get(parameter_name, None)

                if restriction is None:
                    continue

                restrictions[variable] = restriction

        # create the restrictions as random event
        result = SimpleEvent(restrictions)
        result.fill_missing_variables(self.variables)
        return result


def leaf_type_to_variable(name: str, leaf_type: Type) -> Variable:
    """
    Convert a leaf type to a random events variable.
    :param name: The name of the variable.
    :param leaf_type: The leaf type.
    :return: The variable.
    """
    if issubclass(leaf_type, bool):
        return Symbolic(name, Set.from_iterable([True, False]))
    elif issubclass(leaf_type, Enum):
        return Symbolic(name, Set.from_iterable(leaf_type))
    elif issubclass(leaf_type, int):
        return Integer(name)
    elif issubclass(leaf_type, float):
        return Continuous(name)
    else:
        raise NotImplementedError(f"No conversion between {leaf_type} and random_events.Variable is known.")
