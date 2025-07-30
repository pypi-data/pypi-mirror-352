"""
ReplaceMarkersInDocxAJM.py

This module provides a class, `ReplaceMarkersInDocx`, that facilitates the process of manipulating placeholders
referred to as "mail merge markers" in a Word document (.docx). It offers features for extracting and replacing
these markers, ensuring seamless customization of document templates used in mail merges or similar scenarios.

Key Features:
- Extract mail merge markers from different parts of a Word document, including paragraphs, headers, and footers.
- Replace markers dynamically with values from an external dictionary (`info_dict`), allowing for the generation
  of customized output documents.
- Validate the integrity of the information dictionary (`info_dict`) against the markers present in the document.
- Modify document styles and alignments based on specific markers.

Dependencies:
- `python-docx` library for manipulating Word documents.
- `abc` module for abstract method definitions.
- `re` module for regular expression handling.

Classes:
- `ReplaceMarkersInDocx`: The main class containing methods and properties to handle placeholders (markers)
  within a Word document. This class also supports customization through class-level constants and initialization
  parameters.

Usage:
The `ReplaceMarkersInDocx` class is designed to be extended for specific use cases. Subclasses should implement
the `standardize_paragraph_style` abstract method as per the desired functionality.

Example:
This module is commonly used to replace placeholders in document templates such as:
- Generating personalized letters.
- Populating certificates with specific recipient information.
- Dynamically modifying document content for mail merge operations.

"""

import re
from abc import abstractmethod


class ReplaceMarkersInDocx:
    """
    This code defines a class ReplaceMarkersInDocx with methods to extract and replace markers in a Word document.
     It includes properties to retrieve mail merge markers and keys,
     as well as methods for replacing markers in paragraphs and the entire document.

    The mail_merge_markers property extracts markers from the paragraphs of the document and returns them as a set.

    The mail_merge_keys property returns a set of mail merge keys extracted from the mail merge markers.

    The replace_markers method replaces markers in the Word document with values from a dictionary.
    It handles permission errors during saving and AttributeError if the info_dict attribute is not set or invalid.

    The class assumes the existence of attributes like
    _mail_merge_markers, U_CODES_MARKERS, document, and logger for its functioning.

    """
    U_CODES_MARKERS = {'right': '\u00BB', 'left': '\u00AB'}

    def __init__(self, document, logger, info_dict: dict = None, **kwargs):
        self._info_dict = info_dict
        self._mail_merge_markers = set()
        self._mail_merge_keys = set()
        self.Document = document
        self._logger = logger

        self.skip_info_validation = kwargs.get('skip_info_validation', False)
        self._check_main_doc_section_for_markers = kwargs.get('check_main_doc_section_for_markers', True)
        self._check_header_footer_for_markers = kwargs.get('check_header_footer_for_markers', False)

    @abstractmethod
    def standardize_paragraph_style(self, paragraph, **kwargs):
        """
        :param paragraph: The paragraph to be standardized in terms of style.
        :type paragraph: str
        :param kwargs: Optional keyword arguments for customizing the standardization process.
        :type kwargs: dict
        :return: This method is abstract and must be implemented in a subclass.
        :rtype: None
        """
        raise NotImplementedError('This method needs to be implemented in a subclass')

    @property
    def info_dict(self):
        """
        :return: The getter method for accessing the information dictionary.
        :rtype: dict
        """
        return self._info_dict

    @info_dict.setter
    def info_dict(self, value):
        if not self.skip_info_validation:
            if set(value.keys()) != self.mail_merge_keys:
                error_message = f"Keys for info_dict must match mail merge keys {self.mail_merge_keys}"
                self._logger.error(error_message)
                raise AttributeError(error_message)
            print("info dict value validated successfully.")
            self._logger.debug("info dict value validated successfully.")
        self._info_dict = value

    def _get_header_footer_in_section(self, section):
        headers = []
        footers = []
        for x in section.header.paragraphs:
            headers.extend(self._multi_marker_line(x))
        for x in section.footer.paragraphs:
            footers.extend(self._multi_marker_line(x))
        return set(headers), set(footers)

    def _get_main_doc_section_mail_markers(self):
        main_doc = {tuple(self._multi_marker_line(x)) for x in self.Document.paragraphs}
        p1 = {x[0] for x in main_doc if x}
        p2 = {x[1] for x in main_doc if x and len(x) == 2}
        main_doc = p1 | p2
        return main_doc

    def _multi_marker_line(self, para):
        found_markers = []
        if self.__class__.U_CODES_MARKERS['left'] in para.text.strip():
            found_markers.append(para.text.strip()[para.text.strip().index(
                self.__class__.U_CODES_MARKERS['left']):
                                                   (para.text.strip().index(
                                                       self.__class__.U_CODES_MARKERS['right']) + 1)])

            remaining_text = para.text.strip()[para.text.strip().index(
                self.__class__.U_CODES_MARKERS['right']) + 1:]
            if self.__class__.U_CODES_MARKERS['left'] in remaining_text:
                found_markers.append(remaining_text.strip()[
                                     remaining_text.strip().index(
                                         self.__class__.U_CODES_MARKERS['left']):
                                     (remaining_text.strip().index(
                                         self.__class__.U_CODES_MARKERS['right']) + 1)])
        return found_markers

    def _fetch_mail_merge_markers(self):
        main_doc = set()
        header_footer = set()

        if self._check_main_doc_section_for_markers:
            main_doc = self._get_main_doc_section_mail_markers()
        if self._check_header_footer_for_markers:
            for section in self.Document.sections:
                headers, footers = self._get_header_footer_in_section(section)

                # The |= operator in Python is an in-place union operator used with sets.
                # It is a shorthand for performing a union operation between sets and
                # updating the first set with the result of the union.
                header_footer |= headers
                header_footer |= footers

        # returns one NEW combined set (unlike |=) above
        return main_doc | header_footer

    @property
    def mail_merge_markers(self):
        """
        This code defines a property named 'mail_merge_markers' that returns a set of markers extracted from the
        paragraphs of a document.

        Attributes:
            - _mail_merge_markers: A private attribute that stores the extracted markers.

        Methods:
            - mail_merge_markers (): A property getter method that returns the extracted markers.

        Algorithm/Explanation: - The method first checks if the _mail_merge_markers attribute is already populated.
        If it is, it returns the existing value. - If _mail_merge_markers is empty, the code iterates through all the
        paragraphs in the 'document' object. - For each paragraph, it checks if the left marker Unicode character is
        present in the text. - If the left marker character is found, it extracts the substring between the left and
        right marker characters, trims any leading or trailing whitespace, and adds it to the set of markers. - The
        method then returns the set of extracted markers.

        Note:
            - The code assumes the existence of the following attributes:
                - _mail_merge_markers: A set to store the extracted markers.
                - U_CODES_MARKERS: A dictionary containing Unicode characters for left and right markers.
                - document: An object representing the document to extract markers from.

        Example usage:
            # Assuming an instance of the class that contains 'mail_merge_markers' property:
            obj = MyClass()
            markers = obj.mail_merge_markers
            print(markers)  # Output: {'[[', ']]'}
        """
        if self._mail_merge_markers:
            pass
        else:
            self._mail_merge_markers = self._fetch_mail_merge_markers()
        return self._mail_merge_markers

    @property
    def mail_merge_keys(self):
        """
        Returns a set of mail merge keys.

        If the `mail_merge_markers` attribute is not empty, this method extracts the keys from it and returns a set
        containing them.

        Returns:
            set: A set of mail merge keys extracted from `mail_merge_markers` attribute.

        """
        if self.mail_merge_markers:
            return {x[1:-1] for x in self.mail_merge_markers}
        return set()

    @staticmethod
    def _handle_marker_edge_case(marker, paragraph, replacement_text):
        # noinspection GrazieInspection
        """designed to be overwritten, Used for handling markers that need some other processing,
                not just a simple replacement (i.e. paragraph alignment etc.).

                ex:          if marker[1:-1] == 'Document_Number':
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    replacement_text = f'\t{replacement_text}'
                """
        return replacement_text, paragraph

    def _replace_matched_marker(self, paragraph, marker, marker_pattern):
        """
        Replace the text matched with the marker in the paragraph using the information from the info dictionary.
         If the marker corresponds to 'Document_Number', set the alignment of the paragraph to center and prepend a tab
          to the replacement text.
          Finally, update the paragraph text by substituting the marker with the replacement text
          after removing any leading or trailing whitespaces.
        """
        replacement_text = str(self.info_dict[marker[1:-1]]).strip()
        replacement_text, paragraph = self._handle_marker_edge_case(marker, paragraph, replacement_text)
        # adding str.strip() to replacement_text and p.text
        # removed the erroneous whitespace in the output doc
        paragraph.text = re.sub(marker_pattern, replacement_text.strip(), paragraph.text.strip())

    def _replace_markers_in_paragraph(self, paragraph):
        paragraph_replacement_counter = 0
        for marker in self.mail_merge_markers:
            marker_pattern = re.escape(marker)
            if re.search(marker_pattern, paragraph.text):
                self.standardize_paragraph_style(paragraph, only_font=True)
                self._replace_matched_marker(paragraph, marker, marker_pattern)
                paragraph_replacement_counter += 1

        return paragraph_replacement_counter

    def replace_markers(self, **kwargs):
        """
        This method is used to replace markers in a given Word document's
        main body (by default) with the corresponding values from a dictionary.

        Parameters:
        - None

        Returns:
        - None

        Exceptions:
        - PermissionError: if there is a permission error while saving the document
        - AttributeError: if self.employee_id is not set or is invalid

        """
        paragraphs = kwargs.get('paragraphs', self.Document.paragraphs)
        if self.info_dict:
            replacement_counter = 0
            for p in paragraphs:
                # Find and replace markers within the paragraph
                pr_counter = self._replace_markers_in_paragraph(p)
                replacement_counter += pr_counter
            info_str = f'{replacement_counter} marker(s) replaced in {self.Document}.'
            self._logger.info(info_str)
        else:
            raise AttributeError('self.info_dict is empty. This method can only be used if the info_dict is not empty.')

    def replace_all_markers(self):
        """
        Method to replace all markers within the document including the headers and footers.
        Iterates through each section in the document and replaces markers in
        the section's header and footer paragraphs as well.
        """
        self.replace_markers()
        for section in self.Document.sections:
            self.replace_markers(paragraphs=section.header.paragraphs)
            self.replace_markers(paragraphs=section.footer.paragraphs)
