from abc import abstractmethod
from re import Pattern
from typing import Optional, Tuple

import docx


class ReplaceMarkersInDocx:
    U_CODES_MARKERS:dict = None
    def __init__(self, document: docx.Document, logger, info_dict:dict = None, **kwargs):
        self._info_dict = info_dict
        self._mail_merge_markers: Optional[set] = None
        self._mail_merge_keys: Optional[set] = None
        self.document = document
        self._logger = logger
        self._check_main_doc_section_for_markers: bool = None
        self._check_header_footer_for_markers: bool = None
        self.skip_info_validation: bool = None

    @abstractmethod
    def standardize_paragraph_style(self, paragraph:docx.text.Paragraph, **kwargs):
        ...

    @property
    def info_dict(self) -> dict:
        ...

    # noinspection PyUnresolvedReferences
    @info_dict.setter
    def info_dict(self, value):
        ...

    def _get_header_footer_in_section(self, section: docx.text.Section) -> Tuple[set, set]:
        ...

    def _get_main_doc_section_mail_markers(self) -> set:
        ...

    def _multi_marker_line(self, para: docx.text.Paragraph) -> list:
        ...

    def _fetch_mail_merge_markers(self) -> dict:
        ...

    @property
    def mail_merge_markers(self) -> dict:
        ...

    @property
    def mail_merge_keys(self) -> dict:
        ...

    @staticmethod
    def _handle_marker_edge_case(marker, paragraph: docx.text.Paragraph,
                                 replacement_text: str) -> Tuple[str, docx.text.Paragraph]:
        ...

    def _replace_matched_marker(self, paragraph:docx.text.Paragraph, marker:str, marker_pattern:Pattern):
        ...

    def _replace_markers_in_paragraph(self, paragraph:docx.text.Paragraph) -> int:
        ...

    def replace_markers(self, **kwargs) -> None:
        ...