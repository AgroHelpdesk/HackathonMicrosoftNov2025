import httpx
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("acs_identity")

# NOTE: For server-to-server operations, using the ACS access key (primary key) for Authorization header is fine.
# If you need ephemeral tokens for client SDK usage, implement createUser + issueAccessToken flows.

async def create_user_and_token(scopes: list = ["chat"]):
    """
    Create a user and issue a token (expires in short time).
    Useful if frontend must interact directly with ACS (not our case).
    """
    url_user = f"{settings.ACS_ENDPOINT}/identities?api-version=2021-10-01"
    headers = {"Ocp-Apim-Subscription-Key": settings.ACS_ACCESS_KEY}
    async with httpx.AsyncClient() as client:
        res = await client.post(url_user, headers=headers)
        res.raise_for_status()
        user = res.json()
        # issue token
        url_token = f"{settings.ACS_ENDPOINT}/identities/{user['identity']['id']}/:issueAccessToken?api-version=2021-10-01"
        payload = {"scopes": scopes}
        res2 = await client.post(url_token, json=payload, headers=headers)
        res2.raise_for_status()
        token = res2.json()
        return {"user": user, "token": token}
