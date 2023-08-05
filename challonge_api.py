import challonge


def create_tournament():
    challonge.tournaments.destroy("dsadsaddsa3qqsad")
    challonge.tournaments.create("test", "dsadsaddsa3qqsad", subdomain='voltserver', description="voltserver")


def get_tournament_open_matches():
    tournament = challonge.tournaments.show('voltserver-u1ekdgjd')
    matches = challonge.matches.index(tournament["id"])
    open_matches = []
    for match in matches:
        if match["state"] == "open":
            var = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Match of *{}* vs *{}*.".format(
                        challonge.participants.show(tournament["id"], match["player1_id"])["username"],
                        challonge.participants.show(tournament["id"], match["player2_id"])["username"])
                }
            }
            open_matches.append(var)
    return open_matches




def auth_challonge():
    challonge.set_credentials("jordan_garces", "l023Fd0Funogz2JyxDqfPif6UeL10728JcfwLZfM")
