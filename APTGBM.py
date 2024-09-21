import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf


# Function to calculate the expected return using APT model
def calculate_apt_return(ticker):
    """
    Calculate the expected return of a stock using the APT model.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        float: The expected return of the stock.
    """
    # Step 1: Fetch data using yfinance
    stock = yf.Ticker(ticker)
    beta = stock.info.get("beta", None)

    print(f"\nFetching data for {ticker}...")
    print(f"Stock Beta: {beta}" if beta else "Stock Beta: Not Available")

    # Step 2: Prompt user for input
    if beta is None:
        beta_inflation = float(
            input("Enter the stock's sensitivity (beta) to inflation: ")
        )
        beta_gdp_growth = float(
            input("Enter the stock's sensitivity (beta) to GDP growth: ")
        )
    else:
        beta_inflation = beta
        beta_gdp_growth = beta

    # Step 3: Calculate expected return using APT model
    # Example calculation (replace with actual APT model logic)
    risk_free_rate = 0.02  # Example risk-free rate
    expected_inflation = 0.03  # Example expected inflation rate
    expected_gdp_growth = 0.04  # Example expected GDP growth rate

    expected_return = (
        risk_free_rate
        + beta_inflation * expected_inflation
        + beta_gdp_growth * expected_gdp_growth
    )

    return expected_return


# Function to fetch volatility from yfinance based on historical stock prices
def fetch_volatility(ticker):
    # Fetch historical data for the stock (1 year)
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    # Calculate daily returns
    hist["Returns"] = hist["Close"].pct_change()

    # Calculate annualized volatility (standard deviation of returns)
    volatility = hist["Returns"].std() * np.sqrt(252)  # Annualized volatility
    print(f"Annualized Volatility for {ticker}: {volatility:.2f}")

    return volatility


# Function to fetch the initial stock price from yfinance
def fetch_initial_stock_price(ticker):
    """
    Fetch the initial stock price for the given ticker using yfinance.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        float: The initial stock price.
    """
    stock = yf.Ticker(ticker)
    stock_price = stock.history(period="1d")["Close"].iloc[0]
    return stock_price


def simulate_gbm(expected_return, volatility, initial_stock_price):
    """
    Simulate Geometric Brownian Motion (GBM) for stock prices.

    Args:
        expected_return (float): The expected return of the stock.
        volatility (float): The volatility of the stock.
        initial_stock_price (float): The initial stock price.
    """
    # Step 1: Prompt user for GBM-related inputs
    S0 = initial_stock_price  # Use the fetched initial stock price
    try:
        T = float(input("Enter the time horizon in years (e.g., 1 for 1 year): "))
        dt = float(
            input("Enter the time step (e.g., 0.01 for daily steps in 1 year): ")
        )
        n_simulations = int(input("Enter the number of simulation paths: "))
    except ValueError:
        print("Invalid input. Please enter numerical values.")
        return

    N = int(T / dt)  # Number of time steps
    t = np.linspace(0, T, N)  # Array of time points from 0 to T

    # Step 2: Monte Carlo simulation of GBM
    plt.figure(figsize=(10, 6))
    for i in range(n_simulations):
        # Simulate the Wiener process (random component)
        W = np.random.standard_normal(size=N)
        W = np.cumsum(W) * np.sqrt(dt)  # Brownian motion

        # Calculate stock prices using the GBM formula
        S = S0 * np.exp((expected_return - 0.5 * volatility**2) * t + volatility * W)
        plt.plot(t, S)

    plt.title("Geometric Brownian Motion Simulation")
    plt.xlabel("Time (years)")
    plt.ylabel("Stock Price")
    plt.show()


# Main function to run the APT and GBM models
def main():
    # Step 1: Prompt user for stock ticker symbol
    ticker = input("Enter the stock ticker symbol (e.g., AAPL, MSFT): ").upper()

    # Step 2: Fetch initial stock price using yfinance
    initial_stock_price = fetch_initial_stock_price(ticker)
    print(f"Initial Stock Price for {ticker}: {initial_stock_price:.2f}")

    # Example values for expected return and volatility
    expected_return = 0.1  # Example expected return
    volatility = 0.28  # Example volatility

    # Step 3: Simulate GBM
    simulate_gbm(expected_return, volatility, initial_stock_price)


if __name__ == "__main__":
    main()
