"""
Wearable Device Integration Services

Supports OAuth flows for:
- Fitbit
- Apple Health
- Garmin
- Whoop
- Oura Ring
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from requests_oauthlib import OAuth1Session, OAuth2Session
import requests
import logging

from api.config import settings

logger = logging.getLogger(__name__)


class FitbitIntegration:
    """
    Fitbit API integration using OAuth 2.0

    Docs: https://dev.fitbit.com/build/reference/web-api/
    """

    AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    API_BASE = "https://api.fitbit.com/1"

    def __init__(self):
        self.client_id = settings.fitbit_client_id
        self.client_secret = settings.fitbit_client_secret
        self.redirect_uri = settings.fitbit_redirect_uri

    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL for user to authorize access.

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            URL to redirect user to for authorization
        """
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=[
                "activity",
                "heartrate",
                "sleep",
                "weight",
                "profile"
            ]
        )

        authorization_url, _ = oauth.authorization_url(
            self.AUTH_URL,
            state=state
        )

        logger.info(f"Generated Fitbit authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from callback

        Returns:
            dict with access_token, refresh_token, expires_in, user_id
        """
        response = requests.post(
            self.TOKEN_URL,
            auth=(self.client_id, self.client_secret),
            data={
                "client_id": self.client_id,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            logger.error(f"Fitbit token exchange failed: {response.text}")
            raise ValueError(f"Token exchange failed: {response.status_code}")

        token_data = response.json()
        logger.info(f"Successfully obtained Fitbit tokens for user {token_data.get('user_id')}")

        return token_data

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh expired access token.

        Args:
            refresh_token: Refresh token from previous authorization

        Returns:
            New token data
        """
        response = requests.post(
            self.TOKEN_URL,
            auth=(self.client_id, self.client_secret),
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        )

        if response.status_code != 200:
            logger.error(f"Fitbit token refresh failed: {response.text}")
            raise ValueError("Token refresh failed")

        return response.json()

    def get_activity_data(
        self,
        access_token: str,
        date: str = None
    ) -> Dict:
        """
        Fetch activity data (steps, distance, calories) for a specific date.

        Args:
            access_token: Valid Fitbit access token
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Activity data including steps, distance, calories, active minutes
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        response = requests.get(
            f"{self.API_BASE}/user/-/activities/date/{date}.json",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            logger.error(f"Fitbit API error: {response.status_code} - {response.text}")
            raise ValueError(f"Failed to fetch activity data: {response.status_code}")

        return response.json()

    def get_heart_rate_data(
        self,
        access_token: str,
        date: str = None
    ) -> Dict:
        """
        Fetch heart rate data for a specific date.

        Returns intraday time series and daily summary.
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        response = requests.get(
            f"{self.API_BASE}/user/-/activities/heart/date/{date}/1d.json",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch heart rate data: {response.status_code}")

        return response.json()

    def get_sleep_data(
        self,
        access_token: str,
        date: str = None
    ) -> Dict:
        """
        Fetch sleep data for a specific date.

        Returns sleep stages (deep, light, REM, awake), duration, efficiency.
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        response = requests.get(
            f"{self.API_BASE}/user/-/sleep/date/{date}.json",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch sleep data: {response.status_code}")

        return response.json()


class AppleHealthIntegration:
    """
    Apple HealthKit integration (server-side)

    Note: Apple Health data sync typically happens via iOS app using HealthKit SDK.
    Server-side access requires Apple Health Records API (for EHR data).

    For MVP, we'll accept data pushed from iOS app.
    """

    def validate_health_data(self, data: Dict) -> bool:
        """
        Validate health data submitted from iOS app.

        Args:
            data: Health data payload from iOS app

        Returns:
            True if valid
        """
        required_fields = ["device_type", "recorded_timestamp"]
        return all(field in data for field in required_fields)

    def process_health_data(self, data: Dict) -> Dict:
        """
        Process and normalize Apple Health data.

        Apple Health uses different units/formats than Fitbit,
        so normalize to standard format.
        """
        normalized = {
            "recorded_timestamp": data.get("recorded_timestamp"),
            "device_type": "apple_health",
            "steps": data.get("step_count"),
            "distance_meters": data.get("distance_walking_running"),  # meters
            "active_minutes": data.get("apple_exercise_time"),  # minutes
            "calories_burned": data.get("active_energy_burned"),  # kcal
            "resting_heart_rate": data.get("resting_heart_rate"),
            "avg_heart_rate": data.get("heart_rate_avg"),
            "sleep_minutes": data.get("sleep_analysis_in_bed"),
            "sleep_quality_score": None  # Apple doesn't provide quality score
        }

        return {k: v for k, v in normalized.items() if v is not None}


class GarminIntegration:
    """
    Garmin Connect API integration using OAuth 1.0

    Docs: https://developer.garmin.com/connect-api/
    """

    REQUEST_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/request_token"
    AUTHORIZE_URL = "https://connect.garmin.com/oauthConfirm"
    ACCESS_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    API_BASE = "https://apis.garmin.com"

    def __init__(self):
        self.consumer_key = settings.garmin_consumer_key
        self.consumer_secret = settings.garmin_consumer_secret

    def get_authorization_url(self, callback_uri: str) -> tuple[str, Dict]:
        """
        Get OAuth 1.0a authorization URL.

        Returns:
            (authorization_url, request_token_credentials)
        """
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            callback_uri=callback_uri
        )

        # Step 1: Get request token
        request_token = oauth.fetch_request_token(self.REQUEST_TOKEN_URL)

        # Step 2: Get authorization URL
        authorization_url = oauth.authorization_url(self.AUTHORIZE_URL)

        logger.info("Generated Garmin authorization URL")
        return authorization_url, request_token

    def exchange_verifier_for_token(
        self,
        oauth_token: str,
        oauth_token_secret: str,
        oauth_verifier: str
    ) -> Dict:
        """
        Exchange OAuth verifier for access token.

        Args:
            oauth_token: Request token
            oauth_token_secret: Request token secret
            oauth_verifier: Verifier from callback

        Returns:
            Access token credentials
        """
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=oauth_verifier
        )

        access_token = oauth.fetch_access_token(self.ACCESS_TOKEN_URL)

        logger.info("Successfully obtained Garmin access token")
        return access_token

    def get_daily_summary(
        self,
        access_token: str,
        access_token_secret: str,
        date: str = None
    ) -> Dict:
        """
        Fetch daily activity summary from Garmin.

        Args:
            access_token: OAuth access token
            access_token_secret: OAuth access token secret
            date: Date in YYYY-MM-DD format

        Returns:
            Daily summary including steps, calories, heart rate, sleep
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )

        response = oauth.get(
            f"{self.API_BASE}/wellness-api/rest/dailies",
            params={"uploadStartTimeInSeconds": int(datetime.fromisoformat(date).timestamp())}
        )

        if response.status_code != 200:
            logger.error(f"Garmin API error: {response.status_code}")
            raise ValueError(f"Failed to fetch Garmin data: {response.status_code}")

        return response.json()


# Wearable integration factory
def get_wearable_integration(device_type: str):
    """
    Factory function to get appropriate wearable integration.

    Args:
        device_type: Device type ('fitbit', 'apple_health', 'garmin', etc.)

    Returns:
        Integration instance

    Raises:
        ValueError if device type not supported
    """
    integrations = {
        "fitbit": FitbitIntegration,
        "apple_health": AppleHealthIntegration,
        "garmin": GarminIntegration,
    }

    integration_class = integrations.get(device_type.lower())
    if not integration_class:
        raise ValueError(f"Unsupported device type: {device_type}")

    return integration_class()