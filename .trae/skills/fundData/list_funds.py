import sys
sys.path.insert(0, r'd:\mycode\fundAnalyser\.trae\skills\fundData')
from portfolio_manager import list_portfolio_funds
import json

funds = list_portfolio_funds(2)
print(json.dumps(funds, ensure_ascii=False, indent=2, default=str))
