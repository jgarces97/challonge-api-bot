from models.tournament import Tournament


def get_report_scores_modal(tournament: Tournament, slack_username):
    report_blocks = []

    report_blocks.append(
        tournament.get_user_report_block(slack_username)
    )
    for game_num in range(1, 4):
        report_blocks.append({
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"Game {game_num}",
                    "emoji": True
                }
            })

        options_block = []
        for i in range(1, 22):
            options_block.append({
                                "text": {
                                    "type": "plain_text",
                                    "text": f"{i}",
                                    "emoji": True
                                },
                                "value": f"value-{i}"
                            })

        report_blocks.append({
            "type": "actions",
            "block_id": f"game-{game_num}-selects",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": options_block,
                    "action_id": "ack-select-action-1"
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": options_block,
                    "action_id": "ack-select-action-2"
                }
            ]
        })

    return {
        "title": {
            "type": "plain_text",
            "text": "Report Scores",
            "emoji": True
        },
        "callback_id": "report_score_callback",
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "type": "modal",
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": report_blocks
    }
