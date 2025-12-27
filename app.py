import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Tính Doanh Thu (Cộng Dồn KM)", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .target-box { background-color: #d1eaed; padding: 15px; border-radius: 10px; border-left: 5px solid #00cec9; }
    .result-box { background-color: #ffeaa7; padding: 15px; border-radius: 10px; border-left: 5px solid #fdcb6e; }
    .big-number { font-size: 24px; font-weight: bold; color: #2d3436; }
    .plus-sign { color: #d63031; font-weight: bold; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Tính Doanh Thu: Kịch Bản Chồng Khuyến Mại")

# --- 1. SIDEBAR: CẤU HÌNH ---
with st.sidebar:
    st.header("1. Thông số Cơ bản")
    price = st.number_input("Giá bán niêm yết (VNĐ)", value=120000, step=1000)
    base_cogs = st.number_input("Giá vốn gốc (VNĐ)", value=30000, step=1000)
    
    st.header("2. Chi phí Vận hành (% Doanh thu)")
    pct_mgmt = st.number_input("% Chi phí quản lý", value=10.0)
    pct_salary = st.number_input("% Lương Trình dược viên", value=15.0)
    pct_bonus = st.number_input("% Thưởng khách hàng", value=20.0)
    
    total_opex_pct = (pct_mgmt + pct_salary + pct_bonus) / 100
    st.info(f"Tổng chi phí vận hành: {total_opex_pct*100:.1f}%")

# --- 2. GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 1.1])

# === KỊCH BẢN 1: KM CŨ (MUA 3 TẶNG 1) ===
with col1:
    st.subheader("1️⃣ Kịch bản Cũ (Mốc chuẩn)")
    current_rev = st.number_input("Doanh thu hiện tại (VNĐ)", value=550000000, step=10000000)
    
    st.markdown("<b>Khuyến mại nền (KM1):</b>", unsafe_allow_html=True)
    c1a, c1b = st.columns(2)
    with c1a: buy_1 = st.number_input("Mua (SL)", value=3, key="b1")
    with c1b: get_1 = st.number_input("Tặng (SL)", value=1, key="g1")

    # --- TÍNH TOÁN SCENARIO 1 ---
    # Giá vốn tăng thêm do KM1
    added_cost_1 = (get_1 * base_cogs) / buy_1
    total_cogs_unit_1 = base_cogs + added_cost_1
    
    # Tính lợi nhuận mục tiêu
    cogs_amount_1 = current_rev * (total_cogs_unit_1 / price)
    opex_amount_1 = current_rev * total_opex_pct
    target_profit = current_rev - cogs_amount_1 - opex_amount_1
    
    st.markdown(f"""
    <div class="target-box">
        <p>Lợi nhuận ròng hiện tại:</p>
        <p class="big-number">{target_profit:,.0f} VNĐ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Giá vốn 1 sp = {base_cogs:,.0f} (Gốc) + {added_cost_1:,.0f} (Do KM 3 tặng 1)")

# === KỊCH BẢN 2: KM CŨ + KM MỚI (CHỒNG CẢ 2) ===
with col2:
    st.subheader("2️⃣ Kịch bản Mới (Cộng dồn)")
    st.caption("Áp dụng đồng thời KM cũ VÀ KM mới (Mua 20 tặng 3).")
    
    st.markdown("---")
    st.markdown("<b>Khuyến mại thêm (KM2):</b>", unsafe_allow_html=True)
    c2a, c2b = st.columns(2)
    with c2a: buy_2 = st.number_input("Mua (SL) Thêm", value=20, key="b2")
    with c2b: get_2 = st.number_input("Tặng (SL) Thêm", value=3, key="g2")
    
    # --- TÍNH TOÁN SCENARIO 2 (QUAN TRỌNG) ---
    # 1. Tính chi phí tăng thêm của từng loại KM
    cost_km1 = (get_1 * base_cogs) / buy_1  # Chi phí từ KM cũ
    cost_km2 = (get_2 * base_cogs) / buy_2  # Chi phí từ KM mới
    
    # 2. Tổng giá vốn mới (Cộng dồn tất cả)
    total_cogs_unit_2 = base_cogs + cost_km1 + cost_km2
    
    # 3. Tỷ lệ %
    cogs_pct_2 = total_cogs_unit_2 / price
    net_margin_pct_2 = 1 - (cogs_pct_2 + total_opex_pct)
    
    # Hiển thị cấu trúc giá vốn mới
    st.write("🔻 **Cấu trúc Giá vốn mới/sp:**")
    st.text(f"   {base_cogs:,.0f} (Gốc)")
    st.text(f"+  {cost_km1:,.0f} (Do KM Mua {buy_1} Tặng {get_1})")
    st.text(f"+  {cost_km2:,.0f} (Do KM Mua {buy_2} Tặng {get_2})")
    st.markdown(f"**= {total_cogs_unit_2:,.0f} VNĐ/sp** (Tổng vốn)")

    if net_margin_pct_2 <= 0:
        st.error(f"⛔ QUÁ TẢI! Tổng khuyến mại làm giá vốn lên tới {total_cogs_unit_2:,.0f}đ. Lỗ trên mỗi sp bán ra.")
    else:
        # 4. TÍNH DOANH THU MỤC TIÊU
        required_rev = target_profit / net_margin_pct_2
        diff_rev = required_rev - current_rev
        pct_increase = (diff_rev / current_rev) * 100
        
        st.markdown(f"""
        <div class="result-box">
            <p>Doanh thu mới CẦN ĐẠT:</p>
            <p class="big-number" style="color:#d63031">{required_rev:,.0f} VNĐ</p>
            <p>Cần tăng: <b>{diff_rev:+,.0f} VNĐ</b> ({pct_increase:+.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.latex(r"DoanhThu = \frac{\text{Lợi Nhuận Cũ (" + f"{target_profit:,.0f}" + r")}}{\text{Biên Lãi Mới (" + f"{net_margin_pct_2*100:.1f}\%" + r")}}")

# --- BIỂU ĐỒ ---
st.divider()
chart_df = pd.DataFrame({
    'Loại': ['Doanh Thu', 'Doanh Thu', 'Giá Vốn/SP', 'Giá Vốn/SP'],
    'Kịch bản': ['1. Chỉ KM Cũ', '2. Cộng thêm KM Mới', '1. Chỉ KM Cũ', '2. Cộng thêm KM Mới'],
    'Giá trị': [current_rev, required_rev if net_margin_pct_2 > 0 else 0, total_cogs_unit_1, total_cogs_unit_2]
})

c = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X('Kịch bản', axis=None),
    y=alt.Y('Giá trị', title='Giá trị'),
    color=alt.Color('Kịch bản', scale=alt.Scale(range=['#7f8c8d', '#e74c3c'])),
    column=alt.Column('Loại', header=alt.Header(titleOrient="bottom")),
    tooltip=['Loại', 'Kịch bản', alt.Tooltip('Giá trị', format=',.0f')]
).properties(width=200)

st.altair_chart(c)
