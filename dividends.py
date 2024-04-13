import yfinance as yf

def fetch_financial_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    dividends = hist['Dividends'].sum()  # Total dividends paid over the last 5 years
    earnings = stock.earnings
    cashflow = stock.cashflow
    return dividends, earnings, cashflow

def calculate_ratios(dividends, earnings, cashflow):
    net_income = earnings['Net Income'].sum() if 'Net Income' in earnings else 0
    dividends_paid = dividends
    cash_from_operations = cashflow['Total Cash From Operating Activities'].sum() if 'Total Cash From Operating Activities' in cashflow else 0
    capital_expenditures = cashflow['Capital Expenditures'].sum() if 'Capital Expenditures' in cashflow else 0

    dividend_payout_ratio = dividends_paid / net_income if net_income != 0 else float('inf')
    free_cash_flow = cash_from_operations + capital_expenditures
    free_cash_flow_coverage = free_cash_flow / dividends_paid if dividends_paid != 0 else float('inf')

    return {
        "dividend_payout_ratio": dividend_payout_ratio,
        "free_cash_flow": free_cash_flow,
        "free_cash_flow_coverage": free_cash_flow_coverage
    }

def assess_dividend_sustainability(ratios):
    if ratios['dividend_payout_ratio'] > 0.8 or ratios['free_cash_flow_coverage'] < 1.5:
        return "Dividends may not be sustainable."
    else:
        return "Dividends appear to be sustainable."

def main(ticker):
    dividends, earnings, cashflow = fetch_financial_data(ticker)
    ratios = calculate_ratios(dividends, earnings, cashflow)
    assessment = assess_dividend_sustainability(ratios)
    print(assessment)

# Example usage
main('MO')  # Example ticker for Altria Group, a major tobacco company
