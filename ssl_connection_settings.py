# Functions to change SSL settings
# Emilio Lehoucq
# This script uses code generated by ChatGPT and GitHub Copilot

# Importing libraries
import requests
import urllib3
import ssl

# Function to create a session with legacy SSL settings
# https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled/71646353#71646353

class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))    
    return session

if __name__ == '__main__':
    print('Module to change SSL settings run successfully!')