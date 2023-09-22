import datetime
import os
import ssl
import json
import slack_sdk
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from models.registered_user import RegisteredUser
from models.tournament import Tournament
from views.create_tournament_modal import get_create_tournament_modal
from views.register_message_view import get_register_message_blocks
from views.report_scores_modal import get_report_scores_modal
from views.tournament_in_progress_view import get_tournament_in_progress_blocks


# Global Configurations
ssl._create_default_https_context = ssl._create_unverified_context
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
current_tournament: Tournament = None
slack_to_challonge_config = {}
channel_id = 'D05L6AJJGS2'


# Message Handlers
@app.message("user")
def message_matches(body, ack, say, client):
    global current_tournament
    global channel_id

    ack()
    current_tournament.add_user_to_tournament(user=RegisteredUser(
        {"name": "test", "profile": {"display_name_normalized": "test", "image_original": "google.com"}}, "", ""))


# Action Handlers
@app.action("join_tournament_button_click")
def join_tournament_button_click(body, ack, client, logger):
    global current_tournament
    global channel_id

    ack()
    if current_tournament is None or current_tournament.started is True:
        return

    user_info = client.users_info(user=body['user']['id'])['user']

    if body['user']['id'] not in slack_to_challonge_config:
        slack_to_challonge_config[body['user']['id']] = ''

    current_tournament.add_user_to_tournament(RegisteredUser(user_info, channel_id,
                                                             slack_to_challonge_config[body['user']['id']]))

    try:
        response = client.chat_update(
            channel=channel_id,
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
    global channel_id

    ack()

    current_tournament.toggle_ready_user_for_match(body['user']['name'])
    try:
        response = client.chat_update(
            channel=channel_id,
            text="Start",
            ts=current_tournament.in_progress_message_ts,
            blocks=get_tournament_in_progress_blocks(current_tournament)
        )
        print({"message": f"/start-tournament successful",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.action("ack-select-action")
def register_ack_select_action(ack):
    ack()


@app.action("ack-select-action-1")
def register_ack_select_action(ack, body):
    errors = {
        "input_select": "Please select a team option",
        "input_select2": "Please select an elimination option",
    }

    if any(errors.values()):
        ack(response_action="errors", errors=errors)
        return
    ack()


@app.action("ack-select-action-2")
def register_ack_select_action(ack, body):
    ack()


# View Handlers
@app.view("create_tournament_callback")
def handle_create_tournament_submission(ack, body, client, view, logger):
    global current_tournament
    global channel_id

    teams_option = view["state"]["values"]["input_select"]["ack-select-action"].get('selected_option')
    elim_option = view["state"]["values"]["input_select2"]["ack-select-action"].get('selected_option')
    start_time = view["state"]["values"]["input_time"]["timepicker-action"].get('selected_time')

    errors = {
        "input_select": "Please select a team option" if not teams_option else None,
        "input_select2": "Please select an elimination option" if not elim_option else None
    }

    tournament_type = ''
    if elim_option['text']['text'].__eq__('Single Elim'):
        tournament_type = 'single elimination'
    else:
        tournament_type = 'double elimination'

    if any(errors.values()):
        ack(response_action="errors", errors=errors)
        return
    ack()

    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text="Creating Tournament"
        )

        current_tournament = Tournament(teams_option['text']['text'], tournament_type,
                                        start_time, response['ts'])

        response = client.chat_update(
            channel=channel_id,
            text="Creating Tournament",
            ts=response['ts'],
            blocks=get_register_message_blocks(current_tournament)
        )

        print({"message": f"Tournament {current_tournament.tournament_id} Created",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


@app.view("report_score_callback")
def handle_report_score_submission(ack, body, view, client, logger):
    global current_tournament
    global channel_id

    ack()
    game_1_p1_score = view["state"]["values"]["game-1-selects"][
        "ack-select-action-1"].get('selected_option')
    game_1_p2_score = view["state"]["values"]["game-1-selects"][
        "ack-select-action-2"].get('selected_option')
    game_2_p1_score = view["state"]["values"]["game-2-selects"][
        "ack-select-action-1"].get('selected_option')
    game_2_p2_score = view["state"]["values"]["game-2-selects"][
        "ack-select-action-2"].get('selected_option')
    game_3_p1_score = view["state"]["values"]["game-3-selects"][
        "ack-select-action-1"].get('selected_option')
    game_3_p2_score = view["state"]["values"]["game-3-selects"][
        "ack-select-action-2"].get('selected_option')

    p1_games_won = 0
    p2_games_won = 0
    g1p1 = game_1_p1_score['text']['text']
    g1p2 = game_1_p2_score['text']['text']
    g2p1 = game_2_p1_score['text']['text']
    g2p2 = game_2_p2_score['text']['text']

    if int(g1p1) - int(g1p2) > 0:
        p1_games_won = 1 + p1_games_won
    else:
        p2_games_won +=1 + p2_games_won

    if int(g2p1) - int(g2p2) > 0:
        p1_games_won += 1 + p1_games_won
    else:
        p2_games_won += 1 + p2_games_won

    scores = f'{g1p1}-{g1p2},{g2p1}-{g2p2}'
    if game_3_p1_score and game_3_p2_score is not None:
        g3p1 = game_3_p1_score['text']['text']
        g3p2 = game_3_p2_score['text']['text']
        scores += f',{g3p1}-{g3p2}'
        if int(g3p1) - int(g3p2) > 0:
            p1_games_won += 1 + p1_games_won
        else:
            p2_games_won += 1 + p2_games_won

    if p1_games_won > p2_games_won:
        current_tournament.submit_match_scores("jordan.garces", scores, 1)
    else:
        current_tournament.submit_match_scores("jordan.garces", scores, 2)

    try:

        response = client.chat_update(
            channel=channel_id,
            text="Start",
            ts=current_tournament.in_progress_message_ts,
            blocks=get_tournament_in_progress_blocks(current_tournament)
        )
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


# Slash commands
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
    global channel_id

    ack()
    try:
        slack_to_challonge_config[command['user_id']] = command['text']
        save_config()
        response = client.chat_postEphemeral(
            channel=channel_id,
            text=f"Successfully connected your slack account to the challonge account {command['text']}",
        )
        print({"message": f"/link-challonge {command['user_id']} linked to {command['text']  }",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to create tournament {e}")


@app.command("/start-tournament")
def start_tournament_command(ack, body, client, logger):
    global current_tournament
    global channel_id

    ack()
    if current_tournament is None or current_tournament.started:
        return

    try:
        client.chat_delete(
            channel=channel_id,
            ts=current_tournament.register_message_ts,
        )

        response = client.chat_postMessage(
            channel=channel_id,
            text="Starting Tournament"
        )

        current_tournament.start_tournament(response['ts'])

        response = client.chat_update(
            channel=channel_id,
            text="Start",
            ts=response['ts'],
            blocks=get_tournament_in_progress_blocks(current_tournament)
        )

        print({"message": f"/start-tournament successful",
               "ts": datetime.datetime.now().strftime('%X'), "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.command("/report")
def report_score_command(ack, body, client, logger):
    ack()

    try:
        response = client.views_open(trigger_id=body["trigger_id"],
                                     view=get_report_scores_modal(current_tournament, body['user_name']))
        print({"message": "/report", "ts": datetime.datetime.now().strftime('%X'),
               "Response": response.__str__()})
    except Exception as e:
        logger.exception(f"Failed to create tournament {e}")


@app.command("/end-tournament")
def end_tournament_tournament(ack, command, client):
    global current_tournament

    ack()

    client.chat_delete(
        channel=channel_id,
        ts=current_tournament.in_progress_message_ts,
    )
    current_tournament.end_tournament()


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
