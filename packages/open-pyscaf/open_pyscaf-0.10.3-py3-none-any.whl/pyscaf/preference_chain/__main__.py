import os

from .dependency_loader import load_and_complete_dependencies
from .topologic_tree import best_execution_order
from .tree_walker import DependencyTreeWalker

# Utility to get direct dependants of a node
# Returns the list of RawDependency that directly depend on parent_id


def get_direct_dependants(dependencies, parent_id):
    """Return the list of RawDependency that directly depend on parent_id."""
    return [dep for dep in dependencies if dep.depends and parent_id in dep.depends]


# Utility to build a node for best_execution_order
# Uses DependencyTreeWalker to compute the fullfilled and external dependencies for a given node


def build_node(dep, dependencies):
    walker = DependencyTreeWalker(dependencies, dep.id)
    return {
        "id": dep.id,
        "fullfilled": list(walker.fullfilled_depends),
        "external": list(walker.external_depends),
    }


# Recursive function to build the optimal order
# For a given current_id, finds all direct dependants, orders them optimally,
# and recursively applies the same logic to each dependant.
# The result is a flattened list starting with current_id, followed by the optimal order of all subtrees.


def recursive_best_order(dependencies, current_id):
    direct_dependants = get_direct_dependants(dependencies, current_id)
    if not direct_dependants:
        return [current_id]
    nodes = [build_node(dep, dependencies) for dep in direct_dependants]
    local_order = best_execution_order(nodes)
    result = [current_id]
    for node_id in local_order:
        result.extend(recursive_best_order(dependencies, node_id))
    return result


if __name__ == "__main__":
    # Load and complete dependencies from YAML
    yaml_path = os.path.join(os.path.dirname(__file__), "dependencies.yaml")
    dependencies = load_and_complete_dependencies(yaml_path)
    # Recursive optimal order from 'root'
    order = recursive_best_order(dependencies, "root")
    print("Ordre optimal récursif :", order)
