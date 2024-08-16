import os
from django.shortcuts import render, redirect
from django.conf import settings
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.http import HttpResponseBadRequest
from .models import CredentialsModel
from django.utils import timezone

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback'

def gmail_authenticate(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('admin')

    credentials = CredentialsModel.objects.filter(user=user).first()
    if credentials:
        creds = Credentials(
            token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            CredentialsModel.objects.update_or_create(
                user=user,
                defaults={
                    'access_token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_expiry': creds.expiry,
                    'scope': ' '.join(creds.scopes),
                    'token_type': creds.token_type
                }
            )
        
        service = build('gmail', 'v1', credentials=creds)
        print('access_token = ', creds.token)
        status = True
        return render(request, 'index.html', {'status': status})
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, SCOPES)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
        )
        request.session['state'] = state
        return redirect(authorization_url)


def auth_return(request):
    state = request.session.get('state')
    if not state:
        return HttpResponseBadRequest()

    flow = InstalledAppFlow.from_client_secrets_file(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, SCOPES)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    user = request.user
    CredentialsModel.objects.update_or_create(
        user=user,
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': credentials.expiry,
            'scope': ' '.join(credentials.scopes),
            'token_type': credentials.token_type
        }
    )

    print("access_token: %s" % credentials.token)
    return redirect("/")

def home(request):
    status = True

    if not request.user.is_authenticated:
        return redirect('admin')

    credentials = CredentialsModel.objects.filter(user=request.user).first()
    if credentials:
        creds = Credentials(
            token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            CredentialsModel.objects.update_or_create(
                user=request.user,
                defaults={
                    'access_token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_expiry': creds.expiry,
                    'scope': ' '.join(creds.scopes),
                    'token_type': creds.token_type
                }
            )

        service = build('gmail', 'v1', credentials=creds)
        try:
            results = service.users().messages().list(userId='me').execute()
            status = bool(results.get('messages', []))
        except Exception as e:
            status = False
            print('Error fetching data:', e)
    else:
        status = False

    return render(request, 'index.html', {'status': status})
