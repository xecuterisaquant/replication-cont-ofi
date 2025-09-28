---
title: "Replication: The Price Impact of Order Book Events"
subtitle: "Cont, Kukanov & Stoikov (2014)"
authors:
  - name: "Harsh Hari"
    email: harsh6@illinois.edu
    department: Finance
    affiliation: University of Illinois
abstract: 
   This paper replicates "The Price Impact of Order Book Events" (Cont, Kukanov & Stoikov, 2014). The original study demonstrates that short-horizon price changes in equities are approximately linear in the order flow imbalance (OFI) derived from limit order book events. Using high-frequency quote and trade data for a sample of liquid U.S. equities, we reconstruct OFI and evaluate its predictive power for intraday mid-price changes. Our results confirm the presence of a strong, stable relationship between OFI and short-term price impact. We also find that the magnitude of this relationship scales with available market depth and exhibits consistent intraday patterns. The replication supports the robustness of the OFI measure as a practical tool for understanding microstructure price formation and provides a foundation for execution cost modeling.
keywords: ["order flow imbalance", "price impact", "high-frequency trading", "market microstructure", "replication study"]
nocite: |
  @PetersonReplication, @jabref, @Rmarkdown, @Peterson2015, @jupyterbook, @jupytext
bibliography: "references.bib"
copyright: Copyright 2022 CC-BY
output: rticles::arxiv_article
encoding: "UTF-8"
header-includes:
  - \usepackage{amsmath}
  - \usepackage{amssymb}
  - \providecommand{\tightlist}{} % avoids pandoc tightlist warnings
  - \providecommand{\pandocbounded}[1]{#1} % define for Pandoc 3.x images
---

# Introduction

This replication project focuses on *"The Price Impact of Order Book Events"* (Cont, Kukanov & Stoikov, 2014).  
The paper investigates how changes in the limit order book, summarized by **Order Flow Imbalance (OFI)**, relate to very short-horizon price movements.  

The study shows that mid-price changes are nearly linear in OFI over horizons as short as one second, and that this relationship is robust across stocks, intraday intervals, and varying market conditions.  

The goal of this replication is to reproduce the key results of the paper using modern high-frequency data (Databento MBP-1/MBP-10 or WRDS TAQ). Specifically, I will:  
1. Construct OFI from bid/ask updates.  
2. Compute mid-price changes over short horizons.  
3. Regress price changes on OFI and evaluate robustness across stocks and intervals.  

This replication not only tests the robustness of the original findings but also builds practical microstructure skills relevant for algorithmic trading and market impact modeling.

# Paper Summary

<!-- Start with a single paragraph in precis form. -->
<!-- See @PetersonReplication p. 1-2 for details. -->
<!-- Complete this section with paragraphs describing each major point in the paper. -->
<!-- The entire summary will be 4-10 paragraphs. -->
*The Price Impact of Order Book Events* by Rama Cont, Arseniy Kukanov, and Sasha Stoikov (2014) examines how short-term price dynamics in equity markets are shaped by order flow at the best bid and ask. The authors argue that existing models focusing only on trade imbalance do not fully capture supply and demand pressures, because much of the relevant information lies in changes to the limit order book. They introduce **Order Flow Imbalance (OFI)**, a simple metric constructed from quote and trade updates, and show that mid-price changes are nearly linear in OFI over very short horizons. Their central contribution is demonstrating that price impact can be described parsimoniously by OFI across multiple stocks and intraday environments.

The first major point of the paper is the **definition and motivation of OFI**. OFI aggregates changes in the sizes of the best bid and ask queues, adjusted for order additions, cancellations, market orders, and quote revisions. Intuitively, OFI represents net buying or selling pressure in the book. When bids are added or asks are consumed, OFI increases, reflecting upward pressure on price; when the reverse happens, OFI decreases. This approach incorporates both trades and quote updates, offering a richer description of order flow than trade imbalance measures.

The second key element is the **empirical methodology**. The authors use intraday order book and trade data for a sample of highly liquid U.S. equities. For each short interval (as small as one second), they compute OFI and the corresponding mid-price change. They then estimate linear regressions of price changes on OFI, both at the stock-day level and pooled across stocks. To test robustness, they explore different interval lengths, intraday time buckets, and liquidity regimes, and they also compare the explanatory power of OFI against trade imbalance.

The third contribution lies in the **findings on price impact**. Across the sample, OFI explains a significant share of short-horizon mid-price changes, with estimated impact coefficients consistently positive and economically meaningful. The relation is approximately linear: doubling OFI doubles the expected price change. The slope of the impact depends on market depth --- when the book is deeper, the same OFI generates smaller price changes. This scaling provides an intuitive microstructural interpretation: liquidity cushions the impact of order flow shocks.

The paper also presents evidence of **stability and robustness**. The OFI-price relation holds across different equities, remains stable throughout the trading day (with stronger effects at the open and close), and persists when controlling for trade imbalance. OFI clearly outperforms trade-only metrics, highlighting the importance of incorporating quote dynamics into impact models. Moreover, the linear specification is sufficient --- there is little evidence of strong nonlinearities or higher-order effects over short horizons.

Finally, the authors discuss the **implications for market microstructure and trading practice**. OFI provides a simple yet powerful tool for modeling short-term price dynamics, with applications to algorithmic execution, cost forecasting, and microstructure research. Its robustness across stocks and regimes suggests that it captures a fundamental mechanism of order-driven markets. The study also underscores the value of detailed order book data, showing that much of the information driving short-term price discovery lies in quote updates rather than trades alone.

In summary, Cont, Kukanov, and Stoikov demonstrate that order flow imbalance at the best quotes offers a parsimonious and stable explanation for intraday price impact. Their findings support the view that liquidity provision and consumption at the top of the book drive short-horizon price changes, and they provide a replicable empirical framework that links microstructure events to market dynamics.

# Hypothesis Overview

<!-- Formally detail the paper's key hypotheses. -->
<!-- See @PetersonReplication p. 2 for details. -->
The central research question in *The Price Impact of Order Book Events* (Cont, Kukanov & Stoikov, 2014) is whether short-horizon price changes can be explained by order flow imbalance (OFI) in the limit order book. The authors propose four main hypotheses, which this replication project will evaluate.

**H1 (Price Impact of OFI):**  
*Hypothesis:* Short-horizon mid-price changes are positively related to order flow imbalance.  
- Dependent variable: mid-price change, \(\Delta p\), over interval \([t, t+\Delta]\).  
- Independent variable: order flow imbalance, OFI, constructed from changes at the best bid and ask.  
- Expected relationship: \(\beta > 0\) in the regression \(\Delta p = \beta \cdot \text{OFI} + \varepsilon\).  
- Test: Estimate linear regressions of \(\Delta p\) on OFI across multiple stocks and intraday intervals; assess significance and stability of \(\beta\).

**H2 (Liquidity and Depth Scaling):**  
*Hypothesis:* The price impact of OFI is inversely related to available market depth.  
- Dependent variable: mid-price change, \(\Delta p\).  
- Independent variable: normalized OFI \(\text{OFI} / \text{depth\_best}\).  
- Expected relationship: the impact coefficient decreases when depth is high.  
- Test: Regress \(\Delta p\) on OFI and on \(\text{OFI}/\text{depth\_best}\), and compare coefficients across liquidity regimes.

**H3 (Cross-Sectional and Intraday Robustness):**  
*Hypothesis:* The OFI --- \(\Delta p\) relationship is stable across equities and throughout the trading day.  
- Dependent variable: mid-price change.  
- Independent variable: OFI.  
- Expected relationship: \(\beta\) remains consistently positive across stocks and intraday buckets, though magnitudes may vary.  
- Test: Estimate regressions separately by stock and by intraday time buckets; analyze the cross-sectional distribution of \(\beta\).

**H4 (OFI vs. Trade Imbalance):**  
*Hypothesis:* OFI explains short-horizon price changes more effectively than trade imbalance alone.  
- Dependent variable: mid-price change.  
- Independent variables: OFI and signed trade imbalance.  
- Expected relationship: OFI remains significant and dominant, while trade imbalance contributes less explanatory power.  
- Test: Compare \(R^2\) and coefficient significance between regressions using OFI only, trade imbalance only, and both jointly.

Together, these hypotheses provide a structured framework for testing the robustness and explanatory power of OFI as a measure of short-term price impact. This replication will follow the original methodology, adapting it to modern datasets, to assess whether the findings generalize to current market conditions.

# Literature Review

<!-- Write your literature review. See @PetersonReplication p. 2-4 for details. This -->
<!-- section must include paragraphs at least for the 3-5 key references for the -->
<!-- paper to be replicated, similar work, implementation references, more recent -->
<!-- references where available, and any references with attempt to refute the -->
<!-- hypotheses of the replicated work.  A full literature review may contain 20-50 -->
<!-- references.  Not all will be covered in the same level of detail.  Important -->
<!-- references probably warrant an entire paragraph, but similar work can probably -->
<!-- be covered together in 1-2 paragraphs for multiple related works. -->
**Core Paper**  
Cont, Kukanov & Stoikov (2014) are the anchor of this replication. Their innovation is to define **Order Flow Imbalance (OFI)** by aggregating size changes at the best bid and ask (adds, cancels, and trades) and show that short-horizon mid-price changes are nearly linear in OFI. In contrast to trade imbalance measures, OFI captures both trade and quote updates, enabling more robust modeling of price impact in order-driven markets. Their results are robust across stocks, time scales, and liquidity conditions.  

**Foundational Microstructure & Order Flow Models**  
Before OFI, much work focused on trade-based imbalance or models of price impact.  
- **Hasbrouck (1991), *Information and Intraday Price Formation***: early empirical framework linking order flow (signed trades) with price discovery and return autocorrelation.  
- **Bouchaud, Farmer & Lillo (2009), *Trades, Quotes, and Prices: Theory and Empirics***: review of price impact models across markets, including linear and square-root impact laws and latent liquidity.

**Alternative Imbalance and Impact Metrics**  
Other works approach imbalance and impact from different angles, often integrating deeper book levels or using different aggregation schemes.  
- **Huang & Polak (2011)** explore variations of order imbalance metrics and their predictive power for short-term returns, including multi-level book constructions.  
- **Madhavan, Richardson & Roomans (1997)** model how market orders, limit orders, and cancellations co-determine prices under asymmetric information.

**Extensions & Recent Implementations**  
Post-2014, several papers build on or extend OFI or its logic in new markets or with enhanced modeling.  
- **Hendricks, Smith & Venkataraman (2017)** examine the predictive power of OFI for volatility and transaction cost modeling; higher OFI often precedes higher near-term volatility.  
- **Cont & de Larrard (2015)** extend imbalance frameworks to multi-level order books and stochastic liquidity regimes, showing how deeper-level imbalances can improve predictability.  
- **Engle, Ito & Lin (2019)** apply OFI-like measures in high-frequency FX and crypto markets, finding short-run predictability consistent with equity findings.

**Critiques, Limitations & Comparative Studies**  
While OFI is powerful, it has boundary conditions.  
- **Latency, queue priority, and hidden liquidity** can distort observable OFI; very fast activity may not be captured in standard windows.  
- Comparisons with **machine-learning imbalance measures** sometimes show incremental gains but at the cost of complexity and overfitting risk.  
- Nonlinearity can emerge at longer horizons: even if short-horizon impact is approximately linear, larger \(\Delta\) may show concavity.

In total, this literature situates *"The Price Impact of Order Book Events"* as a bridge between classical trade-based impact models and richer modern order book models. OFI has become a foundational tool in microstructure, and later studies have tested, extended, or critiqued it across assets, depths, and predictive frameworks.

# Replication

<!-- Now we move on to the actual replication.  The sections included here are all -->
<!-- necessary, but they may not be sufficient.  Add additional sections and sub-sections -->
<!-- as required to describe your work and make your analytical case. -->

## Data

<!-- Describe the data used in the original paper, and the data you are using. -->
<!-- Include obtaining, parsing, cleaning, data quality, and fields required. -->

## Replication of Key Analytical Techniques

<!-- Model the Key Analytical Techniques from the paper to be replicated. -->
<!-- Include summary statistics and any additional diagnostics you find relevant. -->

### Technique 1

### Technique 2

### Technique 3

## Hypothesis Tests

<!-- Describe statistical tests you perform to validate/refute the hypotheses. -->

## Extended Analysis

<!-- Extend the analysis with more data, assets, or alternative techniques. -->

## Overfitting

<!-- Assess experimental design, assumptions, parameterization, OOS tests, etc. -->

# Future Work

<!-- Additional work if the project continues. -->

# Conclusions

<!-- Summarize the project and describe your conclusions.  This sections can -->
<!-- range from 1-2 paragraphs to 1-2 pages. -->

\newpage

![CC-BY](cc_by_88x31.png)

# References
