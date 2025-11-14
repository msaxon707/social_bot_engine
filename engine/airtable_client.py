import os
import requests
from .utils import log

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

def _headers():
    return {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

def airtable_get(table):
    """Fetch rows from Airtable table."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table}"
    res = requests.get(url, headers=_headers())

    if res.status_code != 200:
        log(f"Airtable GET error: {res.text}")
        return None

    return res.json().get("records", [])

def airtable_create(table, fields):
    """Create a row in Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table}"
    payload = {"fields": fields}

    res = requests.post(url, headers=_headers(), json=payload)

    if res.status_code not in (200, 201):
        log(f"Airtable CREATE error: {res.text}")
        return None

    return res.json()

def airtable_update(table, record_id, fields):
    """Update an Airtable row."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table}/{record_id}"
    payload = {"fields": fields}

    res = requests.patch(url, headers=_headers(), json=payload)

    if res.status_code not in (200, 201):
        log(f"Airtable UPDATE error: {res.text}")
        return None

    return res.json()
