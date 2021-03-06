# An exotic option who's value is dependant on a basket of various underlying assets, these are bought or sold as a basket if the option is excersied

import QuantLib as ql

# global data
todaysDate = ql.Date(15, ql.May, 1998)
ql.Settings.instance().evaluationDate = todaysDate
settlementDate = ql.Date(17, ql.May, 1998)
riskFreeRate = ql.FlatForward(settlementDate, 0.05, ql.Actual365Fixed())

# option parameters
exercise = ql.EuropeanExercise(ql.Date(17, ql.May, 1999))
payoff = ql.PlainVanillaPayoff(ql.Option.Call, 8.0)

# market data
underlying1 = ql.SimpleQuote(7.0)
volatility1 = ql.BlackConstantVol(todaysDate, ql.TARGET(), 0.10, ql.Actual365Fixed())
dividendYield1 = ql.FlatForward(settlementDate, 0.05, ql.Actual365Fixed())
underlying2 = ql.SimpleQuote(7.0)
volatility2 = ql.BlackConstantVol(todaysDate, ql.TARGET(), 0.10, ql.Actual365Fixed())
dividendYield2 = ql.FlatForward(settlementDate, 0.05, ql.Actual365Fixed())


process1 = ql.BlackScholesMertonProcess(
    ql.QuoteHandle(underlying1),
    ql.YieldTermStructureHandle(dividendYield1),
    ql.YieldTermStructureHandle(riskFreeRate),
    ql.BlackVolTermStructureHandle(volatility1),
)

process2 = ql.BlackScholesMertonProcess(
    ql.QuoteHandle(underlying2),
    ql.YieldTermStructureHandle(dividendYield2),
    ql.YieldTermStructureHandle(riskFreeRate),
    ql.BlackVolTermStructureHandle(volatility2),
)

matrix = ql.Matrix(2, 2)
matrix[0][0] = 1.0
matrix[1][1] = 1.0
matrix[0][1] = 0.5
matrix[1][0] = 0.5

process = ql.StochasticProcessArray([process1, process2], matrix)
basketoption = ql.BasketOption(ql.MaxBasketPayoff(payoff), exercise)
basketoption.setPricingEngine(
    ql.MCEuropeanBasketEngine(process, "pseudorandom", timeStepsPerYear=1, requiredTolerance=0.02, seed=42)
)
print(basketoption.NPV())

basketoption = ql.BasketOption(ql.MinBasketPayoff(payoff), exercise)
basketoption.setPricingEngine(
    ql.MCEuropeanBasketEngine(process, "pseudorandom", timeStepsPerYear=1, requiredTolerance=0.02, seed=42)
)
print(basketoption.NPV())

basketoption = ql.BasketOption(ql.AverageBasketPayoff(payoff, 2), exercise)
basketoption.setPricingEngine(
    ql.MCEuropeanBasketEngine(process, "pseudorandom", timeStepsPerYear=1, requiredTolerance=0.02, seed=42)
)
print(basketoption.NPV())

americanExercise = ql.AmericanExercise(settlementDate, ql.Date(17, ql.May, 1999))
americanbasketoption = ql.BasketOption(ql.MaxBasketPayoff(payoff), americanExercise)
americanbasketoption.setPricingEngine(
    ql.MCAmericanBasketEngine(
        process,
        "pseudorandom",
        timeSteps=10,
        requiredTolerance=0.02,
        seed=42,
        polynomOrder=5,
        polynomType=ql.LsmBasisSystem.Hermite,
    )
)
print(americanbasketoption.NPV())
