import enum

class PurchaseStatus(str, enum.Enum):
    PENDING = 'pending'
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"