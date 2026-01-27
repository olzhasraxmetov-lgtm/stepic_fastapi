from app.repositories.purchase import PurchaseRepository

class PurchaseService:
    def __init__(self, purchase_repo: PurchaseRepository):
        self.purchase_repo = purchase_repo

