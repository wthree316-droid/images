import os
from fastapi import APIRouter, HTTPException
from database import supabase, execute_supabase
from pydantic import BaseModel

BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "assets_image") 

router = APIRouter(prefix="/api/assets", tags=["Lotto Assets"])

class AssetCreate(BaseModel):
    name: str
    url: str

@router.get("")
def get_assets():
    try:
        response = execute_supabase(supabase.table("assets_image").select("*").order("created_at", desc=True))
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
def create_asset(request: AssetCreate):
    try:
        data = {"name": request.name, "url": request.url}
        execute_supabase(supabase.table("assets_image").insert(data))
        return {"message": "Asset added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{asset_id}")
def delete_asset(asset_id: str):
    try:
        # 1. ดึง URL มาก่อนเพื่อเตรียมลบไฟล์ใน Storage
        asset_res = execute_supabase(supabase.table("assets_image").select("url").eq("id", asset_id).limit(1))
        
        # 2. ลบข้อมูลจาก Database
        execute_supabase(supabase.table("assets_image").delete().eq("id", asset_id))

        # 3. ลบไฟล์จริงๆ ออกจาก Storage
        if asset_res.data and asset_res.data[0].get("url"):
            url = asset_res.data[0]["url"]
            

            if f"{BUCKET_NAME}/" in url:
                file_path = url.split(f"{BUCKET_NAME}/")[1]
                supabase.storage.from_(BUCKET_NAME).remove([file_path])
    
        return {"message": "Asset deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))