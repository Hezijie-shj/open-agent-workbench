"""智能体广场服务."""

from app.mock_data import AGENTS


class MarketService:
    """智能体广场服务."""

    def list_agents(self) -> list[dict]:
        """获取智能体列表.

        :return: 智能体列表.
        :rtype: list[dict]
        """
        return AGENTS


market_service = MarketService()

