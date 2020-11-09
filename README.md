# twine2plural
A tool to convert Twine scripts into importable json for UE4 Plural conversation engine

How to develop:
- Install python 3.8
- pip install pipenv
- pipenv --python 3.8
- pipenv shell
- python app.py 

How to use:
1. Build your twine the way you normally would. Use a tag for the speaker of a particular passage.
2. Export it using the Publish button or View Proofing Copy button. Proofing copies are faster.
3. Run the program from the command line, and it give it an argument of the file you just saved (or just drag the html file onto the .exe)

`twine2plural.exe test.html`

If you have a twine v1 twee file you want to import, you can do that too, but setting conversation heads is not supported. Alert a v1 file by adding '-v 1'

`twine2plural.exe test.tw -v 1`

Additional control options can be added with lines starting with two "#"s, with arguments separated by ":"s.

You can start/finish quests, or set the conversation heads (the passage you'll get the next time you interact with an NPC). You can set the conversation heads for any NPC in the game this way, not just the one you're interacting with, so if you wanted to, say, blow up your whole friend circle because you were a massive dickhead to someone, you could do that.

Anyway, tagging control options:

Quests:
- Valid states are "Started" and "Completed"
- ##quest:state:name
- e.g. ##quest:Started:get-a-date
- e.g. ##quest:Completed:get-a-date

Conversations:
- Like links, you reset the conversation head (the one you get next time you interact) to the correct one with the title of the passage. 
- ##conversation:npc_name:passagename
- e.g. ##conversation:Kristin:phase2 

You can use this to reset multiple conversation heads, say if you normally interact with Astro and get a "hi" back with no options, but you reach a point where Kristin tells you to go talk to Astro, and this then sets a new conversation head for both Kristin and Astro:
- ##conversation:Kristin:go-see-astro
- ##conversation:Astro:whats-up

How to use Plural:

The example file provided uses an NPC named Kristin, in "test.html"

1. Download (ask me) the UE project file
2. Take the .json file this program spits out and put it in your UE project folder
3. Point the data table source at this file
4. Go back to the content browser, right click on the data table and reimport from source
5. Place a chr_base actor onto the map in the level editor
6. Click on it, set the variable NPC_Name to Kristin and the variable dialogue start to "line_1"
7. Assign a skeletal mesh or static mesh to the character
8. Hit play. Hit E to interact with an NPC.

You can do this with as many different base_chr actors as you want. Go forth, and make games.

Notes:
- quests don't do anything inherently. how you use them is up to you
- bpw_simple_ui is for conversations, you can tell it to load a conversation_id or just feed it a single screen of text
