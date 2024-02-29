from services.content_manager_service import ContentManagerService
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from abc import ABC, abstractmethod


class ForgeBaseView(ABC):

    def __init__(self, speakers_handler: SpeakerManagerService, model_service: ModelManagerService, content_service: ContentManagerService):
        self.model_service = model_service
        self.speakers_handler = speakers_handler
        self.content_service = content_service

    @abstractmethod
    def init_ui(self):
        pass
