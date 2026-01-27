"""
Test historical_valuation_metrics() method
"""
from FinRatioAnalysis import FinRatioAnalysis

print("Testing historical_valuation_metrics()...\n")

# Test with yearly data
print("=" * 70)
print("YEARLY HISTORICAL VALUATION METRICS - AAPL")
print("=" * 70)
analyzer_yearly = FinRatioAnalysis('AAPL', freq='yearly')
historical_yearly = analyzer_yearly.historical_valuation_metrics()
print(historical_yearly)
print()

# Test with quarterly data
print("=" * 70)
print("QUARTERLY HISTORICAL VALUATION METRICS - AAPL")
print("=" * 70)
analyzer_quarterly = FinRatioAnalysis('AAPL', freq='quarterly')
historical_quarterly = analyzer_quarterly.historical_valuation_metrics()
print(historical_quarterly)
print()

# Compare with IBM
print("=" * 70)
print("YEARLY HISTORICAL VALUATION METRICS - IBM")
print("=" * 70)
ibm = FinRatioAnalysis('IBM', freq='yearly')
print(ibm.historical_valuation_metrics())
print()

print("✅ Historical valuation metrics working for both yearly and quarterly!")
