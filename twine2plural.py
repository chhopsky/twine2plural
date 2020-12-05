import json
import argparse
from bs4 import BeautifulSoup
from dialogue import Stats, Quest, Gate, Postrouting, Response, Dialogue

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

commands = ['quest', 'conversation','stats']
quest_commands = ['Started', 'Completed']

def parse_effects(line, dialogue_map):
    line = line.lstrip("##")
    breakout = line.split(":")
    if len(breakout) < 2 or breakout[0] not in commands:
        return None

    if breakout[0] == 'quest' and len(breakout) == 3 and breakout[1] in quest_commands:
        quest_update = {
            "quests" : [{ 
                "questname": breakout[2],
                "state": breakout[1]
            }]
        }
        return quest_update
    
    if breakout[0] == 'conversation' and len(breakout) == 3:
        convo_update = {
            "conversations" : {
                breakout[1] : dialogue_map[breakout[2]]
            }
        }
        return convo_update

    if breakout[0] == 'stats' and len(breakout) == 4:
        convo_update = {
            "stats" : [{
                "stat name" : breakout[1],
                "operator" : breakout[2],
                "operand" : breakout[3]                
            }
        }]
        return convo_update

    return None


def parse_inline_set(line):
    line = line.lstrip("<<")
    line = line.rstrip(">>")
    commands = line.split(";")
    user_vars = { "items" : {}, "variables": {}}
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
            user_vars["variables"][command[0]] = command[2]
        else:
            if command[1] == "-=":
                command[2] = int(command[2]) * -1
            user_vars["items"][command[0]] = command[2]

    return user_vars

def twine_v2():
    with open(f"{args.filename}", "r") as f:
        dialogue_map = {}
        dialogue_adv = []
        page = f.read()
        soup = BeautifulSoup(page, "html.parser")
        items = soup.findAll('tw-passagedata')
        for item in items:
            dialogue_map[item["name"]] = f"line_{item['pid']}"
        
        for item in items:
            responses = []
            dialogue_text = { "text": ""}
            dialogue = { "Dialogue_Text": [] }
            for line in item.string.splitlines():
                # handle responses
                if line.startswith("[["):
                    row_map = line.lstrip("[").rstrip(" ").rstrip("]")
                    row_map = row_map.split("][")
                    
                    target_dialogue = dialogue_map[row_map[0]]
                    
                    response = {
                        "response_text" : row_map[0],
                        "post_routing": [ {
                            "target_dialogue": target_dialogue
                        }]
                    }

                    # handle post-response routing requirements
                    if len(row_map) > 1:
                        meta = {}
                        if row_map[1].startswith("##"):
                            meta = parse_effects(row_map[1], dialogue_map)
                        else:
                            meta = parse_inline_set(row_map[1])
                        response["post_routing"][0] = { **meta, **response["post_routing"][0]}
                    responses.append(response)

                # set speaker
                elif line.startswith("@"):
                    line = line.lstrip("@")
                    dialogue_text["Speaker"] = line

                # handle effects
                elif line.startswith("##"):
                    meta = parse_effects(line, dialogue_map)
                    if meta is not None:
                        if dialogue.get("Effects"):
                            dialogue["Effects"] = {**meta, **dialogue["Effects"]}
                        else:
                            dialogue["Effects"] = meta

                # handle twine user variables
                elif line.startswith("<<"):
                    user_vars = parse_inline_set(line)
                    if user_vars != { "items" : {}, "variables": {}}:
                        if dialogue.get("Effects"):
                            if dialogue["Effects"].get("user_vars"):
                                dialogue["Effects"]["user_vars"]["items"] = {**user_vars["items"], **dialogue["Effects"]["user_vars"]["items"]}
                                dialogue["Effects"]["user_vars"]["variables"] = {**user_vars["variables"], **dialogue["Effects"]["user_vars"]["variables"]}
                            else:
                                dialogue["Effects"]["user_vars"] = user_vars
                        else:
                            dialogue["Effects"]["user_vars"] = user_vars

                # handle dialogue text chunks            
                elif line.startswith("--") or line.startswith("++"):
                    if line.startswith("++"):
                        dialogue_text["append"] = True
                    dialogue["Dialogue_Text"].append(dialogue_text)
                    dialogue_text = { "text": "" }
                else:
                    dialogue_text["text"] += line
            dialogue_text["text"] = dialogue_text["text"].rstrip("\n")
            dialogue["Dialogue_Text"].append(dialogue_text)
            dialogue["Speaker"] = item["tags"]
            dialogue["Name"] = f"line_{item['pid']}"
            dialogue["Response"] = responses
            dialogue_adv.append(dialogue)

        f.close

        with open(f"{args.filename}.json", "w") as of:
            of.write(json.dumps(dialogue_adv, indent=4))
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
