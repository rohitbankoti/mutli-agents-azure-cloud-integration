# Quant Analyst agent - fetch records from Yahoo finance. Compare two stocks (define FundamentalAnalysis)

# define input schema

# what input tools expect
# stock analysis input : define fundamental analysis tool - single text ticker (MSFT)
#compare stocks input : define CompareStocksTool : ticker_a and ticker_b

from typing import Type,Dict,Any,Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import yfinance as yf


# Input schemas (input will go to tools)

class StockAnalysisInput(BaseModel):
    '''
    
    Input schema for fundamental analysis tool
    Enforce ticker symbol is provided as string : Ellipsis
    
    '''
    ticker : str = Field(..., description="The stock ticker symbol (e.g. 'APPL', 'MSFT')")

class CompareStocksInput(BaseModel):

    ticker_a : str = Field(...,description="The first stock ticker to analyse")
    ticker_b : str = Field(...,description="The second stock ticker to analyse")    

# Tools definition

class FundamentalAnalysisTool(BaseTool):

    name : str = "Fetch fundamental metrics"
    description : str = ("Fetches key metrics for specific stock ticker and useful for quant analysis and return JSON \
                         data including - PE ratio, Market cap, 52 Week high etc")
    

    args_schema : type[BaseModel] = StockAnalysisInput

    def _run(self, ticker:str) -> str:
        
        '''
        Execute data fetching from yahoo finance
        Args : ticker(str) :
        returns : stringified JSON dictionary contains selected metrics or contain error if it fails

    '''
        try : 

            #initialize ticker object
            stock = yf.Ticker(ticker)
            info : Dict[str,Any] = stock.info

            #we explicitely select robust metrics to avoid context bloat
            metrics = {
                "Ticker" : ticker.upper(),
                "Current Price" : info.get("currentPrice", "N/A"),
                "Market Cap" : info.get("marketCap", "N/A"),
                "P/E Ratio (trailing)" : info.get("trailingPE","N/A"),
                "Forward P/E" : info.get("forwardPE","N/A"),
                "PEG Ratio" : info.get("pegRatio","N/A"),
                "BETA (Volatilty)" : info.get("beta","N/A"),
                "EPS (trailing)" : info.get("trailingEps","N/A"),
                "52 Week High" : info.get("fiftyTwoWeekHigh","N/A"),          
                "52 Week Low" : info.get("fiftyTwoWeekLow","N/A"),     
                "Analyst Recommendation" : info.get("recommendationKey","none"),                                           
            } 
            return str(metrics)
        
        except Exception as e:
            return f"Error fetching fundamental data for '{ticker} : {str(e)}'"
    

class CompareStocksTool(BaseTool):
    '''
    calculate relative performance between two assets - answer the questions "Did NVIDIA beat APPLE last year?
    '''

    name : str = "Compare Stock Performance"
    description : str = ("Compares the historical performance of two stocks over last 365 days, returns the percentage gain or loss for both assets")

    args_schema : Type[BaseModel] = CompareStocksInput

    def _run(self, ticker_a : str, ticker_b : str) -> str:
        '''
    Fetch historical data and calculates percentage return
    formula = (last price - first price)/(first price) *100
    '''
        try:
            tickers= f"{ticker_a}{ticker_b}"
            data = yf.download(tickers, period= "1y", progress=False)['Close']

        #helper function to calculate return 
            def calculate_return(symbol:str) -> float:
                start_price = data[symbol].iloc[0]  #iloc[0] : price of day 1 out of 365 days
                end_price = data[symbol].iloc[-1]
                return ((end_price-start_price)/start_price)*100
        
            perf_a = calculate_return(ticker_a)
            perf_b = calculate_return(ticker_b)

            return (
            "Performance Comparison (Last 1 Year)\n"
            f"{ticker_a}: {perf_a:.2f}%\n"
            f"{ticker_b}: {perf_b:.2f}%"
        )

        except Exception as e:
            return f"Error comparing stocks '{ticker_a}' and '{ticker_b}' : {str(e)}"