class ObjectTracker:
    def __init__(self):
        """Initialize counters for object classes"""
        self.class_counters = {}

    def register_class(self, class_name):
        """Register a new object class for tracking"""
        if class_name not in self.class_counters:
            self.class_counters[class_name] = 0

    def get_unique_id(self, class_name):
        """Assign sequential unique IDs to objects of a given class"""
        if class_name in self.class_counters:
            self.class_counters[class_name] += 1
            return f"{class_name}_{self.class_counters[class_name]}"
        else:
            raise ValueError(f"Class '{class_name}' is not registered. Use `register_class()` first.")
    def reset_class_counter(self, class_name):
        """Reset the counter for a specific class"""
        if class_name in self.class_counters:
            self.class_counters[class_name] = 0
        else:
            raise ValueError(f"Class '{class_name}' is not registered. Use `register_class()` first.")
    def reset_all_counters(self):
        """Reset all class counters"""
        for class_name in self.class_counters:
            self.class_counters[class_name] = 0
    def get_all_counters(self):
        """Get the current state of all class counters"""
        return self.class_counters.copy()
    def __str__(self):
        """String representation of the tracker state"""
        return f"ObjectTracker(class_counters={self.class_counters})"
    def __repr__(self):
        """Official string representation of the tracker state"""
        return f"ObjectTracker(class_counters={self.class_counters})"
    def __contains__(self, class_name):
        """Check if a class is registered"""
        return class_name in self.class_counters
    def __len__(self):
        """Get the number of registered classes"""
        return len(self.class_counters)
    def __iter__(self):
        """Iterate over registered class names"""
        return iter(self.class_counters.keys())
