from app.optscale_api.invitation_api import OptScaleInvitationAPI


async def validate_user_invitation(email: str) -> bool:
    """
    This function checks if an invitation exists for the given email address.
    It's useful to decide whether the registration of a new user has to
    be allowed.
    :param email: The user's email address
    :return: True or False
    """

    invitation_api = OptScaleInvitationAPI()
    response = await invitation_api.get_list_of_invitations(email=email)
    no_invitations = {"invites": []}  # if no invitations were found
    if response.get("data", {}) == no_invitations:
        # there is no invitation
        return False
    else:
        return True
