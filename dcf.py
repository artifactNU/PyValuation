import argparse
import yfinance as yf
import matplotlib.pyplot as plt


def project_cash_flows(last_cash_flow, growth_rate, years=5):
    """Project future cash flows based on the last available cash flow and a constant growth rate."""
    if not isinstance(last_cash_flow, (int, float)) or last_cash_flow <= 0:
        raise ValueError("Last cash flow must be a positive number.")
    if not isinstance(growth_rate, (int, float)) or not -1 < growth_rate < 1:
        raise ValueError(
            "Growth rate must be a decimal between -1 and 1 to be realistic."
        )
    if not isinstance(years, int) or years <= 0:
        raise ValueError("Years must be a positive integer.")

    return [
        last_cash_flow * ((1 + growth_rate) ** year) for year in range(1, years + 1)
    ]


def calculate_terminal_value(last_projected_cf, perpetuity_growth_rate, discount_rate):
    """Calculate the Terminal Value using the Perpetuity Growth Model."""
    if not isinstance(last_projected_cf, (int, float)) or last_projected_cf <= 0:
        raise ValueError("Last projected cash flow must be a positive number.")
    if (
        not isinstance(perpetuity_growth_rate, (int, float))
        or not 0 <= perpetuity_growth_rate < 1
    ):
        raise ValueError("Perpetuity growth rate must be between 0 and 1 (exclusive).")
    if (
        not isinstance(discount_rate, (int, float))
        or discount_rate <= perpetuity_growth_rate
    ):
        raise ValueError(
            "Discount rate must be greater than perpetuity growth rate to be realistic and avoid division by zero."
        )

    return (
        last_projected_cf
        * (1 + perpetuity_growth_rate)
        / (discount_rate - perpetuity_growth_rate)
    )


def calculate_dcf_with_tv(projected_cash_flows, discount_rate, perpetuity_growth_rate):
    """Calculate the DCF valuation including Terminal Value."""
    present_values = [
        cf / ((1 + discount_rate) ** (i + 1))
        for i, cf in enumerate(projected_cash_flows)
    ]
    terminal_value = calculate_terminal_value(
        projected_cash_flows[-1], perpetuity_growth_rate, discount_rate
    )
    terminal_value_pv = terminal_value / (
        (1 + discount_rate) ** len(projected_cash_flows)
    )
    total_dcf_valuation = sum(present_values) + terminal_value_pv
    return total_dcf_valuation, present_values, terminal_value, terminal_value_pv


def calculate_growth_rate(cash_flows, expected_growth_rate):
    """Calculate the blended annual growth rate based on historical cash flows and an expected future growth rate."""
    if not cash_flows or len(cash_flows) < 2:
        raise ValueError(
            "At least two cash flow records are required to calculate historical growth rate."
        )

    growth_rates = [
        (cash_flows[i] - cash_flows[i + 1]) / cash_flows[i + 1]
        for i in range(len(cash_flows) - 1)
    ]
    historical_growth_rate = sum(growth_rates) / len(growth_rates)
    blended_growth_rate = (historical_growth_rate + expected_growth_rate) / 2

    return blended_growth_rate


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Perform DCF analysis on a given stock ticker."
    )
    parser.add_argument(
        "-t",
        "--ticker",
        type=str,
        help="Ticker symbol for the stock (e.g., AAPL), optional if using interactive mode.",
    )
    parser.add_argument(
        "-d",
        "--discount_rate",
        type=float,
        default=0.1,
        help="Discount rate as a decimal (e.g., 0.1 for 10%%).",
    )
    parser.add_argument(
        "-g",
        "--perpetuity_growth_rate",
        type=float,
        default=0.02,
        help="Perpetuity growth rate as a decimal (e.g., 0.02 for 2%%).",
    )
    parser.add_argument(
        "-e",
        "--expected_growth_rate",
        type=float,
        help="Expected future growth rate as a decimal (e.g., 0.05 for 5%%).",
        required=False,
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode. Overrides other arguments.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.ticker is None and not args.interactive:
        args.ticker = input("Enter a ticker symbol (e.g., AAPL): ")

    if args.interactive:
        ticker_symbol = input("Enter a ticker symbol (e.g., AAPL): ")
        discount_rate = float(input("Enter your discount rate (e.g., 0.1 for 10%): "))
        perpetuity_growth_rate = float(
            input("Enter the perpetuity growth rate (e.g., 0.02 for 2%): ")
        )
        expected_growth_rate_input = input(
            "Enter the expected future growth rate (e.g., 0.05 for 5%), or press Enter to skip: "
        )
        expected_growth_rate = (
            float(expected_growth_rate_input) if expected_growth_rate_input else 0.04
        )
    else:
        ticker_symbol = args.ticker
        discount_rate = args.discount_rate
        perpetuity_growth_rate = args.perpetuity_growth_rate
        expected_growth_rate = (
            args.expected_growth_rate if args.expected_growth_rate is not None else 0.04
        )

    try:
        ticker_data = yf.Ticker(ticker_symbol)
        if (
            not ticker_data.info
            or "quoteType" not in ticker_data.info
            or "Free Cash Flow" not in ticker_data.cashflow.index
        ):
            raise ValueError(f"No valid data found for ticker symbol {ticker_symbol}.")

        cash_flows = ticker_data.cashflow.loc["Free Cash Flow"].dropna().values[:4]
        if len(cash_flows) < 2:
            raise ValueError(
                f"Not enough cash flow data for {ticker_symbol} to perform analysis."
            )

        growth_rate = calculate_growth_rate(list(cash_flows), expected_growth_rate)
        latest_cash_flow = cash_flows[0]
        projected_cash_flows = project_cash_flows(latest_cash_flow, growth_rate)

        dcf_valuation, present_values, terminal_value, terminal_value_pv = (
            calculate_dcf_with_tv(
                projected_cash_flows, discount_rate, perpetuity_growth_rate
            )
        )
        market_cap = ticker_data.info.get("marketCap", "N/A")

        print(f"Projected cash flows: {projected_cash_flows}")
        print(f"Present Values of Projected Cash Flows: {present_values}")
        print(f"Terminal Value (before discounting): ${terminal_value:,.2f}")
        print(f"Terminal Value (Present Value): ${terminal_value_pv:,.2f}")
        print(f"Total DCF valuation: ${dcf_valuation:,.2f}")
        print(f"Current Market Cap: ${market_cap:,.2f}")

        if dcf_valuation > market_cap:
            print("Based on DCF, the stock appears to be undervalued.")
        else:
            print("Based on DCF, the stock appears to be overvalued.")

        years = list(range(1, len(projected_cash_flows) + 1))
        terminal_year = len(projected_cash_flows) + 1

        plt.figure(figsize=(10, 7))
        # Projected Cash Flows
        plt.plot(years, projected_cash_flows, "-o", label="Projected Cash Flows")

        # Highlighting Terminal Value
        plt.plot([terminal_year], [terminal_value_pv], "ro", label="Terminal Value")
        plt.annotate(
            f"Terminal Value\n${terminal_value_pv:,.2f}",
            (terminal_year, terminal_value_pv),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )

        # Highlighting Current Market Cap
        plt.plot([terminal_year], [market_cap], "go", label="Current Market Cap")
        plt.annotate(
            f"Current Market Cap\n${market_cap:,.2f}",
            (terminal_year, market_cap),
            textcoords="offset points",
            xytext=(0, -25),
            ha="center",
        )

        # Highlighting Total DCF Valuation
        plt.plot([terminal_year], [dcf_valuation], "bo", label="Total DCF Valuation")
        plt.annotate(
            f"Total DCF Valuation\n${dcf_valuation:,.2f}",
            (terminal_year, dcf_valuation),
            textcoords="offset points",
            xytext=(-40, 10),
            ha="center",
        )

        plt.title(f"DCF Analysis of {ticker_symbol.upper()}")
        plt.xlabel("Year")
        plt.ylabel("Amount ($)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except ValueError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
