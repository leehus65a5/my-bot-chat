#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import dotenv

dotenv.load_dotenv()
""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", os.getenv("MicrosoftAppId"))
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", os.getenv("MicrosoftAppPassword"))
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ORG_ID = os.getenv('OPENAI_ORG_ID')
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    QDRANT_ENDPOINT = os.getenv('QDRANT_ENDPOINT')
    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
    