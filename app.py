import json
import argparse
from bs4 import BeautifulSoup
from pprint import pprint
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
                    dialogue["Row_Name"] = dialogue_map.get(row_map)
                else:
                    new_row_name = f"{dialogue_prefix}{dialogue_number}"
                    dialogue_map[row_map] = new_row_name
                    dialogue["Row_Name"] = new_row_name
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


    pprint(dialogue_adv)
    pprint(dialogue_map)
            
    f.close


    with open(f"{args.filename}.json", "w") as of:
        of.write(json.dumps(dialogue_adv, indent=4))

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
                else:
                    dialogue_text += line
            dialogue["Dialogue_Text"] = dialogue_text.rstrip("\n")
            dialogue["Response"] = responses
            dialogue["Speaker"] = item["tags"]
            dialogue_adv.append(dialogue)

        pprint(dialogue_adv)
        pprint(dialogue_map)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a twine script to json.')
    parser.add_argument('filename', type=str, help='The filename to import')
    parser.add_argument('version', type=int, choices=[1,2], help='Version 1 or 2 of twine')
    parser.add_argument('--output', type=str, help='Filename to export to (defaults to same filename but .json')
    args = parser.parse_args()

    if args.version == 1:
        twine_v1()
    else:
        twine_v2()