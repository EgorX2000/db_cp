from fastapi import APIRouter, HTTPException
import subprocess

router = APIRouter(prefix="/batch", tags=["Массовый импорт"])


@router.post("/import")
def batch_import():
    try:
        result = subprocess.run(
            ["python", "scripts/data_load.py"],
            cwd=".",
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            return {"status": "success", "message": "Данные загружены"}
        else:
            return {"status": "error", "message": "Ошибка при загрузке"}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Таймаут загрузки данных")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
