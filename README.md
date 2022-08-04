# Notion Tasker

Keep track of your progress and to do list using terminal commands. Either through typing or voice, use commands to directly see your tasks in Notion Todo Template. 

Create a task while you're building a project without opening Notion or during a busy conference call.

Just click, type or speak and tasks will appear for you in a simple command line.

![Image](/assets/screenshot.png)

## Configuration
1. Create a new notion integration and copy token value
2. Duplicate the below notion page and copy the database ID
> https://luodiwang/notion.site/4db66931896240198d9781850b8bf6d5 
3. Copy config.py.sample to a new file config.py and replace the placeholders with your own interation token and database id
4. Install all requirements
```bash
   $ pip install -r requirements.txt
```
5. Finally run it 🎉

## Commands

Run without arguements to use voice commands 

```bash
  $ python slate.py
```

To add a new task to your notion database

```bash
   $ python slate.py add [TASK]
```

To remove an existing task from your notion database

```bash
  $ python slate.py remove [TASK_NUM]
```

To uncheck an existing task in your notion database

```bash
  $ python slate.py uncheck [TASK_NUM]
```

To list all existing unchecked tasks in your notion database

```bash
  $ python slate.py list
```

To open this help

```bash
   $ python slate.py help
```
