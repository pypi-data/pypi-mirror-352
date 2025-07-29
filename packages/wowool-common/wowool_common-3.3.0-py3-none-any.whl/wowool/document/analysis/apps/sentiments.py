# {"positive": positive, "negative": negative, "sentiments": sentiments},

from dataclasses import dataclass, field


@dataclass
class Sentiment:
    polarity: str
    text: str
    begin_offset: int
    end_offset: int
    object: str | None = None
    adjective: str | None = None
    expression: str | None = None
    comp: str | None = None
    verb: str | None = None


@dataclass
class SentimentResults:
    positive: float
    negative: float
    locations: list[Sentiment] = field(default_factory=list)


def convert_sentiments(jo_sentiments: dict) -> SentimentResults:

    sentiments = SentimentResults(
        positive=jo_sentiments.get("positive", 0.0),
        negative=jo_sentiments.get("negative", 0.0),
    )

    for s in jo_sentiments["sentiments"]:
        sentiment = Sentiment(
            polarity=s["polarity"],
            text=s["text"],
            begin_offset=s["begin_offset"],
            end_offset=s["end_offset"],
            object=s.get("object"),
            adjective=s.get("adjective"),
            expression=s.get("expression"),
            comp=s.get("comp"),
            verb=s.get("verb"),
        )
        sentiments.locations.append(sentiment)
    return sentiments
