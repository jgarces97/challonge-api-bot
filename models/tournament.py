import os
import datetime
import challonge
import random
import string
from models.registered_user import RegisteredUser
import cairosvg
from imgurpython import ImgurClient

USERNAME = os.getenv("CHALLONGE_USERNAME", "jordan_garces")
API_KEY = os.getenv("CHALLONGE_API_KEY", "l023Fd0Funogz2JyxDqfPif6UeL10728JcfwLZfM")


class Tournament:
    def __init__(self, player_mode, elimination_mode, start_time, register_message_ts):
        self.player_mode = player_mode
        self.elimination_mode = elimination_mode
        self.start_time = start_time
        self.register_message_ts = register_message_ts
        self.registered_users: list[RegisteredUser] = []
        challonge.set_credentials(USERNAME, API_KEY)
        try:
            self.tournament_info = challonge.tournaments.create(
                name=f"Ping Pong {player_mode} {datetime.datetime.now().strftime('%A')} "
                     f"{datetime.datetime.now().strftime('%d')}{datetime.datetime.now().strftime('%b')}"
                     f"{datetime.datetime.now().strftime('%y')}",
                url=''.join(random.choice
                            (string.ascii_uppercase + string.ascii_lowercase + string.digits)
                            for _ in range(16)),
                subdomain='voltserver', description='voltserver')
        except Exception as e:
            print(f"Error creating tournament: {e}")
        self.tournament_id = self.tournament_info['id']
        self.started = False
        self.bracket_image_url = None

    def add_user_to_tournament(self, user):
        if self.registered_users.__contains__(user):
            return

        self.registered_users.append(user)
        try:
            challonge.participants.create(
                tournament=self.tournament_id, name=user.slack_name,
                challonge_username=user.challonge_name)
        except Exception as e:
            print(f"Error adding user to tournament: {e}")

    def update_bracket_image_url(self):
        try:
            response = challonge.tournaments.show(tournament=self.tournament_id)
            self.convert_svg_to_png(response['live_image_url'], 'test.png')
            self.bracket_image_url = self.upload_to_imgur('test.png', '9d46ad026c630af',
                                                          '6b86792a2498ff35bac40279072e610e63a0ba35')
        except Exception as e:
            print(f"Error adding user to tournament: {e}")

    def start_tournament(self):
        try:
            response = challonge.tournaments.start(tournament=self.tournament_id)
            self.update_bracket_image_url()
            return response
        except Exception as e:
            print(f"Error adding user to tournament: {e}")

    def get_match_head_to_head_blocks(self):
        matches = self.get_current_matches()
        register_blocks = []

        for match in matches:
            name1 = challonge.participants.show(self.tournament_id, match['player1_id'])['name']
            name2 = challonge.participants.show(self.tournament_id, match['player2_id'])['name']

            ready_img = 'https://cdn1.iconfinder.com/data/icons/' \
                        'jetflat-multimedia-vol-4/90/0042_089_check_well_ready_okey-512.png'
            not_ready_img = 'https://www.robertdylina.com/wp-content/' \
                            'uploads/2021/05/Flat_design_stop_sign_icon_vector-1024x972.jpg'

            img1 = 'https://cdn1.iconfinder.com/data/icons/' \
                        'jetflat-multimedia-vol-4/90/0042_089_check_well_ready_okey-512.png'
            img2 = 'https://www.robertdylina.com/wp-content/' \
                            'uploads/2021/05/Flat_design_stop_sign_icon_vector-1024x972.jpg'

            for user in self.registered_users:
                if user.slack_name is name1:
                    if user.ready_for_match:
                        img1 = ready_img
                    else:
                        img1 = not_ready_img
                else:
                    if user.ready_for_match:
                        img2 = ready_img
                    else:
                        img2 = not_ready_img

            register_blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": f"{img1}",
                        "alt_text": "cute cat"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f" *{name1}* vs.*{name2}* "
                    },

                    {
                        "type": "image",
                        "image_url": f"{img2}",
                        "alt_text": "cute cat"
                    }
                ]
            })
        return register_blocks

    def get_current_matches(self):
        try:
            response = challonge.matches.index(tournament=self.tournament_id)
            matches = []

            for match in response:
                if match['state'] == 'open':
                    matches.append(match)
            return matches
        except Exception as e:
            print(f"Error adding user to tournament: {e}")

    def is_slack_user_registered(self, slack_username):
        for user in self.registered_users:
            if user.slack_name is slack_username:
                return True
        return False

    def toggle_ready_user_for_match(self, slack_username):
        if not self.started:
            return

        for user in self.registered_users:
            if user.slack_name is slack_username:
                user.ready_for_match = not user.ready_for_match

    def unready_all_users(self):
        for user in self.registered_users:
            user.ready_for_match = False

    @staticmethod
    def convert_svg_to_png(input_svg_path, output_png_path):
        """Converts an SVG file to PNG."""
        cairosvg.svg2png(url=input_svg_path, write_to=output_png_path)

    @staticmethod
    def upload_to_imgur(png_path, client_id, client_secret):
        """Uploads a PNG file to Imgur and returns its direct link."""
        client = ImgurClient(client_id, client_secret)
        result = client.upload_from_path(png_path, config=None, anon=True)
        return result['link']

    def __str__(self):
        thing = {
            "id": self.tournament_id,
            "player_mode": self.player_mode,
            "elim_type": self.elimination_mode,
            "start_time": self.start_time,
            "register_msg_ts": self.register_message_ts,
            "registered_users": self.registered_users,
            "tournament_info": self.tournament_info
        }
        return thing.__str__()
