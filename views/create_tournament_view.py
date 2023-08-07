def get_create_view():
    return {
        "type": "modal",
        "callback_id": "view_1",
        "title": {"type": "plain_text", "text": "Create A New Tournament"},
        "submit": {"type": "plain_text", "text": "Create"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Singles or Doubles Tournament"},
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
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Doubles",
                                "emoji": True
                            },
                            "value": "value-1"
                        }
                    ],
                    "action_id": "static_select-action"
                }
            }
        ]
    }
