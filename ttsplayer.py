"""
Register HyperTTS voices with the Anki {{tts}} tag.
code modeled after 
https://ankiweb.net/shared/info/391644525 
https://github.com/ankitects/anki-addons/blob/master/code/gtts_player/__init__.py
"""

import sys
from concurrent.futures import Future
from dataclasses import dataclass
from typing import List, cast

# import aqt
import aqt.tts
import anki

from . import root_logger

logger = root_logger.getChild(__name__)
languages = __import__('languages', globals(), locals(), [], sys._addon_import_level_base)


class AnkiHyperTTSPlayer(aqt.tts.TTSProcessPlayer):
    def __init__(self, taskman: aqt.taskman.TaskManager, hypertts) -> None:
        super(aqt.tts.TTSProcessPlayer, self).__init__(taskman)
        self.hypertts = hypertts
        logger.info('created AnkiHyperTTSPlayer')

    # this is called the first time Anki tries to play a TTS file
    def get_available_voices(self) -> List[aqt.tts.TTSVoice]:

        # register a voice for every possible language HyperTTS supports. This avoids forcing the user to do a restart when
        # they configure a new TTS tag
        
        voices = []
        for audio_language in languages.AudioLanguage:
            language_name = audio_language.name
            voices.append(aqt.tts.TTSVoice(name="HyperTTS", lang=language_name))

        return voices  # type: ignore

    # this is called on a background thread, and will not block the UI
    def _play(self, tag: anki.sound.AVTag):
        self.audio_file_path = None
        self.playback_error = False
        self.playback_error_message = None

        assert isinstance(tag, anki.sound.TTSTag)
        logger.info(f'playing TTS sound for {tag}')

        audio_filename = self.hypertts.get_audio_filename_tts_tag(tag)
        return audio_filename

    # this is called on the main thread, after _play finishes
    def _on_done(self, ret: Future, cb: aqt.sound.OnDoneCallback) -> None:
        with self.hypertts.error_manager.get_single_action_context('Playing Realtime Audio'):
            audio_filename = ret.result()
            logger.info(f'got audio_filename: {audio_filename}')
            aqt.sound.av_player.insert_file(audio_filename)
        cb()

