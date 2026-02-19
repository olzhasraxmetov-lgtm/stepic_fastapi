from app.repositories.progress import ProgressRepository


class ProgressService:
    def __init__(self, progress_repo: ProgressRepository):
        self.progress_repo = progress_repo
