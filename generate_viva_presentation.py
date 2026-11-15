import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    # 16:9 widescreen format
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Palette
    BG_COLOR = RGBColor(11, 19, 43)        # #0B132B Deep Obsidian Navy
    CARD_BG = RGBColor(30, 41, 59)         # #1E293B Dark Slate Card
    CARD_BORDER = RGBColor(51, 65, 85)     # #334155 Slate Border
    TEXT_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC Pure White
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 Slate Muted
    ACCENT_CYAN = RGBColor(56, 189, 248)   # #38BDF8 Electric Cyan
    ACCENT_GREEN = RGBColor(16, 185, 129)  # #10B981 Emerald Green
    ACCENT_AMBER = RGBColor(245, 158, 11)  # #F59E0B Amber
    ACCENT_RED = RGBColor(239, 68, 68)     # #EF4444 Crimson Red
    ACCENT_BLUE = RGBColor(99, 102, 241)   # #6366F1 Indigo / Royal Blue

    charts_dir = os.path.abspath(r"data\processed\final_charts")

    def set_slide_background(slide):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

    def add_header(slide, title_text, category_text="M.Sc. QUANTITATIVE FINANCE | SURABHI INVESTMENT SERVICES", slide_num=None):
        # Header category
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = ACCENT_CYAN
        p_c.font.name = "Segoe UI"

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.55))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT
        p_t.font.name = "Segoe UI"

        # Footer divider line & page number
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.color.rgb = CARD_BORDER

        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(10.0), Inches(0.3))
        tf_f = foot_box.text_frame
        tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = "Pondicherry University • Ramanujan School of Mathematical Sciences • Diviya C. (25MSQUFPY0018)"
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = TEXT_MUTED
        p_f.font.name = "Segoe UI"

        if slide_num:
            num_box = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.5), Inches(0.3))
            tf_n = num_box.text_frame
            tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
            p_n = tf_n.paragraphs[0]
            p_n.alignment = PP_ALIGN.RIGHT
            p_n.text = f"Slide {slide_num} of 14"
            p_n.font.size = Pt(9)
            p_n.font.bold = True
            p_n.font.color.rgb = ACCENT_CYAN
            p_n.font.name = "Segoe UI"

    def add_card(slide, left, top, width, height, title=None, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.35))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title.upper()
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN
            p.font.name = "Segoe UI"
        return shape

    def add_speaker_note(slide, note_text):
        notes_slide = slide.notes_slide
        text_frame = notes_slide.notes_text_frame
        text_frame.text = note_text

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    blank_layout = prs.slide_layouts[6]
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # University & Department Sub-heading
    u_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.8))
    tf_u = u_box.text_frame
    tf_u.word_wrap = True
    p_u1 = tf_u.paragraphs[0]
    p_u1.text = "PONDICHERRY UNIVERSITY"
    p_u1.font.size = Pt(16)
    p_u1.font.bold = True
    p_u1.font.color.rgb = ACCENT_AMBER
    p_u1.font.name = "Segoe UI"
    p_u2 = tf_u.add_paragraph()
    p_u2.text = "Ramanujan School of Mathematical Sciences • Department of Statistics"
    p_u2.font.size = Pt(12)
    p_u2.font.color.rgb = TEXT_MUTED
    p_u2.font.name = "Segoe UI"

    # Main Project Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.0))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t1 = tf_t.paragraphs[0]
    p_t1.text = "MACHINE-LEARNING-DRIVEN IMPLIED VOLATILITY FORECASTING & RELATIVE OPTION VALUATION"
    p_t1.font.size = Pt(28)
    p_t1.font.bold = True
    p_t1.font.color.rgb = TEXT_LIGHT
    p_t1.font.name = "Segoe UI"
    p_t2 = tf_t.add_paragraph()
    p_t2.text = "An Empirical Study on NIFTY 50 Weekly Index Options"
    p_t2.font.size = Pt(18)
    p_t2.font.bold = True
    p_t2.font.color.rgb = ACCENT_CYAN
    p_t2.font.name = "Segoe UI"

    # Divider
    l1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.0), Inches(11.3), Inches(0.03))
    l1.fill.solid()
    l1.fill.fore_color.rgb = ACCENT_CYAN
    l1.line.color.rgb = ACCENT_CYAN

    # 3 Metadata Cards
    # Card 1: Candidate
    add_card(s1, Inches(1.0), Inches(4.3), Inches(3.5), Inches(2.3), "CANDIDATE DETAILS")
    c1_box = s1.shapes.add_textbox(Inches(1.2), Inches(4.8), Inches(3.1), Inches(1.6))
    tf_c1 = c1_box.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "DIVIYA C."
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p2 = tf_c1.add_paragraph()
    p2.text = "Reg. No.: 25MSQUFPY0018\nM.Sc. Quantitative Finance\nBatch: 2025–2027\nViva Defense: November 2026"
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_MUTED

    # Card 2: Company
    add_card(s1, Inches(4.9), Inches(4.3), Inches(3.5), Inches(2.3), "CORPORATE PARTNER")
    c2_box = s1.shapes.add_textbox(Inches(5.1), Inches(4.8), Inches(3.1), Inches(1.6))
    tf_c2 = c2_box.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "Surabhi Investment Services Pvt. Ltd."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p2 = tf_c2.add_paragraph()
    p2.text = "Quantitative Research & Derivatives Desk\nTiruchirappalli, Tamil Nadu\nInternship: 18th June – 15th Aug 2026\nROC CIN: U67190TN2022PTC153288"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

    # Card 3: Academic Scope
    add_card(s1, Inches(8.8), Inches(4.3), Inches(3.5), Inches(2.3), "COURSE & CREDENTIALS")
    c3_box = s1.shapes.add_textbox(Inches(9.0), Inches(4.8), Inches(3.1), Inches(1.6))
    tf_c3 = c3_box.text_frame
    tf_c3.word_wrap = True
    p = tf_c3.paragraphs[0]
    p.text = "MSQF 534: Corporate Internship"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p2 = tf_c3.add_paragraph()
    p2.text = "Practical Examination Board\nRamanujan School of Math. Sciences\nFaculty Mentorship & Industry Guide\nPondicherry University, Puducherry"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

    add_speaker_note(s1, "Respected members of the examination board, I am Diviya C., presenting my M.Sc. Quantitative Finance corporate internship project conducted at Surabhi Investment Services Pvt. Ltd. in Tiruchirappalli. This empirical study focuses on high-frequency 5-minute implied volatility forecasting, Greek risk diagnostics, and relative mispricing detection across NIFTY 50 weekly index options.")

    # -------------------------------------------------------------
    # SLIDE 2: Company Profile — Surabhi Investment Services Pvt. Ltd.
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Company Profile: Surabhi Investment Services Pvt. Ltd.", slide_num=2)

    # Left Column: Overview & Corporate Governance
    add_card(s2, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "CORPORATE OVERVIEW & GOVERNANCE")
    tb2_left = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf2_l = tb2_left.text_frame
    tf2_l.word_wrap = True

    p = tf2_l.paragraphs[0]
    p.text = "Corporate Identity & Roots"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p2 = tf2_l.add_paragraph()
    p2.text = "• Established financial advisory, wealth management, and securities consulting firm located in Tiruchirappalli (Trichy), Tamil Nadu.\n• Incorporated under Companies Act (ROC Chennai: U67190TN2022PTC153288).\n• Registered Office: Jenne Plaza Complex, Bharathiyar Salai, Cantonment, Trichy."
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf2_l.add_paragraph()
    p3.text = "\nBoard of Directors & Governance"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_CYAN
    p4 = tf2_l.add_paragraph()
    p4.text = "• Led by Directors Mr. Shanmuganantham Sethuraman & Mr. Ramanathan Vijayakumar.\n• Four functional divisions: Wealth Advisory, Client Operations, Compliance & IT, and the Equity & Derivatives Desk."
    p4.font.size = Pt(10)
    p4.font.color.rgb = TEXT_LIGHT

    p5 = tf2_l.add_paragraph()
    p5.text = "\nCore Institutional Values"
    p5.font.size = Pt(13)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_GREEN
    p6 = tf2_l.add_paragraph()
    p6.text = "1. Fiduciary Integrity  2. Quantitative Rigor  3. Client Centricity\n4. Technological Agility  5. Strict Regulatory Compliance (SEBI/AMFI/NSE)."
    p6.font.size = Pt(10)
    p6.font.color.rgb = TEXT_LIGHT

    # Right Column: Business Architecture & Internship Mandate
    add_card(s2, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "SERVICE VERTICALS & DESK MANDATE")
    tb2_right = s2.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf2_r = tb2_right.text_frame
    tf2_r.word_wrap = True

    p = tf2_r.paragraphs[0]
    p.text = "Business Verticals & Client Offerings"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf2_r.add_paragraph()
    p2.text = "• Mutual Funds & SIP Planning (Retail & Salaried segments)\n• Direct Equity & Index Derivatives (HNI & Active proprietary trading)\n• Portfolio Management Services (PMS) & AIF bespoke mandates\n• Fixed Income (G-Secs, SGBs, Corporate FDs) & Capital Protection\n• Digital Platform: 24/7 web portal & portfolio monitoring"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf2_r.add_paragraph()
    p3.text = "\nEquity & Derivatives Desk: Industry Problem & Mandate"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_AMBER
    p4 = tf2_r.add_paragraph()
    p4.text = "• Operational Role: Quantitative Research Intern (18/06/2026 – 15/08/2026).\n• Industry Bottleneck 1: Naive IV stationarity assumptions (IV_{t+5} = IV_t) exposed quoting engines to toxic adverse selection.\n• Industry Bottleneck 2: Manual quote scanning failed to isolate rich vs. cheap options in fast-moving order books.\n• Institutional Mandate: Architect an automated end-to-end ML pipeline with Upstox API v2, 5-min IV forecasting, and a real-time Streamlit risk dashboard."
    p4.font.size = Pt(10)
    p4.font.color.rgb = TEXT_LIGHT

    add_speaker_note(s2, "During my corporate internship at Surabhi Investment Services Pvt. Ltd. in Tiruchirappalli, I was stationed at the Equity & Derivatives Desk under the institutional mentorship of Director Mr. Shanmuganantham Sethuraman. As trading in NIFTY 50 weekly options exploded, the desk faced major challenges: traders assumed static volatility over short horizons, leading to quoting slippage and unhedged gamma risk. My assigned mandate was to construct a high-frequency machine learning forecasting framework and automated decision-support dashboard.")

    # -------------------------------------------------------------
    # SLIDE 3: Research Problem & Quantitative Hypotheses
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Research Problem: The Fallacy of the Persistence Benchmark", slide_num=3)

    # Left: The Research Problem
    add_card(s3, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "THE RESEARCH PROBLEM & MARKET REALITY")
    tb3_l = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf3_l = tb3_l.text_frame
    tf3_l.word_wrap = True

    p = tf3_l.paragraphs[0]
    p.text = "The Persistence Fallacy in High-Frequency Trading"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p2 = tf3_l.add_paragraph()
    p2.text = "• Industry Baseline: Quoting engines frequently assume static volatility:\n  IV_{t+5} = IV_t  <=>  Delta_IV_{t+5} = 0\n• High Autocorrelation Trap: Although IV has high autocorrelation (rho approx 0.98), sudden volatility expansions and microstructural shocks cause significant mispricing.\n• Lagged Pricing & Adverse Selection: Quoting at stale IV leads to instant toxic fills by aggressive liquidity takers.\n• Delta Hedging Errors: Outdated IV distorts theoretical delta, creating unhedged market exposure.\n• Linear Infeasibility: OLS fails completely because cross-sectional volatility exhibits non-linear smile curvature and asymmetric skew."
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf3_l.add_paragraph()
    p3.text = "\nCore Research Question:"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_CYAN
    p4 = tf3_l.add_paragraph()
    p4.text = "\"Can a non-linear tree-based machine learning framework—engineered with short-horizon volatility memory, momentum velocity, and order-book liquidity metrics—statistically and economically outperform the random walk persistence benchmark in 5-minute IV forecasting without look-ahead bias?\""
    p4.font.size = Pt(10)
    p4.font.color.rgb = TEXT_MUTED

    # Right: The 4 Formal Quantitative Hypotheses
    add_card(s3, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "FORMAL QUANTITATIVE HYPOTHESES")
    tb3_r = s3.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf3_r = tb3_r.text_frame
    tf3_r.word_wrap = True

    def add_hypothesis_box(tf, title, desc, tag_color):
        p_t = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = tag_color
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_LIGHT

    add_hypothesis_box(tf3_r, "Hypothesis 1 (H1: Persistence Subjugation)",
                       "Tree-based non-linear regressors (Random Forest) utilizing short-term autoregressive and momentum features will achieve lower out-of-sample MAE and RMSE than the Persistence benchmark.", ACCENT_GREEN)

    add_hypothesis_box(tf3_r, "Hypothesis 2 (H2: Linear Specification Breakdown)",
                       "Standard Ordinary Least Squares (OLS) linear regression will fail to capture cross-sectional smile curvature, yielding negative out-of-sample explanatory power (R² < 0).", ACCENT_RED)

    add_hypothesis_box(tf3_r, "Hypothesis 3 (H3: Directional Conviction Edge)",
                       "Imposing an absolute forecast conviction threshold (|Delta_IV| >= 0.10 pts) will significantly increase directional trading accuracy over the baseline unthresholded signal.", ACCENT_CYAN)

    add_hypothesis_box(tf3_r, "Hypothesis 4 (H4: Expiry-Day Structural Non-Stationarity)",
                       "Implied volatility dynamics during the final 90 minutes of weekly contract expiry exhibit structural collapse, rendering mid-week models invalid without regime switching.", ACCENT_AMBER)

    add_speaker_note(s3, "Here we state the fundamental quantitative problem: in high-frequency trading, everyone uses the persistence benchmark because IV is strongly autocorrelated. But persistence lags during news shocks, and classical OLS fails because option smiles are non-linear. To address this rigorously, we formulated four formal hypotheses: H1 on beating persistence, H2 on linear breakdown, H3 on conviction filtering, and H4 on expiry-day structural collapse.")

    # -------------------------------------------------------------
    # SLIDE 4: Theoretical Foundations & Option Greeks
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Theoretical Foundations & Option Greeks in Weekly Cycles", slide_num=4)

    # Left: BSM Framework & The Greeks
    add_card(s4, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "BSM FRAMEWORK & INSTITUTIONAL GREEKS")
    tb4_l = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf4_l = tb4_l.text_frame
    tf4_l.word_wrap = True

    p = tf4_l.paragraphs[0]
    p.text = "Black-Scholes-Merton Baseline Pricing"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf4_l.add_paragraph()
    p2.text = "C = S_t * N(d1) - K * exp(-r*tau) * N(d2)\nP = K * exp(-r*tau) * N(-d2) - S_t * N(-d1)\nwhere d1 = [ln(S/K) + (r + 0.5*sigma^2)*tau] / (sigma * sqrt(tau))"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    p3 = tf4_l.add_paragraph()
    p3.text = "\nDesk Sensitivity Framework (50-Share NIFTY Lot)"
    p3.font.size = Pt(11)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_AMBER
    p4 = tf4_l.add_paragraph()
    p4.text = "• Delta (Delta = dV/dS): Directional hedge ratio. Delta=0.50 gains Rs. 25/lot per 1-point NIFTY move.\n• Gamma (Gamma = d2V/dS2): Curvature/stability of delta hedge. High gamma creates explosive rebalancing needs.\n• Vega (nu = dV/d_sigma): Sensitivity to 1% IV shift (S*sqrt(tau)*N'(d1)). Scales directly with sqrt(tau).\n• Theta (Theta = dV/dt): Deterministic daily erosion of extrinsic value."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = TEXT_LIGHT

    p5 = tf4_l.add_paragraph()
    p5.text = "\nBSM Carry Equilibrium (Mirror Principle)"
    p5.font.size = Pt(11)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_GREEN
    p6 = tf4_l.add_paragraph()
    p6.text = "Theta approx -0.5 * sigma^2 * S^2 * Gamma\nFundamental Rule: A delta-neutral book cannot collect Theta rent without taking on negative Gamma risk!"
    p6.font.size = Pt(9.5)
    p6.font.color.rgb = TEXT_LIGHT

    # Right: Weekly Expiry Peculiarities
    add_card(s4, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "WEEKLY EXPIRY PECULIARITIES & RISKS")
    tb4_r = s4.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf4_r = tb4_r.text_frame
    tf4_r.word_wrap = True

    p = tf4_r.paragraphs[0]
    p.text = "1. Delta Discontinuity (tau -> 0)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf4_r.add_paragraph()
    p2.text = "As expiry approaches, delta snaps into a step function: jumping to 1.0 for ITM and 0.0 for OTM, making smooth linear hedging impossible."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf4_r.add_paragraph()
    p3.text = "\n2. Asymptotic Gamma Explosion (lim tau->0 Gamma = +infinity)"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_RED
    p4 = tf4_r.add_paragraph()
    p4.text = "Because Gamma has sqrt(tau) in the denominator, ATM Gamma explodes vertically. A 20-point index swing flips delta from 0.20 to 0.80 instantly."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = TEXT_LIGHT

    p5 = tf4_r.add_paragraph()
    p5.text = "\n3. Vanishing Vega (lim tau->0 Vega = 0)"
    p5.font.size = Pt(12)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_AMBER
    p6 = tf4_r.add_paragraph()
    p6.text = "Vega collapses to zero on expiry afternoon. Weekly options become pure delta instruments; volatility hedges cannot protect near-expiry options."
    p6.font.size = Pt(9.5)
    p6.font.color.rgb = TEXT_LIGHT

    p7 = tf4_r.add_paragraph()
    p7.text = "\n4. Hyperbolic Theta Acceleration"
    p7.font.size = Pt(12)
    p7.font.bold = True
    p7.font.color.rgb = ACCENT_GREEN
    p8 = tf4_r.add_paragraph()
    p8.text = "Theta decay does not occur in daily steps; it bleeds minute-by-minute, creating severe pin risk around strike boundaries."
    p8.font.size = Pt(9.5)
    p8.font.color.rgb = TEXT_LIGHT

    add_speaker_note(s4, "This slide reviews the foundational mathematics. The Black-Scholes PDE gives us the no-arbitrage carry equilibrium: Theta and Gamma are exact mirror images. An options seller collecting Theta is mathematically forced to absorb negative Gamma risk. In weekly options, as tau approaches zero, Gamma explodes asymptotically while Vega vanishes, changing the mathematical behavior of the contracts entirely.")

    # -------------------------------------------------------------
    # SLIDE 5: End-to-End System Architecture & Workflow
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "End-to-End System Taxonomy & Architectural Workflow", slide_num=5)

    # 5 Process Flow Cards across the slide
    card_w = Inches(2.2)
    card_h = Inches(5.1)
    gap = Inches(0.18)
    start_x = Inches(0.8)
    top_y = Inches(1.5)

    stages = [
        ("1. INGESTION", ACCENT_CYAN, [
            ("Upstox API v2", "Direct broker REST gateway querying full NIFTY 50 option chains."),
            ("Wall-Clock Sync", "Synchronized 300s sleep targeting XX:00, XX:05, ..., XX:55 precisely."),
            ("Raw Snapshot Store", "Serializes real-time market depth into structured CSV files.")
        ]),
        ("2. PREPROCESSING", ACCENT_AMBER, [
            ("Quantitative Hygiene", "Purges non-economic quotes (IV <= 0) and crossed/wide spreads."),
            ("Moneyness Bounds", "Filters liquid near-ATM strikes (0.95 <= K/S <= 1.05)."),
            ("Exact Fractional TTE", "Derives continuous remaining life in exact decimal hours.")
        ]),
        ("3. MODELING", ACCENT_GREEN, [
            ("Temporal Integrity", "Enforces strict chronological train/test split (no look-ahead)."),
            ("Feature Synthesis", "Generates 39 features: multi-horizon lags, momentum, liquidity."),
            ("Ensemble Fitting", "Trains tuned Random Forest and XGBoost vs Persistence baseline.")
        ]),
        ("4. VALUATION", ACCENT_BLUE, [
            ("Conviction Gating", "Filters signals with |Delta_IV| >= 0.10 pts to eliminate churn."),
            ("Relative Screener", "Tags contracts as Fair, Rich (> +0.50), or Cheap (< -0.50)."),
            ("BSM Stress Matrix", "Simulates simultaneous Spot, IV, and Time-decay shocks.")
        ]),
        ("5. EXECUTION & UI", ACCENT_RED, [
            ("Live Daemon", "Continuous 5-min background process updating predictions."),
            ("Streamlit UI", "Institutional multi-page dashboard with 2D/3D Plotly surfaces."),
            ("Expiry Kill-Switch", "Operational safety stop halting ML 2 hours before expiry.")
        ])
    ]

    for idx, (title, color, items) in enumerate(stages):
        x = start_x + idx * (card_w + gap)
        add_card(s5, x, top_y, card_w, card_h, title, border_color=color)
        tb = s5.shapes.add_textbox(x + Inches(0.12), top_y + Inches(0.55), card_w - Inches(0.24), card_h - Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        for it_idx, (head, text) in enumerate(items):
            p = tf.add_paragraph() if it_idx > 0 else tf.paragraphs[0]
            p.text = head
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = color
            p.font.name = "Segoe UI"
            p2 = tf.add_paragraph()
            p2.text = text
            p2.font.size = Pt(9)
            p2.font.color.rgb = TEXT_LIGHT
            p2.font.name = "Segoe UI"

    add_speaker_note(s5, "Slide 5 illustrates our modular 5-stage production pipeline. The system connects Upstox API v2 live data harvesting to quantitative hygiene, continuous fractional time-to-expiry engineering, ensemble modeling, relative valuation screening, and real-time live execution via our background daemon and multi-page Streamlit dashboard.")

    # -------------------------------------------------------------
    # SLIDE 6: High-Frequency Data Engineering & Exact Fractional TTE
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "High-Frequency Data Ingestion & Exact Fractional TTE", slide_num=6)

    # Left: Upstox Ingestion & Hygiene
    add_card(s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "INGESTION & QUANTITATIVE HYGIENE")
    tb6_l = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf6_l = tb6_l.text_frame
    tf6_l.word_wrap = True

    p = tf6_l.paragraphs[0]
    p.text = "Wall-Clock Boundary Synchronization"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf6_l.add_paragraph()
    p2.text = "• Generic sleep(300) causes cumulative latency drift.\n• Exact formula: Delta_t_wait = 300 - (t_now mod 300).\n• Guarantees harvesting precisely at XX:00, XX:05, ..., XX:55."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf6_l.add_paragraph()
    p3.text = "\nThree Sequential Quantitative Hygiene Filters"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_AMBER
    p4 = tf6_l.add_paragraph()
    p4.text = "1. Zero-IV Purge: Discards quotes with IV <= 0 or NaN where exchange BSM solvers failed to converge.\n2. Spread Sanity: Requires Bid > 0, Ask >= Bid, and (Ask - Bid) <= 50 index points to eliminate phantom quotes.\n3. Moneyness Bounds: Constrains strikes to 0.95 <= K/S <= 1.05. Captures 92% of Open Interest and 95% of daily volume while eliminating illiquid deep-wing quote noise."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = TEXT_LIGHT

    # Right: Exact Fractional TTE
    add_card(s6, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "EXACT FRACTIONAL TIME-TO-EXPIRY (TTE)")
    tb6_r = s6.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf6_r = tb6_r.text_frame
    tf6_r.word_wrap = True

    p = tf6_r.paragraphs[0]
    p.text = "The Flaw of Standard Day Discretization"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p2 = tf6_r.add_paragraph()
    p2.text = "• Standard libraries discretize maturity into integer days: tau = Days / 365.\n• On expiry Thursday at 09:30 IST, integer rounding yields Days=0 (division-by-zero error in d1/d2) or Days=1 (overestimating remaining life by 400%)."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf6_r.add_paragraph()
    p3.text = "\nExact Decimal Hour Formulation"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GREEN
    p4 = tf6_r.add_paragraph()
    p4.text = "TTE_hours = (T_expiry - t_current) / 3600 seconds\ntau = TTE_hours / 8760 annual hours\nwhere T_expiry is fixed at Thursday 15:30:00 IST in epoch seconds."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = ACCENT_CYAN

    p5 = tf6_r.add_paragraph()
    p5.text = "\nTrader's Intuition & Continuity"
    p5.font.size = Pt(12)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_AMBER
    p6 = tf6_r.add_paragraph()
    p6.text = "• On weekly options, theta decay bleeds continuously by the minute.\n• At 14:00 IST on Thursday, exactly 1.50 trading hours remain (tau = 0.000171).\n• Fractional hours preserve smooth mathematical continuity, allowing regression trees to learn hyper-theta acceleration without boundary distortion."
    p6.font.size = Pt(9.5)
    p6.font.color.rgb = TEXT_LIGHT

    add_speaker_note(s6, "In Slide 6, we address two fundamental engineering challenges. First, our wall-clock synchronization algorithm avoids cumulative timing drift. Second, we solved the day-rounding fallacy by engineering continuous Fractional Time-to-Expiry in decimal hours down to second-level precision, preventing mathematical singularities in Black-Scholes formulas on expiry day.")

    # -------------------------------------------------------------
    # SLIDE 7: 39-Dimensional Feature Space & Temporal Integrity
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "39-Dimensional Feature Space & Temporal Non-Leakage", slide_num=7)

    # Left: Feature Catalog Table
    add_card(s7, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2), "ENGINEERED FEATURE SPACE (39 FEATURES)")
    tb7_l = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.6), Inches(4.5))
    tf7_l = tb7_l.text_frame
    tf7_l.word_wrap = True

    feat_cats = [
        ("Strike Geometry (4)", "strike (K), spot (S), moneyness (K/S), log_moneyness ln(S/K)"),
        ("Micro-Temporal Dynamics (4)", "exact_tte_hours, hour_of_day, minute_of_hour, time_fraction"),
        ("Market State Variables (7)", "IV (sigma_t), LTP, Bid, Ask, bid_ask_spread, spread_pct, spot"),
        ("Autoregressive Memory (6)", "IV_lag_5m, IV_lag_10m, spot_lag_5m, 10m, spread_lag_5m, 10m"),
        ("Volatility Velocity & Momentum (6)", "IV_change_prev_5m, 10m, spot_return_5m, 10m, spread_change_5m, LTP_change_5m"),
        ("Order-Book Liquidity & Sentiment (12)", "Volume, OI, pcr (OIPE/OICE), is_call, is_atm, Volume_change_5m, OI_change_5m, iv_spread_interaction (IV * spread_pct)")
    ]

    for c_idx, (cat_name, cat_desc) in enumerate(feat_cats):
        p = tf7_l.add_paragraph() if c_idx > 0 else tf7_l.paragraphs[0]
        p.text = cat_name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p2 = tf7_l.add_paragraph()
        p2.text = cat_desc
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_LIGHT

    # Right: Strict Chronological Partitioning
    add_card(s7, Inches(7.2), Inches(1.5), Inches(5.3), Inches(5.2), "STRICT CHRONOLOGICAL PARTITIONING")
    tb7_r = s7.shapes.add_textbox(Inches(7.4), Inches(2.0), Inches(4.9), Inches(4.5))
    tf7_r = tb7_r.text_frame
    tf7_r.word_wrap = True

    p = tf7_r.paragraphs[0]
    p.text = "The Danger of Shuffled Cross-Validation"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p2 = tf7_r.add_paragraph()
    p2.text = "• In quantitative finance, standard randomized K-fold splits are fatal.\n• Shuffling observations allows future prices (t+5) to leak into the training set while predicting past prices (t).\n• Autoregressive correlation yields artificially inflated R² that collapses immediately upon live deployment."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf7_r.add_paragraph()
    p3.text = "\nStrict Chronological Split Implementation"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GREEN
    p4 = tf7_r.add_paragraph()
    p4.text = "• Training Set (T_train): Oct 15 09:15 to Oct 16 11:30 IST (74.6 to 100.6 hours to expiry).\n• Test Set (T_test): Oct 16 11:35 to Oct 16 15:30 IST (strictly unseen future timestamps).\n• Zero Look-Ahead Invariant: All scalers and feature imputation medians are computed exclusively on T_train and applied forward."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = TEXT_LIGHT

    p5 = tf7_r.add_paragraph()
    p5.text = "\nTarget Formulation"
    p5.font.size = Pt(12)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_AMBER
    p6 = tf7_r.add_paragraph()
    p6.text = "Target = Delta_IV_{t+5} = IV_{t+5} - IV_t\nPredicting the change rather than raw level prevents the model from trivially memorizing the autoregressive level."
    p6.font.size = Pt(9.5)
    p6.font.color.rgb = ACCENT_CYAN

    add_speaker_note(s7, "Slide 7 outlines our 39 engineered features across geometry, time, market state, autoregressive memory, and liquidity. Crucially, we enforce strict chronological train/test partitioning. Shuffled cross-validation causes catastrophic look-ahead bias in financial time series. Our models were trained on Oct 15 to midday Oct 16, and tested exclusively on subsequent unseen data.")

    # -------------------------------------------------------------
    # SLIDE 8: Numerical & Algorithmic Engines
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Numerical & Algorithmic Engines: Inversion & Gating", slide_num=8)

    # Left: Newton-Raphson Solver
    add_card(s8, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "NEWTON-RAPHSON IV SOLVER")
    tb8_l = s8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf8_l = tb8_l.text_frame
    tf8_l.word_wrap = True

    p = tf8_l.paragraphs[0]
    p.text = "Numerical BSM Inversion Formulation"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf8_l.add_paragraph()
    p2.text = "f(sigma) = C_BSM(S, K, tau, r, sigma) - C_market = 0\nsigma_{n+1} = sigma_n - [C_BSM(sigma_n) - C_market] / Vega(sigma_n)"
    p2.font.size = Pt(10)
    p2.font.color.rgb = ACCENT_AMBER

    p3 = tf8_l.add_paragraph()
    p3.text = "\nBrenner-Subrahmanyam Analytical Seeding"
    p3.font.size = Pt(11)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GREEN
    p4 = tf8_l.add_paragraph()
    p4.text = "sigma_0 = sqrt(2*pi / tau) * (C_market / S)\nProvides a near-instant starting estimate, cutting iteration counts from ~15 down to 3–4 steps."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = TEXT_LIGHT

    p5 = tf8_l.add_paragraph()
    p5.text = "\nVega Singularity Trap & Safeguard"
    p5.font.size = Pt(11)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_RED
    p6 = tf8_l.add_paragraph()
    p6.text = "• As tau -> 0, Vega collapses toward zero.\n• Dividing price error by Vega -> 0 causes Newton-Raphson to diverge wildly.\n• Production Safeguard: If Vega < 10^-7, the solver falls back to bracketed Brent bisection."
    p6.font.size = Pt(9.5)
    p6.font.color.rgb = TEXT_LIGHT

    # Right: Conviction Filter & Valuation Logic
    add_card(s8, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "CONVICTION GATING & VALUATION LOGIC")
    tb8_r = s8.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf8_r = tb8_r.text_frame
    tf8_r.word_wrap = True

    p = tf8_r.paragraphs[0]
    p.text = "Directional Conviction Gating (|Delta_IV| >= theta)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf8_r.add_paragraph()
    p2.text = "HitRate(theta) = sum_{i in S_theta} I(sgn(pred) == sgn(actual)) / |S_theta|\n• Eliminates low-conviction predictions (|Delta_IV| < 0.10) where expected alpha is eaten by bid-ask spreads."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf8_r.add_paragraph()
    p3.text = "\nRelative IV Mispricing Screener"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_AMBER
    p4 = tf8_r.add_paragraph()
    p4.text = "Valuation Spread = IV_market - IV_forecast\n• High IV / Rich (Spread > +0.50 pts):\n  Option is relatively overvalued -> Credit spreads, Iron Condors.\n• Fair / Neutral (|Spread| <= 0.50 pts):\n  Pricing aligns with model equilibrium -> Delta-neutral market making.\n• Low IV / Cheap (Spread < -0.50 pts):\n  Option is relatively undervalued -> Debit spreads, Long straddles."
    p4.font.size = Pt(9.5)
    p4.font.color.rgb = TEXT_LIGHT

    p5 = tf8_r.add_paragraph()
    p5.text = "\nMulti-Factor Stress Matrix"
    p5.font.size = Pt(11)
    p5.font.bold = True
    p5.font.color.rgb = ACCENT_GREEN
    p6 = tf8_r.add_paragraph()
    p6.text = "Stresses contract values across Spot (+-2%), IV (+-20%), and Time Decay (0 to 24h) to measure joint tail risk."
    p6.font.size = Pt(9.5)
    p6.font.color.rgb = TEXT_LIGHT

    add_speaker_note(s8, "Slide 8 details our algorithmic engines. To invert implied volatility accurately near expiry, our Newton-Raphson solver utilizes Brenner-Subrahmanyam seeding and a Vega singularity check that switches to Brent bisection when Vega drops below 10^-7. We also define our conviction filter and the relative IV screener logic that tags contracts as Rich, Fair, or Cheap.")

    # -------------------------------------------------------------
    # SLIDE 9: Master Empirical Model Benchmarks
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Master Empirical Model Benchmarks & Comparison", slide_num=9)

    # Left: Empirical Comparison Table & Insights
    add_card(s9, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2), "OUT-OF-SAMPLE BENCHMARK EVALUATION")
    
    # Add Table
    table_shape = s9.shapes.add_table(5, 5, Inches(1.0), Inches(2.0), Inches(5.6), Inches(2.1))
    table = table_shape.table
    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(0.9)
    table.columns[2].width = Inches(0.9)
    table.columns[3].width = Inches(0.8)
    table.columns[4].width = Inches(1.0)

    headers = ["Model Architecture", "MAE", "RMSE", "R²", "vs. Persist."]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p.alignment = PP_ALIGN.CENTER

    data_rows = [
        ("Persistence (Baseline)", "0.5505", "1.3207", "0.9843", "0.00%"),
        ("Linear OLS Regression", "6.1720", "8.4103", "-0.2410", "-1021%"),
        ("XGBoost Regressor", "0.5530", "1.2964", "0.9849", "-0.45%"),
        ("Random Forest (Tuned)", "0.5214", "1.2188", "0.9866", "+5.28%")
    ]

    for row_idx, r in enumerate(data_rows):
        for col_idx, val in enumerate(r):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row_idx < 3 else RGBColor(20, 45, 45)
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9)
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
            if row_idx == 3:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            elif row_idx == 1:
                p.font.color.rgb = ACCENT_RED
            else:
                p.font.color.rgb = TEXT_LIGHT

    tb9 = s9.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(5.6), Inches(2.2))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "Key Quantitative Findings:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p2 = tf9.add_paragraph()
    p2.text = "• H1 Confirmed: Random Forest beats persistence, achieving a 5.28% reduction in MAE (0.5214 vs 0.5505) and 7.72% reduction in RMSE (1.2188 vs 1.3207).\n• H2 Confirmed: OLS fails catastrophically (R² = -0.2410, MAE = 6.1720) because linear planes cannot fit volatility smiles.\n• RF vs. XGBoost: Bagging in Random Forest averages out high-frequency quote bounce; boosting overfits initial noise residuals."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_LIGHT

    # Right: Chart 03_rf_vs_persistence.png
    chart_p1 = os.path.join(charts_dir, "03_rf_vs_persistence.png")
    if os.path.exists(chart_p1):
        s9.shapes.add_picture(chart_p1, Inches(7.1), Inches(1.5), width=Inches(5.4))
    else:
        add_card(s9, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), "BENCHMARK VISUALIZATION")

    add_speaker_note(s9, "This slide displays our master out-of-sample empirical benchmark results. Random Forest successfully beats the persistence random walk, reducing MAE by 5.28% and RMSE by 7.72%, validating Hypothesis 1. Linear regression fails catastrophically with a negative R² of -0.2410, proving Hypothesis 2. Random Forest also outperforms XGBoost because bagging averages out high-frequency bid-ask quote noise.")

    # -------------------------------------------------------------
    # SLIDE 10: Quantitative Feature Importance Hierarchy
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Quantitative Feature Importance Hierarchy (MDI)", slide_num=10)

    # Left: Feature Hierarchy Table & Discussion
    add_card(s10, Inches(0.8), Inches(1.5), Inches(5.8), Inches(5.2), "FEATURE WEIGHTS & ECONOMIC INTERPRETATION")
    tb10 = s10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.4), Inches(4.5))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    top_feats = [
        ("1. IV_change_prev_5m", "7.21%", "Short-term volatility velocity (momentum shock)"),
        ("2. IV_change_prev_10m", "6.74%", "Multi-period trend acceleration over 10 mins"),
        ("3. IV", "6.53%", "Current baseline market implied volatility level"),
        ("4. IV_lag_5m", "4.27%", "First-order autoregressive lag (persistence baseline)"),
        ("5. bid_ask_spread", "3.52%", "LOB liquidity cost / dealer inventory imbalance"),
        ("6. spot_lag_5m", "3.39%", "Past index level capturing directional trend"),
        ("7. bid_ask_spread_lag_5m", "3.36%", "Spread widening velocity (liquidity distress)"),
        ("8. IV_lag_10m", "3.35%", "Second-order autoregressive memory baseline")
    ]

    for f_idx, (fname, weight, fdesc) in enumerate(top_feats):
        p = tf10.add_paragraph() if f_idx > 0 else tf10.paragraphs[0]
        p.text = f"{fname}  [{weight}]"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN if f_idx < 2 else (ACCENT_CYAN if f_idx < 5 else ACCENT_AMBER)
        p2 = tf10.add_paragraph()
        p2.text = fdesc
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_LIGHT

    p3 = tf10.add_paragraph()
    p3.text = "\nCore Economic Takeaway:"
    p3.font.size = Pt(10.5)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_CYAN
    p4 = tf10.add_paragraph()
    p4.text = "Recent volatility velocity and order-book liquidity dominate static strike geometry. Momentum and spreads account for nearly 21% of total model variance."
    p4.font.size = Pt(9)
    p4.font.color.rgb = TEXT_MUTED

    # Right: Chart 04_feature_importance.png
    chart_p2 = os.path.join(charts_dir, "04_feature_importance.png")
    if os.path.exists(chart_p2):
        s10.shapes.add_picture(chart_p2, Inches(6.9), Inches(1.5), width=Inches(5.6))
    else:
        add_card(s10, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.2), "FEATURE IMPORTANCE CHART")

    add_speaker_note(s10, "In Slide 10, we examine the Gini impurity feature importance. A vital empirical insight emerges: short-term volatility velocity and order book bid-ask spreads heavily dominate static strike variables like moneyness or days-to-expiry. The 5-minute and 10-minute volatility velocity features alone capture 14% of predictive power, proving that market makers reprice volatility dynamically based on order book liquidity.")

    # -------------------------------------------------------------
    # SLIDE 11: Directional Conviction Gating Analysis
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Directional Conviction Gating: Monetizing the Edge", slide_num=11)

    # Left: Threshold Performance Table
    add_card(s11, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2), "CONVICTION THRESHOLDING RESULTS")

    table_shape11 = s11.shapes.add_table(7, 5, Inches(1.0), Inches(2.0), Inches(5.6), Inches(2.5))
    table11 = table_shape11.table
    table11.columns[0].width = Inches(1.2)
    table11.columns[1].width = Inches(1.1)
    table11.columns[2].width = Inches(1.1)
    table11.columns[3].width = Inches(1.1)
    table11.columns[4].width = Inches(1.1)

    h11 = ["Threshold (theta)", "Signals", "Coverage", "Hit-Rate", "Desk Utility"]
    for col_idx, h in enumerate(h11):
        cell = table11.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p.alignment = PP_ALIGN.CENTER

    t_rows = [
        ("0.00 pts", "1,137", "100.0%", "53.20%", "Unfiltered Noise"),
        ("0.05 pts", "318", "28.0%", "61.32%", "Cuts 72% noise"),
        ("0.10 pts", "204", "17.9%", "63.40%", "Optimal Filter"),
        ("0.15 pts", "142", "12.5%", "63.38%", "High Precision"),
        ("0.20 pts", "105", "9.2%", "63.81%", "Breakout Focus"),
        ("0.25 pts", "76", "6.7%", "64.47%", "Highest Alpha")
    ]

    for row_idx, r in enumerate(t_rows):
        for col_idx, val in enumerate(r):
            cell = table11.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(20, 45, 45) if row_idx == 2 else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.alignment = PP_ALIGN.CENTER
            if row_idx == 2:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            else:
                p.font.color.rgb = TEXT_LIGHT

    tb11 = s11.shapes.add_textbox(Inches(1.0), Inches(4.7), Inches(5.6), Inches(1.8))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    p = tf11.paragraphs[0]
    p.text = "Validation of Hypothesis 3 (H3):"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p2 = tf11.add_paragraph()
    p2.text = "• At theta = 0.10 pts, directional accuracy leaps from 53.20% to 63.40% (+10.20% gain).\n• Eliminates 82% of uninformative trades, saving the desk from bid-ask churn and slippage.\n• Average absolute move in the gated set is 16.85 IV points, providing ample margin to cover execution costs."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_LIGHT

    # Right: Chart 02_actual_vs_predicted_delta_iv.png
    chart_p3 = os.path.join(charts_dir, "02_actual_vs_predicted_delta_iv.png")
    if os.path.exists(chart_p3):
        s11.shapes.add_picture(chart_p3, Inches(7.1), Inches(1.5), width=Inches(5.4))
    else:
        add_card(s11, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), "DELTA IV PREDICTIONS")

    add_speaker_note(s11, "Slide 11 validates Hypothesis 3 through directional conviction gating. In high-frequency options, trading on tiny predicted movements creates friction drag. By applying an absolute threshold of 0.10 IV points, our directional hit-rate jumps from 53.20% to 63.40%, eliminating 82% of low-conviction noise trades and providing institutional traders with a high-edge execution filter.")

    # -------------------------------------------------------------
    # SLIDE 12: Relative IV Valuation Screener & Stress Testing
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Relative IV Valuation Screener & Multi-Factor Stress Testing", slide_num=12)

    # Left: Valuation Distribution & Screener
    add_card(s12, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "RELATIVE VALUATION SCREENER")
    tb12_l = s12.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf12_l = tb12_l.text_frame
    tf12_l.word_wrap = True

    p = tf12_l.paragraphs[0]
    p.text = "Contract Classification (983 Near-ATM Strikes)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf12_l.add_paragraph()
    p2.text = "• Fair / Neutral IV (77.92% | 766 contracts):\n  |Spread| <= 0.50 pts. Efficient market alignment; optimal for delta-neutral market making.\n• Rich / Overvalued (15.46% | 152 contracts):\n  Spread > +0.50 pts. Market IV trades above model forecast; candidate for credit spreads & iron condors.\n• Cheap / Undervalued (6.61% | 65 contracts):\n  Spread < -0.50 pts. Market IV discounted; candidate for long debit spreads and straddles."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    # Embed distribution chart thumbnail if available
    chart_p4 = os.path.join(charts_dir, "05_relative_iv_valuation_distribution.png")
    if os.path.exists(chart_p4):
        s12.shapes.add_picture(chart_p4, Inches(1.1), Inches(4.3), width=Inches(5.0))

    # Right: Multi-Factor Stress Matrix
    add_card(s12, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "MULTI-FACTOR BLACK-SCHOLES STRESS MATRIX")
    tb12_r = s12.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf12_r = tb12_r.text_frame
    tf12_r.word_wrap = True

    p = tf12_r.paragraphs[0]
    p.text = "Case Study: NIFTY 23,150 CE (Base Value = Rs. 85.07)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p2 = tf12_r.add_paragraph()
    p2.text = "• Spot +1%: Value surges +188.83% (Rs. 245.70).\n• Spot -1%: Value drops -74.32% (Rs. 21.85).\n• IV Spike (+20% rel): Value gains +21.33% (Rs. 103.22).\n• IV Crush (-20% rel): Value drops -21.46% (Rs. 66.82).\n• Crash Scenario (Spot -2% & IV +20%):\n  Call value plummets by -94.84% (down to Rs. 4.39)!"
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf12_r.add_paragraph()
    p3.text = "\nCritical Quantitative Desk Takeaways:"
    p3.font.size = Pt(11)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_CYAN
    p4 = tf12_r.add_paragraph()
    p4.text = "1. Delta Heavily Dominates Vega: A 1% spot move has 9x the impact of a 20% relative IV expansion.\n2. Inefficacy of Long Vega in Crashes: Positive vega gains are completely wiped out by delta destruction in market selloffs.\n3. Trading Takeaway: Volatility trading must always be coupled with dynamic delta hedging."
    p4.font.size = Pt(9)
    p4.font.color.rgb = TEXT_MUTED

    add_speaker_note(s12, "Slide 12 demonstrates the translation of statistical forecasts into trading decisions. Our Relative IV screener tagged 77.9% of contracts as Fair, 15.5% as Rich, and 6.6% as Cheap. In the multi-factor stress test of the 23,150 Call, Delta heavily dominated Vega. Notably, in a market crash where spot dropped 2% and volatility spiked 20%, the call still lost 95% of its value, proving that long vega cannot protect against directional moves without active delta hedging.")

    # -------------------------------------------------------------
    # SLIDE 13: Expiry-Day Structural Regime Breakdown
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Forensic Analysis: The Expiry-Day Structural Regime Shift", slide_num=13)

    # Left: October 19 Breakdown Table & Mechanisms
    add_card(s13, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2), "OCTOBER 19 EXPIRY FORENSIC BREAKDOWN")

    table_shape13 = s13.shapes.add_table(6, 3, Inches(1.0), Inches(2.0), Inches(5.6), Inches(2.1))
    table13 = table_shape13.table
    table13.columns[0].width = Inches(2.2)
    table13.columns[1].width = Inches(1.6)
    table13.columns[2].width = Inches(1.8)

    h13 = ["Metric", "Development (74-100h TTE)", "Expiry Day (<1.58h TTE)"]
    for col_idx, h in enumerate(h13):
        cell = table13.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p.alignment = PP_ALIGN.CENTER

    b_rows = [
        ("Time-to-Expiry (TTE)", "74.6 to 100.6 hours", "0.17 to 1.58 hours (-98.4%)"),
        ("Random Forest MAE", "0.5214 pts", "17.42 pts (+3,241% surge)"),
        ("Persistence MAE", "0.5505 pts", "14.47 pts (Beats ML by 2.95)"),
        ("Directional Hit-Rate", "53.20% (63.4% @ 0.1)", "19.09% (Sub-random flip)"),
        ("Maximum Single Error", "3.42 pts", "148.60 pts (Extreme tail)")
    ]

    for row_idx, r in enumerate(b_rows):
        for col_idx, val in enumerate(r):
            cell = table13.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(45, 20, 20) if row_idx in [1, 3] else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
            if row_idx in [1, 3]:
                p.font.bold = True
                p.font.color.rgb = ACCENT_RED
            else:
                p.font.color.rgb = TEXT_LIGHT

    tb13 = s13.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(5.6), Inches(2.2))
    tf13 = tb13.text_frame
    tf13.word_wrap = True

    p = tf13.paragraphs[0]
    p.text = "Confirmation of Hypothesis 4 (H4) — 4 Root Causes:"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p2 = tf13.add_paragraph()
    p2.text = "1. Hyperbolic Gamma/Theta Singularity: Extrinsic value vanishes vertically; continuous diffusion assumptions fail.\n2. Vanishing Vega Divergence: As Vega -> 0, Delta_sigma = -Delta_C / Vega -> infinity. A 10-paise anomaly causes a 150-pt IV spike.\n3. Severe Covariate Shift: TTE in [0.17, 1.58] is totally outside training bounds [74.6, 100.6].\n4. Institutional Pin Risk: Aggressive book squaring causes erratic jumps rather than smooth flow."
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = TEXT_LIGHT

    # Right: Chart 08_expiry_day_deterioration.png
    chart_p5 = os.path.join(charts_dir, "08_expiry_day_deterioration.png")
    if os.path.exists(chart_p5):
        s13.shapes.add_picture(chart_p5, Inches(7.1), Inches(1.5), width=Inches(5.4))
    else:
        add_card(s13, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), "EXPIRY DAY BREAKDOWN")

    add_speaker_note(s13, "Slide 13 is a key academic discovery of this thesis: the Expiry-Day Structural Breakdown. When we deployed our mid-week trained model onto unseen October 19 expiry data with under 95 minutes to settlement, MAE exploded by 3,241% from 0.52 to 17.42 points! Because Vega vanishes, inverting market prices causes a division by near-zero, producing massive artificial volatility spikes. This validates Hypothesis 4 and proves that a single static ML model cannot be used across the entire contract lifecycle.")

    # -------------------------------------------------------------
    # SLIDE 14: Conclusions, Operational Recommendations & Future Scope
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Conclusions, Operational Protocols & Future Directions", slide_num=14)

    # Left: 5 Key Research Contributions
    add_card(s14, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), "5 KEY RESEARCH CONTRIBUTIONS")
    tb14_l = s14.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf14_l = tb14_l.text_frame
    tf14_l.word_wrap = True

    contribs = [
        ("1. Beat Persistence Benchmark", "Random Forest achieved 5.28% lower MAE (0.5214) and 7.72% lower RMSE (1.2188) over persistence under strict chronological evaluation."),
        ("2. Proved OLS Failure", "Linear models failed completely (R² = -0.2410) due to non-linear smile curvature."),
        ("3. Microstructure Dominance", "Volatility velocity and bid-ask spreads account for ~21% of variance, heavily dominating static strike geometry."),
        ("4. Monetized Conviction Edge", "Gating at |Delta_IV| >= 0.10 boosted directional accuracy from 53.20% to 63.40% while cutting 82% noise churn."),
        ("5. Diagnosed Expiry Collapse", "Discovered mathematical breakdown as tau -> 0; proved the necessity of a Regime-Switching Architecture.")
    ]

    for c_idx, (head, text) in enumerate(contribs):
        p = tf14_l.add_paragraph() if c_idx > 0 else tf14_l.paragraphs[0]
        p.text = head
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN
        p2 = tf14_l.add_paragraph()
        p2.text = text
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_LIGHT

    # Right: 4 Desk Recommendations & Future Scope
    add_card(s14, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), "DESK PROTOCOLS & FUTURE RESEARCH")
    tb14_r = s14.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf14_r = tb14_r.text_frame
    tf14_r.word_wrap = True

    p = tf14_r.paragraphs[0]
    p.text = "4 Operational Desk Protocols for Surabhi Investments:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    recs = [
        ("Protocol 1: Dynamic Quote Shading", "Automated quoters should shade bids higher when Delta_IV > +0.10 to prevent adverse selection."),
        ("Protocol 2: Mandatory Conviction Filter", "Enforce |Delta_IV| >= 0.10 to capture 63.4% directional edge and avoid fee drag."),
        ("Protocol 3: Relative Value Spreads", "Sell Rich strikes (> +0.50 pts) via credit spreads; buy Cheap strikes (< -0.50 pts)."),
        ("Protocol 4: The 2-Hour Expiry Kill Switch", "MANDATORY: Automatically halt ML IV forecasting at 13:30 IST on expiry day; transition to parity arbitrage and gamma-scalping!")
    ]

    for r_head, r_text in recs:
        p = tf14_r.add_paragraph()
        p.text = r_head
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_AMBER
        p2 = tf14_r.add_paragraph()
        p2.text = r_text
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_LIGHT

    p3 = tf14_r.add_paragraph()
    p3.text = "\nDirections for Future Research:"
    p3.font.size = Pt(10.5)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_BLUE
    p4 = tf14_r.add_paragraph()
    p4.text = "• Temporal Fusion Transformers (TFT) with cross-attention on limit order book depth.\n• Endogenous Markov-Switching models handling Normal vs Expiry regimes.\n• Reinforcement Learning (PPO) agents for dynamic delta-gamma hedging."
    p4.font.size = Pt(8.5)
    p4.font.color.rgb = TEXT_MUTED

    add_speaker_note(s14, "To conclude, this internship delivered an end-to-end quantitative framework combining data ingestion, machine learning forecasting, and real-time risk screening. We established four operational protocols for Surabhi Investment Services, including our 2-hour expiry kill-switch. I express my gratitude to my mentors and the Department of Statistics. Thank you, and I look forward to your questions.")

    # Save presentation
    output_path = os.path.abspath(r"D:\Internship Project\NIFTY50_IV_Forecasting_Viva_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    build_presentation()
