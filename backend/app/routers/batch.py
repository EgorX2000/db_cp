from fastapi import APIRouter, HTTPException
import subprocess
import os

router = APIRouter(prefix="/batch", tags=["Массовый импорт"])


@router.post("/import")
def batch_import():
    try:
        result = subprocess.run(
            ["python", "scripts/data_load.py"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            return {"status": "success", "message": "Данные загружены", "output": result.stdout}
        else:
            return {"status": "error", "error": result.stderr}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Таймаут загрузки данных")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
