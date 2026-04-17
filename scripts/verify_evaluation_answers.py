"""Verify reference answers for evaluation.xml

Systematically calls each MCP tool to determine correct answers for the 10 evaluation questions.
Results will be recorded as comments in evaluation.xml.

Run with: uv run python scripts/verify_evaluation_answers.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import MCP tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from finratioanalysis_mcp.tools.return_ratios import finratio_return_ratios
from finratioanalysis_mcp.tools.efficiency_ratios import finratio_efficiency_ratios
from finratioanalysis_mcp.tools.leverage_ratios import finratio_leverage_ratios
from finratioanalysis_mcp.tools.liquidity_ratios import finratio_liquidity_ratios
from finratioanalysis_mcp.tools.ccc import finratio_ccc
from finratioanalysis_mcp.tools.z_score import finratio_z_score
from finratioanalysis_mcp.tools.capm import finratio_capm
from finratioanalysis_mcp.tools.wacc import finratio_wacc
from finratioanalysis_mcp.tools.valuation_growth_metrics import finratio_valuation_growth_metrics
from finratioanalysis_mcp.tools.historical_valuation_metrics import finratio_historical_valuation_metrics


def verify_q1():
    """Q1: DuPont analysis - Which of AAPL/MSFT/GOOGL had highest 2022 ROE? What was their Asset Turnover?"""
    print("\n" + "="*80)
    print("Q1: DuPont ROE decomposition (AAPL/MSFT/GOOGL 2022)")
    print("="*80)
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    roe_data = {}
    
    for ticker in tickers:
        result = finratio_return_ratios(ticker=ticker, freq="yearly")
        # Find 2022 data
        for row in result["data"]:
            if "2022" in row["date"]:
                roe_data[ticker] = {
                    "ROE": row.get("ROE"),
                    "date": row["date"]
                }
                print(f"  {ticker} (2022): ROE = {row.get('ROE')}")
                break
    
    # Find highest ROE
    winner = max(roe_data.items(), key=lambda x: x[1]["ROE"] if x[1]["ROE"] is not None else float('-inf'))
    winner_ticker = winner[0]
    print(f"\n  ✓ Highest ROE: {winner_ticker} with {winner[1]['ROE']}")
    
    # Get Asset Turnover for winner
    eff_result = finratio_efficiency_ratios(ticker=winner_ticker, freq="yearly")
    for row in eff_result["data"]:
        if "2022" in row["date"]:
            asset_turnover = row.get("AssetTurnover")
            print(f"  ✓ {winner_ticker} Asset Turnover (2022): {asset_turnover}")
            if asset_turnover is not None:
                answer = f"{asset_turnover:.2f}"
                print(f"\n  ANSWER: {answer}")
                return answer
            break
    
    return "DATA_UNAVAILABLE"


def verify_q2():
    """Q2: Lowest Debt-to-Equity among AAPL/AMZN/MSFT in 2022?"""  
    print("\n" + "="*80)
    print("Q2: Tech company Debt-to-Equity comparison (AAPL/AMZN/MSFT 2022)")
    print("="*80)
    
    tickers = ["AAPL", "AMZN", "MSFT"]
    de_data = {}
    
    for ticker in tickers:
        result = finratio_leverage_ratios(ticker=ticker, freq="yearly")
        for row in result["data"]:
            if "2022" in row["date"]:
                de_ratio = row.get("DebtEquityRatio")
                de_data[ticker] = de_ratio
                print(f"  {ticker} (2022): Debt-to-Equity = {de_ratio}")
                break
    
    if de_data:
        winner = min(de_data.items(), key=lambda x: x[1] if x[1] is not None else float('inf'))
        print(f"\n  ANSWER: {winner[0]} (Debt-to-Equity = {winner[1]})")
        return winner[0]
    return "DATA_UNAVAILABLE"


def verify_q3():
    """Q3: Highest ROIC among KO/PEP/KDP in 2022?"""
    print("\n" + "="*80)
    print("Q3: Beverage company ROIC comparison (KO/PEP/KDP 2022)")
    print("="*80)
    
    tickers = ["KO", "PEP", "KDP"]
    roic_data = {}
    
    for ticker in tickers:
        result = finratio_return_ratios(ticker=ticker, freq="yearly")
        for row in result["data"]:
            if "2022" in row["date"]:
                roic = row.get("ROIC")
                roic_data[ticker] = roic
                print(f"  {ticker} (2022): ROIC = {roic}")
                break
    
    if roic_data:
        winner = max(roic_data.items(), key=lambda x: x[1] if x[1] is not None else float('-inf'))
        print(f"\n  ANSWER: {winner[0]} (ROIC = {winner[1]})")
        return winner[0]
    
    return "DATA_UNAVAILABLE"


def verify_q4():
    """Q4: NVDA Beta from valuation_growth_metrics > 1.5?"""
    print("\n" + "="*80)
    print("Q4: NVIDIA Beta from valuation_growth_metrics (> 1.5?)")
    print("="*80)
    
    result = finratio_valuation_growth_metrics(ticker="NVDA")
    beta = result["data"]["beta"]  # lowercase 'beta' in valuation_growth_metrics
    print(f"  NVDA Beta: {beta}")
    
    answer = "TRUE" if beta and beta > 1.5 else "FALSE"
    print(f"\n  ANSWER: {answer}")
    return answer


def verify_q5():
    """Q5: JNJ - Is ROIC > WACC (positive EVA)?"""
    print("\n" + "="*80)
    print("Q5: Johnson & Johnson EVA spread (ROIC > WACC?)")
    print("="*80)
    
    wacc_result = finratio_wacc(ticker="JNJ")
    wacc = wacc_result["data"]["WACC"]
    print(f"  JNJ WACC: {wacc}")
    
    roic_result = finratio_return_ratios(ticker="JNJ", freq="yearly")
    roic_2022 = None
    for row in roic_result["data"]:
        if "2022" in row["date"]:
            roic_2022 = row.get("ROIC")
            print(f"  JNJ ROIC (2022): {roic_2022}")
            break
    
    if wacc and roic_2022:
        answer = "YES" if roic_2022 > wacc else "NO"
        print(f"  Spread: {roic_2022 - wacc:.2f}%")
        print(f"\n  ANSWER: {answer}")
        return answer
    
    return "DATA_UNAVAILABLE"


def verify_q6():
    """Q6: GE Z-Score in Safe Zone?"""
    print("\n" + "="*80)
    print("Q6: General Electric Z-Score Zone")
    print("="*80)
    
    result = finratio_z_score(ticker="GE")
    zone = result["data"]["Zone"]
    z_score = result["data"]["Z Score"]
    print(f"  GE Z-Score: {z_score}")
    print(f"  Zone: {zone}")
    
    answer = "TRUE" if "Safe" in zone else "FALSE"
    print(f"\n  ANSWER: {answer}")
    return answer


def verify_q7():
    """Q7: NFLX 3Y Revenue CAGR positive?"""
    print("\n" + "="*80)
    print("Q7: Netflix 3-year Revenue CAGR")
    print("="*80)
    
    result = finratio_valuation_growth_metrics(ticker="NFLX")
    revenue_cagr_3y = result["data"]["revenue_cagr_3y"]  # lowercase field name
    print(f"  NFLX revenue_cagr_3y: {revenue_cagr_3y}")
    
    answer = "TRUE" if revenue_cagr_3y and revenue_cagr_3y > 0 else "FALSE"
    print(f"\n  ANSWER: {answer}")
    return answer


def verify_q8():
    """Q8: Apple CCC < 0 in 2022?"""  
    print("\n" + "="*80)
    print("Q8: Apple Cash Conversion Cycle (2022)")
    print("="*80)
    
    result = finratio_ccc(ticker="AAPL", freq="yearly")
    for row in result["data"]:
        if "2022" in row["date"]:
            ccc = row.get("CCC")
            print(f"  AAPL CCC (2022): {ccc}")
            
            answer = "TRUE" if ccc and ccc < 0 else "FALSE"
            print(f"\n  ANSWER: {answer}")
            return answer
    return "DATA_UNAVAILABLE"


def verify_q9():
    """Q9: CVS Quick Ratio < 1.0 in 2022?"""  
    print("\n" + "="*80)
    print("Q9: CVS Health Quick Ratio (2022)")
    print("="*80)
    
    result = finratio_liquidity_ratios(ticker="CVS", freq="yearly")
    for row in result["data"]:
        if "2022" in row["date"]:
            quick_ratio = row.get("QuickRatio")
            print(f"  CVS Quick Ratio (2022): {quick_ratio}")
            answer = "TRUE" if quick_ratio and quick_ratio < 1.0 else "FALSE"
            print(f"\n  ANSWER: {answer}")
            return answer
    
    return "DATA_UNAVAILABLE"


def verify_q10():
    """Q10: META P/E < 15 on Dec 31, 2022?"""
    print("\n" + "="*80)
    print("Q10: Meta P/E ratio (Dec 31, 2022)")
    print("="*80)
    
    result = finratio_historical_valuation_metrics(ticker="META", freq="yearly")
    for row in result["data"]:
        if "2022" in row["date"]:
            pe_ratio = row.get("PE_Ratio")
            print(f"  META P/E (2022): {pe_ratio}")
            
            answer = "TRUE" if pe_ratio and pe_ratio < 15 else "FALSE"
            print(f"\n  ANSWER: {answer}")
            return answer
    
    return "DATA_UNAVAILABLE"


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FINRATIOANALYSIS MCP EVALUATION - ANSWER VERIFICATION")
    print("="*80)
    print("\nVerifying reference answers for all 10 evaluation questions...")
    print("This will call live Yahoo Finance data through the MCP tools.\n")
    
    answers = {
        "Q1": verify_q1(),
        "Q2": verify_q2(),
        "Q3": verify_q3(),
        "Q4": verify_q4(),
        "Q5": verify_q5(),
        "Q6": verify_q6(),
        "Q7": verify_q7(),
        "Q8": verify_q8(),
        "Q9": verify_q9(),
        "Q10": verify_q10(),
    }
    
    print("\n" + "="*80)
    print("SUMMARY OF VERIFIED ANSWERS")
    print("="*80)
    for q_id, answer in answers.items():
        print(f"  {q_id}: {answer}")
    
    print("\n✓ Verification complete!")
    print("Update evaluation.xml with these answers, replacing PLACEHOLDER values.")
