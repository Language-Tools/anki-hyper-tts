import sys
import aqt.qt
import time
import html

from . import root_logger

logger = root_logger.getChild(__name__)
constants = __import__('constants', globals(), locals(), [], sys._addon_import_level_base)
component_common = __import__('component_common', globals(), locals(), [], sys._addon_import_level_base)
batch_status = __import__('batch_status', globals(), locals(), [], sys._addon_import_level_base)


class BatchPreviewTableModel(aqt.qt.QAbstractTableModel):
    def __init__(self, batch_status):
        aqt.qt.QAbstractTableModel.__init__(self, None)
        self.batch_status = batch_status
        self.note_id_header = 'Note Id'
        self.source_text_header = 'Source Text'
        self.processed_text_header = 'Processed Text'
        self.status_header = 'Status'

    def flags(self, index):
        return aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled

    def rowCount(self, parent):
        # logger.debug('SourceTextPreviewTableModel.rowCount')
        return len(self.batch_status.note_id_list)

    def columnCount(self, parent):
        # logger.debug('SourceTextPreviewTableModel.columnCount')
        return 4
    
    def notifyChange(self, row):
        start_index = self.createIndex(row, 0)
        end_index = self.createIndex(row, 2)
        self.dataChanged.emit(start_index, end_index, [aqt.qt.Qt.ItemDataRole.DisplayRole])

    def data(self, index, role):
        if role != aqt.qt.Qt.ItemDataRole.DisplayRole:
            return None
        # logger.debug('SourceTextPreviewTableModel.data')
        if not index.isValid():
            return aqt.qt.QVariant()
        data = None
        note_status = self.batch_status[index.row()]
        if index.column() == 0:
            data = note_status.note_id
        elif index.column() == 1:
            data = note_status.source_text
        elif index.column() == 2:
            data = note_status.processed_text            
        elif index.column() == 3:
            if note_status.status != None:
                data = note_status.status.name
        if data != None:
            return aqt.qt.QVariant(data)
        return aqt.qt.QVariant()

    def headerData(self, col, orientation, role):
        # logger.debug('SourceTextPreviewTableModel.headerData')
        if orientation == aqt.qt.Qt.Orientation.Horizontal and role == aqt.qt.Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return aqt.qt.QVariant(self.note_id_header)
            elif col == 1:
                return aqt.qt.QVariant(self.source_text_header)
            elif col == 2:
                return aqt.qt.QVariant(self.processed_text_header)
            elif col == 3:
                return aqt.qt.QVariant(self.status_header)
        return aqt.qt.QVariant()

class BatchPreview(component_common.ComponentBase):
    def __init__(self, hypertts, note_id_list, sample_selection_fn, batch_start_fn, batch_end_fn):
        self.hypertts = hypertts
        self.note_id_list = note_id_list
        self.sample_selection_fn = sample_selection_fn
        self.batch_start_fn = batch_start_fn
        self.batch_end_fn = batch_end_fn

        self.batch_status = batch_status.BatchStatus(hypertts.anki_utils, note_id_list, self)
        self.batch_preview_table_model = BatchPreviewTableModel(self.batch_status)

        # create certain widgets right away
        self.stack = aqt.qt.QStackedWidget()
        self.progress_bar = aqt.qt.QProgressBar()
        self.progress_bar.setMaximum(len(self.note_id_list))        

        self.selected_row = None

        self.apply_to_notes_batch_started = False

    def load_model(self, model):
        self.batch_model = model
        self.hypertts.anki_utils.run_in_background(self.update_batch_status_task, self.update_batch_status_task_done)

    def update_batch_status_task(self):
        if self.batch_status.is_running():
            # stop current batch
            self.batch_status.stop()
        while self.batch_status.is_running():
            time.sleep(0.1)

        logger.info('update_batch_status_task')
        if self.batch_model.text_processing != None:
            self.hypertts.populate_batch_status_processed_text(self.note_id_list, self.batch_model.source, self.batch_model.text_processing, self.batch_status)

    def update_batch_status_task_done(self, result):
        logger.info('update_batch_status_task_done')

    def draw(self):
        # populate processed text

        self.batch_preview_layout = aqt.qt.QVBoxLayout()
        self.table_view = aqt.qt.QTableView()
        self.table_view.setModel(self.batch_preview_table_model)
        self.table_view.setSelectionMode(aqt.qt.QTableView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(aqt.qt.QTableView.SelectionBehavior.SelectRows)
        self.table_view.selectionModel().selectionChanged.connect(self.selection_changed)
        self.batch_preview_layout.addWidget(self.table_view, stretch=1)
        
        self.error_label = aqt.qt.QLabel()
        self.error_label.setWordWrap(True)
        self.batch_preview_layout.addWidget(self.error_label)

        # create stack of widgets which will be toggled when we're running the batch
        self.batchNotRunningStack = aqt.qt.QWidget()
        self.batchRunningStack = aqt.qt.QWidget()
        self.batchCompletedStack = aqt.qt.QWidget()


        # populate the "notRunning" stack
        notRunningLayout = aqt.qt.QVBoxLayout()
        self.batchNotRunningStack.setLayout(notRunningLayout)

        # poulate the "running" stack
        runningLayout = aqt.qt.QVBoxLayout()
        self.stop_button = aqt.qt.QPushButton('Stop')
        runningLayout.addWidget(self.stop_button)
        runningLayout.addWidget(self.progress_bar)
        self.batchRunningStack.setLayout(runningLayout)

        # populate the completed stack
        completedLayout = aqt.qt.QVBoxLayout()
        label = aqt.qt.QLabel(constants.GUI_TEXT_BATCH_COMPLETED)
        label.setWordWrap(True)
        completedLayout.addWidget(label)
        self.batchCompletedStack.setLayout(completedLayout)

        self.stack.addWidget(self.batchNotRunningStack)
        self.stack.addWidget(self.batchRunningStack)
        self.stack.addWidget(self.batchCompletedStack)
        self.show_not_running_stack()
        self.batch_preview_layout.addWidget(self.stack)

        # wire events
        self.stop_button.pressed.connect(self.stop_button_pressed)

        return self.batch_preview_layout

    def show_not_running_stack(self):
        self.stack.setCurrentIndex(0)
        self.progress_bar.setValue(0)

    def show_running_stack(self):
        self.stack.setCurrentIndex(1)

    def show_completed_stack(self):
        self.stack.setCurrentIndex(2)

    def selection_changed(self):
        logger.info('selection_changed')
        self.report_sample_text()
        self.update_error_label_for_selected()

    def report_sample_text(self):
        note_status = self.get_selected_note_status()
        if note_status != None:
            text = note_status.processed_text
            self.sample_selection_fn(note_status.note_id, text)

    def update_error_label_for_selected(self):
        note_status = self.get_selected_note_status()
        if note_status != None:        
            if note_status.status == constants.BatchNoteStatus.Error:
                # show error label
                self.error_label.setText('<b>Error:</b> ' + html.escape(str(note_status.error)))
            else:
                self.error_label.setText('')

    def get_selected_note_status(self):
        row_indices = self.table_view.selectionModel().selectedIndexes()
        if len(row_indices) >= 1:
            self.selected_row = row_indices[0].row()
            return self.batch_status[self.selected_row]
        return None

    def apply_audio_to_notes(self):
        self.apply_to_notes_batch_started = True
        self.hypertts.anki_utils.run_in_background(self.load_audio_task, self.load_audio_task_done)

    def stop_button_pressed(self):
        self.batch_status.stop()

    def load_audio_task(self):
        logger.info('load_audio_task')
        self.hypertts.process_batch_audio(self.note_id_list, self.batch_model, self.batch_status)

    def load_audio_task_done(self, result):
        logger.info('load_audio_task_done')


    def batch_start(self):
        self.hypertts.anki_utils.run_on_main(self.show_running_stack)
        self.hypertts.anki_utils.run_on_main(self.batch_start_fn)

    def batch_end(self, completed):
        if completed and self.apply_to_notes_batch_started == True:
            self.hypertts.anki_utils.run_on_main(self.show_completed_stack)
        else:
            self.hypertts.anki_utils.run_on_main(self.show_not_running_stack)
        if self.apply_to_notes_batch_started:
            self.batch_end_fn(completed)

    def update_progress_bar(self, row):
        self.progress_bar.setValue(row + 1)

    def batch_change(self, note_id, row):
        # logger.info(f'change_listener row {row}')
        self.batch_preview_table_model.notifyChange(row)
        self.hypertts.anki_utils.run_on_main(lambda: self.update_progress_bar(row))
        if row == self.selected_row:
            self.hypertts.anki_utils.run_on_main(self.update_error_label_for_selected)