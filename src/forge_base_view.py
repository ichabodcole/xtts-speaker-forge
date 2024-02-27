from content_handler import ContentHandler
from model_handler import ModelHandler
from speakers_handler import SpeakersHandler
from abc import ABC, abstractmethod


class ForgeBaseView(ABC):

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler, content_handler: ContentHandler):
        self.model_handler = model_handler
        self.speakers_handler = speakers_handler
        self.content_handler = content_handler

    @abstractmethod
    def init_ui(self):
        pass
