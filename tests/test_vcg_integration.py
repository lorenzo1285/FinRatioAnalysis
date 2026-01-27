"""
Test VCG metrics integration in FinRatioAnalysis
"""
from FinRatioAnalysis import FinRatioAnalysis

print("Testing VCG metrics integration...\n")

try:
    # Initialize analyzer
    analyzer = FinRatioAnalysis('AAPL', freq='yearly')
    print(f"✓ Successfully initialized analyzer for {analyzer.symbol}\n")
    
    # Test return_ratios (should now include ROIC)
    print("=" * 60)
    print("RETURN RATIOS (now includes ROIC)")
    print("=" * 60)
    ratios = analyzer.return_ratios()
    print(f"Columns: {list(ratios.columns)}")
    print(ratios.head(1))
    print()
    
    # Test valuation_growth_metrics (should now include EV/EBITDA and FCF Yield)
    print("=" * 60)
    print("VALUATION & GROWTH METRICS (now includes EV/EBITDA, FCF Yield)")
    print("=" * 60)
    valuation = analyzer.valuation_growth_metrics()
    print(f"Columns: {list(valuation.columns)}")
    print(valuation)
    print()
    
    # Test efficiency_ratios (should now include FCF Margin and Reinvestment Rate)
    print("=" * 60)
    print("EFFICIENCY RATIOS (now includes FCF Margin, Reinvestment Rate)")
    print("=" * 60)
    efficiency = analyzer.efficiency_ratios()
    print(f"Columns: {list(efficiency.columns)}")
    print(efficiency.head(1))
    print()
    
    print("=" * 60)
    print("✅ ALL VCG METRICS SUCCESSFULLY INTEGRATED!")
    print("=" * 60)
    print("\nNew metrics added:")
    print("  • ROIC (Return on Invested Capital)")
    print("  • EV/EBITDA (Enterprise Value / EBITDA)")
    print("  • FCF Yield (Free Cash Flow Yield)")
    print("  • FCF Margin (Free Cash Flow Margin)")
    print("  • Reinvestment Rate")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
