from typing import TypedDict
from strenum import StrEnum


class Phase(StrEnum):
  EXTRACTION = "extraction"
  TEXT_JOINT = "text-joint"
  FOOTNOTE_JOINT = "footnote-joint"
  COMPLETED = "completed"

class State(TypedDict):
  phase: Phase
  max_data_tokens: int
  max_paragraph_tokens: int
  max_paragraphs: int
  completed_ranges: list[list[int]]

class SequenceType(StrEnum):
  TEXT = "text"
  FOOTNOTE = "footnote"

class Truncation(StrEnum):
  YES = "truncated"
  NO = "not-truncated"
  PROBABLY = "probably"
  UNCERTAIN = "uncertain"