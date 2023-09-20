from models.challonge_api import ChallongeAPI
import os
import datetime

USERNAME = os.getenv("CHALLONGE_USERNAME", "jordan_garces")
API_KEY = os.getenv("CHALLONGE_API_KEY", "l023Fd0Funogz2JyxDqfPif6UeL10728JcfwLZfM")


class Tournament:
    def __init__(self, player_mode, elimination_mode, start_time, register_message_ts):
        self.player_mode = player_mode
        self.elimination_mode = elimination_mode
        self.start_time = start_time
        self.register_message_ts = register_message_ts
        self.registered_users = []
        ChallongeAPI(USERNAME, API_KEY)
        self.tournament_info = ChallongeAPI.create_tournament(
            name=f"Ping Pong {player_mode} {datetime.datetime.now().strftime('%A')} "
            f"{datetime.datetime.now().strftime('%d')}{datetime.datetime.now().strftime('%b')}"
            f"{datetime.datetime.now().strftime('%y')}")
        self.tournament_id = self.tournament_info['id']

    def add_user_to_tournament(self, user):
        self.registered_users.append(user)
        ChallongeAPI.add_user_to_tournament(username=user.slack_name, tournament_id=self.tournament_id,
                                            challonge_user=user.challonge_name)

    def get_bracket_image_url(self):
        return ChallongeAPI.get_bracket_image_url(self.tournament_id)

