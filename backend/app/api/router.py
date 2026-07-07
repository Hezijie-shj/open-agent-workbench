"""接口路由聚合."""

from fastapi import APIRouter

from app.api.endpoints import bank_statement, document_diff, market, regulations

api_router = APIRouter()
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(bank_statement.router, prefix="/bank_statement", tags=["bank_statement"])
api_router.include_router(regulations.router, prefix="/regulations", tags=["regulations"])
api_router.include_router(document_diff.router, prefix="/document_diff", tags=["document_diff"])
