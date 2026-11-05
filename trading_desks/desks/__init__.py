"""Desks package exporting all 30 unique trading desks"""
from trading_desks.desks.base_desk import BaseTradingDesk
from trading_desks.desks.all_desks import get_all_trading_desks, get_desk_by_id, ALL_DESK_CLASSES

__all__ = ["BaseTradingDesk", "get_all_trading_desks", "get_desk_by_id", "ALL_DESK_CLASSES"]
