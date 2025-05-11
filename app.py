import yfinance as yf
import streamlit as st

st.title("📊 Stock Research Agent (Beta)")

ticker_input = st.text_input("Enter Stock Ticker (e.g. HDFCBANK.NS)", "HDFCBANK.NS")

if st.button("Analyze"):
    stock = yf.Ticker(ticker_input)

    st.header("📌 Basic Info")
    st.write(stock.info.get('longName', 'N/A'))
    st.write(f"📈 Market Cap: ₹{stock.info.get('marketCap', 0) / 1e7:.2f} Cr")
    st.write(f"🏦 Sector: {stock.info.get('sector', 'N/A')}")

    st.header("📉 Key Ratios")
    st.write(f"💹 P/E Ratio: {stock.info.get('trailingPE', 'N/A')}")
    st.write(f"📘 ROE: {stock.info.get('returnOnEquity', 'N/A')}")
    st.write(f"💰 Debt to Equity: {stock.info.get('debtToEquity', 'N/A')}")

    st.header("📄 Profit & Loss")
    try:
        income_stmt = stock.financials.T
        st.dataframe(income_stmt)
    except:
        st.warning("P&L data not available.")

    st.header("📊 ROCE Calculation")
    try:
        balance_sheet = stock.balance_sheet
        income_statement = stock.financials

        ebit = income_statement.loc["EBIT"].iloc[0]
        total_assets = balance_sheet.loc["Total Assets"].iloc[0]
        current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]

        capital_employed = total_assets - current_liabilities
        roce = (ebit / capital_employed) * 100

        st.write(f"✅ ROCE: {roce:.2f}%")
    except Exception as e:
        st.warning("ROCE data not available or calculation failed.")
    # 🧠 Decision Engine
    st.header("📊 Buy / Hold / Sell Decision")

    score = 0

    try:
        roe = stock.info.get("returnOnEquity", 0) * 100
        pe = stock.info.get("trailingPE", 0)
        debt_eq = stock.info.get("debtToEquity", 0)

        if roce > 15:
            score += 1
        if roe > 15:
            score += 1
        if 10 < pe < 30:
            score += 1
        if debt_eq < 0.5:
            score += 1

        # Check earnings sentiment (optional, requires summary)
        if "positive" in call_text.lower():
            score += 1

        if score >= 4:
            verdict = "✅ BUY"
        elif 2 <= score < 4:
            verdict = "⚠️ HOLD"
        else:
            verdict = "❌ AVOID"

        st.write(f"Score: {score} / 5")
        st.success(f"**Final Verdict: {verdict}**")

    except:
        st.warning("❗ Could not calculate decision due to missing data.")

# ✅ GPT Earnings Call Summarizer (Independent of button)
st.header("📞 Earnings Call Summary (Paste Text Below)")

call_text = st.text_area("Paste the last earnings call transcript or bullet points here:")

if call_text and st.button("Summarize Call"):
    import os
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        prompt = f"""Summarize the following earnings call in bullet points. Highlight: 
        1) Key management commentary
        2) Business outlook
        3) Any risks or red flags:\n\n{call_text}"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )

        summary = response.choices[0].message.content
        st.subheader("📋 Call Summary")
        st.success("✅ Summary generated below:")
        st.markdown(summary)

    except Exception as e:
        st.error("❌ Failed to summarize. Check your API key or internet connection.")
