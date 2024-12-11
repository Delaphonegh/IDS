import atexit
import csv
import os
from os import environ
from uuid import uuid4
import secrets
from random import randint, choice
import string
import requests
from requests.auth import HTTPBasicAuth
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, Blueprint, session, redirect, url_for, jsonify, current_app, request
from flask_login import login_required
from sqlalchemy import and_, or_, desc
from flask_mail import Mail, Message
from datetime import date,datetime
from structure import db,mail ,photos,app
from structure.core.forms import FilterForm,SipRequestForm , IssueForm,NumberSearchForm,ExtForm
from structure.about.forms import AboutForm
from structure.web.forms import SearchForm ,AddFoodsForm
from structure.models import User 
from werkzeug.utils import secure_filename
# from PIL import Image
# import pytesseract 
# from io import BytesIO
import base64
from faker import Faker

web = Blueprint('web', __name__)
