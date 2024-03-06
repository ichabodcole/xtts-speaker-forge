from services.content_manager_service import ContentManagerService
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from abc import ABC, abstractmethod


class ForgeBaseView(ABC):

    def __init__(self, speaker_service: SpeakerManagerService, model_service: ModelManagerService, content_service: ContentManagerService):
        self.model_service = model_service
        self.speaker_service = speaker_service
        self.content_service = content_service

    @abstractmethod
    def init_ui(self):
        pass
