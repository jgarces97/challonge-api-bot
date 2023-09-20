def get_join_tournament_modal():
    return {
        "type": "modal",
        "callback_id": "join_tournament_modal",
        "title": {"type": "plain_text", "text": "Join Tournament"},
        "submit": {"type": "plain_text", "text": "Join"},
        "blocks": [
            {
                "type": "input",
                "block_id": "section-radio",
                "element": {
                    "type": "radio_buttons",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Use Challonge Username",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Use Slack Username",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Use Custom Username",
                                "emoji": True
                            },
                            "value": "value-2"
                        }
                    ],
                    "action_id": "ack-select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "How would you like to be known?",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "section-challonge",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "ack-select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Challonge/Custom Username",
                    "emoji": True
                }
            }
        ]
    }
