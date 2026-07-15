from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import uuid

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models.user import User
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAToggleRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    await db.flush()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        image=user.image,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # Find user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=30),
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        image=current_user.image,
        created_at=current_user.created_at,
    )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Simulating sending forgot password email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user:
        # Avoid user enumeration - return success anyway
        return {"status": "success", "message": "If the email exists, a reset link has been sent."}
    
    # Mock token generation & sending
    return {"status": "success", "message": "If the email exists, a reset link has been sent.", "token": f"mock-token-{uuid.uuid4()}"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Verify mock token and reset password
    if not request.token.startswith("mock-token-"):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Normally we lookup the user by token. For mock we'll just return success
    return {"status": "success", "message": "Password has been reset successfully."}


@router.get("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(current_user: User = Depends(get_current_user)):
    # Generate mock TOTP secret and QR code
    mock_secret = "JBSWY3DPEHPK3PXP"
    mock_qr = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=otpauth://totp/ContentPilot:" + current_user.email + "%3Fsecret%3D" + mock_secret + "%26issuer%3DContentPilot"
    return MFASetupResponse(secret=mock_secret, qr_code=mock_qr)


@router.post("/mfa/verify")
async def mfa_verify(request: MFAVerifyRequest, current_user: User = Depends(get_current_user)):
    # Verify mock TOTP code (always accept '123456' or verify format)
    if request.code == "123456" or len(request.code) == 6:
         return {"status": "success", "message": "MFA code verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification code")


@router.post("/mfa/toggle")
async def mfa_toggle(request: MFAToggleRequest, current_user: User = Depends(get_current_user)):
    # Toggle MFA status (mock backend state update)
    return {"status": "success", "mfa_enabled": request.enabled}

