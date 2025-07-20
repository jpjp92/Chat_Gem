# 라이브러리 설정
import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from pypdf import PdfReader
import io
from PIL import Image
import base64
import uuid