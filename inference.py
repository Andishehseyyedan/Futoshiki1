from collections import deque


def forward_check(csp, var, value):
    """
    Performs forward checking after assigning 'value' to 'var'.
    Removes inconsistent values from the domains of unassigned neighboring variables.
    Returns True if consistent, False if any domain becomes empty.
    """
    r_var, c_var = var

    # Temporarily update the domain for 'var' for consistency checks
    original_domain = csp.board.domains[var]
    csp.board.domains[var] = {value}

    # Keep track of domain changes for backtracking
    pruned_values = {}

    for neighbor in csp.board.get_neighbors(var):
        if csp.board.grid[neighbor[0]][neighbor[1]] == 0:  # Only check unassigned neighbors
            r_neighbor, c_neighbor = neighbor
            original_neighbor_domain = set(csp.board.domains[neighbor])

            for val_n in list(csp.board.domains[neighbor]):  # Iterate over a copy as we modify
                # Check consistency if 'val_n' is assigned to 'neighbor'
                # and 'value' is assigned to 'var'.

                # Check All-Different constraint
                if val_n == value and (r_var == r_neighbor or c_var == c_neighbor):
                    csp.board.domains[neighbor].discard(val_n)

                # Check Inequality constraint
                is_inequality_involved = False
                for (v1, v2, op) in csp.board.inequality_constraints:
                    if (v1 == var and v2 == neighbor) or (v2 == var and v1 == neighbor):
                        is_inequality_involved = True

                        if (v1 == var and v2 == neighbor):  # var < neighbor or var > neighbor
                            if op == '<' and not (value < val_n):
                                csp.board.domains[neighbor].discard(val_n)
                            elif op == '>' and not (value > val_n):
                                csp.board.domains[neighbor].discard(val_n)
                        elif (v2 == var and v1 == neighbor):  # neighbor < var or neighbor > var
                            if op == '<' and not (val_n < value):
                                csp.board.domains[neighbor].discard(val_n)
                            elif op == '>' and not (val_n > value):
                                csp.board.domains[neighbor].discard(val_n)
                        break  # Only one inequality per pair of cells

            if not csp.board.domains[neighbor]:
                # Restore domains if an inconsistency is found
                csp.board.domains[var] = original_domain
                for p_var, p_vals in pruned_values.items():
                    csp.board.domains[p_var].update(p_vals)
                return False  # Domain became empty, backtrack

            pruned_values[neighbor] = original_neighbor_domain - csp.board.domains[neighbor]

    # Restore the original domain for 'var' if it wasn't a fixed value (already handled by assign)
    # The actual assignment in CSP is handled by `assign` method which changes the grid value
    # and sets the domain. Here, we just deal with temporary domain updates for consistency checks.
    csp.board.domains[var] = original_domain

    return pruned_values  # Return pruned values for backtracking


def revise(csp, xi, xj):
    """
    Revises the domain of xi relative to xj.
    Returns True if the domain of xi was changed, False otherwise.
    """
    revised = False
    to_remove = set()

    for x in csp.board.domains[xi]:
        # Assume x is assigned to xi. Is there any value y in D(xj)
        # such that the constraint between xi and xj is satisfied?
        consistent_found = False
        for y in csp.board.domains[xj]:
            # Temporarily assign x to xi and y to xj for checking consistency
            # This is a simplified check that only considers the binary constraint between xi and xj.
            # For Futoshiki, we need to consider both all-different and inequality.

            # Check All-Different (if same row/col)
            if xi[0] == xj[0] or xi[1] == xj[1]:
                if x == y:
                    continue  # Not consistent

            # Check Inequality
            is_inequality = False
            for (v1, v2, op) in csp.board.inequality_constraints:
                if (v1 == xi and v2 == xj):  # xi < xj or xi > xj
                    is_inequality = True
                    if op == '<' and (x < y):
                        consistent_found = True
                        break
                    elif op == '>' and (x > y):
                        consistent_found = True
                        break
                elif (v1 == xj and v2 == xi):  # xj < xi or xj > xi
                    is_inequality = True
                    if op == '<' and (y < x):
                        consistent_found = True
                        break
                    elif op == '>' and (y > x):
                        consistent_found = True
                        break

            if not is_inequality and (xi[0] != xj[0] and xi[1] != xj[1]):
                # If no inequality and not same row/col, any combination is fine (for binary check)
                consistent_found = True

            if is_inequality and consistent_found:  # Found a consistent y for x
                break
            elif not is_inequality and (xi[0] == xj[0] or xi[1] == xj[1]):  # All-Different case
                if x != y:  # If they are different, and no inequality applies, it's consistent.
                    consistent_found = True
                    break
            elif not is_inequality and not (xi[0] == xj[0] or xi[1] == xj[1]):  # No direct constraint
                consistent_found = True
                break

        if not consistent_found:
            to_remove.add(x)

    if to_remove:
        csp.board.domains[xi] = csp.board.domains[xi] - to_remove
        revised = True
    return revised


def ac2(csp):
    """
    Implements the AC-2 arc consistency algorithm.
    Propagates constraints throughout the CSP by repeatedly revising arcs.
    Returns True if arc consistency is achieved, False if any domain becomes empty.
    """
    queue = deque()

    # Initializing the queue with all binary constraints (arcs)
    variables = [(r, c) for r in range(csp.board.size) for c in range(csp.board.size)]
    for i in range(len(variables)):
        xi = variables[i]
        for j in range(i + 1, len(variables)):
            xj = variables[j]

            # Check if there's any direct constraint between xi and xj
            # This includes All-Different (same row/col) and inequality constraints

            is_constrained = False
            if xi[0] == xj[0] or xi[1] == xj[1]:  # Same row or same column
                is_constrained = True

            for (v1, v2, op) in csp.board.inequality_constraints:
                if (v1 == xi and v2 == xj) or (v1 == xj and v2 == xi):
                    is_constrained = True
                    break

            if is_constrained:
                queue.append((xi, xj))
                queue.append((xj, xi))  # Add reverse arc as well

    while queue:
        xi, xj = queue.popleft()
        if revise(csp, xi, xj):
            if not csp.board.domains[xi]:
                return False  # Domain empty, inconsistency detected
            for xk in csp.board.get_neighbors(xi):  # For each neighbor xk of xi
                if xk != xj:  # Except xj
                    queue.append((xk, xi))  # Add (xk, xi) to the queue
    return True