import ast
import tokenize
from io import TextIOWrapper

from gi.repository import Geany as geany
from gi.repository import Peasy as peasy
from inspectortiger.session import Session


class InspectorTigerGeanyInterface(peasy.Plugin):
    def do_enable(self):
        self.session = Session()
        self.session.start()
        return True

    def do_disable(self):
        pass

    def on_document_notify(self, _, document):
        if document.file_type.id != geany.FiletypeID.FILETYPES_PYTHON:
            return False

        filename = document.real_path or document.file_name
        source = document.editor.sci.get_contents(
            document.editor.sci.get_length() + 1
        ).strip()
        try:
            source = ast.parse(source)
        except (TypeError, SyntaxError):
            return False

        geany.msgwin_clear_tab(geany.MessageWindowTabNum.MESSAGE)
        inspections = self.session.single_inspection(source)
        for plugin, reports in inspections.items():
            for report in reports:
                geany.msgwin_msg_add_string(
                    geany.MsgColors.RED,
                    report.lineno,
                    document,
                    f"Inspector Tiger [{report.plugin}] - {report.lineno}:{report.column} - {report.code}",
                )
        if inspections:
            geany.msgwin_switch_tab(geany.MessageWindowTabNum.MESSAGE, False)
        return False
