import enum

class StepType(str,enum.Enum):
    TEXT = "text"
    VIDEO = "video"
    QUIZ = "quiz"