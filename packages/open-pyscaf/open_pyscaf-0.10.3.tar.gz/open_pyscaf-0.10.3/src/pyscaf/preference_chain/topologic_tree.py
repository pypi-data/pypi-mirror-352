def best_execution_order(nodes):
    # Compute reverse dependencies: who depends on what
    external_map = {node["id"]: set(node.get("external", [])) for node in nodes}

    # Initialize sets to track satisfied and executed nodes, and the final order
    satisfied = set()
    executed = set()
    execution_order = []
    violations = []

    # Main loop: keep executing nodes until all are done
    while len(executed) < len(nodes):
        candidates = []
        for node in nodes:
            node_id = node["id"]
            if node_id in executed:
                continue
            # A candidate is a node whose external dependencies are all satisfied
            if all(dep in satisfied for dep in external_map[node_id]):
                candidates.append(node)

        if not candidates:
            # If no candidate is found, there is a cycle or unsatisfiable dependency
            # Pick the first remaining node (stable order) and record a violation
            remaining = sorted(
                [node for node in nodes if node["id"] not in executed],
                key=lambda n: n["id"],
            )
            chosen = remaining[0]
            violations.append(chosen["id"])
        else:
            # Greedy: choose the candidate that contributes the most new fulfilled dependencies
            chosen = max(
                candidates, key=lambda node: len(set(node["fullfilled"]) - satisfied)
            )

        # Update the execution order and mark the node as executed
        execution_order.append(chosen["id"])
        satisfied.update(chosen["fullfilled"])
        executed.add(chosen["id"])

    if violations:
        print(f"Warning: Circular or unsatisfiable dependencies for: {violations}")

    return execution_order
