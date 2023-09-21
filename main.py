import datetime
import os
import ssl
import json
import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from models.challonge_api import ChallongeAPI
from models.registered_user import RegisteredUser
from models.tournament import Tournament
from views.create_tournament_modal import get_create_tournament_modal
from views.register_message_view import get_register_message_blocks
from views.tournament_in_progress_view import get_tournament_in_progress_blocks
from views.join_tournament_modal import get_join_tournament_modal


# Global Configurations
ssl._create_default_https_context = ssl._create_unverified_context
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
current_tournament: Tournament
slack_to_challonge_config = {}


# Message Handlers
@app.message("user")
def message_matches(body, ack, say, client):
    global current_tournament

    ack()
    print(body)
    response = client.chat_postEphemeral(
        channel=body['event']['user'],
        text="Create Tournament",
        user=body['event']['user']
    )
    current_tournament.add_user_to_tournament(user=RegisteredUser(
        {"name": "test", "profile": {"display_name_normalized": "test", "image_original": "google.com"}}, "", ""))


# Action Handlers
@app.action("join_tournament_button_click")
def join_tournament_button_click(body, ack, client, logger):
    global current_tournament

    ack()
    if current_tournament is None or current_tournament.started is True:
        return

    user_channel_id = client.conversations_open(users=body['user']['id'])['channel']['id']
    user_info = client.users_info(user=body['user']['id'])['user']

    if body['user']['id'] not in slack_to_challonge_config:
        slack_to_challonge_config[body['user']['id']] = ''

    current_tournament.add_user_to_tournament(RegisteredUser(user_info, user_channel_id,
                                                             slack_to_challonge_config[body['user']['id']]))

    try:
        response = client.chat_update(
            channel=user_channel_id,
            text="Update",
            ts=current_tournament.register_message_ts,
            blocks=get_register_message_blocks(current_tournament)
        )
        print({"message": f"User {user_info['name']} joined tournament {current_tournament.tournament_id}",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.action("toggle_ready_match_button_click")
def toggle_ready_match_button_click(body, ack, client, logger):
    global current_tournament

    ack()
    if current_tournament is None or current_tournament.started is False:
        return

    user_info = client.users_info(user=body['user']['id'])['user']
    if not current_tournament.is_slack_user_registered(user_info['name']):
        return

    user_channel_id = client.conversations_open(users=body['user']['id'])['channel']['id']

    try:
        response = client.chat_postMessage(
            channel=user_channel_id,
            text="Start",
            blocks=get_tournament_in_progress_blocks(current_tournament)
        )
        print({"message": f"/start-tournament successful",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.action("ack-select-action")
def register_ack_select_action(ack):
    ack()


# View Handlers
@app.view("create_tournament_view")
def handle_create_tournament_submission(ack, body, client, view, logger):
    global current_tournament

    teams_option = view["state"]["values"]["input_select"]["ack-select-action"].get('selected_option')
    elim_option = view["state"]["values"]["input_select2"]["ack-select-action"].get('selected_option')
    start_time = view["state"]["values"]["input_time"]["timepicker-action"].get('selected_time')
    user = body["user"]["id"]

    errors = {
        "input_select": "Please select a team option" if not teams_option else None,
        "input_select2": "Please select an elimination option" if not elim_option else None
    }

    if any(errors.values()):
        ack(response_action="errors", errors=errors)
        return
    ack()

    try:
        response = client.chat_postMessage(
            channel=user,
            text="Creating Tournament"
        )

        current_tournament = Tournament(teams_option['text']['text'], elim_option['text']['text'],
                                        start_time, response['ts'])

        response = client.chat_update(
            channel=client.conversations_open(users=user)['channel']['id'],
            text="Creating Tournament",
            ts=response['ts'],
            blocks=get_register_message_blocks(current_tournament)
        )

        print({"message": f"Tournament {current_tournament.tournament_id} Created",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


@app.command("/new-tournament")
def create_tournament_command(ack, body, client, logger):
    ack()
    try:
        response = client.views_open(trigger_id=body["trigger_id"], view=get_create_tournament_modal())
        print({"message": "/new-tournament", "ts": datetime.datetime.now().strftime('%X'),
               "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to create tournament {e}")


@app.command("/link-challonge")
def link_challonge_command(ack, command, client, logger):
    ack()
    try:
        slack_to_challonge_config[command['user_id']] = command['text']
        save_config()
        response = client.chat_postEphemeral(
            channel=command['user_id'],
            text=f"Successfully connected your slack account to the challonge account {command['text']}",
        )
        print({"message": f"/link-challonge {command['user_id']} linked to {command['text']  }",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to create tournament {e}")


@app.command("/start-tournament")
def start_tournament_command(ack, body, client, logger):
    global current_tournament

    ack()
    if current_tournament is None or current_tournament.started is True:
        return

    try:
        user_channel_id = client.conversations_open(users=body['user_id'])['channel']['id']
        current_tournament.start_tournament()
        response = client.chat_postMessage(
            channel=user_channel_id,
            text="Start",
            blocks=get_tournament_in_progress_blocks(current_tournament)
        )
        print({"message": f"/start-tournament successful",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.command("/end-tournament")
def end_tournament_tournament(ack, command, client):
    global current_tournament

    ack()
    if current_tournament is None:
        return

    slack_to_challonge_config[command['user_id']] = command['text']
    save_config()
    response = client.chat_postMessage(
        channel=command['user_id'],
        text=f"Successfully connected your slack to the challonge account {command['text']}",
    )


# Helpers
def save_config():
    global slack_to_challonge_config

    """Save data to a JSON file."""
    with open('config.json', 'w') as f:
        json.dump(slack_to_challonge_config, f)


def load_config():
    global slack_to_challonge_config
    """Load data from a JSON file. If the file doesn't exist, return an empty dict."""
    try:
        with open('config.json', 'r') as f:
            slack_to_challonge_config = json.load(f)
    except FileNotFoundError:
        return {}





if __name__ == '__main__':
    load_config()
    context = ssl._create_unverified_context()
    sc = slack_sdk.WebClient(os.environ["SLACK_APP_TOKEN"], ssl=context)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], web_client=sc).start()
