"""智能体广场接口."""

from fastapi import APIRouter

from app.services.market_service import market_service

router = APIRouter()


@router.get("/agents")
def list_agents() -> dict:
    """获取智能体广场列表.

    :return: 智能体列表响应.
    :rtype: dict
    """
    return {"code": 0, "message": "success", "data": market_service.list_agents()}

