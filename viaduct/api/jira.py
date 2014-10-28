import json
import requests
from requests.auth import HTTPBasicAuth
from viaduct import application


class JiraAPI:

    @staticmethod
    def create_issue(form):
        """ Method to query JIRA API to create a new issue. """

        # Use the ict@svia.nl account for to authenticate
        auth = HTTPBasicAuth(
            application.config['JIRA_ACCOUNT']['username'],
            application.config['JIRA_ACCOUNT']['password'])

        jira_url = 'https://viaduct.atlassian.net/rest/api/2/issue'
        headers = {'content-type': 'application/json'}

        payload = {"fields":
                   {"project": {"key": "VIA"},
                    "summary": "{}".format(form.summary.data),
                    "description": "{}\n{}".format(
                        form.email.data, form.description.data),
                    "issuetype": {"id": "{}".format(form.issue_type.data)}
                    }
                   }

        # Send POST request using json data
        response = requests.post(
            jira_url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth)
        return response
