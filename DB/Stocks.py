import os
import re
import datetime


from ..Models import DatabaseManager as DB, yId, normal
from ..Utils import ResultsParse as RP
from itertools import chain
from sqlite3 import IntegrityError, OperationalError
# for debugging
from pprint import pprint

################################################################################
################################################################################


esgTypes = ("adult", "alcoholic", "animalTesting", "catholic", "coal", "controversialWeapons",
                "furLeather", "gambling", "gmo", "militaryContract", "nuclear", "palmOil",
                "pesticides", "smallArms", "tobacco"
)





################################################################################
################################################################################


class STOCKSDB(DB):

    _abrv = "stocks"

    _schema = ("""
                    CREATE TABLE info (
                        sym_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        exchange TEXT,
                        industry TEXT,
                        sector TEXT,
                        summary TEXT,
                        quote_type TEXT
                    )
                """,
                """
                    CREATE TABLE dates (
                        sym_id TEXT PRIMARY KEY,
                        earnings TEXT,
                        dividend TEXT,
                        ex_dividend TEXT,
                        FOREIGN KEY (sym_id) REFERENCES info (sym_id)
                    )
                """,
                """
                    CREATE TABLE earnings (
                        sym_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        revenue INT NOT NULL,
                        earnings INT NOT NULL,
                        PRIMARY KEY (sym_id, date),
                        FOREIGN KEY (sym_id) REFERENCES info (sym_id)
                    )
                """,
                """
                    CREATE TABLE estimates (
                        sym_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        estimate REAL NOT NULL,
                        eps REAL NOT NULL,
                        PRIMARY KEY (sym_id, date),
                        FOREIGN KEY (sym_id) REFERENCES info (sym_id)
                    )
                """,
                """
                    CREATE TABLE esg_types (
                        esg_id INT PRIMARY KEY,
                        title TEXT NOT NULL
                    )
                """,
                """
                    CREATE TABLE esgs (
                        sym_id TEXT NOT NULL,
                        esg_id TEXT NOT NULL,
                        PRIMARY KEY (sym_id, esg_id),
                        FOREIGN KEY (sym_id) REFERENCES info (sym_id),
                        FOREIGN KEY (esg_id) REFERENCES esg_types (esg_id)
                    )
                """,
                """
                    CREATE TABLE finances (
                        sym_id TEXT PRIMARY KEY,
                        book_value REAL,
                        dividend_date TEXT,
                        dividend REAL,
                        dividend_yield REAL,
                        ebitda INT,
                        eps REAL,
                        ex_div_date TEXT,
                        pe REAL,
                        so INT,


                        FOREIGN KEY (sym_id) REFERENCES info (sym_id)
                    )
                """,
                """
                    CREATE TABLE prices (
                        sym_id TEXT NOT NULL,
                        year INT NOT NULL,
                        date REAL NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume INT NOT NULL,
                        PRIMARY KEY (sym_id, year,date),
                        FOREIGN KEY (sym_id) REFERENCES info (sym_id)
                    )
                """,
                """
                    CREATE TABLE updates (
                        sym_id TEXT PRIMARY KEY,
                        date REAL NOT NULL,
                        FOREIGN KEY (sym_id) REFERENCES info (sym_id)
                    )
                """
                )


    def __init__(self):
        super().__init__("/home/ededub/FEFelson/stocks/stocks.db")


    def insertGame(self, gameData):
        pass


    def setInfo(self, info):
        sym = info["symbol"]
        try:
            name = info["quoteType"]["shortName"]
        except:
            name = sym
        try:
            exchange = info["price"]["exchangeName"]
        except:
            exchange = "N/A"
        try:
            industry = info["summaryProfile"]["industry"]
            sector = info["summaryProfile"]["sector"]
            summary = info["summaryProfile"]["longBusinessSummary"]
        except:
            industry = None
            sector = None
            summary = None
        quote_type = info["quoteType"]["quoteType"]
        self.insert("info", values=(sym, name, exchange, industry, sector, summary, quote_type))


    def setFinancials(self, info):
        sym = info["symbol"]
        book_value = info["defaultKeyStatistics"].get("bookValue", {}).get("raw", None)
        shares_out = info["defaultKeyStatistics"].get("sharesOutstanding",{}).get("raw", None)
        shares_float = info["defaultKeyStatistics"].get("floatShares", {}).get("raw", None)
        try:
            ebitda = info["financialData"]["ebitda"].get("raw", None)
            cash_flow = info["financialData"]["freeCashflow"].get("raw", None)
            gross_profits = info["financialData"]["grossProfits"].get("raw", None)
            gross_margins = info["financialData"]["grossMargins"].get("raw", None)
            total_debt = info["financialData"]["totalDebt"].get("raw", None)
            debt_equity = info["financialData"]["debtToEquity"].get("raw", None)
            dividend = info["summaryDetail"]["dividendRate"].get("raw", None)
            profit_margin = info["financialData"]["profitMargins"].get("raw", None)

            self.insert("finances", values=(sym, book_value, shares_out, shares_float, ebitda,
                                        cash_flow, gross_profits, gross_margins,
                                        total_debt, debt_equity, dividend, profit_margin))
        except KeyError:
            pass

    def setDates(self, info):
        sym = info["symbol"]
        try:
            earnings = info["calendarEvents"]["earnings"]["earningsDate"][0]["fmt"]
        except (IndexError, KeyError):
            earnings = None
        try:
            dividend = info["calendarEvents"]["dividendDate"].get("fmt", None)
            ex_dividend = info["calendarEvents"]["exDividendDate"].get("fmt", None)
            self.insert("dates", values=(sym, earnings, dividend, ex_dividend))
        except KeyError:
            pass


    def setEarnings(self, info):
        sym = info["symbol"]
        try:
            for item in chain(info["earnings"]["financialsChart"]["quarterly"], info["earnings"]["financialsChart"]["yearly"]):
                date = item["date"]
                revenue = item["revenue"]["raw"]
                earnings = item["earnings"]["raw"]
                self.insert("earnings", values=(sym, date, revenue, earnings))
        except (KeyError, IntegrityError):
            pass


    def setEstimates(self, info):
        sym = info["symbol"]
        try:
            for item in info["earnings"]["earningsChart"]["quarterly"]:
                date = item["date"]
                estimate = item["estimate"]["raw"]
                eps = item["actual"]["raw"]
                self.insert("estimates", values=(sym, date, estimate, eps))
        except KeyError:
            pass


    def setEsg(self, info):
        sym = info["symbol"]
        for i, esg in enumerate(esgTypes):
            if info["esgScores"].get(esg, False) == True:
                self.insert("esgs", values=(sym, i+1))


    def seed(self):
        for i, esg in enumerate(esgTypes):
            self.insert("esg_types", values=(i+1,esg))

        self.commit()
