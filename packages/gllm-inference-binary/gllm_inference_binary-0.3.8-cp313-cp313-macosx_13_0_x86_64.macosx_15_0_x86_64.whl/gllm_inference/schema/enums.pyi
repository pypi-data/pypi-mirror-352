from enum import StrEnum

class PromptRole(StrEnum):
    """Defines valid prompt roles."""
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class MimeType(StrEnum):
    """Defines valid mime types."""
    AUDIO = 'audio'
    DOCUMENT = 'document'
    IMAGE = 'image'
    VIDEO = 'video'
