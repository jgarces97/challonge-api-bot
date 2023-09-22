def get_create_tournament_modal():
    return {
        "type": "modal",
        "callback_id": "create_tournament_callback",
        "title": {"type": "plain_text", "text": "Create A New Tournament"},
        "submit": {"type": "plain_text", "text": "Create"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Singles or Teams?"},
                "block_id": "input_select",
                "accessory": {
                    "type": "static_select",

                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Singles",
                                "emoji": True
                            },
                            "value": "single"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Teams",
                                "emoji": True
                            },
                            "value": "team"
                        }
                    ],
                    "action_id": "ack-select-action"
                }
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Elimination Type"},
                "block_id": "input_select2",
                "accessory": {
                    "type": "static_select",

                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Single Elim",
                                "emoji": True
                            },
                            "value": "single-elim"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Double Elim",
                                "emoji": True
                            },
                            "value": "double-elim"
                        }
                    ],
                    "action_id": "ack-select-action"
                }
            },
            {
                "type": "input",
                "block_id": "input_time",
                "element": {
                    "type": "timepicker",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select time",
                        "emoji": True
                    },
                    "initial_time": "13:00",
                    "action_id": "timepicker-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Tournament Start Time",
                    "emoji": True
                }
            }
        ]
    }
