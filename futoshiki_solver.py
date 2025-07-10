from futoshiki_board import FutoshikiBoard
from csp_solver import CSPSolver
import copy
import time
import matplotlib.pyplot as plt  # Import matplotlib


# No longer needed:
# def parse_input():
#     ...

def run_solver(board_config, solver_type="optimized"):
    """
    Initializes and runs the CSP solver based on the specified type.
    """
    size, initial_grid, inequality_constraints = board_config

    # Create a deep copy of the initial grid and constraints for each solver run
    # to ensure they start from the same fresh state.
    board_copy = FutoshikiBoard(size,
                                initial_grid=copy.deepcopy(initial_grid),
                                inequality_constraints=copy.deepcopy(inequality_constraints))

    print(f"\n--- Running {solver_type.upper()} Solver ---")
    print("Initial Board:")
    board_copy.display()

    if solver_type == "simple":
        solver = CSPSolver(board_copy)
    elif solver_type == "optimized":
        solver = CSPSolver(board_copy, use_forward_checking=True, use_ac2=True, use_mrv=True, use_lcv=True)
    else:
        raise ValueError("Invalid solver type. Choose 'simple' or 'optimized'.")

    solution_found = solver.solve()

    if solution_found:
        print("\nSolution Found:")
        board_copy.display()
    else:
        print("\nNo solution exists for this puzzle.")

    # Return backtrack count and elapsed time
    return solver.backtracks, (time.time() - solver.start_time)


# در تابع plot_results
def plot_results(puzzle_name, results):
    """
    Plots the comparison results for a given puzzle.
    """
    labels = ['Simple', 'Optimized']
    times = [results['simple']['time'], results['optimized']['time']]
    backtracks = [results['simple']['backtracks'], results['optimized']['backtracks']]

    x = range(len(labels))

    # تغییر figsize به (14, 6) یا حتی بزرگتر
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Performance Comparison for {puzzle_name}', fontsize=14) # می توانید fontsize را برای عنوان اصلی هم تنظیم کنید

    # Plot for Time
    ax1.bar(x, times, color=['skyblue', 'lightcoral'])
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Solving Time')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    for i, v in enumerate(times):
        ax1.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom', fontsize=9) # fontsize را کمی کاهش دهید

    # Plot for Backtracks
    ax2.bar(x, backtracks, color=['lightgreen', 'salmon'])
    ax2.set_ylabel('Number of Backtracks')
    ax2.set_title('Total Backtracks')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    for i, v in enumerate(backtracks):
        ax2.text(i, v + 0.01, f'{int(v)}', ha='center', va='bottom', fontsize=9) # fontsize را کمی کاهش دهید

    # حذف پارامتر rect یا تنظیم دقیق‌تر آن در صورت نیاز
    plt.tight_layout()
    # اگر هنوز هم عنوان اصلی همپوشانی دارد، می توانید از این استفاده کنید:
    # plt.tight_layout(rect=[0, 0, 1, 0.95]) # اگر عنوان کلی بالا باشد، 0.95 می تواند مناسب باشد

    plt.show()

if __name__ == "__main__":
    # Define a sample Futoshiki puzzle (e.g., the one from your image)

    # From image_e5203b.png (مثال):
    # Size: 5x5 (based on the image structure)

    # Initial grid (assuming '3', '5', '2' are fixed, others are 0)
    example_initial_grid = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 3, 0, 5],
        [2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    # Inequality constraints from image_e5203b.png (مثال):
    example_inequality_constraints = [
        # Horizontal constraints
        ((0, 0), (0, 1), '>'),
        ((1, 1), (1, 2), '<'),
        ((1, 2), (1, 3), '>'),
        ((1, 3), (1, 4), '<'),
        ((3, 3), (3, 4), '>'),

        # Vertical constraints (using (r1,c1) > (r2,c2) for V or (r1,c1) < (r2,c2) for ^)
        ((1, 1), (2, 1), '>'),  # V means greater than
        ((3, 1), (4, 1), '>'),  # V means greater than
        ((3, 4), (4, 4), '>'),  # V means greater than
        ((0, 3), (1, 3), '<'),  # ^ means less than
    ]

    puzzle_1_config = (5, example_initial_grid, example_inequality_constraints)

    # You can define more puzzles here as `puzzle_2_config`, `puzzle_3_config`, etc.
    # For example, a smaller 4x4 puzzle:
    puzzle_2_initial_grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    puzzle_2_inequality_constraints = [
        ((0, 0), (0, 1), '<'),
        ((1, 0), (1, 1), '>'),
        ((0, 0), (1, 0), '>'),
        ((2, 1), (3, 1), '<'),
        ((0, 2), (0, 3), '>'),
        ((1, 2), (2, 2), '<'),
        ((3, 0), (3, 1), '<'),
        ((1, 3), (2, 3), '>'),
    ]
    puzzle_2_config = (4, puzzle_2_initial_grid, puzzle_2_inequality_constraints)

    puzzles_to_solve = {
        "Example Puzzle 1 (5x5)": puzzle_1_config,
        "Small Puzzle 2 (4x4)": puzzle_2_config,  # Added a second puzzle for better comparison
    }

    results_data = {}  # Store results for plotting

    for puzzle_name, config in puzzles_to_solve.items():
        print(f"\n===== Solving: {puzzle_name} =====")

        # Run Simple Solver
        simple_backtracks, simple_time = run_solver(config, "simple")

        # Run Optimized Solver
        optimized_backtracks, optimized_time = run_solver(config, "optimized")

        results_data[puzzle_name] = {
            "simple": {"backtracks": simple_backtracks, "time": simple_time},
            "optimized": {"backtracks": optimized_backtracks, "time": optimized_time}
        }

    print("\n\n--- Overall Performance Comparison ---")
    for puzzle_name, res in results_data.items():
        print(f"\n--- Results for: {puzzle_name} ---")
        print(f"{'Solver Type':<15} | {'Time (s)':<10} | {'Backtracks':<12}")
        print(f"{'-' * 15} | {'-' * 10} | {'-' * 12}")
        print(f"{'Simple':<15} | {res['simple']['time']:<10.4f} | {res['simple']['backtracks']:<12}")
        print(f"{'Optimized':<15} | {res['optimized']['time']:<10.4f} | {res['optimized']['backtracks']:<12}")

        if res['optimized']['time'] < res['simple']['time']:
            print("The Optimized solver was faster!")
        elif res['optimized']['time'] > res['simple']['time']:
            print("The Simple solver was faster (unlikely for complex puzzles).")
        else:
            print("Both solvers took approximately the same time.")

        if res['optimized']['backtracks'] < res['simple']['backtracks']:
            print("The Optimized solver performed fewer backtracks.")
        elif res['optimized']['backtracks'] > res['simple']['backtracks']:
            print("The Simple solver performed more backtracks (unlikely).")
        else:
            print("Both solvers performed the same number of backtracks.")

        # Plot the results for the current puzzle
        plot_results(puzzle_name, res)