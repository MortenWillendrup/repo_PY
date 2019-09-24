import QuantLib as ql
import math

todaysDate = ql.Date(30, ql.September, 2018)
ql.Settings.instance().evaluationDate = todaysDate
settlementDate = todaysDate
riskFreeRate = ql.FlatForward(settlementDate, 0.0, ql.Actual365Fixed())
dividendYield = ql.FlatForward(settlementDate, 0.0, ql.Actual365Fixed())
underlying = ql.SimpleQuote(30.0)
volatility = ql.BlackConstantVol(todaysDate, ql.TARGET(), 0.20, ql.Actual365Fixed())


exerciseDates = [ql.Date(1, ql.January, 2019) + i for i in range(31)]

swingOption = ql.VanillaSwingOption(
    ql.VanillaForwardPayoff(ql.Option.Call, underlying.value()), ql.SwingExercise(exerciseDates), 0, len(exerciseDates)
)

bsProcess = ql.BlackScholesMertonProcess(
    ql.QuoteHandle(underlying),
    ql.YieldTermStructureHandle(dividendYield),
    ql.YieldTermStructureHandle(riskFreeRate),
    ql.BlackVolTermStructureHandle(volatility),
)

swingOption.setPricingEngine(ql.FdSimpleBSSwingEngine(bsProcess))

print("Black Scholes Price: %f" % swingOption.NPV())

x0 = 0.0
x1 = 0.0

beta = 4.0
eta = 4.0
jumpIntensity = 1.0
speed = 1.0
volatility = 0.1

curveShape = []
for d in exerciseDates:
    t = ql.Actual365Fixed().yearFraction(todaysDate, d)
    gs = (
        math.log(underlying.value())
        - volatility * volatility / (4 * speed) * (1 - math.exp(-2 * speed * t))
        - jumpIntensity / beta * math.log((eta - math.exp(-beta * t)) / (eta - 1.0))
    )
    curveShape.append((t, gs))

ouProcess = ql.ExtendedOrnsteinUhlenbeckProcess(speed, volatility, x0, lambda x: x0)
jProcess = ql.ExtOUWithJumpsProcess(ouProcess, x1, beta, jumpIntensity, eta)

swingOption.setPricingEngine(ql.FdSimpleExtOUJumpSwingEngine(jProcess, riskFreeRate, 25, 25, 200, curveShape))

print("Kluge Model Price  : %f" % swingOption.NPV())
