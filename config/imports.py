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
from datetime import datetime, timedelta, timezone
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

# Logger 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # 기본 로그 레벨 설정

# Supabase 클라이언트 초기화 (환경 변수 사용)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# 나머지 임포트
from timezonefinder import TimezoneFinder
# import yt_dlp