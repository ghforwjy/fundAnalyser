from portfolio_manager import PortfolioManager

pm = PortfolioManager()
result = pm.get_portfolio_profit_loss_report(2, '2025-12-31', '2026-02-16')
print("Result:", result)
