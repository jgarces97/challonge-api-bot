def get_waiting_to_start_view(teams_option, elimination_type, start_time, registered_users):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{teams_option} {elimination_type} Ping Pong Tournament scheduled for {start_time} is going to begin soon. *Join now*!"
            },
            "accessory": {
                "type": "image",
                "image_url": "https://rlv.zcache.com/dark_green_blue_solid_color_ping_pong_paddle-r6c0a21b1140e4bbaae07939d8c5586ba_zvmtl_630.jpg?rlvnet=1&view_padding=%5B285%2C0%2C285%2C0%5D",
                "alt_text": "cute cat"
            }},
        registered_users,
        {
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
                    "action_id": "button_click"
                }
            ]
        }
    ]
