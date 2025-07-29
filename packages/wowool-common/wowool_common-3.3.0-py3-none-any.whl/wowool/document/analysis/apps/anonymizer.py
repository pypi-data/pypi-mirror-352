from dataclasses import dataclass, field


@dataclass
class Location:
    begin_offset: int
    end_offset: int
    uri: str
    anonymized: str
    text: str
    byte_begin_offset: int | None = None
    byte_end_offset: int | None = None


@dataclass
class AnonymizerResults:
    test: str
    locations: list[Location] = field(default_factory=list)


def convert_anonymizer(jo_data: dict) -> AnonymizerResults:
    results = AnonymizerResults(jo_data["text"])
    for location in jo_data["locations"]:
        location = Location(**location)
        results.locations.append(location)

    return results
