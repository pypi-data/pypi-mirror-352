
## Usage

Import the package and start tracking objects dynamically.

```python
from tracking import ObjectTracker

# Initialize tracker
tracker = ObjectTracker()

# Register object classes
tracker.register_class("car")
tracker.register_class("bus")

# Get unique IDs
print(tracker.get_unique_id("car"))  # Output: car_1
print(tracker.get_unique_id("bus"))  # Output: bus_1
print(tracker.get_unique_id("car"))  # Output: car_2

# Reset tracking for a specific class
tracker.reset_class_counter("car")

# Reset all tracking counters
tracker.reset_all_counters()

# View current counters
print(tracker.get_all_counters())  # Output: {'car': 0, 'bus': 0}
