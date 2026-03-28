import streamlit as st
from backend import load_data, recommend_menu

# --- UI CONFIG ---
st.set_page_config(page_title="กินไรดี AI", page_icon="spoon.png")

# --- LOAD DATA ---
df = load_data()

if df.empty:
    st.error("ไม่พบ API Key หรือ โหลด CSV ไม่ได้")

st.title("กินไรดี AI By เจ๊ส้มตามสั่ง")
st.write("พิมพ์สิ่งที่อยากกิน เช่น: *อยากกินเมนูหมู งบ 50 ไม่เผ็ด*")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดง chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# รับ input
if prompt := st.chat_input("วันนี้อยากกินอะไรดี?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("กำลังเลือกเมนู..."):
            result = recommend_menu(prompt, df)
            final_text = ""
            spicy_map = {"none": "ไม่เผ็ด", "medium": "ปานกลาง", "high": "เผ็ด"}

            if result and "recommendations" in result:
                if len(result["recommendations"]) == 0:
                    st.warning("กรุณาพิมพ์เกี่ยวกับอาหาร")
                    final_text = "กรุณาพิมพ์เกี่ยวกับอาหาร"
                else:
                    for item in result["recommendations"]:
                        menu_name = item.get("name")
                        menu_row = df[df["name"] == menu_name]

                        if not menu_row.empty:
                            row = menu_row.iloc[0]
                            st.success(row['name'])
                            st.write(f"หมวดหมู่: {row['category']}")
                            st.write(f"ราคา: {row['price']} บาท | {row['calories']} kcal")
                            st.write(f"ความเผ็ด: {spicy_map.get(row['spiciness'], row['spiciness'])}")
                            st.write(f"ผัก: {row['vegetables']}")
                            st.write(f"เครื่องปรุง: {row['seasoning']}")
                            st.write(f"เนื้อสัตว์: {row['protein']}")
                            st.markdown("---")
                            final_text += f"{row['name']}\n"
                        else:
                            st.warning(f"{menu_name} ไม่พบข้อมูล")
                    
                    if final_text == "":
                        final_text = "ไม่พบเมนูในระบบ"
            else:
                final_text = f"ขออภัย AI ไม่สามารถประมวลผลได้: {result.get('error', '')}"

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_text
            })

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"เมนูทั้งหมด: {len(df)} รายการ")
    if not df.empty:
        menu_list = sorted(df["name"].dropna().unique().tolist())
        selected_menu = st.selectbox("เลือกดูเมนู", menu_list)
        if selected_menu:
            row = df[df["name"] == selected_menu].iloc[0]
            st.write(f"ราคา: {row['price']} บาท")
            st.write(f"แคลอรี่: {row['calories']} kcal")
            st.write(f"ความเผ็ด: {row['spiciness']}")
            st.write(f"protein: {row['protein']}")

    if st.button("ล้างแชท", use_container_width=True):
        st.session_state.messages = []
        st.rerun()