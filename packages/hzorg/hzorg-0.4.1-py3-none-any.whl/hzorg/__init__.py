import json
from hcloud import Client
import os
import sys
import time
import requests
import rich
from rich.pretty import pprint as PP
import datetime


g_token = None
g_token_ns = None


g_client = None
g_client_ns = None


def load_clients():
    global g_client
    global g_client_ns
    global g_token
    global g_token_ns
    g_token = os.environ.get("HZORG_TOKEN", "")
    if g_token != "":
        g_client = Client(token=g_token)
    g_token_ns = os.environ.get("HZORG_TOKEN_NS", "")
    if g_token_ns != "":
        g_client_ns = Client(token=g_token_ns)

    if g_client is None and g_client_ns is None:
        raise Exception("No Clients initalized")

def main():
    load_clients()
    print("main")
    all = g_client.servers.get_all()
    lines = [x.name for x in all]
    PP(lines)
