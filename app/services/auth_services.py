import requests,os
from flask import session

AUTH_URL = os.getenv('AUTH_URL')

def refresh_token():
    """Solicita un nuevo accessToken usando el refreshToken"""
    if "refresh_token" not in session:
        print("refresh_token no existe en la sesión")
        return None
    
    res = requests.post(
        f"{AUTH_URL}/refresh-token",
        json={"refreshToken": session["refresh_token"]}
    )

    if not res.ok:
        print("Error renovando token:", res.text)
        return None

    data = res.json()
    session["access_token"] = data["accessToken"]
    return data["accessToken"]

def t_api_get(url, params=None):
    """Hace GET con auto-renovación de tokens"""
    token = session.get("access_token")

    res = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )

    if res.status_code == 401:   # token expiró
        new_token = refresh_token()

        if not new_token:
            return {"statusCode": 400, "message": "No hay refresh token"}

        res = requests.get(
            url,
            headers={"Authorization": f"Bearer {new_token}"},
            params=params
        )

    return res.json()


def t_api_post(url, json=None):
    """Hace POST con auto-renovación de tokens"""
    token = session.get("access_token")

    res = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=json
    )

    if res.status_code == 401:
        new_token = refresh_token()

        if not new_token:
            return {"statusCode": 400, "message": "No hay refresh token"}

        res = requests.post(
            url,
            headers={"Authorization": f"Bearer {new_token}"},
            json=json
        )
    return res.json()

def t_api_put(url, json=None):
    token = session.get("access_token")

    res = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=json
    )

    if res.status_code == 401:
        new_token = refresh_token()

        if not new_token:
            return {"statusCode": 400, "message": "No hay refresh token"}

        res = requests.put(
            url,
            headers={"Authorization": f"Bearer {new_token}"},
            json=json
        )
    return res.json()

def t_api_delete(url, json=None):
    token = session.get("access_token")

    res = requests.delete(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=json
    )

    if res.status_code == 401:
        new_token = refresh_token()

        if not new_token:
            return {"statusCode": 400, "message": "No hay refresh token"}

        res = requests.delete(
            url,
            headers={"Authorization": f"Bearer {new_token}"},
            json=json
        )
    return res.json()