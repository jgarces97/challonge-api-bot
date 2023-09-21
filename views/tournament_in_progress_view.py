import datetime


def get_tournament_in_progress_blocks(tournament):
    register_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":ping_pong: Tournament for {datetime.datetime.now().strftime('%x')}  :ping_pong:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Bracket",
                "emoji": True
            },
            "image_url": f"{tournament.bracket_image_url}",
            "alt_text": "bracket"
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f" :memo: *Current matches to play*"
            }
        }
    ]

    for match in tournament.get_match_head_to_head_blocks():
        register_blocks.append(match)

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
                    "text": "Ready/Unready for Match",
                    "emoji": True
                },
                "style": "primary",
                "value": "click_me_123",
                "action_id": "toggle_ready_match_button_click"
            }
        ]
    })

    return register_blocks
