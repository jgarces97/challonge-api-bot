class RegisteredUser:
    def __init__(self, slack_user_info, slack_dm_channel_id, challonge_name=None):
        self.slack_username = slack_user_info['name']
        self.slack_name = slack_user_info['profile']['display_name_normalized']
        self.slack_dm_channel_id = slack_dm_channel_id
        self.slack_picture_url = slack_user_info['profile']['image_original']
        self.challonge_name = challonge_name
