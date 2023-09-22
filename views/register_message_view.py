import datetime
import string

from models.tournament import Tournament

def get_register_message_blocks(current_tournament: Tournament):

    register_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":ping_pong:  Tournament Signup for {datetime.datetime.now().strftime('%x')}  :ping_pong:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f" :memo: *{len(current_tournament.registered_users)} Entries*"
            }
        }
    ]

    for user in current_tournament.registered_users:
        register_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{user.slack_name}"
            },
            "accessory": {
                "type": "image",
                "image_url": f"{user.slack_picture_url}",
                "alt_text": "cute cat"
            }})

    register_blocks.append({
        "type": "divider"
    })

    register_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":alarm_clock: Tournament starts at "
                        f"*{datetime.datetime.strptime(current_tournament.start_time,'%H:%M').strftime('%I:%M %p')}*"
                        f"\n:standing_person: Entry Type: {current_tournament.player_mode}"
                        f"\n:crossed_swords: Tournament Type: {string.capwords(current_tournament.elimination_mode)}"
            }
        })

    register_blocks.append({
        "type": "divider"
    })

    register_blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Join",
                    "emoji": True
                },
                "style": "primary",
                "value": "click_me_123",
                "action_id": "join_tournament_button_click"
            }
        ]
    })
    return register_blocks
