"""Chunking of course records.

Only the course description is embedded, split into sentence windows (one sentence of overlap)
so long descriptions are not averaged into a single vector. Each chunk is prefixed with a
contextual header (code, title, requirement area) so its embedding still knows which course
it belongs to, and so requirement-area queries such as "statistics elective" still match.

Catalog notes are deliberately not embedded: in the MS2 data they are mostly logistics (rooms,
former course numbers, enrollment forms). Short notes or metadata chunks were tried first, but
they are dominated by the header, behave like title matches, and outrank the description chunk
that actually explains the course. Notes stay on the course record for MS3 prerequisite parsing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .data import Course

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    course_id: str
    header: str
    body: str  # description text shown to the user as supporting context; "" if none exists

    @property
    def embedding_text(self) -> str:
        return f"{self.header} {self.body}".strip()


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in SENTENCE_END.split(text) if sentence.strip()]


def sentence_windows(text: str, max_words: int) -> list[str]:
    """Group sentences into windows of at most ``max_words`` with one sentence of overlap.

    A single sentence longer than ``max_words`` is kept whole rather than cut mid-sentence.
    """
    sentences = split_sentences(text)
    if not sentences:
        return []
    windows: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        candidate = current + [sentence]
        if current and sum(len(s.split()) for s in candidate) > max_words:
            windows.append(" ".join(current))
            current = [current[-1], sentence] if len(current) > 1 else [sentence]
            if sum(len(s.split()) for s in current) > max_words:
                current = [sentence]
        else:
            current = candidate
    windows.append(" ".join(current))
    return windows


def course_header(course: Course) -> str:
    area = f" ({course.requirement_area})" if course.requirement_area else ""
    return f"{course.course_id}: {course.title}{area}."


def chunk_course(course: Course, max_words: int = 120) -> list[Chunk]:
    header = course_header(course)
    # A course without a description is still indexed by its header so it stays findable.
    bodies = sentence_windows(course.summary, max_words) or [""]
    return [
        Chunk(chunk_id=f"{course.course_id}#{index}", course_id=course.course_id, header=header, body=body)
        for index, body in enumerate(bodies)
    ]


def chunk_courses(courses: list[Course], max_words: int = 120) -> list[Chunk]:
    return [chunk for course in courses for chunk in chunk_course(course, max_words)]
