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
        
    def reload_speaker_data(self, *args):
        """
        Reloads speaker data from the speaker file.
        This method can be called when switching to a view to ensure data is fresh.
        Views can override this method to perform additional updates.
        Accepts *args to handle any arguments Gradio might pass
        """
        if self.speaker_service.get_speaker_file() is not None:
            # Reload the speaker file data to ensure it's up to date
            self.speaker_service.speakers_file_data = self.speaker_service.load_speaker_file_data()
            return True
        return False
