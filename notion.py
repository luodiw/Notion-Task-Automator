import json
import requests

class NotionClient:

    def __init__(self,token,database_id):
        self.database_id = database_id
        self.token = token

        self.headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": "Bearer "+token
        }

    def map_properties(self, result):
        task_id = result['id']
        properties = result['properties']
        task_num = properties['Task ID']['number']
        description = properties['Description']['title'][0]['text']['content']
        date = properties['Date']['date']['start']
        status = properties['Status']['checkbox']

        return {
            'task_id': task_id,
            'task_num': task_num,
            'description': description,
            'status': status,
            'date': date 
        }

    def get_pages(self):
        query_url = f'https://api.notion.com/v1/databases/{self.database_id}/query'
        res = requests.post(query_url, headers=self.headers)
        res_dict = res.json()
        tasks = res_dict['results']
        tasks_list = []
        for task in tasks:
            task_dict = self.map_properties(task)
            tasks_list.append(task_dict)

        return tasks_list

    def create_page(self,task_id,description,date,status):
        create_url = "https://api.notion.com/v1/pages"

        data = {
        "parent": { "database_id": self.database_id },
        "properties": {
            "Task ID": {
                "number": task_id
            },
            "Description": {
                "title": [
                    {
                        "text": {
                            "content": description
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                            "start": date,
                            "end": None
                        }
            },
            "Status": {
                "checkbox": status
            }
        }}


        data = json.dumps(data)
        res = requests.post(create_url,headers=self.headers,data=data)
        return res

    def update_page(self, task_id, status):
        update_url = f"https://api.notion.com/v1/pages/{task_id}"

        data = {
        "parent": { "database_id": self.database_id },
        "properties": {
            "Status": {
                "checkbox": status
            }
        }}


        data = json.dumps(data)
        res = requests.patch(update_url,headers=self.headers,data=data)
        return res

    def delete_page(self, task_id):
        update_url = f"https://api.notion.com/v1/pages/{task_id}"

        data = {
        'archived' : True
        }


        data = json.dumps(data)
        res = requests.patch(update_url,headers=self.headers,data=data)
        return res
