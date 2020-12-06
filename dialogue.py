from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional

# As you can see in the main app, this file is not used.
# It does accurately describe the hierarchy used by the
# datatypes in Plural, but here it does nothing.
#
# I made it with the intention of firmly typing the objects
# for json creation but as we don't know the things we need
# to instantiate them, I ended up building it with dicts
# This will be used later when I make a full editor
# that supports post-response routing


class Stats_Effect(BaseModel):
    stat_name: str = ""
    operator: str = "Greater"
    operand: int = 0

class Stats_Effect_Array(BaseModel):
    stats: List = [] # stats effect

class Quest(BaseModel):
    questname: str = ""
    state: str = ""

class User_Vars(BaseModel):
    variables: Dict = {}
    items: List = []

class Gate(BaseModel):
    stats_me: Stats_Effect_Array = Stats_Effect_Array()
    stats_them: Dict = {}
    conversations: Dict = {}
    quests: List = [] # type Quest
    user_vars: User_Vars = User_Vars()

class Postrouting(BaseModel):
    target_dialogue: str
    conditions: Optional[Gate]
    effects: Optional[Gate]

class Response(BaseModel):
    response_text: str = ""
    conditions: Optional[Gate]
    postrouting: List = [] # Postrouting

class Reaction(BaseModel):
    Name: str = ""
    Asset_to_play: str = ""

class Dialogue_Options(BaseModel):
    Music: Optional[str]
    Audio: Optional[str]
    Sequence: Optional[str]
    Animation: Optional[List[Reaction]]
    Functions: Optional[List[str]]

class Dialogue(BaseModel):
    Speaker: str = ""
    text: str = ""
    append: bool = False
    Options: Optional[Dialogue_Options]

class Dialogue_Adv(BaseModel):
    Name: str = ""
    Dialogue: List = [] # type Dialogue
    Effects: Gate = Gate()
    Response: List = [] # type Response


    