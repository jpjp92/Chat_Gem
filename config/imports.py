# config/imports.py
# =========================
# Chat_Gem Common Library Imports
# =========================

# --- Standard Library ---
import os
import sys
import io
import re
import json
import uuid
import base64
import logging
import random
import time
import types
import queue
import threading
import multiprocessing
import asyncio
import atexit
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import urllib.parse
import urllib.request

# --- External Libraries & Frameworks ---
import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
# from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from urllib3.util.retry import Retry
from pypdf import PdfReader
from PIL import Image

# --- Other Third-Party Packages ---
import aiohttp
import arxiv
import nest_asyncio
import pandas as pd
import pytz
from diskcache import Cache
from langdetect import detect
from requests.adapters import HTTPAdapter
from supabase import create_client
from timezonefinder import TimezoneFinder
# import yt_dlp

# Logger 설정
logger = logging.getLogger(__name__)