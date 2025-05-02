import json
import requests
import openai
from pathlib import Path
from django.conf import settings
from pydantic import BaseModel  # 데이터 유효성검사 + 자동 타입 변환

