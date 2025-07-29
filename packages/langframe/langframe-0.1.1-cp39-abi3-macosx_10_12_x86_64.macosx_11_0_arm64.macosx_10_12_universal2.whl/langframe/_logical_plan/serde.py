import pickle  # nosec: B403

from langframe._logical_plan import LogicalPlan


class LogicalPlanSerde:
    @staticmethod
    def serialize(plan: LogicalPlan) -> bytes:
        """
        Serialize a LogicalPlan to bytes using pickle.

        Args:
            plan: The LogicalPlan to serialize

        Returns:
            bytes: The serialized plan
        """
        return pickle.dumps(plan)

    @staticmethod
    def deserialize(data: bytes) -> LogicalPlan:
        """
        Deserialize bytes back into a LogicalPlan using pickle.

        Args:
            data: The serialized plan data

        Returns:
            The deserialized plan
        """
        return pickle.loads(data)  # nosec: B301
