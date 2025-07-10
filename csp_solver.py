import time
from collections import deque
from futoshiki_board import FutoshikiBoard
from heuristics import select_unassigned_variable_mrv, order_domain_values_lcv
from inference import forward_check, ac2


class CSPSolver:
    def __init__(self, board, use_forward_checking=False, use_ac2=False, use_mrv=False, use_lcv=False):
        self.board = board
        self.use_forward_checking = use_forward_checking
        self.use_ac2 = use_ac2
        self.use_mrv = use_mrv
        self.use_lcv = use_lcv
        self.backtracks = 0
        self.start_time = 0

    def solve(self):
        self.backtracks = 0
        self.start_time = time.time()

        # Pre-processing with AC-2 if enabled
        if self.use_ac2:
            print("Running initial AC-2 preprocessing...")
            if not ac2(self):
                print("Initial AC-2 detected inconsistency. No solution.")
                return False

        solution_found = self._backtracking_search()
        end_time = time.time()
        print(f"\nSolver finished in {end_time - self.start_time:.4f} seconds.")
        print(f"Total backtracks: {self.backtracks}")
        return solution_found

    def _backtracking_search(self):
        # Check if the assignment is complete
        if not self.board.get_unassigned_variables():
            return True

        # Variable selection
        if self.use_mrv:
            var = select_unassigned_variable_mrv(self)
        else:
            var = self.board.get_unassigned_variables()[0]  # Simple sequential selection

        # Value ordering
        if self.use_lcv:
            domain_values = order_domain_values_lcv(var, self)
        else:
            domain_values = list(self.board.domains[var])  # Get a copy to iterate

        # Try each value in the ordered domain
        for value in domain_values:
            # Check initial consistency (before assignment for fixed values or potential future checks)
            # This is implicitly handled by domain pruning and `_is_consistent` for direct constraints.

            # Make a deep copy of the current domains for backtracking
            original_domains_copy = {v: set(d) for v, d in self.board.domains.items()}
            original_grid_value = self.board.grid[var[0]][var[1]]  # Should be 0 for unassigned

            self.board.assign(var, value)

            if self.board.is_consistent(var, value):  # Check all types of constraints
                pruned = {}
                is_consistent_after_inference = True

                if self.use_forward_checking:
                    # Forward Checking returns pruned values if successful, or False if inconsistency
                    fc_result = forward_check(self, var, value)
                    if fc_result is False:
                        is_consistent_after_inference = False
                    else:
                        pruned = fc_result  # Store pruned values for restoration

                if is_consistent_after_inference and self.use_ac2:
                    # Run AC-2 after assignment and FC (if AC-2 is also enabled)
                    # AC-2 modifies domains directly, so we need to copy domains before it.
                    if not ac2(self):
                        is_consistent_after_inference = False

                if is_consistent_after_inference:
                    if self._backtracking_search():
                        return True

            # Backtrack: Restore the state
            self.backtracks += 1
            self.board.unassign(var)  # Resets grid value to 0 and initial domain set for 'var'
            self.board.domains = original_domains_copy  # Restore all domains to state before current assignment

        return False  # No value worked for this variable