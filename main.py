import os
import ssl
import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from challonge_api import ChallongeAPI
from models.registered_user import RegisteredUser
from views.create_tournament_modal import get_create_view
from views.waiting_to_start_message import get_waiting_to_start_view
from views.join_tournament_modal import get_join_tournament_view

# Global Configurations
ssl._create_default_https_context = ssl._create_unverified_context
USERNAME = os.getenv("CHALLONGE_USERNAME", "jordan_garces")
API_KEY = os.getenv("CHALLONGE_API_KEY", "l023Fd0Funogz2JyxDqfPif6UeL10728JcfwLZfM")
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
challonge_api = ChallongeAPI(USERNAME, API_KEY)
registered_users = []
big_block = []
original_message_ts = None


# Message Handlers
@app.message("matches")
def message_matches(message, say):
    say(text="hello", blocks=challonge_api.get_open_matches("dsadsaddsa3qqsad"))


@app.message("user")
def message_matches(body, ack, say, client):
    ack()
    print(client.users_info(user='U01BL9XTCJY'))


# Action Handlers
@app.action("button_click")
def action_button_click(body, ack, client):
    ack()
    client.views_open(trigger_id=body["trigger_id"], view=get_join_tournament_view())


@app.action("button-action")
def register_action_button_click(body, ack, say):
    ack()
    user_name = body['user']['name']
    selected_value = body['actions'][0]['value']
    registered_users[user_name] = selected_value
    say(str(registered_users))


@app.action("ack-select-action")
def register_ack_select_action(ack):
    ack()


# View Handlers
@app.view("create_tournament_view")
def handle_creation_submission(ack, body, client, view, logger):
    global original_message_ts
    global registered_users
    global big_block

    teamsOption = view["state"]["values"]["input_select"]["ack-select-action"].get('selected_option')
    elimOption = view["state"]["values"]["input_select2"]["ack-select-action"].get('selected_option')
    startTime = view["state"]["values"]["input_time"]["timepicker-action"].get('selected_time')
    user = body["user"]["id"]
    errors = {
        "input_select": "Please select a team option" if not teamsOption else None,
        "input_select2": "Please select an elimination option" if not elimOption else None
    }
    if any(errors.values()):
        ack(response_action="errors", errors=errors)
        return
    ack()
    try:
        registered_users = []
        big_block = get_waiting_to_start_view(teamsOption['text']['text'], elimOption['text']['text'], startTime)
        response = client.chat_postMessage(
            channel=user,
            text="",
            blocks=big_block
        )
        print(response)
        original_message_ts = response['ts']
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


@app.view("join_tournament_modal")
def handle_tournament_join(ack, body, client, view, logger):
    global original_message_ts
    global big_block

    user_option = view["state"]["values"]["section-radio"]["ack-select-action"]
    challonge_name = view["state"]["values"]["section-challonge"]["ack-select-action"].get('value', '')

    ack()
    response = client.conversations_open(users=body['user']['id'])
    registered_users.append(RegisteredUser(body['user']['name'], response['channel']['id'], ""))
    print(body['user'])
    us = client.users_info(user='U01BL9XTCJY')['user']['profile']
    for user in registered_users:
        if user:
            match_text = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Match of *{}* vs *{}*.".format(
                        user.slack_name,
                        user.slack_channel_id
                    )
                }
            }
            big_block.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{us['display_name_normalized']}"
                },
                "accessory": {
                    "type": "image",
                    "image_url": f"{us['image_original']}",
                    "alt_text": "cute cat"
                }})
    try:
        if original_message_ts:
            client.chat_update(
                channel=response['channel']['id'],
                ts=original_message_ts,
                blocks=big_block
            )
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.command("/new_tournament")
def open_create_tournament_modal(ack, body, client, logger):
    ack()
    client.views_open(trigger_id=body["trigger_id"], view=get_create_view())


if __name__ == '__main__':
    context = ssl._create_unverified_context()
    sc = slack_sdk.WebClient(os.environ["SLACK_APP_TOKEN"], ssl=context)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], web_client=sc).start()
