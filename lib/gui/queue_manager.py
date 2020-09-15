import json
from os.path import exists
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QListWidgetItem
from multiprocess.context import Process

from lib.gui.widgets.queue_item_editor import QueueItemEditor, QueueItem
from lib.gui.threading import ThreadPool
from lib.gui.helper import safe_process_stop
import lib.logger as logging

logger = logging.get_logger(__name__)


def load_queue_list(path="settings/gui/queue_list.json"):
    """Load queue list for GUI."""
    if exists(path):
        with open(path, encoding='utf-8') as json_data:
            return json.load(json_data)


def save_queue_list(json_data, path="settings/gui/queue_list.json"):
    """Store queue list."""
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(json_data, file)


class QueueList:
    """Class for working with queue list."""

    def __init__(self, game, list_widget, run_and_stop_button, add_button, edit_button, remove_button):
        """Class initialization.

        :param QListWidget list_widget: list widget.
        :param TwoStateButton run_and_stop_button: button for running the queue.
        :param QPushButton add_button: button for adding new element to queue.
        :param QPushButton edit_button: button for editing existing element in the queue.
        :param QPushButton remove_button: button for removing existing element from the queue.
        """
        self.game = game
        self.widget = list_widget
        self.run_and_stop_button = run_and_stop_button
        self.add_button = add_button
        self.edit_button = edit_button
        self.remove_button = remove_button
        self.setup_buttons()
        self.threads = ThreadPool()
        self.process = None
        self.add_button.clicked.connect(self.add)
        if self.widget.count() == 0:
            self.run_and_stop_button.button.setEnabled(False)
        self.select_all_item = self.add_select_all_checkbox()
        self.widget.itemChanged.connect(self.on_item_change)
        self.load_queue_from_file()
        self.change_select_all_state()
        self.stop_queue_flag = False

    def queue(self):
        """Queue iterator."""
        for i in range(self.widget.count()):
            item = self.widget.item(i)
            if isinstance(item, QueueItem):
                yield item

    def add_select_all_checkbox(self):
        """Creates 'Select All' checkbox with empty line below."""
        select_all = QListWidgetItem()
        select_all.setText("[Select All]")
        select_all.setCheckState(Qt.Checked)
        select_all.setFlags(select_all.flags() | Qt.ItemIsUserCheckable)
        select_all.setFlags(select_all.flags() ^ Qt.ItemIsDragEnabled)
        select_all.setFlags(select_all.flags() ^ Qt.ItemIsSelectable)
        blank_line = QListWidgetItem()
        blank_line.setFlags(blank_line.flags() ^ Qt.ItemIsDragEnabled)
        blank_line.setFlags(blank_line.flags() ^ Qt.ItemIsSelectable)
        self.widget.addItem(select_all)
        self.widget.addItem(blank_line)
        return select_all

    def change_select_all_state(self):
        """Change 'Select All' checkbox state by queue item's states."""
        queue_states = [queue_item.checkState() for queue_item in self.queue()]
        all_checked = [state for state in queue_states if state == Qt.Checked]
        all_unchecked = [state for state in queue_states if state == Qt.Unchecked]
        partially_checked = all_checked and all_unchecked
        if all_checked and not all_unchecked:
            self.select_all_item.setCheckState(Qt.Checked)
        if all_unchecked and not all_checked:
            self.select_all_item.setCheckState(Qt.Unchecked)
        if partially_checked:
            self.select_all_item.setCheckState(Qt.PartiallyChecked)

    def on_item_change(self, item):
        """Select or deselect items when some item was checked.

        :param QListItem item: changed item.
        """
        if item == self.select_all_item:
            state = item.checkState()
            if state == Qt.Checked:
                self.select_all()
            if state == Qt.Unchecked:
                self.deselect_all()
        if isinstance(item, QueueItem):
            self.change_select_all_state()

    def load_queue_from_file(self):
        """Load queue list and apply it to GUI."""
        queue_list_settings = load_queue_list()
        if not queue_list_settings:
            return
        logger.debug(f"Loading {len(queue_list_settings)} items to queue list.")
        for settings in queue_list_settings:
            editor = QueueItemEditor.from_settings(game=self.game, settings=settings)
            item = editor.render_mode(editor.current_mode)
            item.set_checked(settings.get("checked", False))
            self._add(item)

    def save_queue_to_file(self):
        """Save existing queue."""
        queue_list_settings = []
        for item in self.queue():
            settings = {
                "mode_name": item.mode_name,
                "checked": item.is_checked,
                **item.parameters
            }
            queue_list_settings.append(settings)
        logger.debug(f"Saving queue list with {len(queue_list_settings)} items.")
        save_queue_list(queue_list_settings)

    def setup_buttons(self):
        """Setup button's events."""
        self.run_and_stop_button.connect_first_state(self.run_queue)
        self.run_and_stop_button.connect_second_state(self.stop_queue)
        self.run_and_stop_button.connect_first_state(self.widget.setDragDropMode, QAbstractItemView.NoDragDrop)
        self.run_and_stop_button.connect_second_state(self.widget.setDragDropMode, QAbstractItemView.InternalMove)
        self.remove_button.clicked.connect(self.remove_current_item)
        self.edit_button.clicked.connect(self.edit_current_item)

    def add(self):
        """Create editor window and add queue item from it."""
        editor = QueueItemEditor(game=self.game)
        editor.setWindowTitle("Add queue item")
        result = editor.exec_()
        if result and editor.queue_item:
            self._add(editor.queue_item)

    def _add(self, item):
        """Add item to queue."""
        if self.widget.count() == 2:
            self.run_and_stop_button.button.setEnabled(True)
        self.widget.addItem(item)
        self.change_select_all_state()
        return item

    def edit_current_item(self):
        """Edit current item."""
        item = self.widget.currentItem()
        if item and isinstance(item, QueueItem):
            editor = QueueItemEditor.from_result_item(game=self.game, queue_item=item)
            editor.setWindowTitle("Edit queue item")
            result = editor.exec_()
            if result and editor.queue_item:
                self.edit_item(old_item=item, new_item=editor.queue_item)

    def edit_item(self, old_item, new_item):
        """Edit queue item.

        :param old_item: item before editing.
        :param new_item: item after editing.
        """
        widget_index = self.widget.row(old_item)
        self.widget.takeItem(widget_index)
        self.widget.insertItem(widget_index, new_item)
        self.widget.setCurrentRow(widget_index)

    def remove_current_item(self):
        """Remove current item from queue."""
        item = self.widget.currentItem()
        if item and isinstance(item, QueueItem):
            self.remove_item(item)

    def remove_item(self, item):
        """Remove item from queue.

        :param item: queue item.
        """
        self.widget.takeItem(self.widget.row(item))
        self.change_select_all_state()
        if self.widget.count() == 2:
            self.run_and_stop_button.button.setEnabled(False)

    def run_queue(self):
        """Run and execute all items in queue."""
        logger.debug("Running queue.")
        self.run_and_stop_button.set_second_state()
        self.widget.setDragDropMode(QAbstractItemView.NoDragDrop)
        worker = self.threads.run_thread(target=self._run_queue, with_progress=True)
        worker.signals.finished.connect(self.run_and_stop_button.set_first_state)
        worker.signals.finished.connect(self.reset_background)
        worker.signals.progress.connect(self.mark_execution_background)

    def mark_execution_background(self, cur_index):
        """Mark execution queue items with color.

        :param cur_index: index for current item in queue.
        """
        for index, item in enumerate(self.queue()):
            if index == cur_index:
                item.setBackground(Qt.yellow)
                break
            color = Qt.green if item.is_checked else Qt.gray
            item.setBackground(color)

    def reset_background(self):
        """Reset queue colors."""
        for item in self.queue():
            item.setBackground(Qt.transparent)

    @safe_process_stop
    def stop_queue(self):
        """Stop queue execution."""
        self.widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.stop_queue_flag = True
        if self.process:
            logger.debug("Queue was forcibly stopped.")
            self.process.terminate()
        self.threads.thread_pool.clear()
        self.run_and_stop_button.set_first_state()

    def _run_queue(self, progress_callback):
        """Run item's execution.

        :param pyqtSignal progress_callback: signal to emit queue progress.
        """
        for index, item in enumerate(self.queue()):
            if self.stop_queue_flag:
                break
            progress_callback.emit(index)
            executor, settings = item.get_executor()
            if not executor:
                logger.debug(f"Skipping queue item: {item.mode_name}")
                continue
            logger.debug(f"Running {item.mode_name} with settings: {settings}")
            self.process = Process(target=executor, kwargs=settings)
            self.process.start()
            self.process.join()
        self.stop_queue_flag = False
        self.widget.setDragDropMode(QAbstractItemView.InternalMove)
        logger.debug("Queue completed.")

    def select_all(self):
        """Select all items in queue."""
        for item in self.queue():
            item.set_checked(True)

    def deselect_all(self):
        """Deselect all items in queue."""
        for item in self.queue():
            item.set_checked(False)
