import os
import sys
import time
import gtts
import typer
import speech_recognition as sr
from datetime import datetime
from notion import NotionClient
from config import TOKEN,DATABASE_ID
from playsound import playsound

app = typer.Typer()
r = sr.Recognizer()

client = NotionClient(TOKEN, DATABASE_ID)

ADDTASK_COMMAND = "create"
DELTASK_COMMAND = "remove"
CHKTASK_COMMAND = "check"
UNCHKTASK_COMMAND = "undo"
LIST_COMMAND = "list"
HELP_COMMAND = "help"
EXIT_COMMAND = "close"

# ? some numbers that speech recognition gets wrong every time 🥲
ALT_WORDS = {('what','want', 'one'): 1, ('tu','two'):2, ('tree','three'):3, ('sex'):6}

ID_FILE_NAME = "last_task_id.txt"

os.close(sys.stderr.fileno())

def retreive_last_task_id(file_name):
    f_read = open(file_name, 'r')
    last_stored_id = int(f_read.read().strip())
    f_read.close()
    return last_stored_id

def store_last_task_id(file_name, last_task_id):
    f_write = open(file_name, 'w')
    f_write.write(str(last_task_id))
    f_write.close()
    return

def get_audio_init():
    with sr.Microphone() as source:
        typer.secho("Listening...", fg=typer.colors.BRIGHT_GREEN)
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    return audio

def get_audio():
    with sr.Microphone() as source:
        audio = r.listen(source)
    return audio

def audio_to_text(audio):
    text = ""
    try:
        text = r.recognize_google(audio, language='en-in')
    except sr.UnknownValueError:
        print("Did not get you.. Please try again")
    except sr.RequestError:
        print("Something went wrong.. Please try again after a few minutes")
    except Exception as e:
        print("Something went wrong")
    return text

def play_sound(text):
    try:
        tts = gtts.gTTS(text)
        tempfile = "./temp.mp3"
        tts.save(tempfile)
        playsound(tempfile)
        os.remove(tempfile)
    except AssertionError:
        print("could not play sound")

def process_commands(text):

    if ADDTASK_COMMAND in text.lower():
        typer.secho("-> You said 'create'", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho("What task do you have in mind? 🤔", fg=typer.colors.BRIGHT_BLUE)
        play_sound("What task do you have in mind?") 
        task = get_audio()
        task = audio_to_text(task)
        if task:
            add(task)
            print()
            play_sound(f"Added new task: {task}")
            

    elif DELTASK_COMMAND in text.lower():
        typer.secho("-> You said 'remove'", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho("Specify the ID of the task you want to remove ❌", fg=typer.colors.BRIGHT_BLUE)
        play_sound("Specify the ID of the task you want to remove")
        task = get_audio()
        task = audio_to_text(task)
        try:
            task = int(task)
        except:
            alt_words = ALT_WORDS
            for key, value in alt_words.items():
                if str(task).lower() in key:
                    task = value
                    task = int(task)
        
        if task:
            remove(task)
            print()
            play_sound(f"Removed task: {task}")

    elif CHKTASK_COMMAND in text.lower():
        typer.secho("-> You said 'check'", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho("Say the ID of the task you want to check ✅", fg=typer.colors.BRIGHT_BLUE)
        play_sound("Say the ID of the task you want to check")
        task = get_audio()
        task = audio_to_text(task)
        try:
            task = int(task)
        except:
            alt_words = ALT_WORDS
            for key, value in alt_words.items():
                if str(task).lower() in key:
                    task = value
                    task = int(task)
        if task:
            check(task)
            print()
            play_sound(f"Checked task: {task}")

    elif UNCHKTASK_COMMAND in text.lower():
        typer.secho("-> 'undo'? ", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho("What's the ID of the task you want to uncheck", fg=typer.colors.BRIGHT_BLUE)
        play_sound("What's the ID of the task you want to uncheck")
        task = get_audio()
        task = audio_to_text(task)
        try:
            task = int(task)
        except:
            alt_words = ALT_WORDS
            for key, value in alt_words.items():
                if str(task).lower() in key:
                    task = value
                    task = int(task)
        if task:
            uncheck(task)
            print()
            play_sound(f"Unchecked task: {task}")

    elif LIST_COMMAND in text.lower():
        typer.secho("-> 'list'?", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho(f"Here's the available tasks 📃", fg=typer.colors.BRIGHT_MAGENTA)
        list()
        print()
        play_sound("Complete these tasks, and you'll be congratulated 🎉")

    elif HELP_COMMAND in text.lower():
        typer.secho("-> Did you ask for 'help' ?", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho("  List of available voice commands", fg=typer.colors.GREEN)
        typer.secho('''$ create - To add a new task to your notion database
$ remove - To remove an existing task from your notion database
$ check - To check an existing task in your notion database
$ undo - To uncheck an existing task in your notion database
$ list - To list all existing tasks in your notion database
$ help - To open this help
$ close - To exit slate''', fg=typer.colors.BRIGHT_BLUE)
        print()
        play_sound("voice commands it...!")

    elif EXIT_COMMAND in text.lower():
        typer.secho("-> 'close' ?", fg=typer.colors.BRIGHT_YELLOW)
        typer.secho("Exiting Notion Tasker...👋", fg=typer.colors.BRIGHT_MAGENTA)
        play_sound("Exiting Notion Tasker...")
        raise typer.Exit()

    else:
        typer.secho("That is an unrecognized command, try 'help' ", fg=typer.colors.BRIGHT_MAGENTA)
        print()
        play_sound("That is an unrecognized command, try 'help' to see all available commands")

@app.command()
def add(task : str):
    task_id = retreive_last_task_id(ID_FILE_NAME)
    now = datetime.now().astimezone().isoformat()
    res = client.create_page(task_id, task, now, status=False)
    if res.status_code == 200:
            typer.secho(f"Added new task: {task} 🚀", fg=typer.colors.BRIGHT_GREEN)
            task_id += 1
            store_last_task_id(ID_FILE_NAME, task_id)

@app.command()
def remove(task_num: int):
    tasks = client.get_pages()
    task_id = None
    for task in tasks:
        if task['task_num'] == task_num:
            task_id = task['task_id']
    if task_id:
        res = client.delete_page(task_id)
        if res.status_code == 200:
            typer.secho(f"Removed task: {task_num} ❌", fg=typer.colors.BRIGHT_GREEN)
    else:
        typer.secho("That task doesn't seem to exist 🙈", fg=typer.colors.BRIGHT_RED)

@app.command()
def check(task_num: int):
    tasks = client.get_pages()
    task_id = None
    for task in tasks:
        if task['task_num'] == task_num:
            task_id = task['task_id']
    if task_id:
        res = client.update_page(task_id, status=True)
        if res.status_code == 200:
            typer.secho(f"Checked task: {task_num} ✅", fg=typer.colors.BRIGHT_GREEN)
    else:
        typer.secho("That task doesn't seem to exist 🙈", fg=typer.colors.BRIGHT_RED)

@app.command()
def uncheck(task_num: int):
    tasks = client.get_pages()
    task_id = None
    for task in tasks:
        if task['task_num'] == task_num:
            task_id = task['task_id']
    if task_id:
        res = client.update_page(task_id, status=False)
        if res.status_code == 200:
            typer.secho(f"Unchecked task: {task_num} ✔️", fg=typer.colors.BRIGHT_GREEN)
    else:
        typer.secho("That task doesn't seem to exist 🙈", fg=typer.colors.BRIGHT_RED)

@app.command()
def list():
    res = client.get_pages()
    res.reverse()
    for r in res:
        status = 'not done'
        if r['status'] == True:
            status = 'done'
            status = typer.style(f"{status}", fg=typer.colors.BRIGHT_BLUE)
        else:
            status = typer.style(f"{status}", fg=typer.colors.BRIGHT_RED)
        task = typer.style(f"-> {r['task_num']} {r['description']} - ", fg=typer.colors.WHITE)
        typer.secho(task + status)

@app.command()
def help():
    print()
    typer.secho("  List of available text commands", fg=typer.colors.GREEN)
    typer.secho('''$ python slate.py - Run without arguements to use voice commands 
$ python slate.py add [TASK]- To add a new task to your notion database
$ python slate.py remove [TASK_NUM]- To remove an existing task from your notion database
$ python slate.py check [TASK_NUM]- To check an existing task in your notion database
$ python slate.py uncheck [TASK_NUM]- To uncheck an existing task in your notion database
$ python slate.py list - To list all existing tasks in your notion database
$ python slate.py help - To open this help''', fg=typer.colors.BRIGHT_BLUE)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        banner = typer.style('''

,--./ ,--/                 
|   \ |  | 
|  . '|  |
|  |\    | 
|  | \   |
`--'  `--' 

(`-')----. 
( OO).-.  '
( _) | |  |
 \|  |)|  |
  '  '-'  '
   `-----' 

|'--...__) 
`--.  .--' 
   |  |    
   |  |    
   `--'    

    ,--. )  
 |  (`-') 
 |  |OO ) 
(|  |  ' 
 |  |  
 |  |  
 `---  

 (`-')----. 
( OO).-.  '
( _) | |  |
 \|  |)|  |
  '  '-'  '
   `-----' 

   ,--./ ,--/ 
|   \ |  | 
|  . '|  |)
|  |\    | 
|  | \   | 
`--'  `--' 

        ▀▄▀▄▀▄  𝙰𝚞𝚝𝚑𝚘𝚛: Luodi Wang 𝚅𝚎𝚛𝚜𝚒𝚘𝚗: 𝟢.y.z     ▀▄▀▄▀
    ''',  fg=typer.colors.WHITE)
        typer.echo(banner)
        typer.secho('''                     《《Tick off your tasks with Notion Tasker..! 》》''', fg=typer.colors.BRIGHT_YELLOW,  bold=True)

    if(len(sys.argv) <= 1):
        print()
        typer.secho("Initializing speech recognition..", fg=typer.colors.BRIGHT_YELLOW)
        time.sleep(2)
        while True:
            a = get_audio_init()
            text = audio_to_text(a)
            process_commands(text)

if __name__ == "__main__":
    app()