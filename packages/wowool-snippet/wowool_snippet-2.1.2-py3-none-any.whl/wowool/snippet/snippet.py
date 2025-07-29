from wowool.diagnostic import Diagnostics
from wowool.document.analysis.document import AnalysisDocument
from wowool.native.core import Domain
from wowool.native.core.engine import Engine
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)
from wowool.snippet.app_id import APP_ID


class Snippet:

    ID = APP_ID
    docs = """
# Snippet Application

## Arguments
- `source` (str): The Wowool source code

## Example
One or more Adjectives followed by a Noun:

    rule: { (Adj)+ Nn  } = AdjNoun;

"""

    def __init__(self, source: str, engine: Engine):
        """
        Initialize the Snippet application

        :param source: The Wowool source code
        :param source: str
        """
        self.domain = Domain(source=source, engine=engine, cache=False, disable_plugin_calls=True)

    @property
    def concepts(self):
        return self.domain.concepts

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        :param document: The document to be processed and enriched with the annotations from the snippet
        :type document: Document

        :returns: The given document with the new annotations. See the :ref:`JSON format <json_apps_snippet>`
        """
        document = self.domain(document)
        return document
