from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional


class Stats_Effect(BaseModel):
    stat_name: str = ""
    operator: str = "Greater"
    operand: int = 0

class Stats_Effect_Array(BaseModel):
    stats: List[Stats_Effect] = []

class Quest(BaseModel):
    questname: str = ""
    state: str = ""

class User_Vars(BaseModel):
    variables: Dict = {}
    items: List = []

class Gate(BaseModel):
    stats_me: Stats_Effect_Array = Stats_Effect_Array()
    stats_npcs: Dict = {}
    conversations: Dict = {}
    quests: List[Quest] = [] 
    user_vars: User_Vars = User_Vars()

class Postrouting(BaseModel):
    target_dialogue: str = ""
    conditions: Optional[Gate]
    effects: Optional[Gate]

class Response(BaseModel):
    response_text: str = ""
    conditions: Optional[Gate]
    post_routing: List[Postrouting] = []
    show_if_unavailable: bool = True

class Reaction(BaseModel):
    Name: str = ""
    Asset_to_play: str = ""

class Dialogue_Options(BaseModel):
    Music: str = ""
    Audio: str = ""
    Sequence: str = ""
    Animation: List[Reaction] = []
    Functions: List[str] = []

class Dialogue(BaseModel):
    Speaker: str = ""
    text: str = ""
    append: bool = False
    Options: Optional[Dialogue_Options]

class Dialogue_Adv(BaseModel):
    Name: str = ""
    Dialogue_Text: List[Dialogue] = []
    Effects: Gate = Gate()
    Response: List[Response] = [] 


    
