from typing import Optional

import requests


def query_passman(pass_type: str, nick_name: str, token: str) -> Optional[dict]:
    """


    Args:
        nick_name:
        token:

    Returns:

    """
    url = f"http://dev-integ-env.k8s.iflyrec.com/Passman/api/credentials/{pass_type}/{nick_name}"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        return None
