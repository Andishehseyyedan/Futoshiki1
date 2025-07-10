class FutoshikiBoard:
    def __init__(self, size, initial_grid=None, inequality_constraints=None):
        self.size = size
        self.grid = initial_grid if initial_grid else [[0 for _ in range(size)] for _ in range(size)]
        self.domains = {}
        for r in range(size):
            for c in range(size):
                if self.grid[r][c] == 0:
                    self.domains[(r, c)] = set(range(1, size + 1))
                else:
                    self.domains[(r, c)] = {self.grid[r][c]}

        self.inequality_constraints = inequality_constraints if inequality_constraints else []
        self._prune_initial_domains()

    def _prune_initial_domains(self):
        """Prune domains based on initial fixed values."""
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != 0:
                    self._enforce_all_different_constraints((r, c), self.grid[r][c])

    def assign(self, var, value):
        """Assigns a value to a variable and updates its domain."""
        r, c = var
        self.grid[r][c] = value
        self.domains[var] = {value}

    def unassign(self, var):
        """Unassigns a variable and restores its initial domain."""
        r, c = var
        self.grid[r][c] = 0
        # Re-initialize domain for unassigned variable
        self.domains[var] = set(range(1, self.size + 1))
        # Note: For backtracking, actual domain restoration after inference will be handled by the CSP solver.
        # This unassign only resets the grid value and initial domain set for consistency.

    def get_unassigned_variables(self):
        """Returns a list of unassigned variables."""
        unassigned = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    unassigned.append((r, c))
        return unassigned

    def is_consistent(self, var, value):
        """Checks if assigning 'value' to 'var' is consistent with all constraints."""
        r, c = var

        # All-Different constraint for row
        for col in range(self.size):
            if col != c and self.grid[r][col] == value:
                return False

        # All-Different constraint for column
        for row in range(self.size):
            if row != r and self.grid[row][c] == value:
                return False

        # Inequality constraints
        for (r1, c1), (r2, c2), op in self.inequality_constraints:
            val1 = self.grid[r1][c1]
            val2 = self.grid[r2][c2]

            # If the current assignment completes an inequality constraint
            if (r1, c1) == var and val2 != 0:
                if op == '<' and not (value < val2):
                    return False
                if op == '>' and not (value > val2):
                    return False
            elif (r2, c2) == var and val1 != 0:
                if op == '<' and not (val1 < value):
                    return False
                if op == '>' and not (val1 > value):
                    return False
            # If both are assigned (and not the current var), check existing consistency
            elif val1 != 0 and val2 != 0 and ((r1,c1) != var and (r2,c2) != var):
                if op == '<' and not (val1 < val2):
                    return False
                if op == '>' and not (val1 > val2):
                    return False
        return True

    def _enforce_all_different_constraints(self, fixed_var, fixed_value):
        """
        Helper to prune domains of other cells in the same row/column
        when a cell is initially fixed.
        """
        r, c = fixed_var
        for col in range(self.size):
            if col != c and fixed_value in self.domains.get((r, col), set()):
                self.domains[(r, col)].discard(fixed_value)
        for row in range(self.size):
            if row != r and fixed_value in self.domains.get((row, c), set()):
                self.domains[(row, c)].discard(fixed_value)


    def get_neighbors(self, var):
        """Returns neighboring variables based on all-different and inequality constraints."""
        r, c = var
        neighbors = set()

        # All-Different neighbors (row and column)
        for col in range(self.size):
            if col != c:
                neighbors.add((r, col))
        for row in range(self.size):
            if row != r:
                neighbors.add((row, c))

        # Inequality neighbors
        for (r1, c1), (r2, c2), _ in self.inequality_constraints:
            if (r1, c1) == var:
                neighbors.add((r2, c2))
            elif (r2, c2) == var:
                neighbors.add((r1, c1))
        return list(neighbors)

    def display(self):
        """Prints the current state of the board."""
        for r in range(self.size):
            row_str = ""
            for c in range(self.size):
                row_str += str(self.grid[r][c] if self.grid[r][c] != 0 else '_') + " "
                if c < self.size - 1:
                    # Check for horizontal inequality
                    for (r1,c1),(r2,c2),op in self.inequality_constraints:
                        if (r1,c1) == (r,c) and (r2,c2) == (r,c+1):
                            row_str += op + " "
                            break
                        elif (r1,c1) == (r,c+1) and (r2,c2) == (r,c):
                            row_str += ('<' if op == '>' else '>') + " " # Reverse operator
                            break
                    else:
                        row_str += "| " # Just a separator
            print(row_str)
            if r < self.size - 1:
                col_sep_str = ""
                for c in range(self.size):
                    # Check for vertical inequality
                    for (r1,c1),(r2,c2),op in self.inequality_constraints:
                        if (r1,c1) == (r,c) and (r2,c2) == (r+1,c):
                            col_sep_str += "  " + op + " "
                            break
                        elif (r1,c1) == (r+1,c) and (r2,c2) == (r,c):
                            col_sep_str += "  " + ('<' if op == '>' else '>') + " " # Reverse operator
                            break
                    else:
                        col_sep_str += "  - " # Just a separator
                print(col_sep_str)
        print("\n")