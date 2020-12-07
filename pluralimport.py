import json
import argparse
from bs4 import BeautifulSoup
from dialogue import Dialogue, Dialogue_Adv, Dialogue_Options, Reaction, Response, Postrouting, Gate, Quest, Stats_Effect_Array, Stats_Effect

def twine_v1():
    with open(args.filename, "r") as f:
        dialogue_adv = []
        dialogue_map = {}
        dialogue_prefix = "line_"
        dialogue_number = 1
        lines = f.read().splitlines()
        line_number = 0
        dialogue = {"Dialogue_Text": ""}
        responses = []
        while line_number < (len(lines) - 1):
            line = lines[line_number]

            if line.startswith("::"):
                if line_number > 0:
                    dialogue["Dialogue_Text"] = dialogue["Dialogue_Text"].rstrip("\n")
                    dialogue["Response"] = responses
                    dialogue_adv.append(dialogue)
                    dialogue = {"Dialogue_Text": ""}
                    responses = []
                line = line.split("[")
                row_map = ""
                if len(line) > 1:
                    row_map = line[0][3:-1]
                    dialogue["Speaker"] = line[1][:-1]
                else:
                    row_map = line[0][3:]
                    
                if dialogue_map.get(row_map):
                    dialogue["Name"] = dialogue_map.get(row_map)
                else:
                    new_row_name = f"{dialogue_prefix}{dialogue_number}"
                    dialogue_map[row_map] = new_row_name
                    dialogue["Name"] = new_row_name
                    dialogue_number += 1
                    

            elif line.startswith("[["):
                row_map = line[2:-2]
                target_dialogue = ""
                if dialogue_map.get(row_map):
                    target_dialogue = dialogue_map.get(row_map)
                else:
                    target_dialogue = f"{dialogue_prefix}{dialogue_number}"
                    dialogue_map[row_map] = target_dialogue
                    dialogue_number += 1
                response = {
                    "response_text" : row_map,
                    "post_routing": [ {
                        "target_dialogue": target_dialogue
                    }]
                }
                responses.append(response)
            else:
                dialogue["Dialogue_Text"] += f"{line}\n"


            if line_number == len(lines) - 1:
                # if we are at the end, append what we've found
                dialogue_adv.append(dialogue_adv)


            line_number += 1
           
    f.close

    with open(f"{args.filename}.json", "w") as of:
        of.write(json.dumps(dialogue_adv, indent=4))

operators_change = {
    "=" : "Equal",
    "+=" : "Greater",
    "-=" : "Less"
}

operators_compare = {
    "=" : "Equal",
    ">" : "Greater",
    "<" : "Less"
}

def parse_inline_set(line, user_vars):
    line = line.lstrip("<<")
    line = line.rstrip(">>")
    commands = line.split(";")
    for command in commands:
        command = command.split()
        if command[0] == "set":
            command.pop(0)
        command[0].lstrip("$")
        target = "items"
        try:
            value = int(command[2])
        except ValueError:
            target = "variables"
        if target == "variables":
            new_var = { 
                command[0]: command[2]
            }
            user_vars.variables = {**user_vars.variables, **new_var}
        else:
            var_update = Stats_Effect()
            var_update.stat_name = command[0]
            var_update.operator = operators_change[command[1]]
            var_update.operand = command[2]
            user_vars.items.append(var_update)
    return

commands = ['quest', 'conversation','stats']
quest_commands = ['Started', 'Completed']

def parse_effects(line, dialogue_effects):
    line = line.lstrip("##")
    breakout = line.split(":")
    if len(breakout) < 2 or breakout[0] not in commands:
        return None

    if breakout[0] == 'quest' and len(breakout) == 3 and breakout[1] in quest_commands:
        quest_update = Quest()
        quest_update.questname = breakout[2]
        quest_update.state = breakout[1]
        dialogue_effects.quests.append(quest_update)
        return 
    
    if breakout[0] == 'stats' and len(breakout) == 4:
        stat_update = Stats_Effect()
        stat_update.stat_name = breakout[1]
        stat_update.operator = breakout[2]
        stat_update.operand = int(breakout[3])
        dialogue_effects.stats_me.stats.append(stat_update)

    # TODO: apply stats to NPC

    if breakout[0] == 'conversation' and len(breakout) == 3:
        convo_update =  {
                breakout[1] : dialogue_map[breakout[2]]
            }
        dialogue_effects.conversations = {**dialogue_effects.conversations, **convo_update}
        return 

    return 

dialogue_map = {}

def twine_v2():
    with open(f"{args.filename}", "r") as f:
        dialogue_adv = []
        page = f.read()
        soup = BeautifulSoup(page, "html.parser")
        items = soup.findAll('tw-passagedata')
        for item in items:
            dialogue_map[item["name"]] = f"line_{item['pid']}"
        
        for item in items:
            new_dialogue_row = Dialogue_Adv()
            new_dialogue_chunk = Dialogue()
            for line in item.string.splitlines():
                # handle responses
                if line.startswith("[["):
                    row_map = line.lstrip("[").rstrip(" ").rstrip("]")
                    row_map = row_map.split("][")
                    
                    new_response = Response()
                    new_response.response_text = row_map[0]
                    new_postrouting = Postrouting()
                    new_postrouting.target_dialogue = dialogue_map[row_map[0]]
                    new_response.post_routing.append(new_postrouting)
                    
                    # TODO: handle post-response routing requirements
                    new_dialogue_row.Response.append(new_response)

                # set speaker
                elif line.startswith("@"):
                    line = line.lstrip("@")
                    new_dialogue_chunk.Speaker = line

                # handle effects
                elif line.startswith("##"):
                    parse_effects(line, new_dialogue_row.Effects)

                # handle twine user variables 
                # TODO: rewrite this
                elif line.startswith("<<"):
                    parse_inline_set(line, new_dialogue_row.Effects.user_vars)

                # handle dialogue text chunks      
                # TODO: continue rewriting this      
                elif line.startswith("--") or line.startswith("++"):
                    if line.startswith("++"):
                        new_dialogue_chunk.append = True
                    new_dialogue_row.Dialogue_Text.append(new_dialogue_chunk)
                    new_dialogue_chunk = Dialogue()
                else:
                    new_dialogue_chunk.text += line
            # TODO: rewrite this
            new_dialogue_chunk.text = new_dialogue_chunk.text.rstrip("\n")
            new_dialogue_row.Dialogue_Text.append(new_dialogue_chunk)
            new_dialogue_row.Name = f"line_{item['pid']}"
            dialogue_adv.append(new_dialogue_row)

        f.close

        with open(f"{args.filename}.json", "w") as of:
            output_as_list_of_dicts = []
            for row in dialogue_adv:
                add_dict = row.dict()
                output_as_list_of_dicts.append(add_dict)
                
            of.write(json.dumps(output_as_list_of_dicts, indent=4))
            print(f"Saved to {args.filename}.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a twine script to json.')
    parser.add_argument('filename', type=str, help='The filename to import')
    parser.add_argument('--v', type=int, choices=[1,2], default=2, help='Version 1 or 2 of twine')
    parser.add_argument('--output', type=str, help='Filename to export to (defaults to same filename but .json')
    args = parser.parse_args()

    if args.v == 1:
        twine_v1()
    else:
        twine_v2()
