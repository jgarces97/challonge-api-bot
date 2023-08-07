import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from challonge_api import *
from views.create_tournament_view import get_create_view
import os
import ssl

from views.waiting_to_start_view import get_waiting_to_start_view

ssl._create_default_https_context = ssl._create_unverified_context

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


@app.action("static_select-action")
def register_action_button_click(body, ack, say):
    # Acknowledge the action
    ack()


# Update the view on submission
@app.view("view_1")
def handle_submission(ack, body, client, view, logger, say):
    # Assume there's an input block with `input_c` as the block_id and `dreamy_input`
    hopes_and_dreams = view["state"]["values"]["input_select"]["static_select-action"]['selected_option']
    user = body["user"]["id"]
    # Validate the inputs
    errors = {}
    if hopes_and_dreams is not None and len(hopes_and_dreams['text']['text']) <= 5:
        errors["input_c"] = "The value must be longer than 5 characters"
    if hopes_and_dreams is None:
        ack(response_action="errors", errors=errors)
        return
    # Acknowledge the view_submission request and close the modal
    ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"Your submission of {hopes_and_dreams} was successful"
    except Exception as ea:
        # Handle error
        msg = "There was an error with your submission"

    # Message the user
    try:
        client.chat_postMessage(channel=user, text="", blocks=get_waiting_to_start_view())
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


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

    context = ssl._create_unverified_context()

    sc = slack_sdk.WebClient(os.environ["SLACK_APP_TOKEN"], ssl=context)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], web_client=sc).start()
