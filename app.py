import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- تنظیمات صفحه -----------------
st.set_page_config(
    page_title="داشبورد کارنامه تحصیلی",
    layout="wide"
)

st.title("📊 داشبورد تحلیل کارنامه ترم اول ۱۴۰۴")
st.markdown("---")

# ----------------- فایل -----------------
FILE_NAME = "14040919_1300.xlsx"

# ----------------- بارگذاری لیست شیت‌ها -----------------
try:
    xls = pd.ExcelFile(FILE_NAME)
except Exception as e:
    st.error("❌ فایل Excel پیدا نشد یا قابل خواندن نیست")
    st.stop()

# ----------------- Sidebar -----------------
with st.sidebar:
    st.header("⚙️ فیلترها")

    selected_base = st.selectbox(
        "انتخاب پایه",
        xls.sheet_names
    )

# ----------------- بارگذاری شیت انتخابی (cache امن) -----------------
@st.cache_data
def load_sheet(sheet_name):
    return pd.read_excel(FILE_NAME, sheet_name=sheet_name)

df = load_sheet(selected_base)

# ----------------- بررسی ستون‌ها -----------------
if "کلاس" not in df.columns:
    st.error("❌ ستون «کلاس» در فایل وجود ندارد")
    st.stop()

if "نمره" not in df.columns:
    st.error("❌ ستون «نمره» در فایل وجود ندارد")
    st.stop()

df["نمره"] = pd.to_numeric(df["نمره"], errors="coerce")

# ----------------- انتخاب کلاس -----------------
classes = sorted(df["کلاس"].dropna().unique())

with st.sidebar:
    selected_class = st.selectbox(
        "انتخاب کلاس",
        ["همه کلاس‌ها"] + list(classes)
    )

if selected_class != "همه کلاس‌ها":
    df_filtered = df[df["کلاس"] == selected_class]
else:
    df_filtered = df.copy()

# ----------------- شاخص‌های کلیدی -----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("تعداد دانش‌آموزان", df_filtered.shape[0])

with col2:
    st.metric("میانگین نمره", round(df_filtered["نمره"].mean(), 2))

with col3:
    st.metric("بیشترین نمره", df_filtered["نمره"].max())

st.markdown("---")

# ----------------- تب‌ها -----------------
tab1, tab2, tab3 = st.tabs(
    ["📈 تحلیل نمرات", "🏫 مقایسه کلاس‌ها", "📋 جدول داده"]
)

# ---------- تب ۱: توزیع نمرات ----------
with tab1:
    fig_hist = px.histogram(
        df_filtered,
        x="نمره",
        nbins=10,
        title="توزیع نمرات"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------- تب ۲: مقایسه کلاس‌ها ----------
with tab2:
    avg_by_class = (
        df.groupby("کلاس")["نمره"]
        .mean()
        .reset_index()
        .sort_values("نمره", ascending=False)
    )

    fig_bar = px.bar(
        avg_by_class,
        x="کلاس",
        y="نمره",
        title="میانگین نمره هر کلاس",
        text_auto=".2f"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------- تب ۳: جدول ----------
with tab3:
    st.dataframe(df_filtered, use_container_width=True)

# ----------------- دانلود خروجی -----------------
st.markdown("---")

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ دانلود داده‌های فیلتر شده (CSV)",
    data=csv,
    file_name="report_filtered.csv",
    mime="text/csv"
)

st.success("✅ داشبورد با موفقیت ساخته شد")
