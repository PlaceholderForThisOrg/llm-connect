from typing import List, Optional

from pydantic import BaseModel


class License(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class Phonetic(BaseModel):
    text: Optional[str] = None
    audio: Optional[str] = None
    sourceUrl: Optional[str] = None
    license: Optional[License] = None


class Definition(BaseModel):
    definition: str
    example: Optional[str] = None
    synonyms: List[str] = []
    antonyms: List[str] = []


class Meaning(BaseModel):
    partOfSpeech: str
    definitions: List[Definition]
    synonyms: List[str] = []
    antonyms: List[str] = []


class DictionaryEntry(BaseModel):
    word: str
    phonetic: Optional[str] = None
    phonetics: List[Phonetic] = []
    meanings: List[Meaning]
    license: Optional[License] = None
    sourceUrls: List[str] = []


class DictionaryResponse(BaseModel):
    word: str
    phonetic: Optional[str] = None
    phonetics: List[Phonetic] = []
    meanings: List[Meaning]
