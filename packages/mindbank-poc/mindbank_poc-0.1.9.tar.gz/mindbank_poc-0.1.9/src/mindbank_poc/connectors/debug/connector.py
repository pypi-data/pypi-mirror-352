class DebugConnector:
    """A simple connector for debugging purposes."""
    def __init__(self, config: dict):
        print(f"Initializing DebugConnector with config: {config}")
        self.config = config

    def ingest(self):
        """Simulates the ingestion process."""
        print("DebugConnector: Ingesting data...")
        # In a real scenario, this would yield RawEntry or Aggregate objects
        yield {"message": "Debug data point 1"}
        yield {"message": "Debug data point 2"}
        print("DebugConnector: Ingestion finished.")
