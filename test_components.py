import aqt.qt
import os
import copy
import pprint
import component_batch_preview
import component_configuration
import config_models
import servicemanager
import testing_utils
import hypertts
import constants
import languages
import component_voiceselection
import component_source
import component_target
import component_batch
import component_text_processing
import component_realtime_source
import component_realtime_side
import component_realtime

from . import root_logger

logger = root_logger.getChild(__name__)


class EmptyDialog(aqt.qt.QDialog):
    def __init__(self):
        super(aqt.qt.QDialog, self).__init__()
        self.closed = None

    def setupUi(self):
        self.main_layout = aqt.qt.QVBoxLayout(self)

    def getLayout(self):
        return self.main_layout

    def setLayout(self, layout):
        self.main_layout = layout

    def addChildLayout(self, layout):
        self.main_layout.addLayout(layout)
    
    def close(self):
        self.closed = True

class MockModelChangeCallback():
    def __init__(self):
        self.model = None

    def model_updated(self, model):
        logger.info('MockModelChangeCallback.model_updated')
        self.model = copy.deepcopy(model)

class MockBatchPreviewCallback():
    def __init__(self):
        self.sample_text = None
        self.batch_start_called = None
        self.batch_end_called = None

    def sample_selected(self, note_id, text):
        self.note_id = note_id
        self.sample_text = text

    def batch_start(self):
        self.batch_start_called = True

    def batch_end(self, completed):
        self.batch_end_called = True

class MockEditor():
    def __init__(self):
        self.set_note_called = None

    def set_note(self, note):
        self.set_note_called = True

def get_hypertts_instance():
    # return hypertts_instance    
    config_gen = testing_utils.TestConfigGenerator()
    return config_gen.build_hypertts_instance_test_servicemanager('default')


def test_voice_selection_defaults_single(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    expected_output = {
        'voice_selection_mode': 'single',
        'voice': {
            'voice': {
                'gender': 'Male', 
                'language': 'fr_FR',
                'name': 'voice_a_1', 
                'service': 'ServiceA',
                'voice_key': {'name': 'voice_1'}
            },
            'options': {
            }
        }        
    }

    assert voiceselection.serialize() == expected_output

    # dialog.exec_()
    
def test_voice_selection_single_1(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice

    # dialog.exec_()

    expected_output = {
        'voice_selection_mode': 'single',
        'voice': {
            'voice': {
                'gender': 'Female', 
                'language': 'en_US',
                'name': 'voice_a_2', 
                'service': 'ServiceA',
                'voice_key': {'name': 'voice_2'}
            },
            'options': {
            }
        }        
    }
    assert voiceselection.serialize() == expected_output    

    # change options
    speaking_rate_widget = dialog.findChild(aqt.qt.QDoubleSpinBox, "voice_option_speaking_rate")
    speaking_rate_widget.setValue(0.25)

    expected_output = {
        'voice_selection_mode': 'single',
        'voice': {
            'voice': {
                'gender': 'Female', 
                'language': 'en_US',
                'name': 'voice_a_2', 
                'service': 'ServiceA',
                'voice_key': {'name': 'voice_2'}
            },
            'options': {
                'speaking_rate': 0.25
            }
        }        
    }
    assert voiceselection.serialize() == expected_output        

def test_voice_selection_random_1(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # choose random mode
    # qtbot.mouseClick(voiceselection.radio_button_random, aqt.qt.Qt.LeftButton)
    voiceselection.radio_button_random.setChecked(True)

    # pick second voice and add it
    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)

    # pick third voice and add it
    voiceselection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)    

    expected_output = {
        'voice_selection_mode': 'random',
        'voice_list': [
            {
                'voice': {
                    'gender': 'Female', 
                    'language': 'en_US',
                    'name': 'voice_a_2', 
                    'service': 'ServiceA',
                    'voice_key': {'name': 'voice_2'}
                },
                'options': {
                },
                'weight': 1
            },
            {
                'voice': {
                    'gender': 'Female', 
                    'language': 'ja_JP',
                    'name': 'voice_a_3', 
                    'service': 'ServiceA',
                    'voice_key': {'name': 'voice_3'}
                },
                'options': {
                },
                'weight': 1
            }            
        ]
    }
    assert voiceselection.serialize() == expected_output    

def test_voice_selection_random_to_single(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # choose random mode
    # qtbot.mouseClick(voiceselection.radio_button_random, aqt.qt.Qt.LeftButton)
    voiceselection.radio_button_random.setChecked(True)

    # pick second voice and add it
    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)

    # pick third voice and add it
    voiceselection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)    

    # check model change callback
    assert model_change_callback.model.selection_mode == constants.VoiceSelectionMode.random
    assert len(model_change_callback.model.get_voice_list()) == 2

    # go back to single
    voiceselection.radio_button_single.setChecked(True)
    # check model change callback
    assert model_change_callback.model.selection_mode == constants.VoiceSelectionMode.single

    # verify that the selected voices grid is empty
    assert voiceselection.voice_list_grid_layout.count() == 0


def test_voice_selection_random_remove_voices(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # choose random mode
    # qtbot.mouseClick(voiceselection.radio_button_random, aqt.qt.Qt.LeftButton)
    voiceselection.radio_button_random.setChecked(True)

    # pick second voice and add it
    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)

    # pick third voice and add it
    voiceselection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)    

    # check model change callback
    assert model_change_callback.model.selection_mode == constants.VoiceSelectionMode.random
    assert len(model_change_callback.model.get_voice_list()) == 2

    # now remove one of the voices
    logger.info('removing voice_row_1')
    remove_voice_button = dialog.findChild(aqt.qt.QPushButton, 'remove_voice_row_1')
    qtbot.mouseClick(remove_voice_button, aqt.qt.Qt.LeftButton)

    # check model change callback
    assert model_change_callback.model.selection_mode == constants.VoiceSelectionMode.random
    assert len(model_change_callback.model.get_voice_list()) == 1



def test_voice_selection_random_2(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # choose random mode
    voiceselection.radio_button_random.setChecked(True)

    # add the first voice twice, but with different options
    voiceselection.voices_combobox.setCurrentIndex(0)
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)

    # change options
    speaking_rate_widget = dialog.findChild(aqt.qt.QDoubleSpinBox, "voice_option_speaking_rate")
    speaking_rate_widget.setValue(0.25)    

    # add again
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)

    # build expected voice selection model
    expected_model = config_models.VoiceSelectionRandom()
    voice = [x for x in hypertts_instance.service_manager.full_voice_list() if x.service.name == 'ServiceA' and x.name == 'voice_a_1'][0]

    expected_model.add_voice(config_models.VoiceWithOptionsRandom(voice, {}))
    expected_model.add_voice(config_models.VoiceWithOptionsRandom(voice, {'speaking_rate': 0.25}))    

    assert voiceselection.voice_selection_model.serialize() == expected_model.serialize()


def test_voice_selection_priority_1(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # choose random mode
    # qtbot.mouseClick(voiceselection.radio_button_random, aqt.qt.Qt.LeftButton)
    voiceselection.radio_button_priority.setChecked(True)

    # dialog.exec_()

    # pick second voice and add it
    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)

    # pick third voice and add it
    voiceselection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, aqt.qt.Qt.LeftButton)    

    expected_model = config_models.VoiceSelectionPriority()
    voice_2 = [x for x in hypertts_instance.service_manager.full_voice_list() if x.service.name == 'ServiceA' and x.name == 'voice_a_2'][0]
    voice_3 = [x for x in hypertts_instance.service_manager.full_voice_list() if x.service.name == 'ServiceA' and x.name == 'voice_a_3'][0]

    expected_model.add_voice(config_models.VoiceWithOptionsPriority(voice_2, {}))
    expected_model.add_voice(config_models.VoiceWithOptionsPriority(voice_3, {}))

    assert voiceselection.voice_selection_model.serialize() == expected_model.serialize()

    # dialog.exec_()


def test_voice_selection_filters(qtbot):
    manager = servicemanager.ServiceManager(testing_utils.get_test_services_dir(), 'test_services', True)
    manager.init_services()
    manager.get_service('ServiceA').enabled = True
    manager.get_service('ServiceB').enabled = True
    anki_utils = testing_utils.MockAnkiUtils({})

    hypertts_instance = hypertts.HyperTTS(anki_utils, manager)

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # ensure filters are set to All by default
    assert voiceselection.audio_languages_combobox.currentText() == constants.LABEL_FILTER_ALL
    assert voiceselection.languages_combobox.currentText() == constants.LABEL_FILTER_ALL
    assert voiceselection.services_combobox.currentText() == constants.LABEL_FILTER_ALL
    assert voiceselection.genders_combobox.currentText() == constants.LABEL_FILTER_ALL

    # filter language to Japanese
    voiceselection.languages_combobox.setCurrentText('Japanese')

    # ensure japanese filter is enabled
    assert len(voiceselection.filtered_voice_list) < len(voiceselection.voice_list)
    assert len(voiceselection.filtered_voice_list) == voiceselection.voices_combobox.count()
    for voice in voiceselection.filtered_voice_list:
        assert voice.language.lang == languages.Language.ja

    # reset filters
    qtbot.mouseClick(voiceselection.reset_filters_button, aqt.qt.Qt.LeftButton)

    # ensure all voices are available now
    assert len(voiceselection.filtered_voice_list) == len(voiceselection.voice_list)

    # filter gender to male
    voiceselection.genders_combobox.setCurrentText('Male')

    # ensure only male voices appear
    assert len(voiceselection.filtered_voice_list) < len(voiceselection.voice_list)
    assert len(voiceselection.filtered_voice_list) == voiceselection.voices_combobox.count()
    for voice in voiceselection.filtered_voice_list:
        assert voice.gender == constants.Gender.Male

    # reset filters again
    qtbot.mouseClick(voiceselection.reset_filters_button, aqt.qt.Qt.LeftButton)
    # ensure all voices are available now
    assert len(voiceselection.filtered_voice_list) == len(voiceselection.voice_list)
    
    # filter with two different conditions
    voiceselection.languages_combobox.setCurrentText('Japanese')
    voiceselection.genders_combobox.setCurrentText('Female')

    # ensure only female japanese voices are present
    assert len(voiceselection.filtered_voice_list) < len(voiceselection.voice_list)
    assert len(voiceselection.filtered_voice_list) == voiceselection.voices_combobox.count()
    for voice in voiceselection.filtered_voice_list:
        assert voice.gender == constants.Gender.Female
        assert voice.language.lang == languages.Language.ja

    # reset filters again
    qtbot.mouseClick(voiceselection.reset_filters_button, aqt.qt.Qt.LeftButton)    

    # select random mode and add some voices
    # ======================================


    # dialog.exec_()

def test_voice_selection_samples(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    # simulate selection from the preview grid
    voiceselection.sample_text_selected('Bonjour')

    qtbot.mouseClick(voiceselection.play_sample_button, aqt.qt.Qt.LeftButton)

    assert hypertts_instance.anki_utils.played_sound == {
        'source_text': 'Bonjour',
        'voice': {
            'gender': 'Male', 
            'language': 'fr_FR', 
            'name': 'voice_a_1', 
            'service': 'ServiceA',
            'voice_key': {'name': 'voice_1'}
        },
        'options': {}
    }

    # dialog.exec_()

def test_voice_selection_load_model(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(voiceselection.draw())

    voice_list = hypertts_instance.service_manager.full_voice_list()
    voice_a_2 = [x for x in voice_list if x.name == 'voice_a_2'][0]
    voice_a_3 = [x for x in voice_list if x.name == 'voice_a_3'][0]

    # single voice
    # ============

    model = config_models.VoiceSelectionSingle()
    model.voice = config_models.VoiceWithOptions(voice_a_2, {'speaking_rate': 3.5})

    voiceselection.load_model(model)

    assert voiceselection.radio_button_single.isChecked()
    assert voiceselection.voices_combobox.currentText() == str(voice_a_2)


    speaking_rate_widget = voiceselection.voice_options_widgets['voice_option_speaking_rate']
    assert speaking_rate_widget != None
    assert speaking_rate_widget.value() == 3.5

    # random
    # =======

    model = config_models.VoiceSelectionRandom()
    model.add_voice(config_models.VoiceWithOptionsRandom(voice_a_2, {'speaking_rate': 2.5}))
    model.add_voice(config_models.VoiceWithOptionsRandom(voice_a_3, {}))

    voiceselection.load_model(model)
    
    assert voiceselection.radio_button_random.isChecked()

    assert voiceselection.voice_list_grid_layout.itemAt(0).widget().text() == str(voice_a_2) + ' (speaking_rate: 2.5)'
    assert voiceselection.voice_list_grid_layout.itemAt(3).widget().text() == str(voice_a_3)

    # priority
    # ========

    model = config_models.VoiceSelectionPriority()
    model.add_voice(config_models.VoiceWithOptionsPriority(voice_a_2, {'speaking_rate': 2.5}))
    model.add_voice(config_models.VoiceWithOptionsPriority(voice_a_3, {}))

    voiceselection.load_model(model)
    
    assert voiceselection.radio_button_priority.isChecked()

    assert voiceselection.voice_list_grid_layout.itemAt(0).widget().text() == str(voice_a_2) + ' (speaking_rate: 2.5)'
    assert voiceselection.voice_list_grid_layout.itemAt(4).widget().text() == str(voice_a_3)    

    # dialog.exec_()





def test_batch_source_1(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]

    model_change_callback = MockModelChangeCallback()
    field_list = hypertts_instance.get_all_fields_from_notes(note_id_list)
    batch_source = component_source.BatchSource(hypertts_instance, field_list, model_change_callback.model_updated)
    dialog.addChildLayout(batch_source.draw())

    # the field selected should be "Chinese"
    expected_source_model = config_models.BatchSourceSimple('Chinese')

    # the simple stack item should be selected
    assert batch_source.source_config_stack.currentIndex() == batch_source.SOURCE_CONFIG_STACK_SIMPLE

    assert batch_source.batch_source_model.serialize() == expected_source_model.serialize()

    # select another field, 'English'
    batch_source.source_field_combobox.setCurrentText('English')
    expected_source_model.source_field = 'English'

    assert batch_source.batch_source_model.serialize() == expected_source_model.serialize()

    # select template mode
    batch_source.batch_mode_combobox.setCurrentText('template')
    assert batch_source.source_config_stack.currentIndex() == batch_source.SOURCE_CONFIG_STACK_TEMPLATE

    # enter template format
    qtbot.keyClicks(batch_source.simple_template_input, '{Chinese}')

    expected_source_model = config_models.BatchSourceTemplate(constants.BatchMode.template, 
        '{Chinese}', constants.TemplateFormatVersion.v1)

    assert batch_source.batch_source_model.serialize() == expected_source_model.serialize()

    # load model tests
    # ================
    # the field selected should be "English"
    model = config_models.BatchSourceSimple('English')

    batch_source.load_model(model)

    assert batch_source.batch_mode_combobox.currentText() == 'simple'
    assert batch_source.source_field_combobox.currentText() == 'English'

    model.source_field = 'Chinese'

    batch_source.load_model(model)

    assert batch_source.batch_mode_combobox.currentText() == 'simple'
    assert batch_source.source_field_combobox.currentText() == 'Chinese'

    model.mode = constants.BatchMode.template
    model.source_template = '{English}'
    model.template_format_version = constants.TemplateFormatVersion.v1

    batch_source.load_model(model)

    assert batch_source.batch_mode_combobox.currentText() == 'template'
    assert batch_source.simple_template_input.text() == '{English}'

    # load advanced template
    model.mode = constants.BatchMode.advanced_template
    model.source_template = f"""result = 'yoyo'"""
    model.template_format_version = constants.TemplateFormatVersion.v1

    batch_source.load_model(model)

    assert batch_source.advanced_template_input.toPlainText() == f"""result = 'yoyo'"""

    # dialog.exec_()

def test_target(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]

    model_change_callback = MockModelChangeCallback()
    field_list = hypertts_instance.get_all_fields_from_notes(note_id_list)
    batch_target = component_target.BatchTarget(hypertts_instance, field_list, model_change_callback.model_updated)
    dialog.addChildLayout(batch_target.draw())

    # pick the Sound field
    batch_target.target_field_combobox.setCurrentText('Sound')

    assert batch_target.batch_target_model.target_field == 'Sound'
    assert batch_target.batch_target_model.text_and_sound_tag == False
    assert batch_target.batch_target_model.remove_sound_tag == True

    # change some options
    batch_target.radio_button_text_sound.setChecked(True)
    assert batch_target.batch_target_model.text_and_sound_tag == True

    batch_target.radio_button_keep_sound.setChecked(True)
    assert batch_target.batch_target_model.remove_sound_tag == False

    # load model tests
    # ================

    target_field = 'Chinese'
    text_and_sound_tag = False
    remove_sound_tag = True
    model = config_models.BatchTarget(target_field, text_and_sound_tag, remove_sound_tag)
    batch_target.load_model(model)

    assert batch_target.target_field_combobox.currentText() == 'Chinese'
    assert batch_target.radio_button_sound_only.isChecked() == True
    assert batch_target.radio_button_text_sound.isChecked() == False

    assert batch_target.radio_button_keep_sound.isChecked() == False
    assert batch_target.radio_button_remove_sound.isChecked() == True

    target_field = 'Pinyin'
    text_and_sound_tag = True
    remove_sound_tag = True
    model = config_models.BatchTarget(target_field, text_and_sound_tag, remove_sound_tag)
    batch_target.load_model(model)

    assert batch_target.target_field_combobox.currentText() == 'Pinyin'

    assert batch_target.radio_button_sound_only.isChecked() == False
    assert batch_target.radio_button_text_sound.isChecked() == True

    assert batch_target.radio_button_keep_sound.isChecked() == False
    assert batch_target.radio_button_remove_sound.isChecked() == True

    target_field = 'Sound'
    text_and_sound_tag = True
    remove_sound_tag = False
    model = config_models.BatchTarget(target_field, text_and_sound_tag, remove_sound_tag)
    batch_target.load_model(model)

    assert batch_target.target_field_combobox.currentText() == 'Sound'
    assert batch_target.radio_button_sound_only.isChecked() == False
    assert batch_target.radio_button_text_sound.isChecked() == True

    assert batch_target.radio_button_keep_sound.isChecked() == True
    assert batch_target.radio_button_remove_sound.isChecked() == False

    target_field = 'Chinese'
    text_and_sound_tag = False
    remove_sound_tag = False
    model = config_models.BatchTarget(target_field, text_and_sound_tag, remove_sound_tag)
    batch_target.load_model(model)

    assert batch_target.target_field_combobox.currentText() == 'Chinese'
    assert batch_target.radio_button_sound_only.isChecked() == True
    assert batch_target.radio_button_text_sound.isChecked() == False

    assert batch_target.radio_button_keep_sound.isChecked() == True
    assert batch_target.radio_button_remove_sound.isChecked() == False

def test_batch_preview(qtbot):

    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    # configure delay on service A
    # hypertts_instance.service_manager.get_service('ServiceA').configure({'delay': 1.0})

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    

    voice_list = hypertts_instance.service_manager.full_voice_list()

    voice_a_1 = [x for x in voice_list if x.name == 'voice_a_1'][0]
    voice_selection = config_models.VoiceSelectionSingle()
    voice_selection.set_voice(config_models.VoiceWithOptions(voice_a_1, {}))

    batch_config = config_models.BatchConfig()
    source = config_models.BatchSourceSimple('Chinese')
    target = config_models.BatchTarget('Sound', False, True)

    batch_config.set_source(source)
    batch_config.set_target(target)
    batch_config.set_voice_selection(voice_selection)    

    batch_preview_callback = MockBatchPreviewCallback()
    batch_preview = component_batch_preview.BatchPreview(hypertts_instance, note_id_list, 
        batch_preview_callback.sample_selected,
        batch_preview_callback.batch_start,
        batch_preview_callback.batch_end)
    batch_preview.load_model(batch_config)
    dialog.addChildLayout(batch_preview.draw())

    # dialog.exec_()
    # return 


def test_batch_dialog(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    

    # test saving of config
    # =====================

    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())

    # select a source field and target field
    batch.source.source_field_combobox.setCurrentText('English')
    batch.target.target_field_combobox.setCurrentText('Sound')

    # set profile name
    batch.profile_name_combobox.setCurrentText('batch profile 1')

    # save button should be enabled
    assert batch.profile_save_button.isEnabled() == True
    # save
    qtbot.mouseClick(batch.profile_save_button, aqt.qt.Qt.LeftButton)
    # should be disabled after saving
    assert batch.profile_save_button.isEnabled() == False
    assert batch.profile_load_button.isEnabled() == False
    assert batch.profile_save_button.text() == 'Preset Saved'

    print(hypertts_instance.anki_utils.written_config)
    assert 'batch profile 1' in hypertts_instance.anki_utils.written_config[constants.CONFIG_BATCH_CONFIG]

    # try to deserialize that config, it should have the English field selected
    deserialized_model = hypertts_instance.load_batch_config('batch profile 1')
    assert deserialized_model.source.source_field == 'English'
    assert deserialized_model.target.target_field == 'Sound'

    # test loading of config
    # ======================

    dialog = EmptyDialog()
    dialog.setupUi()
    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())    

    # dialog.exec_()

    assert batch.profile_load_button.isEnabled() == False
    # select preset
    batch.profile_name_combobox.setCurrentText('batch profile 1')
    # should be enabled now
    assert batch.profile_load_button.isEnabled() == True
    assert batch.profile_load_button.text() == 'Load'

    # open
    qtbot.mouseClick(batch.profile_load_button, aqt.qt.Qt.LeftButton)

    # button should go back to disabled
    assert batch.profile_load_button.isEnabled() == False
    assert batch.profile_save_button.isEnabled() == False
    assert batch.profile_load_button.text() == 'Preset Loaded'

    # assertions on GUI
    assert batch.source.source_field_combobox.currentText() == 'English'
    assert batch.target.target_field_combobox.currentText() == 'Sound'
    
    # dialog.exec_()

    # test launching with a particular preset
    # =======================================

    dialog = EmptyDialog()
    dialog.setupUi()
    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())
    batch.load_batch('batch profile 1')

    # assertions on GUI
    assert batch.source.source_field_combobox.currentText() == 'English'
    assert batch.target.target_field_combobox.currentText() == 'Sound'

    # dialog.exec_()

    assert batch.profile_load_button.isEnabled() == False
    assert batch.profile_save_button.isEnabled() == False    

    # play sound preview
    # ==================

    # select second row
    index_second_row = batch.preview.batch_preview_table_model.createIndex(1, 0)
    batch.preview.table_view.selectionModel().select(index_second_row, aqt.qt.QItemSelectionModel.Select)
    # press preview button
    qtbot.mouseClick(batch.preview_sound_button, aqt.qt.Qt.LeftButton)
    # dialog.exec_()

    assert hypertts_instance.anki_utils.played_sound == {
        'source_text': 'hello',
        'voice': {
            'gender': 'Male', 
            'language': 'fr_FR', 
            'name': 'voice_a_1', 
            'service': 'ServiceA',
            'voice_key': {'name': 'voice_1'}
        },
        'options': {}
    }    

    # load audio
    # ==========

    batch.source.source_field_combobox.setCurrentText('Chinese')
    qtbot.mouseClick(batch.apply_button, aqt.qt.Qt.LeftButton)

    # make sure notes were updated
    note_1 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)
    assert 'Sound' in note_1.set_values 

    sound_tag = note_1.set_values['Sound']
    audio_full_path = hypertts_instance.anki_utils.extract_sound_tag_audio_full_path(sound_tag)
    audio_data = hypertts_instance.anki_utils.extract_mock_tts_audio(audio_full_path)

    assert audio_data['source_text'] == '老人家'

    note_2 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_2)
    assert 'Sound' in note_2.set_values 

    sound_tag = note_2.set_values['Sound']
    audio_full_path = hypertts_instance.anki_utils.extract_sound_tag_audio_full_path(sound_tag)
    audio_data = hypertts_instance.anki_utils.extract_mock_tts_audio(audio_full_path)

    assert audio_data['source_text'] == '你好'

    # button state
    assert batch.apply_button.isEnabled() == False
    assert batch.cancel_button.isEnabled() == True
    assert batch.cancel_button.text() == 'Close'

    # delete profile
    # ==============

    assert batch.profile_name_combobox.count() == 2
    assert batch.profile_name_combobox.currentText() == 'batch profile 1'
    qtbot.mouseClick(batch.profile_delete_button, aqt.qt.Qt.LeftButton)

    # make sure the profile was deleted
    assert 'batch profile 1' not in hypertts_instance.anki_utils.written_config[constants.CONFIG_BATCH_CONFIG]    

    # make sure the combobox was updated
    assert batch.profile_name_combobox.count() == 1
    assert batch.profile_name_combobox.currentText() == 'Preset 1'

    # dialog.exec_()

def test_batch_dialog_sound_preview_error(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    

    # test saving of config
    # =====================

    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())

    # select English source
    batch.source.source_field_combobox.setCurrentText('English')
    
    # play sound preview with error voice
    # ===================================

    # select error voice
    batch.voice_selection.voices_combobox.setCurrentIndex(5)

    # select second row
    index_second_row = batch.preview.batch_preview_table_model.createIndex(1, 0)
    batch.preview.table_view.selectionModel().select(index_second_row, aqt.qt.QItemSelectionModel.Select)

    # dialog.exec_()

    # press preview button
    qtbot.mouseClick(batch.preview_sound_button, aqt.qt.Qt.LeftButton)

    assert str(hypertts_instance.anki_utils.last_exception) == 'Audio not found for [hello] (voice: ServiceB, Japanese, Male, notfound)'


def test_batch_dialog_manual(qtbot):
    # HYPERTTS_BATCH_DIALOG_DEBUG=yes pytest test_components.py -k test_batch_dialog_manual
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    

    # test saving of config
    # =====================

    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())

    if os.environ.get('HYPERTTS_BATCH_DIALOG_DEBUG', 'no') == 'yes':
        dialog.exec_()


def test_batch_dialog_editor(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    
    note = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)

    mock_editor = MockEditor()

    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_editor(note, mock_editor, False)
    batch.draw(dialog.getLayout())

    # test sound preview
    # ==================
    # dialog.exec_()
    qtbot.mouseClick(batch.preview_sound_button, aqt.qt.Qt.LeftButton)
    assert hypertts_instance.anki_utils.played_sound == {
        'source_text': '老人家',
        'voice': {
            'gender': 'Male', 
            'language': 'fr_FR', 
            'name': 'voice_a_1', 
            'service': 'ServiceA',
            'voice_key': {'name': 'voice_1'}
        },
        'options': {}
    }    


    # test apply to note
    # ==================
    # dialog.exec_()
    
    # set target field
    batch.target.target_field_combobox.setCurrentText('Sound')

    # apply not note
    qtbot.mouseClick(batch.apply_button, aqt.qt.Qt.LeftButton)

    sound_tag = note.set_values['Sound']
    audio_full_path = hypertts_instance.anki_utils.extract_sound_tag_audio_full_path(sound_tag)
    audio_data = hypertts_instance.anki_utils.extract_mock_tts_audio(audio_full_path)

    assert audio_data['source_text'] == '老人家'

    assert mock_editor.set_note_called == True

    assert hypertts_instance.anki_utils.undo_started == True
    assert hypertts_instance.anki_utils.undo_finished == True

    assert dialog.closed == True

def test_batch_dialog_editor_template_error(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    
    note = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)

    mock_editor = MockEditor()

    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_editor(note, mock_editor, False)
    batch.draw(dialog.getLayout())

    # select template mode and enter incorrect advanced template
    batch.source.batch_mode_combobox.setCurrentText('advanced_template')
    # enter template format
    # qtbot.keyClicks(batch.source.advanced_template_input, """field_1 = 'yoyo'""")
    batch.source.advanced_template_input.setPlainText("""field_1 = 'yoyo'""")

    # ensure the preview label is showing an error
    label_error_text = batch.preview.source_preview_label.text()
    expected_label_text = """<b>Encountered Error:</b> No "result" variable found. You must assign the final template output to a result variable."""
    assert label_error_text == expected_label_text

    # dialog.exec_()


def test_text_processing(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    text_processing = component_text_processing.TextProcessing(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(text_processing.draw())

    # dialog.exec_()

    # asserts on the GUI
    assert text_processing.textReplacementTableModel.headerData(0, aqt.qt.Qt.Orientation.Horizontal, aqt.qt.Qt.ItemDataRole.DisplayRole) == 'Type'
    assert text_processing.textReplacementTableModel.headerData(1, aqt.qt.Qt.Orientation.Horizontal, aqt.qt.Qt.ItemDataRole.DisplayRole) == 'Pattern'
    assert text_processing.textReplacementTableModel.headerData(2, aqt.qt.Qt.Orientation.Horizontal, aqt.qt.Qt.ItemDataRole.DisplayRole) == 'Replacement'    
    # should have 0 rows
    assert text_processing.textReplacementTableModel.rowCount(None) == 0    

    # check processing preview
    qtbot.keyClicks(text_processing.sample_text_input, 'abdc1234')
    assert text_processing.sample_text_transformed_label.text() == '<b>abdc1234</b>'

    # add a text transformation rule
    qtbot.mouseClick(text_processing.add_replace_simple_button, aqt.qt.Qt.LeftButton)
    # enter pattern and replacement
    row = 0
    index_pattern = text_processing.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_PATTERN)
    text_processing.textReplacementTableModel.setData(index_pattern, '1234', aqt.qt.Qt.EditRole)
    index_replacement = text_processing.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_REPLACEMENT)
    text_processing.textReplacementTableModel.setData(index_replacement, '5678', aqt.qt.Qt.EditRole)

    # verify preview
    assert text_processing.sample_text_transformed_label.text() == '<b>abdc5678</b>'

    # add another transformation rule
    qtbot.mouseClick(text_processing.add_replace_simple_button, aqt.qt.Qt.LeftButton)
    # enter pattern and replacement
    row = 1
    index_pattern = text_processing.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_PATTERN)
    text_processing.textReplacementTableModel.setData(index_pattern, ' / ', aqt.qt.Qt.EditRole)
    index_replacement = text_processing.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_REPLACEMENT)
    text_processing.textReplacementTableModel.setData(index_replacement, ' ', aqt.qt.Qt.EditRole)

    # check processing preview
    text_processing.sample_text_input.clear()
    qtbot.keyClicks(text_processing.sample_text_input, 'word1 / word2')
    assert text_processing.sample_text_transformed_label.text() == '<b>word1 word2</b>'

    # check model callbacks
    assert len(model_change_callback.model.text_replacement_rules) == 2
    assert model_change_callback.model.text_replacement_rules[0].rule_type == constants.TextReplacementRuleType.Simple
    assert model_change_callback.model.text_replacement_rules[0].source == '1234'
    assert model_change_callback.model.text_replacement_rules[0].target == '5678'
    assert model_change_callback.model.text_replacement_rules[1].rule_type == constants.TextReplacementRuleType.Simple
    assert model_change_callback.model.text_replacement_rules[1].source == ' / '
    assert model_change_callback.model.text_replacement_rules[1].target == ' '

    # add a regex rule
    # add another transformation rule
    qtbot.mouseClick(text_processing.add_replace_regex_button, aqt.qt.Qt.LeftButton)
    # enter pattern and replacement
    row = 2
    index_pattern = text_processing.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_PATTERN)
    text_processing.textReplacementTableModel.setData(index_pattern, '[0-9]+', aqt.qt.Qt.EditRole)
    index_replacement = text_processing.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_REPLACEMENT)
    text_processing.textReplacementTableModel.setData(index_replacement, 'number', aqt.qt.Qt.EditRole)

    text_processing.sample_text_input.clear()
    qtbot.keyClicks(text_processing.sample_text_input, '1234')
    assert text_processing.sample_text_transformed_label.text() == '<b>number</b>'

    # check model callbacks
    assert len(model_change_callback.model.text_replacement_rules) == 3
    assert model_change_callback.model.text_replacement_rules[2].rule_type == constants.TextReplacementRuleType.Regex
    assert model_change_callback.model.text_replacement_rules[2].source == '[0-9]+'
    assert model_change_callback.model.text_replacement_rules[2].target == 'number'

    # do some other model callback checks
    text_processing.html_to_text_line_checkbox.setChecked(False)
    assert model_change_callback.model.html_to_text_line == False
    text_processing.html_to_text_line_checkbox.setChecked(True)
    assert model_change_callback.model.html_to_text_line == True
    text_processing.ssml_convert_characters_checkbox.setChecked(False)
    assert model_change_callback.model.ssml_convert_characters == False
    text_processing.run_replace_rules_after_checkbox.setChecked(False)
    assert model_change_callback.model.run_replace_rules_after == False    

    # dialog.exec_()


    # verify load_model
    # =================

    text_processing = config_models.TextProcessing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Simple)
    rule.source = 'a'
    rule.target = 'b'
    text_processing.add_text_replacement_rule(rule)
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = 'c'
    rule.target = 'd'    
    text_processing.add_text_replacement_rule(rule)

    text_processing.html_to_text_line = False
    text_processing.ssml_convert_characters = True
    text_processing.run_replace_rules_after = False

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    text_processing_component = component_text_processing.TextProcessing(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(text_processing_component.draw())
    text_processing_component.load_model(text_processing)

    # check first row
    row = 0
    index = text_processing_component.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_TYPE)
    rule_type = text_processing_component.textReplacementTableModel.data(index, aqt.qt.Qt.ItemDataRole.DisplayRole)
    assert rule_type.value() == 'Simple'
    index = text_processing_component.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_PATTERN)
    source = text_processing_component.textReplacementTableModel.data(index, aqt.qt.Qt.ItemDataRole.DisplayRole)
    assert source.value() == '"a"'
    index = text_processing_component.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_REPLACEMENT)
    target = text_processing_component.textReplacementTableModel.data(index, aqt.qt.Qt.ItemDataRole.DisplayRole)
    assert target.value() == '"b"'

    # check second row
    row = 1
    index = text_processing_component.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_TYPE)
    rule_type = text_processing_component.textReplacementTableModel.data(index, aqt.qt.Qt.ItemDataRole.DisplayRole)
    assert rule_type.value() == 'Regex'
    index = text_processing_component.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_PATTERN)
    source = text_processing_component.textReplacementTableModel.data(index, aqt.qt.Qt.ItemDataRole.DisplayRole)
    assert source.value() == '"c"'
    index = text_processing_component.textReplacementTableModel.createIndex(row, component_text_processing.COL_INDEX_REPLACEMENT)
    target = text_processing_component.textReplacementTableModel.data(index, aqt.qt.Qt.ItemDataRole.DisplayRole)
    assert target.value() == '"d"'    

    assert text_processing_component.html_to_text_line_checkbox.isChecked() == False
    assert text_processing_component.ssml_convert_characters_checkbox.isChecked() == True
    assert text_processing_component.run_replace_rules_after_checkbox.isChecked() == False

    # dialog.exec_()

def test_text_processing_manual(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    model_change_callback = MockModelChangeCallback()
    text_processing = component_text_processing.TextProcessing(hypertts_instance, model_change_callback.model_updated)
    dialog.addChildLayout(text_processing.draw())

    if os.environ.get('HYPERTTS_TEXT_PROCESSING_DIALOG_DEBUG', 'no') == 'yes':
        dialog.exec_()        

def test_configuration(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')
    # start by disabling both services
    hypertts_instance.service_manager.get_service('ServiceA').enabled = False
    hypertts_instance.service_manager.get_service('ServiceB').enabled = False

    dialog = EmptyDialog()
    dialog.setupUi()

    # model_change_callback = MockModelChangeCallback()
    configuration = component_configuration.Configuration(hypertts_instance, dialog)
    configuration.draw(dialog.getLayout())

    # dialog.exec_()

    # try making changes to the service config and saving
    # ===================================================

    qtbot.keyClicks(configuration.hypertts_pro_api_key, 'error_key')
    assert configuration.model.hypertts_pro_api_key == None

    assert configuration.account_info_label.text() == '<b>error</b>: Key invalid'

    # we entered an error key, so pro mode is not enabled
    assert configuration.service_stack_map['ServiceB'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.service_stack_map['ServiceA'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.header_logo_stack_widget.currentIndex() == configuration.STACK_LEVEL_LITE

    service_a_enabled_checkbox = dialog.findChild(aqt.qt.QCheckBox, "ServiceA_enabled")
    service_a_enabled_checkbox.setChecked(True)
    assert configuration.model.get_service_enabled('ServiceA') == True
    service_a_enabled_checkbox.setChecked(False)
    assert configuration.model.get_service_enabled('ServiceA') == False

    service_a_region = dialog.findChild(aqt.qt.QComboBox, "ServiceA_region")
    service_a_region.setCurrentText('europe')
    assert configuration.model.get_service_configuration_key('ServiceA', 'region') == 'europe'
    service_a_region.setCurrentText('us')
    assert configuration.model.get_service_configuration_key('ServiceA', 'region') == 'us'
    
    service_a_api_key = dialog.findChild(aqt.qt.QLineEdit, "ServiceA_api_key")
    qtbot.keyClicks(service_a_api_key, '6789')
    assert configuration.model.get_service_configuration_key('ServiceA', 'api_key') == '6789'

    service_a_delay = dialog.findChild(aqt.qt.QSpinBox, "ServiceA_delay")
    service_a_delay.setValue(42)
    assert configuration.model.get_service_configuration_key('ServiceA', 'delay') == 42

    service_a_demokey = dialog.findChild(aqt.qt.QCheckBox, "ServiceA_demo_key")
    service_a_demokey.setChecked(True)
    assert configuration.model.get_service_configuration_key('ServiceA', 'demo_key') == True
    service_a_demokey.setChecked(False)
    assert configuration.model.get_service_configuration_key('ServiceA', 'demo_key') == False
    service_a_demokey.setChecked(True)

    assert configuration.save_button.isEnabled() == True

    # press save button
    qtbot.mouseClick(configuration.save_button, aqt.qt.Qt.LeftButton)
    assert 'configuration' in hypertts_instance.anki_utils.written_config
    expected_output = {
        'hypertts_pro_api_key': None,
        'service_enabled': {
            'ServiceA': False,
        },
        'service_config': {
            'ServiceA': {
                'region': 'us',
                'api_key': '6789',
                'delay': 42,
                'demo_key': True
            },
        }
    }
    assert hypertts_instance.anki_utils.written_config['configuration'] == expected_output

    # make sure dialog was closed
    assert dialog.closed == True

    # enter valid API key
    # ===================

    dialog = EmptyDialog()
    dialog.setupUi()
    configuration = component_configuration.Configuration(hypertts_instance, dialog)
    configuration.draw(dialog.getLayout())

    qtbot.keyClicks(configuration.hypertts_pro_api_key, 'valid_key')
    assert '250 chars' in configuration.account_info_label.text()

    assert configuration.service_stack_map['ServiceB'].currentIndex() == configuration.STACK_LEVEL_PRO
    assert configuration.service_stack_map['ServiceA'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.header_logo_stack_widget.currentIndex() == configuration.STACK_LEVEL_PRO

    assert configuration.model.hypertts_pro_api_key == 'valid_key'

    # switch to an invalid key
    configuration.hypertts_pro_api_key.setText('invalid_key')
    assert configuration.model.hypertts_pro_api_key == None
    assert configuration.service_stack_map['ServiceB'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.service_stack_map['ServiceA'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.header_logo_stack_widget.currentIndex() == configuration.STACK_LEVEL_LITE

    assert configuration.account_info_label.text() == '<b>error</b>: Key invalid'

    # dialog.exec_()

    # loading of existing model, no pro api key
    # =========================================

    configuration_model = config_models.Configuration()
    configuration_model.set_hypertts_pro_api_key(None)
    configuration_model.set_service_enabled('ServiceB', True)
    configuration_model.set_service_configuration_key('ServiceA', 'api_key', '123456')
    configuration_model.set_service_configuration_key('ServiceA', 'region', 'europe')
    configuration_model.set_service_configuration_key('ServiceA', 'delay', 7)
    configuration_model.set_service_configuration_key('ServiceA', 'demo_key', True)

    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')
    # start by disabling both services
    hypertts_instance.service_manager.get_service('ServiceA').enabled = False
    hypertts_instance.service_manager.get_service('ServiceB').enabled = False
    hypertts_instance.service_manager.configure(configuration_model)

    dialog = EmptyDialog()
    dialog.setupUi()
    configuration = component_configuration.Configuration(hypertts_instance, dialog)
    configuration.load_model(configuration_model)
    configuration.draw(dialog.getLayout())

    assert configuration.hypertts_pro_api_key.text() == ''

    assert configuration.service_stack_map['ServiceB'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.service_stack_map['ServiceA'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.header_logo_stack_widget.currentIndex() == configuration.STACK_LEVEL_LITE

    service_a_enabled_checkbox = dialog.findChild(aqt.qt.QCheckBox, "ServiceA_enabled")
    assert service_a_enabled_checkbox.isChecked() == False
    service_b_enabled_checkbox = dialog.findChild(aqt.qt.QCheckBox, "ServiceB_enabled")
    assert service_b_enabled_checkbox.isChecked() == True

    service_a_region = dialog.findChild(aqt.qt.QComboBox, "ServiceA_region")
    assert service_a_region.currentText() == 'europe'
    service_a_api_key = dialog.findChild(aqt.qt.QLineEdit, "ServiceA_api_key")
    assert service_a_api_key.text() == '123456'
    service_a_delay = dialog.findChild(aqt.qt.QSpinBox, "ServiceA_delay")
    assert service_a_delay.value() == 7
    service_a_demokey = dialog.findChild(aqt.qt.QCheckBox, "ServiceA_demo_key")
    assert service_a_demokey.isChecked() == True

    # setting the API key should make ServiceB's enable checkbox disabled and checked
    service_b_enabled_checkbox = dialog.findChild(aqt.qt.QCheckBox, "ServiceB_enabled")
    assert service_b_enabled_checkbox.isChecked() == True

    assert configuration.save_button.isEnabled() == False

    # dialog.exec_()

    # loading of existing model, with valid pro API key
    # =================================================

    configuration_model = config_models.Configuration()
    configuration_model.set_hypertts_pro_api_key('valid_key')

    dialog = EmptyDialog()
    dialog.setupUi()
    configuration = component_configuration.Configuration(hypertts_instance, dialog)
    configuration.load_model(configuration_model)
    configuration.draw(dialog.getLayout())

    assert configuration.hypertts_pro_api_key.text() == 'valid_key'

    assert configuration.header_logo_stack_widget.currentIndex() == configuration.STACK_LEVEL_PRO
    assert configuration.service_stack_map['ServiceB'].currentIndex() == configuration.STACK_LEVEL_PRO
    assert configuration.service_stack_map['ServiceA'].currentIndex() == configuration.STACK_LEVEL_LITE

    assert configuration.save_button.isEnabled() == False # since we didn't change anything

    # dialog.exec_()    

def test_configuration_pro_key_exception(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')
    # start by disabling both services
    hypertts_instance.service_manager.get_service('ServiceA').enabled = False
    hypertts_instance.service_manager.get_service('ServiceB').enabled = False

    dialog = EmptyDialog()
    dialog.setupUi()

    # model_change_callback = MockModelChangeCallback()
    configuration = component_configuration.Configuration(hypertts_instance, dialog)
    configuration.draw(dialog.getLayout())

    # dialog.exec_()

    # try making changes to the service config and saving
    # ===================================================

    qtbot.keyClicks(configuration.hypertts_pro_api_key, 'exception_key')
    assert configuration.model.hypertts_pro_api_key == None

    # assert configuration.account_info_label.text() == '<b>error</b>: Key invalid'

    # we entered an error key, so pro mode is not enabled
    assert configuration.service_stack_map['ServiceB'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.service_stack_map['ServiceA'].currentIndex() == configuration.STACK_LEVEL_LITE
    assert configuration.header_logo_stack_widget.currentIndex() == configuration.STACK_LEVEL_LITE

def test_configuration_manual(qtbot):
    # HYPERTTS_CONFIGURATION_DIALOG_DEBUG=yes pytest test_components.py -k test_configuration_manual
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')
    # start by disabling both services
    hypertts_instance.service_manager.get_service('ServiceA').enabled = False
    hypertts_instance.service_manager.get_service('ServiceB').enabled = False

    dialog = EmptyDialog()
    dialog.setupUi()

    # model_change_callback = MockModelChangeCallback()
    configuration = component_configuration.Configuration(hypertts_instance, dialog)
    configuration.draw(dialog.getLayout())    

    if os.environ.get('HYPERTTS_CONFIGURATION_DIALOG_DEBUG', 'no') == 'yes':
        dialog.exec_()    

def test_batch_dialog_load_random(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]    

    # test saving of config
    # =====================

    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())

    # select a source field and target field
    batch.source.source_field_combobox.setCurrentText('English')
    batch.target.target_field_combobox.setCurrentText('Sound')
    
    # select random voice selection mode with two voices
    batch.voice_selection.radio_button_random.setChecked(True)
    # pick second voice and add it
    batch.voice_selection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(batch.voice_selection.add_voice_button, aqt.qt.Qt.LeftButton)
    # pick third voice and add it
    batch.voice_selection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(batch.voice_selection.add_voice_button, aqt.qt.Qt.LeftButton)

    # set profile name
    batch.profile_name_combobox.setCurrentText('batch random 1')
    qtbot.mouseClick(batch.profile_save_button, aqt.qt.Qt.LeftButton)

    assert 'batch random 1' in hypertts_instance.anki_utils.written_config[constants.CONFIG_BATCH_CONFIG]

    # test loading of config
    # ======================

    dialog = EmptyDialog()
    dialog.setupUi()
    batch = component_batch.ComponentBatch(hypertts_instance, dialog)
    batch.configure_browser(note_id_list)
    batch.draw(dialog.getLayout())    

    # dialog.exec_()

    assert batch.profile_load_button.isEnabled() == False
    # select preset
    batch.profile_name_combobox.setCurrentText('batch random 1')

    # open
    qtbot.mouseClick(batch.profile_load_button, aqt.qt.Qt.LeftButton)

    # check that the voice selection mode is random
    assert batch.get_model().voice_selection.selection_mode == constants.VoiceSelectionMode.random
    assert len(batch.get_model().voice_selection.get_voice_list()) == 2

    # apply to notes
    qtbot.mouseClick(batch.apply_button, aqt.qt.Qt.LeftButton)

    # ensure audio was applied to 2 notes
    # make sure notes were updated
    note_1 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)
    assert 'Sound' in note_1.set_values 
    note_2 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_2)
    assert 'Sound' in note_2.set_values     

    # dialog.exec_()

def test_realtime_source(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1]

    model_change_callback = MockModelChangeCallback()
    field_list = hypertts_instance.get_all_fields_from_notes(note_id_list)
    source = component_realtime_source.RealtimeSource(hypertts_instance, field_list, model_change_callback.model_updated)
    dialog.addChildLayout(source.draw())

    # dialog.exec_()

    expected_source_model = config_models.RealtimeSourceAnkiTTS()
    expected_source_model.field_name = 'Chinese'
    expected_source_model.field_type = constants.AnkiTTSFieldType.Regular

    assert source.get_model().serialize() == expected_source_model.serialize()

    # select different field
    source.source_field_combobox.setCurrentText('English')
    expected_source_model.field_name = 'English'
    assert model_change_callback.model.serialize() == expected_source_model.serialize()

    # select different field type
    source.source_field_type_combobox.setCurrentText(constants.AnkiTTSFieldType.Cloze.name)
    expected_source_model.field_type = constants.AnkiTTSFieldType.Cloze
    assert model_change_callback.model.serialize() == expected_source_model.serialize()

    # load config
    # ===========
    source_model = config_models.RealtimeSourceAnkiTTS()
    source_model.field_name = 'Pinyin'
    source_model.field_type = constants.AnkiTTSFieldType.Cloze 

    source.load_model(source_model)
    assert source.source_type_combobox.currentText() == 'AnkiTTSTag'
    assert source.source_field_combobox.currentText() == 'Pinyin'
    assert source.source_field_type_combobox.currentText() == 'Cloze'


def test_realtime_side_component(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()


    # initialize dialog
    # =================

    def existing_preset_fn(preset_name):
        pass

    note_id = config_gen.note_id_1
    note_1 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)
    model_change_callback = MockModelChangeCallback()
    realtime_side = component_realtime_side.ComponentRealtimeSide(hypertts_instance,
        constants.AnkiCardSide.Front, 0, model_change_callback.model_updated, existing_preset_fn)
    realtime_side.configure_note(note_1)
    dialog.addChildLayout(realtime_side.draw())

    # some initial checks
    assert realtime_side.get_model().side_enabled == False
    assert realtime_side.side_enabled_checkbox.isChecked() == False    
    assert realtime_side.tabs.isEnabled() == False
    assert realtime_side.preview_groupbox.isEnabled() == False

    # enable this side
    realtime_side.side_enabled_checkbox.setChecked(True)
    assert model_change_callback.model.side_enabled == True
    assert realtime_side.tabs.isEnabled() == True
    assert realtime_side.preview_groupbox.isEnabled() == True

    # dialog.exec_()

    # select a field
    realtime_side.source.source_field_combobox.setCurrentText('English')
    assert model_change_callback.model.source.field_name == 'English'
    # preview should be updated
    assert realtime_side.text_preview_label.text() == 'old people'

    # press sound preview
    qtbot.mouseClick(realtime_side.preview_sound_button, aqt.qt.Qt.LeftButton)

    # ensure sound was played
    assert hypertts_instance.anki_utils.played_sound == {
        'source_text': 'old people',
        'voice': {
            'gender': 'Male', 
            'language': 'fr_FR', 
            'name': 'voice_a_1', 
            'service': 'ServiceA',
            'voice_key': {'name': 'voice_1'}
        },
        'options': {}
    }        
    

    # dialog.exec_()

def test_realtime_component(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    # instantiate dialog
    # ==================

    note_id = config_gen.note_id_1
    note_1 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)
    realtime = component_realtime.ComponentRealtime(hypertts_instance, dialog, 0)
    realtime.configure_note(note_1)
    realtime.draw(dialog.getLayout())

    # enable TTS on each side
    # =======================

    assert realtime.apply_button.isEnabled() == False

    # enable front side, select a field
    realtime.front.side_enabled_checkbox.setChecked(True)
    realtime.front.source.source_field_combobox.setCurrentText('English')

    assert realtime.get_model().front.side_enabled == True
    assert realtime.get_model().front.source.field_name == 'English'
    assert realtime.get_model().front.source.field_type == constants.AnkiTTSFieldType.Regular

    # enable back side
    realtime.back.side_enabled_checkbox.setChecked(True)
    realtime.back.source.source_field_combobox.setCurrentText('Chinese')
    assert realtime.get_model().back.side_enabled == True
    assert realtime.get_model().back.source.field_name == 'Chinese'

    # click apply
    assert realtime.apply_button.isEnabled() == True
    qtbot.mouseClick(realtime.apply_button, aqt.qt.Qt.LeftButton)

    # assertions on config saved
    assert constants.CONFIG_REALTIME_CONFIG in hypertts_instance.anki_utils.written_config
    assert 'realtime_0' in hypertts_instance.anki_utils.written_config[constants.CONFIG_REALTIME_CONFIG]

    realtime_config_saved = hypertts_instance.anki_utils.written_config[constants.CONFIG_REALTIME_CONFIG]['realtime_0']
    assert realtime_config_saved['front']['source']['field_name'] == 'English'
    assert realtime_config_saved['back']['source']['field_name'] == 'Chinese'

    # pprint.pprint(hypertts_instance.anki_utils.written_config)

    # assertions on note type updated
    assert hypertts_instance.anki_utils.updated_note_model != None
    question_format = hypertts_instance.anki_utils.updated_note_model['tmpls'][0]['qfmt'].replace('\n', ' ')
    answer_format = hypertts_instance.anki_utils.updated_note_model['tmpls'][0]['afmt'].replace('\n', ' ')

    expected_front_tts_tag = '{{tts fr_FR hypertts_preset=Front_realtime_0 voices=HyperTTS:English}}'
    expected_back_tts_tag = '{{tts fr_FR hypertts_preset=Back_realtime_0 voices=HyperTTS:Chinese}}'

    assert expected_front_tts_tag in question_format
    assert expected_back_tts_tag in answer_format

    pprint.pprint(hypertts_instance.anki_utils.updated_note_model)

    # try to load an existing configuration
    # =====================================

    logger.info('loading an existing realtime configuration')

    # patch the config
    hypertts_instance.anki_utils.config[constants.CONFIG_REALTIME_CONFIG] = hypertts_instance.anki_utils.written_config[constants.CONFIG_REALTIME_CONFIG]

    # patch the templates
    # note_1.note_type()['tmpls'][0]['qfmt'] += '\n' + expected_front_tts_tag
    # note_1.note_type()['tmpls'][0]['afmt'] += '\n' + expected_back_tts_tag

    pprint.pprint(note_1.note_type())

    # launch dialog
    dialog = EmptyDialog()
    dialog.setupUi()
    realtime = component_realtime.ComponentRealtime(hypertts_instance, dialog, 0)
    realtime.configure_note(note_1)
    realtime.draw(dialog.getLayout())    
    realtime.load_existing_preset()

    # we haven't changed anything at this point
    assert realtime.apply_button.isEnabled() == False

    assert realtime.front.side_enabled_checkbox.isChecked() == True
    assert realtime.front.source.source_field_combobox.currentText() == 'English'
    assert realtime.front.text_preview_label.text() == 'old people'

    assert realtime.back.side_enabled_checkbox.isChecked() == True
    assert realtime.back.source.source_field_combobox.currentText() == 'Chinese'
    assert realtime.back.text_preview_label.text() == '老人家'

    # disable the front TTS tag
    realtime.front.side_enabled_checkbox.setChecked(False)

    # save
    qtbot.mouseClick(realtime.apply_button, aqt.qt.Qt.LeftButton)

    # assertions on config saved
    assert constants.CONFIG_REALTIME_CONFIG in hypertts_instance.anki_utils.written_config
    assert 'realtime_0' in hypertts_instance.anki_utils.written_config[constants.CONFIG_REALTIME_CONFIG]

    realtime_config_saved = hypertts_instance.anki_utils.written_config[constants.CONFIG_REALTIME_CONFIG]['realtime_0']
    assert realtime_config_saved['front']['side_enabled'] == False

    # assertions on note type updated
    assert hypertts_instance.anki_utils.updated_note_model != None
    assert '{{tts' not in hypertts_instance.anki_utils.updated_note_model['tmpls'][0]['qfmt']

def test_realtime_component_manual(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

    dialog = EmptyDialog()
    dialog.setupUi()

    # instantiate dialog
    # ==================

    note_id = config_gen.note_id_1
    note_1 = hypertts_instance.anki_utils.get_note_by_id(config_gen.note_id_1)
    realtime = component_realtime.ComponentRealtime(hypertts_instance, dialog, 0)
    realtime.configure_note(note_1)
    realtime.draw(dialog.getLayout())    

    if os.environ.get('HYPERTTS_REALTIME_DIALOG_DEBUG', 'no') == 'yes':
        dialog.exec_()    