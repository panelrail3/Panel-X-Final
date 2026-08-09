import io, base64
import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.subscription import Subscription
from ..models.user import User
from ..security import require_admin
from ..api.subscriptions import make_uri
router=APIRouter(prefix="/api/qr",tags=["qr"])
@router.get("/{token}")
def qr(token:str,db:Session=Depends(get_db),_=Depends(require_admin)):
    sub=db.query(Subscription).filter(Subscription.token==token).first()
    if not sub: raise HTTPException(404,"subscription not found")
    user=db.get(User,sub.user_id)
    uri=make_uri(user)
    img=qrcode.make(uri); buf=io.BytesIO(); img.save(buf,format="PNG")
    return Response(buf.getvalue(),media_type="image/png")
