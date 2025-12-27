import streamlit as st
import pandas as pd
import altair as alt

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Công cụ Tính Hòa Vốn & Lợi Nhuận",
    page_icon="💼",
    layout="wide"
)

# --- CSS TÙY CHỈNH (Làm đẹp giao diện) ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .success { color: #28a745; font-weight: bold; }
    .danger { color: #dc3545; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ ---
st.title("💼 Phân Tích Điểm Hòa Vốn Chiến Dịch Khuyến Mại")
st.markdown("*(Công cụ hỗ trợ ra quyết định kinh doanh - Dành cho SME)*")
st.divider()

# --- CỘT NHẬP LIỆU (SIDEBAR) ---
with st.sidebar:
    st.header("1. Thông số Sản phẩm")
    price = st.number_input("Giá bán niêm yết (VNĐ)", value=100000, step=1000)
    cogs = st.number_input("Giá vốn hàng bán (COGS) (VNĐ)", value=60000, step=1000)
    current_vol = st.number_input("Sản lượng bán trung bình (tháng)", value=1000, step=10)
    
    st.header("2. Kịch bản Khuyến mại")
    st.info("Nhập chi phí tăng thêm khi làm KM (VD: Quà tặng, bao bì, voucher...)")
    promo_cost = st.number_input("Chi phí KM/sản phẩm (VNĐ)", value=10000, step=1000)

# --- XỬ LÝ LOGIC ---
old_margin = price - cogs
new_margin = price - (cogs + promo_cost)

# --- HIỂN THỊ KẾT QUẢ ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📊 Kết quả tính toán")
    
    # Check lỗ lãi
    if new_margin <= 0:
        st.error(f"❌ CẢNH BÁO ĐỎ: Bạn đang lỗ {abs(new_margin):,.0f} VNĐ trên mỗi sản phẩm bán ra!")
        st.stop() # Dừng chương trình nếu lỗ
        
    req_ratio = old_margin / new_margin
    target_vol = current_vol * req_ratio
    add_vol = target_vol - current_vol
    growth_pct = (add_vol / current_vol) * 100

    # Hiển thị Metric
    m1, m2 = st.columns(2)
    m1.metric("Biên Lợi Nhuận Cũ", f"{old_margin:,.0f} đ")
    m2.metric("Biên Lợi Nhuận Mới", f"{new_margin:,.0f} đ", delta=f"-{promo_cost:,.0f} đ", delta_color="inverse")
    
    st.divider()
    
    st.markdown(f"""
    Để giữ nguyên tổng lợi nhuận là **{(current_vol * old_margin):,.0f} VNĐ**, bạn cần đạt:
    """)
    
    st.success(f"🎯 SẢN LƯỢNG MỤC TIÊU: {target_vol:,.0f} sản phẩm")
    st.warning(f"📈 Cần bán thêm: {add_vol:,.0f} sp (+{growth_pct:.1f}%)")

with col2:
    st.subheader("📈 Mô phỏng Lợi Nhuận")
    # Tạo dữ liệu giả lập để vẽ biểu đồ
    # Kịch bản: Volume tăng từ 0% đến 100%
    data = []
    for pct in range(0, int(growth_pct * 1.5), 5):
        vol_sim = current_vol * (1 + pct/100)
        profit_sim = vol_sim * new_margin
        is_breakeven = profit_sim >= (current_vol * old_margin)
        data.append({
            "Tăng trưởng (%)": pct,
            "Lợi nhuận dự kiến (VNĐ)": profit_sim,
            "Trạng thái": "Có lãi hơn cũ" if is_breakeven else "Thấp hơn cũ"
        })
    
    df_chart = pd.DataFrame(data)
    
    # Đường kẻ ngang tham chiếu (Lợi nhuận cũ)
    base_profit_rule = alt.Chart(pd.DataFrame({'y': [current_vol * old_margin]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')
    
    # Biểu đồ cột
    bar_chart = alt.Chart(df_chart).mark_bar().encode(
        x='Tăng trưởng (%):O',
        y='Lợi nhuận dự kiến (VNĐ):Q',
        color=alt.Color('Trạng thái', scale=alt.Scale(domain=['Thấp hơn cũ', 'Có lãi hơn cũ'], range=['#ffcccb', '#90ee90'])),
        tooltip=['Tăng trưởng (%)', 'Lợi nhuận dự kiến (VNĐ)']
    )
    
    st.altair_chart(bar_chart + base_profit_rule, use_container_width=True)
    st.caption("Đường gạch đỏ: Mức lợi nhuận gốc cần đạt được.")

# --- KẾT LUẬN TƯ VẤN (Phần "ăn tiền" khi phỏng vấn) ---
st.divider()
st.subheader("💡 Đề xuất từ Phân tích dữ liệu")

if growth_pct > 50:
    st.error(f"RỦI RO CAO: Bạn cần tăng trưởng tới {growth_pct:.1f}%. Hãy cân nhắc kỹ xem thị trường có hấp thụ nổi lượng hàng này không?")
elif growth_pct > 20:
    st.warning(f"RỦI RO TRUNG BÌNH: Cần tăng {growth_pct:.1f}%. Cần phối hợp chặt chẽ với Marketing để đẩy hàng.")
else:
    st.success(f"KHẢ THI: Chỉ cần tăng {growth_pct:.1f}%. Đây là mức tăng trưởng có thể đạt được dễ dàng.")
