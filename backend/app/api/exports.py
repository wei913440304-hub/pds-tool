"""CSV 导出文件 API。"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..auth import get_current_user
from ..config import DATA_DIR
from .. import models

router = APIRouter(prefix="/api/exports", tags=["exports"])

EXPORTS_DIR = DATA_DIR / "exports"


@router.get("/")
async def list_exports(
    current_user: models.User = Depends(get_current_user),
):
    """列出所有 CSV 导出文件。"""
    if not EXPORTS_DIR.exists():
        return {"files": []}

    files = []
    for f in sorted(EXPORTS_DIR.glob("*.csv"), reverse=True):
        stat = f.stat()
        files.append({
            "filename": f.name,
            "size": stat.st_size,
            "created_at": stat.st_mtime,
        })

    return {"files": files}


@router.get("/{filename}/download")
async def download_export(
    filename: str,
    current_user: models.User = Depends(get_current_user),
):
    """下载指定 CSV 文件。"""
    # 路径遍历防护
    filepath = (EXPORTS_DIR / filename).resolve()
    if not str(filepath).startswith(str(EXPORTS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Invalid filename")

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="text/csv",
    )
