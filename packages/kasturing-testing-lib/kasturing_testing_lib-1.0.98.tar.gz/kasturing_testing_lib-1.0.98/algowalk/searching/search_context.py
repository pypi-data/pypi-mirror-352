from algowalk.searching.tracker import StepTracker


class SearchContext:
    def __init__(self, strategy, visualizer=None, pseudocode_builder=None):
        self.strategy = strategy
        self.visualizer = visualizer
        self.pseudocode_builder = pseudocode_builder

    def execute_search(self, data, target):

        # Initialize Step Tracker
        tracker = StepTracker(visualizer=self.visualizer, pseudocode_builder=self.pseudocode_builder)

        # Perform Search
        result_index = self.strategy.search(data, target, tracker)

        # Build Pseudocode
        self.strategy.pseudocode(tracker)
        # Print Summary and Steps
        tracker.print_summary()
        tracker.print_steps()

        # Print Pseudocode and Visualize
        tracker.print_pseudocode()
        tracker.visualize()

        if result_index != -1:
            print(f"\n✅ Target {target} found at index {result_index}\n")
        else:
            print(f"\n❌ Target {target} not found in the list\n")
        return result_index
