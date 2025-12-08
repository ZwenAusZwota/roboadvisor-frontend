from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging

from database import get_db
from models import User, UserSettings
from main import get_current_user, get_password_hash, verify_password

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class UserProfileResponse(BaseModel):
    id: int
    name: Optional[str]
    email: str
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserSettingsResponse(BaseModel):
    timezone: Optional[str]
    language: Optional[str]
    currency: Optional[str]
    riskProfile: Optional[str]
    investmentHorizon: Optional[str]
    notifications: Optional[Dict[str, bool]]
    two_factor_enabled: bool
    
    class Config:
        from_attributes = True

class UserSettingsUpdate(BaseModel):
    timezone: Optional[str] = None
    language: Optional[str] = None
    currency: Optional[str] = None
    riskProfile: Optional[str] = None
    investmentHorizon: Optional[str] = None
    notifications: Optional[Dict[str, bool]] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class TwoFactorSetupRequest(BaseModel):
    enable: bool
    password: str

class DataExportResponse(BaseModel):
    message: str
    data: Dict

# Helper function to get or create user settings
def get_or_create_user_settings(db: Session, user_id: int) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.userId == user_id).first()
    if not settings:
        settings = UserSettings(
            userId=user_id,
            timezone="Europe/Berlin",
            language="de",
            currency="EUR",
            notifications={
                "dailyMarket": False,
                "weeklySummary": False,
                "aiRecommendations": False,
                "riskWarnings": True
            }
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

# GET /api/user/profile
@router.get("/api/user/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email
    )

# PUT /api/user/profile
@router.put("/api/user/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Check if email is being changed and if it's already taken
        if profile_update.email and profile_update.email != current_user.email:
            existing_user = db.query(User).filter(User.email == profile_update.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Diese E-Mail-Adresse ist bereits vergeben"
                )
            current_user.email = profile_update.email
        
        if profile_update.name is not None:
            current_user.name = profile_update.name
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile updated for user {current_user.id}")
        return UserProfileResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Aktualisieren des Profils"
        )

# GET /api/user/settings
@router.get("/api/user/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    settings = get_or_create_user_settings(db, current_user.id)
    return UserSettingsResponse(
        timezone=settings.timezone,
        language=settings.language,
        currency=settings.currency,
        riskProfile=settings.riskProfile,
        investmentHorizon=settings.investmentHorizon,
        notifications=settings.notifications or {},
        two_factor_enabled=settings.two_factor_enabled
    )

# PUT /api/user/settings
@router.put("/api/user/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    try:
        settings = get_or_create_user_settings(db, current_user.id)
        
        # Validate enum values
        if settings_update.language and settings_update.language not in ['de', 'en']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültige Sprache. Erlaubt: 'de', 'en'"
            )
        
        if settings_update.currency and settings_update.currency not in ['EUR', 'USD', 'CHF']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültige Währung. Erlaubt: 'EUR', 'USD', 'CHF'"
            )
        
        if settings_update.riskProfile and settings_update.riskProfile not in ['conservative', 'balanced', 'growth', 'aggressive']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges Risikoprofil. Erlaubt: 'conservative', 'balanced', 'growth', 'aggressive'"
            )
        
        if settings_update.investmentHorizon and settings_update.investmentHorizon not in ['short', 'medium', 'long']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiger Anlagehorizont. Erlaubt: 'short', 'medium', 'long'"
            )
        
        # Update fields
        if settings_update.timezone is not None:
            settings.timezone = settings_update.timezone
        if settings_update.language is not None:
            settings.language = settings_update.language
        if settings_update.currency is not None:
            settings.currency = settings_update.currency
        if settings_update.riskProfile is not None:
            settings.riskProfile = settings_update.riskProfile
        if settings_update.investmentHorizon is not None:
            settings.investmentHorizon = settings_update.investmentHorizon
        if settings_update.notifications is not None:
            # Merge notifications to keep existing values
            current_notifications = settings.notifications or {}
            current_notifications.update(settings_update.notifications)
            settings.notifications = current_notifications
        
        settings.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Settings updated for user {current_user.id}")
        return UserSettingsResponse(
            timezone=settings.timezone,
            language=settings.language,
            currency=settings.currency,
            riskProfile=settings.riskProfile,
            investmentHorizon=settings.investmentHorizon,
            notifications=settings.notifications or {},
            two_factor_enabled=settings.two_factor_enabled
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Aktualisieren der Einstellungen"
        )

# POST /api/user/change-password
@router.post("/api/user/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_request.current_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Aktuelles Passwort ist falsch"
            )
        
        # Validate new password
        if len(password_request.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Neues Passwort muss mindestens 6 Zeichen lang sein"
            )
        
        if len(password_request.new_password) > 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Neues Passwort ist zu lang (max. 128 Zeichen)"
            )
        
        # Update password
        current_user.password = get_password_hash(password_request.new_password)
        db.commit()
        
        logger.info(f"Password changed for user {current_user.id}")
        return {"message": "Passwort erfolgreich geändert"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Ändern des Passworts"
        )

# POST /api/user/2fa/setup
@router.post("/api/user/2fa/setup")
async def setup_2fa(
    two_factor_request: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup or disable 2FA"""
    try:
        # Verify password
        if not verify_password(two_factor_request.password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Passwort ist falsch"
            )
        
        settings = get_or_create_user_settings(db, current_user.id)
        
        if two_factor_request.enable:
            # In a real implementation, you would generate a TOTP secret here
            # For now, we just set the flag
            import secrets
            settings.two_factor_secret = secrets.token_urlsafe(32)
            settings.two_factor_enabled = True
            logger.info(f"2FA enabled for user {current_user.id}")
            return {
                "message": "2FA erfolgreich aktiviert",
                "secret": settings.two_factor_secret,  # In production, return QR code URL instead
                "enabled": True
            }
        else:
            settings.two_factor_enabled = False
            settings.two_factor_secret = None
            db.commit()
            logger.info(f"2FA disabled for user {current_user.id}")
            return {
                "message": "2FA erfolgreich deaktiviert",
                "enabled": False
            }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting up 2FA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Einrichten der 2FA"
        )

# POST /api/user/data-export
@router.post("/api/user/data-export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data"""
    try:
        settings = get_or_create_user_settings(db, current_user.id)
        
        # Collect all user data
        user_data = {
            "profile": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "created_at": None  # Add if you have this field
            },
            "settings": {
                "timezone": settings.timezone,
                "language": settings.language,
                "currency": settings.currency,
                "riskProfile": settings.riskProfile,
                "investmentHorizon": settings.investmentHorizon,
                "notifications": settings.notifications,
                "two_factor_enabled": settings.two_factor_enabled
            },
            "export_date": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data export requested for user {current_user.id}")
        
        # Return as JSON response
        return JSONResponse(
            content=user_data,
            headers={
                "Content-Disposition": f"attachment; filename=user_data_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Exportieren der Daten"
        )

# DELETE /api/user
@router.delete("/api/user")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    try:
        user_id = current_user.id
        user_email = current_user.email
        
        # Delete user (cascade will delete related data)
        db.delete(current_user)
        db.commit()
        
        logger.info(f"Account deleted for user {user_id} ({user_email})")
        return {"message": "Konto erfolgreich gelöscht"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Löschen des Kontos"
        )

