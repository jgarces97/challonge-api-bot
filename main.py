import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from challonge_api import *
from views.create.create_tournament import get_create_view

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
registered_users = {}


@app.message("hello")
def message_hello(message, say, ack, body, client):
    body['trigger_id'] = '1'
    open_modal(ack, body, client)


@app.message("matches")
def message_matches(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=get_tournament_open_matches()
    )


@app.message("register")
def message_register(client, message, say):
    # say() sends a message to the channel where the event was triggered
    if message['user'] in registered_users:
        pass
    else:
        tournament = challonge.tournaments.show('voltserver-u1ekdgjd')
        participants = challonge.participants.index(tournament["id"])

        partLst = []
        for person in participants:
            var = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "User: {}".format(person['username'])
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Register"
                    },
                    "value": person['username'],
                    "action_id": "button-action"
                }
            }
            partLst.append(var)

        say(
            blocks=partLst
        )

        channel_id = message['channel']
        client.chat_postMessage(
            channel=channel_id,
            text="Works"
        )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


@app.action("button-action")
def register_action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    registered_users[body['user']['name']] = body['actions'][0]['value']
    say(registered_users.__str__())


@app.command("/new_tournament")
def open_modal(ack, body, client):
    # Acknowledge the command request
    ack()
    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view=get_create_view()
    )


if __name__ == '__main__':
    auth_challonge()

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
