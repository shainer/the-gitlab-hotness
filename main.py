#!/usr/bin/python3

import fedmsg
import gitlab
import json

TOPIC = 'org.fedoraproject.dev.anitya.project.version.update'

def GetMessages():
    """Waits for messages on the fedmsg bus."""
    return fedmsg.tail_messages()

def GetExampleMessage():
    """Returns an example message, parsed as JSON."""
    msg = None

    with open('data/example.txt', 'r') as f:
        msg = f.read()

    return [(None, None, TOPIC, json.loads(msg))]

def GetToken():
    """Reads the GitLab API token from a file."""
    tk = None

    # File not included in the repo on purpose.
    with open('data/token.txt', 'r') as f:
        tk = f.read()

    return tk.rstrip()

def GetActionForPackage(package_name):
    """Returns a name identifying the action to take when a new version
    is released for the package.

    At the moment the supported action names are "bug" and "rebuild".
    """

    # For now we always return bug. I'll add more logic when we figure out
    # the best way to store the intended action for the packages.
    return "rebuild"

if __name__ == '__main__':
    glab = gitlab.Gitlab('https://gitlab.chakralinux.org',
                         GetToken())
    # We can only create issue attached to a specific project.
    # Which means that if we want to be correct, we need to find out
    # which repo a package belongs to and use the corresponding
    # project. I'll do that later if needed.
    desktop_repo = glab.projects.get('packages/desktop')

    for _, _, topic, msg in GetExampleMessage():
        if topic != TOPIC:
            print('Received message for topic %s, ignoring' % topic)
            continue

        print('Received message on topic %s' % topic)

        project_name = msg['msg']['message']['project']['name']
        project_version = msg['msg']['message']['project']['version']

        if GetActionForPackage(project_name) == 'bug':
            print('-- Filing new bug')

            bug_title = ('[GitLab hotness] %s released version %s' %
                        (project_name, project_version))

            bug_message = 'Website: %s' % msg['msg']['message']['project']['homepage']
            bug_assignee = 15  # shainer

            try:
                issue = desktop_repo.issues.create({'title': bug_title,
                                                    'description': bug_message,
                                                    'assignee_ids': [bug_assignee]})
            except gitlab.GitlabCreateError as err:
                print('Error creating bug: %s' % err)

            print('Bug %d created successfully' % issue.id)
        elif GetActionForPackage(project_name) == 'rebuild':
            print('-- Triggering automated rebuild [TODO]')
