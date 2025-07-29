from wowool.diagnostic import Diagnostics
from wowool.document.analysis.document import AnalysisDocument
from wowool.annotation import Concept
from wowool.string import canonicalize
import logging
from typing import cast, List, Optional
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
    check_requires_concepts,
)
from wowool.sentiments.app_id import APP_ID

logger = logging.getLogger(__name__)


sentiment_uri = set(["PositiveSentiment", "NegativeSentiment"])


def is_sentiment(concept):
    return concept.uri in sentiment_uri


uri_mappings = {
    "PositiveSentiment": "positive",
    "NegativeSentiment": "negative",
    "SentimentObject": "object",
    "AdjPos": "adjective",
    "AdjNeg": "adjective",
    "VerbNeg": "verb",
    "VerbPos": "verb",
    "NounNeg": "noun",
    "NounPos": "noun",
    "ExprNeg": "expression",
    "ExprPos": "expression",
}

sentiment_parts_uri = set(uri_mappings.keys())


def is_sentiment_part(concept):
    return concept.uri in sentiment_parts_uri


def _mapping(uri):
    return uri_mappings.get(uri, uri)


def _calculate(positive, negative, sentiments):
    total = positive + negative
    if total == 0:
        return 0, 0
    return round((positive / total) * 100, 1), round((negative / total) * 100, 1)


class Sentiments:
    ID = APP_ID

    def __init__(self, context: Optional[List[int]] = None):
        self.context = context
        if self.context:
            if self.context != [0]:
                raise RuntimeError("Not implemented yet, context can only be the current sentence.")

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        :param document:  The document we want to enrich with sentiments information.
        :type document: AnalysisDocument

        :returns: The given document with the result data. See the :ref:`json format <json_apps_sentiments>`
        """

        check_requires_concepts(self.ID, document, diagnostics, sentiment_uri)

        sentiments = []
        positive = 0.0
        negative = 0.0
        # document = self.domain(document)
        for sent in document.analysis:
            for scope in Concept.iter(sent, is_sentiment):
                sentiment_polarity = _mapping(scope.uri)
                sentiment = {
                    "polarity": sentiment_polarity,
                    "text": canonicalize(scope),
                    "begin_offset": scope.begin_offset,
                    "end_offset": scope.end_offset,
                }
                if sentiment_polarity == "positive":
                    positive += 1.0
                elif sentiment_polarity == "negative":
                    negative += 1.0

                logger.debug(f"Sentiment:, {scope.uri}, {scope.literal}")
                for concept in Concept.iter(scope, is_sentiment_part):
                    logger.debug(f" -  {concept.uri}, {concept.literal}")
                    text = concept.canonical
                    if concept.uri == "SentimentObject":
                        person = concept.Person
                        if person:
                            text = cast(Concept, person).canonical
                    else:
                        for k, v in concept.attributes.items():
                            sentiment[_mapping(k)] = v[0]

                    sentiment[_mapping(concept.uri)] = text
                    if self.context:
                        if self.context == [0]:
                            sentiment["context"] = sent.text
                        else:
                            raise RuntimeError("Not implemented yet")
                sentiments.append(sentiment)
        positive, negative = _calculate(positive, negative, sentiments)
        positive, negative = _calculate(positive, negative, sentiments)
        document.add_results(
            self.ID,
            {"positive": positive, "negative": negative, "locations": sentiments},
        )
        return document
