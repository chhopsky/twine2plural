from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional

class Stats(BaseModel):
    Health: int = 0
    Energy: int = 0
    Hungry: int = 0
    Happy: int = 0
    Depressed: int = 0
    Angry: int = 0
    Tired: int = 0
    Confused: int = 0
    Horny: int = 0
    Love: int = 0
    Bond: int = 0
    Embarassed: int = 0
    Courage: int = 0

class Quest(BaseModel):
    questname: str
    state: str

class Gate(BaseModel):
    stats_you: Optional[Stats]
    stats_them: Optional[Dict]
    conversations: Optional[Dict]
    quests: Optional[List[Quest]]

class Postrouting(BaseModel):
    target_dialogue: str
    conditions: Optional[Gate]
    effects: Optional[Gate]

class Response(BaseModel):
    response_text: str
    conditions: Optional[Gate]
    postrouting: Optional[List[Postrouting]]

class Dialogue_Options(BaseModel):
    Reaction: Optional[str]
    Music: Optional[str]
    Animation: Optional[str]
    VO: Optional[str]

class Dialogue(BaseModel):
    Row_Name: str
    Dialogue_Text: str
    Speaker: Optional[str]
    Response: Optional[List[Response]]
    Dialogue_Options: Optional[List[Dialogue_Options]]

    