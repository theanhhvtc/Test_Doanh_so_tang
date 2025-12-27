import streamlit as st
import pandas as pd
import altair as alt

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tính Doanh Thu Hòa Vốn", page_icon="💰")

# CSS tùy chỉnh để làm nổi bật số liệu quan trọng
st.markdown("""
<style>
    .big-metric { font-size: 30px !important; color: #0068c9; font-weight: bold; }
    .fixed-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #d6d6d6; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Phân Tích Doanh Thu Mục Tiêu")
st.markdown("*(Dựa trên nguyên tắc bảo toàn lợi nhuận)*")

# --- PHẦN 1: CẤU HÌNH CƠ BẢN (Ẩn gọn gàng) ---
with st.expander("⚙️ Cấu hình Giá & Giá vốn (Nhấn để sửa)", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("Giá bán niêm yết (VNĐ)", value=100000, step=1000)
    with c2:
        cogs = st.number_input("Giá vốn hàng bán (VNĐ)", value=50000, step=1000)

# --- PHẦN 2: NHẬP LIỆU THEO YÊU CẦU ---
st.header("1. Nhập liệu")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.markdown('<div class="fixed-box">', unsafe_allow_html=True)
    st.markdown("#### 📌 Kịch bản Cũ")
    # Doanh thu fix cứng 550tr theo yêu cầu
    old_revenue = st.number_input("Doanh thu cũ (VNĐ)", value=550000000, disabled=True)
    st.caption("Con số này được cố định.")
    
    # Khuyến mại 1 cho phép tự điền
    promo_1 = st.number_input("Khuyến mại 1 (VNĐ/sp)", value=0, step=1000, help="Chi phí KM đang áp dụng hiện tại")
    st.markdown('</div>', unsafe_allow_html=True)

with col_input2:
    st.markdown("#### ⚡ Kịch bản Mới")
    st.write("Nhập mức khuyến mại mới để xem doanh thu cần đạt:")
    
    # Khuyến mại 2 - Biến số chính
    promo_2 = st.number_input("Khuyến mại 2 (VNĐ/sp)", value=5000, step=1000)

# --- PHẦN 3: TÍNH TOÁN LOGIC ---
# Lợi nhuận gộp đơn vị (Margin)
base_margin = price - cogs
margin_1 = base_margin - promo_1
margin_2 = base_margin - promo_2

# Tính toán
if margin_2 <= 0:
    st.divider()
    st.error(f"⛔ CẢNH BÁO: Với mức KM 2 là {promo_2:,.0f}đ, bạn đang bán LỖ hoặc không có lãi. Không thể tính doanh thu mục tiêu.")
else:
    # Công thức: Rev2 = Rev1 * (Margin1 / Margin2)
    ratio = margin_1 / margin_2
    target_revenue = old_revenue * ratio
    
    diff_rev = target_revenue - old_revenue
    pct_change = (diff_rev / old_revenue) * 100

    # --- PHẦN 4: HIỂN THỊ KẾT QUẢ ---
    st.divider()
    st.header("2. Kết quả Tính toán")
    
    res_col1, res_col2 = st.columns([1.5, 1])
    
    with res_col1:
        st.write("Để đạt cùng mức lợi nhuận như cũ, Doanh thu mới phải là:")
        st.markdown(f'<p class="big-metric">{target_revenue:,.0f} VNĐ</p>', unsafe_allow_html=True)
        
        if diff_rev > 0:
            st.warning(f"📈 Bạn cần tăng doanh thu thêm: **{diff_rev:,.0f} VNĐ** (+{pct_change:.1f}%)")
        elif diff_rev < 0:
            st.success(f"📉 Bạn có thể giảm doanh thu: **{abs(diff_rev):,.0f} VNĐ** ({pct_change:.1f}%)")
        else:
            st.info("Doanh thu giữ nguyên.")

    with res_col2:
        # So sánh Lợi nhuận đơn vị
        st.write("**So sánh Lãi trên 1 sản phẩm:**")
        st.write(f"- Lúc KM 1: **{margin_1:,.0f}** đ")
        st.write(f"- Lúc KM 2: **{margin_2:,.0f}** đ")
        
        # Logic giải thích
        if margin_1 > margin_2:
            st.caption(f"Do lãi giảm **{margin_1 - margin_2:,.0f}đ/sp**, bạn phải bán nhiều hàng hơn -> Doanh thu phải tăng.")
        elif margin_1 < margin_2:
             st.caption(f"Do lãi tăng, áp lực doanh thu giảm đi.")

    # --- BIỂU ĐỒ TRỰC QUAN ---
    st.write("### 📊 Biểu đồ so sánh")
    chart_data = pd.DataFrame({
        'Kịch bản': ['Doanh thu Cũ', 'Doanh thu Mới (Target)'],
        'Giá trị (VNĐ)': [old_revenue, target_revenue],
        'Color': ['#bdc3c7', '#3498db']
    })
    
    c = alt.Chart(chart_data).mark_bar().encode(
        x='Kịch bản',
        y='Giá trị (VNĐ)',
        color=alt.Color('Color', scale=None),
        tooltip=['Kịch bản', alt.Tooltip('Giá trị (VNĐ)', format=',.0f')]
    ).properties(height=300)
    
    st.altair_chart(c, use_container_width=True)
