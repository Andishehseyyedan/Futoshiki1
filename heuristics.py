def select_unassigned_variable_mrv(csp):
    """
    Selects the unassigned variable with the minimum remaining values (MRV heuristic).
    If there's a tie, it can be broken arbitrarily (e.g., by the order they appear).
    """
    unassigned_vars = csp.board.get_unassigned_variables()
    if not unassigned_vars:
        return None

    min_domain_size = float('inf')
    best_var = None

    for var in unassigned_vars:
        domain_size = len(csp.board.domains[var])
        if domain_size < min_domain_size:
            min_domain_size = domain_size
            best_var = var
    return best_var


def order_domain_values_lcv(var, csp):
    """
    Orders the values in the domain of 'var' using the Least Constraining Value (LCV) heuristic.
    Values that rule out the fewest choices for neighboring unassigned variables are preferred.
    """
    domain = list(csp.board.domains[var])

    # Calculate the 'constraint count' for each value
    # A lower constraint count means the value is less constraining
    value_constraint_counts = []
    for value in domain:
        # Temporarily assign the value to evaluate its impact
        csp.board.assign(var, value)

        constraining_count = 0
        for neighbor in csp.board.get_neighbors(var):
            if csp.board.grid[neighbor[0]][neighbor[1]] == 0:  # If neighbor is unassigned
                # Count how many values in the neighbor's domain would be eliminated
                # if 'value' is assigned to 'var' and consistency is enforced.
                # This is a simplified LCV; a full LCV would run a light propagation
                # or check domain reductions for each neighbor if 'value' were chosen.
                # For Futoshiki, primarily it's about not eliminating future options for All-Different
                # and satisfying inequality.

                # Check for all-different impact on neighbor's domain
                if value in csp.board.domains[neighbor] and len(csp.board.domains[neighbor]) == 1:
                    # If this value is the only option for a neighbor, assigning it here
                    # would make the neighbor's domain empty. This value is highly constraining.
                    constraining_count += 100  # Give a high penalty

                # Check for inequality constraint impact
                for (v1, v2, op) in csp.board.inequality_constraints:
                    if (v1 == var and v2 == neighbor) or (v2 == var and v1 == neighbor):
                        # If assigning 'value' to 'var' makes a neighbor's domain empty,
                        # it's highly constraining.
                        temp_neighbor_domain = set(csp.board.domains[neighbor])
                        if (v1 == var and v2 == neighbor):  # var < neighbor or var > neighbor
                            if op == '<':  # var < neighbor => neighbor must be > value
                                temp_neighbor_domain = {x for x in temp_neighbor_domain if x > value}
                            elif op == '>':  # var > neighbor => neighbor must be < value
                                temp_neighbor_domain = {x for x in temp_neighbor_domain if x < value}
                        elif (v2 == var and v1 == neighbor):  # neighbor < var or neighbor > var
                            if op == '<':  # neighbor < var => neighbor must be < value
                                temp_neighbor_domain = {x for x in temp_neighbor_domain if x < value}
                            elif op == '>':  # neighbor > var => neighbor must be > value
                                temp_neighbor_domain = {x for x in temp_neighbor_domain if x > value}

                        if not temp_neighbor_domain:
                            constraining_count += 100  # High penalty for making a domain empty

        value_constraint_counts.append((value, constraining_count))

        # Unassign for the next iteration
        csp.board.unassign(var)  # This resets the grid value to 0, not fully restores the domain

    # Sort values by their constraint count (ascending)
    value_constraint_counts.sort(key=lambda x: x[1])
    return [value for value, _ in value_constraint_counts]