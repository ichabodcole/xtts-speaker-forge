from speakers_handler import SpeakersHandler
from model_handler import ModelHandler


class SpeakerForgeBase:
    speakers_data = None

    def __init__(self, speakers_handler: SpeakersHandler, model_handler: ModelHandler):
        self.speakers_handler = speakers_handler
        self.model_handler = model_handler
