from __future__ import annotations
from wowool.annotation import Concept
from wowool.apps.contact_info.app_id import APP_ID
from wowool.diagnostic import Diagnostics
from wowool.document.analysis.document import AnalysisDocument
import logging
from wowool.annotation.concept import Concept

from wowool.string import to_text
from typing import Iterator, List, Union, Iterator
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
    check_requires_concepts,
)

logger = logging.getLogger(__name__)


uris = set(["Person", "Company", "City", "Address", "PhoneNr"])
default_contact_uris = set(["Person", "Company", "City"])


def aggregate_contact(contacts, contact_info_section):
    entry = contact_info_section["entry"] if "entry" in contact_info_section else None
    if entry:
        if entry not in contacts:
            contacts[entry] = contact_info_section
        else:
            contacts[entry] = {**contacts[entry], **contact_info_section}


def top_level_candidate(concepts) -> Iterator[Concept]:
    idx = 0
    length = len(concepts)
    while idx < length:
        yield concepts[idx]
        next_idx = idx + 1
        while next_idx < length and concepts[idx].end_offset >= concepts[next_idx].end_offset:
            next_idx += 1
        idx = next_idx


class ContactInfo:
    ID = APP_ID

    def __init__(self, contact_uris: Union[List[str], None] = None):
        """
        Initialize the Contact-Info application.
        """
        self.contact_uris = contact_uris if contact_uris != None else default_contact_uris

    def is_contact(self, concept: Concept) -> bool:
        return concept.uri in self.contact_uris

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        :param document:  The document we want to collect the contact info.
        :type document: AnalysisDocument

        :returns: The given document with the quotes. See the :ref:`json format <json_apps_quotes>`

        """
        assert document.analysis != None, f"Missing Document analysis for {document.id}"
        contacts = {}
        contact_info = {}
        contacts = {}
        nrof_lines_with_no_info = 0
        for idx, sent in enumerate(document.analysis):
            candidates = [concept for concept in Concept.iter(sent, lambda concept: concept.uri in uris)]
            if len(candidates):
                for concept in top_level_candidate(candidates):
                    if self.is_contact(concept):
                        aggregate_contact(contacts, contact_info)
                        contact_info = {}
                        contact_info["type"] = concept.uri
                        contact_info["entry"] = concept.canonical

                for concept in top_level_candidate(candidates):
                    contact_info[concept.uri] = concept.canonical
                    for key, values in concept.attributes.items():
                        contact_info[f"{concept.uri}.{key}"] = values[0]
            else:
                nrof_lines_with_no_info += 1
                if nrof_lines_with_no_info >= 2:
                    aggregate_contact(contacts, contact_info)
                    contact_info = {}
                    # new person.

        aggregate_contact(contacts, contact_info)
        document.analysis.reset()
        app_results = []
        for k, v in contacts.items():
            app_results.append(v)

        document.add_results(APP_ID, app_results)
        return document
