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
from views.join_tournament_modal import get_join_tournament_modal
import cairosvg
from imgurpython import ImgurClient

# Global Configurations
ssl._create_default_https_context = ssl._create_unverified_context
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
current_tournament = None
slack_to_challonge_config = {}


# Message Handlers
@app.message("user")
def message_matches(body, ack, say, client):
    global current_tournament

    ack()
    convert_svg_to_png(current_tournament.get_bracket_image_url()['live_image_url'], 'test.png')
    image_link = upload_to_imgur('test.png', '9d46ad026c630af', '6b86792a2498ff35bac40279072e610e63a0ba35')
    response = client.chat_postMessage(
        channel=body['event']['user'],
        text="",
        blocks=[{
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "I Need a Marg",
                "emoji": True
            },
            "image_url": f"{image_link}",
            "alt_text": "marg"
        }]
    )


# Action Handlers
@app.action("join_tournament_button_click")
def join_tournament_button_click(body, ack, client, logger):
    global current_tournament

    ack()
    user_channel_id = client.conversations_open(users=body['user']['id'])['channel']['id']
    user_info = client.users_info(user=body['user']['id'])['user']

    current_tournament.add_user_to_tournament(RegisteredUser(user_info, user_channel_id,
                                                             slack_to_challonge_config[body['user']['id']]))

    try:
        client.chat_update(
            channel=user_channel_id,
            ts=current_tournament.register_message_ts,
            blocks=get_register_message_blocks(current_tournament.player_mode,
                                               current_tournament.elimination_mode,
                                               current_tournament.start_time, current_tournament.registered_users)
        )
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.action("button-action")
def register_action_button_click(body, ack, say):
    ack()
    user_name = body['user']['name']
    selected_value = body['actions'][0]['value']


@app.action("ack-select-action")
def register_ack_select_action(ack):
    ack()


# View Handlers
@app.view("create_tournament_view")
def handle_creation_submission(ack, body, client, view, logger):
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
            text="",
            blocks=get_register_message_blocks(teams_option['text']['text'],
                                               elim_option['text']['text'], start_time)
        )

        current_tournament = Tournament(teams_option['text']['text'], elim_option['text']['text'],
                                        start_time, response['ts'])
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


@app.view("join_tournament_modal")
def handle_tournament_join(ack, body, client, view, logger):
    global current_tournament

    user_option = view["state"]["values"]["section-radio"]["ack-select-action"]
    challonge_name = view["state"]["values"]["section-challonge"]["ack-select-action"].get('value', '')

    ack()
    user_channel_id = client.conversations_open(users=body['user']['id'])['channel']['id']
    user_info = client.users_info(user=body['user']['id'])['user']

    current_tournament.add_user_to_tournament(RegisteredUser(user_info, user_channel_id,
                                                             slack_to_challonge_config[body['user']['id']]))

    try:
        client.chat_update(
            channel=user_channel_id,
            ts=current_tournament.register_message_ts,
            blocks=get_register_message_blocks(current_tournament.player_mode,
                                               current_tournament.elimination_mode,
                                               current_tournament.start_time, current_tournament.registered_users)
        )
    except Exception as e:
        logger.exception(f"Failed to update the message {e}")


@app.command("/new-tournament")
def open_create_tournament_modal(ack, body, client):
    ack()
    client.views_open(trigger_id=body["trigger_id"], view=get_create_tournament_modal())


@app.command("/link-challonge")
def open_create_tournament_modal(ack, command, client):
    ack()
    slack_to_challonge_config[command['user_id']] = command['text']
    save_config()
    response = client.chat_postMessage(
        channel=command['user_id'],
        text=f"Successfully connected your slack to the challonge account {command['text']}",
    )


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


def convert_svg_to_png(input_svg_path, output_png_path):
    """Converts an SVG file to PNG."""
    cairosvg.svg2png(url=input_svg_path, write_to=output_png_path)


def upload_to_imgur(png_path, client_id, client_secret):
    """Uploads a PNG file to Imgur and returns its direct link."""
    client = ImgurClient(client_id, client_secret)
    result = client.upload_from_path(png_path, config=None, anon=True)
    return result['link']


if __name__ == '__main__':
    load_config()
    context = ssl._create_unverified_context()
    sc = slack_sdk.WebClient(os.environ["SLACK_APP_TOKEN"], ssl=context)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], web_client=sc).start()
