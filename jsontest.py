import json
from dialogue import Dialogue_Adv, Dialogue, Dialogue_Options, Reaction, Response, Postrouting, Gate, Quest, Stats_Effect_Array, Stats_Effect

new_dialogue_adv = Dialogue_Adv()
new_dialogue_chunk = Dialogue()
new_dialogue_chunk.Speaker = "Kristin"
new_dialogue_chunk.text = "Hey, how's it going?"
new_dialogue_adv.Dialogue.append(new_dialogue_chunk)
new_dialogue_chunk.Speaker = "Kristin"
new_dialogue_chunk.text = "Virus times, hey?"
new_dialogue_adv.Dialogue.append(new_dialogue_chunk)
new_dialogue_chunk.Speaker = "Kristin"
new_dialogue_chunk.text = "Fucked."
new_dialogue_adv.Dialogue.append(new_dialogue_chunk)
new_response = Response()
new_dialogue_adv.Response.append(new_response)

print(f"{new_dialogue_adv.dict()}")