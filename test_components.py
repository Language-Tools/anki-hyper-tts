import PyQt5
import config_models
import servicemanager
import testing_utils
import hypertts
import constants
import component_voiceselection
import component_source
import component_target

class EmptyDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self):
        super(PyQt5.QtWidgets.QDialog, self).__init__()

    def setupUi(self):
        self.main_layout = PyQt5.QtWidgets.QVBoxLayout(self)

    def getLayout(self):
        return self.main_layout

def get_hypertts_instance():
    # return hypertts_instance    
    config_gen = testing_utils.TestConfigGenerator()
    return config_gen.build_hypertts_instance_test_servicemanager('default')


def test_voice_selection_defaults_single(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )    
    voiceselection.draw(dialog.getLayout())

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
    
def test_voice_selection_single_1(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )    
    voiceselection.draw(dialog.getLayout())

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
    speaking_rate_widget = dialog.findChild(PyQt5.QtWidgets.QDoubleSpinBox, "voice_option_speaking_rate")
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

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )    
    voiceselection.draw(dialog.getLayout())

    # choose random mode
    # qtbot.mouseClick(voiceselection.radio_button_random, PyQt5.QtCore.Qt.LeftButton)
    voiceselection.radio_button_random.setChecked(True)

    # pick second voice and add it
    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, PyQt5.QtCore.Qt.LeftButton)

    # pick third voice and add it
    voiceselection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, PyQt5.QtCore.Qt.LeftButton)    

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

def test_voice_selection_random_2(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )    
    voiceselection.draw(dialog.getLayout())

    # choose random mode
    voiceselection.radio_button_random.setChecked(True)

    # add the first voice twice, but with different options
    voiceselection.voices_combobox.setCurrentIndex(0)
    qtbot.mouseClick(voiceselection.add_voice_button, PyQt5.QtCore.Qt.LeftButton)

    # change options
    speaking_rate_widget = dialog.findChild(PyQt5.QtWidgets.QDoubleSpinBox, "voice_option_speaking_rate")
    speaking_rate_widget.setValue(0.25)    

    # add again
    qtbot.mouseClick(voiceselection.add_voice_button, PyQt5.QtCore.Qt.LeftButton)

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

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )    
    voiceselection.draw(dialog.getLayout())

    # choose random mode
    # qtbot.mouseClick(voiceselection.radio_button_random, PyQt5.QtCore.Qt.LeftButton)
    voiceselection.radio_button_priority.setChecked(True)

    # dialog.exec_()

    # pick second voice and add it
    voiceselection.voices_combobox.setCurrentIndex(1) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, PyQt5.QtCore.Qt.LeftButton)

    # pick third voice and add it
    voiceselection.voices_combobox.setCurrentIndex(2) # pick second voice
    qtbot.mouseClick(voiceselection.add_voice_button, PyQt5.QtCore.Qt.LeftButton)    

    expected_model = config_models.VoiceSelectionPriority()
    voice_2 = [x for x in hypertts_instance.service_manager.full_voice_list() if x.service.name == 'ServiceA' and x.name == 'voice_a_2'][0]
    voice_3 = [x for x in hypertts_instance.service_manager.full_voice_list() if x.service.name == 'ServiceA' and x.name == 'voice_a_3'][0]

    expected_model.add_voice(config_models.VoiceWithOptionsPriority(voice_2, {}))
    expected_model.add_voice(config_models.VoiceWithOptionsPriority(voice_3, {}))

    assert voiceselection.voice_selection_model.serialize() == expected_model.serialize()

    # dialog.exec_()


def test_voice_selection_filters(qtbot):
    manager = servicemanager.ServiceManager(testing_utils.get_test_services_dir(), 'test_services')
    manager.init_services()
    manager.get_service('ServiceA').set_enabled(True)
    manager.get_service('ServiceB').set_enabled(True)
    anki_utils = testing_utils.MockAnkiUtils({})

    hypertts_instance = hypertts.HyperTTS(anki_utils, manager)

    dialog = EmptyDialog()
    dialog.setupUi()

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )    
    voiceselection.draw(dialog.getLayout())

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
        assert voice.language.lang == constants.Language.ja

    # reset filters
    qtbot.mouseClick(voiceselection.reset_filters_button, PyQt5.QtCore.Qt.LeftButton)

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
    qtbot.mouseClick(voiceselection.reset_filters_button, PyQt5.QtCore.Qt.LeftButton)
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
        assert voice.language.lang == constants.Language.ja

    # reset filters again
    qtbot.mouseClick(voiceselection.reset_filters_button, PyQt5.QtCore.Qt.LeftButton)    

    # select random mode and add some voices
    # ======================================


    # dialog.exec_()

def test_voice_selection_samples(qtbot):
    hypertts_instance = get_hypertts_instance()

    dialog = EmptyDialog()
    dialog.setupUi()

    voiceselection = component_voiceselection.VoiceSelection(hypertts_instance)
    voiceselection.configure(
        ['Bonjour', 'Comment allez vous?', 'Au revoir']
    )
    voiceselection.draw(dialog.getLayout())

    qtbot.mouseClick(voiceselection.play_sample_button, PyQt5.QtCore.Qt.LeftButton)

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

def test_batch_source_1(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]

    batch_source = component_source.BatchSource(hypertts_instance, note_id_list)
    batch_source.draw(dialog.getLayout())

    # the field selected should be "Chinese"
    expected_source_model = config_models.BatchSource()
    expected_source_model.mode = constants.BatchMode.simple
    expected_source_model.source_field = 'Chinese'

    assert batch_source.batch_source_model.serialize() == expected_source_model.serialize()

    # select another field, 'English'
    batch_source.source_field_combobox.setCurrentText('English')
    expected_source_model.source_field = 'English'

    assert batch_source.batch_source_model.serialize() == expected_source_model.serialize()

    # select template mode
    batch_source.batch_mode_combobox.setCurrentText('template')

    # enter template format
    qtbot.keyClicks(batch_source.simple_template_input, '{Chinese}')

    expected_source_model = config_models.BatchSource()
    expected_source_model.mode = constants.BatchMode.template
    expected_source_model.source_template = '{Chinese}'
    expected_source_model.template_format_version = constants.TemplateFormatVersion.v1

    assert batch_source.batch_source_model.serialize() == expected_source_model.serialize()


    # dialog.exec_()

def test_target(qtbot):
    config_gen = testing_utils.TestConfigGenerator()
    hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')    

    dialog = EmptyDialog()
    dialog.setupUi()

    note_id_list = [config_gen.note_id_1, config_gen.note_id_2]

    batch_target = component_target.BatchTarget(hypertts_instance, note_id_list)
    batch_target.draw(dialog.getLayout())

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

    model = config_models.BatchTarget('Chinese', False, True)
    batch_target.load_model(model)

    assert batch_target.target_field_combobox.currentText() == 'Chinese'
    assert batch_target.radio_button_sound_only.isChecked() == True
    assert batch_target.radio_button_remove_sound.isChecked() == True

    model = config_models.BatchTarget('Pinyin', True, True)
    batch_target.load_model(model)

    assert batch_target.target_field_combobox.currentText() == 'Pinyin'
    assert batch_target.radio_button_sound_only.isChecked() == False
    assert batch_target.radio_button_remove_sound.isChecked() == True