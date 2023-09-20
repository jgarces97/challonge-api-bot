import datetime


def get_register_message_blocks(teams_option, elimination_type, start_time, registered_users=None):
    if registered_users is None:
        registered_users = []

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
                "text": f" :memo: *{len(registered_users)} Entries*"
            }
        }
    ]

    for user in registered_users:
        register_blocks.append({
            "type": "divider"
        })
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
                        f"*{datetime.datetime.strptime(start_time,'%H:%M').strftime('%I:%M %p')}*"
                        f"\n:standing_person: Entry Type: {teams_option}"
                        f"\n:crossed_swords: Tournament Type: {elimination_type}"
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