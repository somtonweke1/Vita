"""
Wearable Device API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import secrets
import logging

from api.database import get_db, AuditLogger
from api.dependencies.auth import get_current_user
from api.services.wearable_integrations import get_wearable_integration
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wearables", tags=["Wearables"])


class WearableConnectRequest(BaseModel):
    member_id: str
    device_type: str  # 'fitbit', 'apple_health', 'garmin', 'whoop', 'oura'
    callback_url: Optional[str] = None


class WearableConnectResponse(BaseModel):
    authorization_url: str
    state: str


class WearableCallbackRequest(BaseModel):
    code: Optional[str] = None
    state: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_verifier: Optional[str] = None


class WearableConnectionStatus(BaseModel):
    member_id: str
    device_type: str
    connected: bool
    last_sync: Optional[datetime] = None
    data_points_synced: int = 0


@router.post(
    "/connect",
    response_model=WearableConnectResponse,
    summary="Initiate wearable device connection"
)
async def connect_wearable(
    request: WearableConnectRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Initiate OAuth flow to connect member's wearable device.

    Supported devices:
    - fitbit: Fitbit devices
    - apple_health: Apple Watch/iPhone Health app
    - garmin: Garmin watches
    - whoop: Whoop strap
    - oura: Oura ring

    Returns authorization URL for user to approve access.

    Flow:
    1. User clicks "Connect Fitbit" in portal
    2. Frontend calls this endpoint
    3. Backend generates OAuth URL
    4. Frontend redirects user to OAuth URL
    5. User approves access on device provider's site
    6. Provider redirects to callback URL
    7. Frontend calls /wearables/callback with code
    8. Backend exchanges code for tokens and saves
    """
    try:
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Get appropriate integration
        integration = get_wearable_integration(request.device_type)

        # Generate authorization URL
        if request.device_type == 'fitbit':
            auth_url = integration.get_authorization_url(state)
        elif request.device_type == 'garmin':
            callback_uri = request.callback_url or "http://localhost:3000/wearables/callback"
            auth_url, request_token = integration.get_authorization_url(callback_uri)

            # Store request token temporarily (in production: Redis/database)
            # In MVP, we'll return it in state
            state = f"{request.member_id}:{request_token['oauth_token']}:{request_token['oauth_token_secret']}"

        elif request.device_type == 'apple_health':
            # Apple Health doesn't use OAuth - data comes from iOS app
            # Return instructions URL instead
            auth_url = "vitanexus://connect-apple-health"
            state = request.member_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device type {request.device_type} not yet implemented"
            )

        # Store state temporarily for validation (in production: Redis with TTL)
        # For MVP, state validation will be basic

        logger.info(
            f"Generated wearable connection URL for member {request.member_id}, "
            f"device {request.device_type}"
        )

        return WearableConnectResponse(
            authorization_url=auth_url,
            state=state
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to initiate wearable connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect wearable device"
        )


@router.post(
    "/callback",
    response_model=WearableConnectionStatus,
    summary="OAuth callback handler"
)
async def wearable_oauth_callback(
    request: WearableCallbackRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Handle OAuth callback from wearable provider.

    This endpoint is called after user approves access on provider's site.

    For Fitbit (OAuth 2.0):
    - code: Authorization code
    - state: State parameter for validation

    For Garmin (OAuth 1.0a):
    - oauth_token: Request token
    - oauth_verifier: Verifier code
    """
    try:
        # Validate state (in production, verify against stored value)
        if not request.state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing state parameter"
            )

        # Determine device type from state or stored session
        # For MVP, we'll extract from state
        member_id = request.state.split(":")[0] if ":" in request.state else request.state

        # Handle Fitbit OAuth 2.0 callback
        if request.code:
            integration = get_wearable_integration("fitbit")
            token_data = integration.exchange_code_for_token(request.code)

            # Store tokens in database (encrypted)
            # In production:
            # wearable_connection = WearableConnection(
            #     member_id=member_id,
            #     device_type='fitbit',
            #     fitbit_user_id=token_data['user_id'],
            #     access_token=encrypt(token_data['access_token']),
            #     refresh_token=encrypt(token_data['refresh_token']),
            #     token_expires_at=datetime.now() + timedelta(seconds=token_data['expires_in']),
            #     connected_at=datetime.now()
            # )
            # db.add(wearable_connection)
            # db.commit()

            logger.info(f"Successfully connected Fitbit for member {member_id}")

            # Trigger initial data sync in background
            # background_tasks.add_task(sync_fitbit_data, member_id, token_data['access_token'])

        # Handle Garmin OAuth 1.0a callback
        elif request.oauth_token and request.oauth_verifier:
            # Extract request token secret from state
            parts = request.state.split(":")
            if len(parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state parameter"
                )

            member_id, oauth_token, oauth_token_secret = parts

            integration = get_wearable_integration("garmin")
            access_token = integration.exchange_verifier_for_token(
                oauth_token,
                oauth_token_secret,
                request.oauth_verifier
            )

            # Store Garmin tokens
            logger.info(f"Successfully connected Garmin for member {member_id}")

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing OAuth parameters"
            )

        # Log connection
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='create',
            table_name='wearable_connections',
            record_id=member_id,
            member_id=member_id,
            success=True,
            details={'device_type': 'fitbit'}  # Would be dynamic
        )

        return WearableConnectionStatus(
            member_id=member_id,
            device_type='fitbit',  # Would be determined from context
            connected=True,
            last_sync=datetime.utcnow(),
            data_points_synced=0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process wearable callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete device connection"
        )


@router.get(
    "/{member_id}/status",
    response_model=List[WearableConnectionStatus],
    summary="Get connected wearable devices"
)
async def get_wearable_connections(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve list of connected wearable devices for member.

    Returns connection status, last sync time, and data availability.
    """
    try:
        # In production: query database for connections
        # connections = db.query(WearableConnection)\
        #     .filter(WearableConnection.member_id == member_id)\
        #     .all()

        # Mock response
        mock_connections = [
            WearableConnectionStatus(
                member_id=member_id,
                device_type="fitbit",
                connected=True,
                last_sync=datetime.utcnow(),
                data_points_synced=1543
            )
        ]

        return mock_connections

    except Exception as e:
        logger.error(f"Failed to get wearable connections: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wearable connections"
        )


@router.delete(
    "/{member_id}/disconnect/{device_type}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect wearable device"
)
async def disconnect_wearable(
    member_id: str,
    device_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect and revoke access to wearable device.

    This will:
    1. Revoke OAuth tokens with provider
    2. Delete stored tokens from database
    3. Stop data sync

    Historical data is retained for analytics.
    """
    try:
        # In production:
        # 1. Get connection from database
        # connection = db.query(WearableConnection).filter(
        #     WearableConnection.member_id == member_id,
        #     WearableConnection.device_type == device_type
        # ).first()
        #
        # 2. Revoke tokens with provider
        # integration = get_wearable_integration(device_type)
        # integration.revoke_token(decrypt(connection.access_token))
        #
        # 3. Delete connection
        # db.delete(connection)
        # db.commit()

        logger.info(f"Disconnected {device_type} for member {member_id}")

        # Log disconnection
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='delete',
            table_name='wearable_connections',
            record_id=f"{member_id}:{device_type}",
            member_id=member_id,
            success=True
        )

        return None

    except Exception as e:
        logger.error(f"Failed to disconnect wearable: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect device"
        )