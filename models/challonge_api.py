import challonge
import random
import string


class ChallongeAPI:
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key
        self._authenticate()

    def _authenticate(self):
        challonge.set_credentials(self.username, self.api_key)


    @staticmethod
    def create_tournament(name, subdomain='voltserver', description='voltserver'):
        try:
            response = challonge.tournaments.create(
                name=name, url=''.join(random.choice
                                       (string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                       for _ in range(16)),
                subdomain=subdomain, description=description)
            return response
        except Exception as e:
            print(f"Error creating tournament: {e}")

    @staticmethod
    def add_user_to_tournament(username, tournament_id, challonge_user=None):
        try:
            response = challonge.participants.create(tournament=tournament_id, name=f''.join(random.choice
                                       (string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                       for _ in range(16)), challonge_username=challonge_user)
            print(response)
        except Exception as e:
            print(f"Error adding user to tournament: {e}")

    @staticmethod
    def get_bracket_image_url(tournament_id):
        try:
            response = challonge.tournaments.show(tournament=tournament_id)
            return response
        except Exception as e:
            print(f"Error adding user to tournament: {e}")

    @staticmethod
    def get_open_matches(tournament_identifier):
        open_matches = []
        try:
            tournament = challonge.tournaments.show(tournament_identifier)
            matches = challonge.matches.index(tournament["id"])
            for match in matches:
                if match["state"] == "open":
                    match_text = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Match of *{}* vs *{}*.".format(
                                challonge.participants.show(tournament["id"], match["player1_id"])["username"],
                                challonge.participants.show(tournament["id"], match["player2_id"])["username"]
                            )
                        }
                    }
                    open_matches.append(match_text)
        except Exception as e:
            print(f"Error fetching open matches: {e}")

        return open_matches

    @staticmethod
    def get_tournament_participants(tournament_identifier):
        try:
            tournament = challonge.tournaments.show(tournament_identifier)
            participants = challonge.participants.index(tournament["id"])
            print(participants)
            return participants
        except Exception as e:
            print(f"Error fetching open matches: {e}")

    @staticmethod
    def is_valid_challonge_name(tournament_identifier, challonge_name):
        try:
            participants = challonge.participants.index(tournament_identifier)
            for participant in participants:
                if participant["username"] == challonge_name:
                    return True
            return False
        except Exception as e:
            print(f"Error validating Challonge name: {e}")
            return False
