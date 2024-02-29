from services.content_manager_service import ContentManagerService
from services.model_manager_service import ModelManagerService
from services.speaker_manager_service import SpeakerManagerService
from abc import ABC, abstractmethod


class ForgeBaseView(ABC):

    def __init__(self, speakers_handler: SpeakerManagerService, model_handler: ModelManagerService, content_handler: ContentManagerService):
        self.model_handler = model_handler
        self.speakers_handler = speakers_handler
        self.content_handler = content_handler

    @abstractmethod
    def init_ui(self):
        pass
