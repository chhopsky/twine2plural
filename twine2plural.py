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

def parse_meta(line, dialogue_map):
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

    return None

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
            dialogue_text = ""
            dialogue = {}
            for line in item.string.splitlines():
                if line.startswith("[["):
                    row_map = line.lstrip("[").rstrip(" ").rstrip("]")
                    target_dialogue = dialogue_map[row_map]
                    response = {
                        "response_text" : row_map,
                        "post_routing": [ {
                            "target_dialogue": target_dialogue
                        }]
                    }
                    responses.append(response)
                elif line.startswith("##"):
                    meta = parse_meta(line, dialogue_map)
                    if meta is not None:
                        if dialogue.get("Effects"):
                            dialogue["Effects"] = {**meta, **dialogue["Effects"]}
                        else:
                            dialogue["Effects"] = meta
                else:
                    dialogue_text += line
            dialogue["Dialogue_Text"] = dialogue_text.rstrip("\n")
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
