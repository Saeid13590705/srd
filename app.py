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

# ----------------- بارگذاری فایل -----------------
FILE_NAME = "14040919_1300.xlsx"

@st.cache_data
def load_excel(file_name):
    return pd.ExcelFile(file_name)

xls = load_excel(FILE_NAME)

# ----------------- انتخاب پایه -----------------
with st.sidebar:
    st.header("⚙️ فیلترها")

    selected_base = st.selectbox(
        "انتخاب پایه",
        xls.sheet_names
    )

df = pd.read_excel(xls, sheet_name=selected_base)

# ----------------- بررسی ستون کلاس -----------------
if "کلاس" not in df.columns:
    st.error("ستون «کلاس» در فایل وجود ندارد")
    st.stop()

# ----------------- انتخاب کلاس -----------------
classes = sorted(df["کلاس"].dropna().unique())

with st.sidebar:
    selected_class = st.selectbox(
        "انتخاب کلاس",
        ["همه کلاس‌ها"] + list(classes)
    )

if selected_class != "همه کلاس‌ها":
    df = df[df["کلاس"] == selected_class]

# ----------------- بررسی ستون نمره -----------------
if "نمره" not in df.columns:
    st.error("ستون «نمره» در فایل وجود ندارد")
    st.stop()

df["نمره"] = pd.to_numeric(df["نمره"], errors="coerce")

# ----------------- شاخص‌های کلیدی -----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("تعداد دانش‌آموزان", df.shape[0])

with col2:
    st.metric("میانگین نمره", round(df["نمره"].mean(), 2))

with col3:
    st.metric("بیشترین نمره", df["نمره"].max())

st.markdown("---")

# ----------------- نمودارها -----------------
tab1, tab2, tab3 = st.tabs(["📈 تحلیل نمرات", "🏫 مقایسه کلاس‌ها", "📋 جدول داده"])

with tab1:
    fig_hist = px.histogram(
        df,
        x="نمره",
        nbins=10,
        title="توزیع نمرات"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    df_all = pd.read_excel(xls, sheet_name=selected_base)

    avg_by_class = (
        df_all.groupby("کلاس")["نمره"]
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

with tab3:
    st.dataframe(df, use_container_width=True)

# ----------------- دانلود خروجی -----------------
st.markdown("---")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ دانلود فایل CSV این فیلتر",
    data=csv,
    file_name="report_filtered.csv",
    mime="text/csv"
)

st.success("✅ داشبورد با موفقیت ساخته شد")
