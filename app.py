import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------- تنظیمات صفحه -----------------
st.set_page_config(
    page_title="داشبورد تحلیل کارنامه تحصیلی",
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
    st.error(f"❌ فایل Excel پیدا نشد یا قابل خواندن نیست: {e}")
    st.stop()

# ----------------- Sidebar -----------------
with st.sidebar:
    st.header("⚙️ فیلترها")
    
    selected_base = st.selectbox(
        "انتخاب پایه",
        xls.sheet_names
    )

# ----------------- بارگذاری شیت انتخابی -----------------
@st.cache_data
def load_sheet(sheet_name):
    return pd.read_excel(FILE_NAME, sheet_name=sheet_name)

df = load_sheet(selected_base)

# ----------------- نمایش اطلاعات اولیه -----------------
with st.expander("🔍 مشاهده ساختار فایل"):
    st.write(f"تعداد سطرها: {df.shape[0]}")
    st.write(f"تعداد ستون‌ها: {df.shape[1]}")
    st.write("نام ستون‌ها:", df.columns.tolist())
    st.dataframe(df.head())

# ----------------- شناسایی ستون‌های دروس -----------------
# لیست دروس موجود در فایل
possible_subjects = [
    'قرآن', 'دینی', 'املا', 'انشا', 'ادبیات', 'عربی', 'زبان', 
    'علوم', 'ریاضی', 'اجتماعی', 'تفکر', 'هنر', 'هوش', 'کار و فناوری'
]

# پیدا کردن ستون‌هایی که نام دروس را دارند
subject_columns = []
for col in df.columns:
    col_str = str(col).strip()
    if col_str in possible_subjects:
        subject_columns.append(col_str)

st.info(f"📚 دروس شناسایی شده: {subject_columns}")

if not subject_columns:
    st.error("❌ هیچ ستون درسی شناسایی نشد!")
    st.stop()

# ----------------- محاسبه میانگین نمرات -----------------
# تبدیل نمرات به عددی
for col in subject_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# محاسبه میانگین نمرات برای هر دانش‌آموز
df['میانگین نمرات'] = df[subject_columns].mean(axis=1).round(2)

# حذف سطرهای بدون نمره
df = df.dropna(subset=['میانگین نمرات'])

# ----------------- شناسایی ستون کلاس -----------------
class_keywords = ['کلاس', 'class', 'رده']
class_column = None

for col in df.columns:
    col_str = str(col).strip().lower()
    for keyword in class_keywords:
        if keyword in col_str:
            class_column = col
            break
    if class_column:
        break

if class_column is None:
    # استفاده از اولین ستون غیرعددی
    for col in df.columns:
        if col not in subject_columns and col != 'میانگین نمرات':
            class_column = col
            break

if class_column is None:
    class_column = df.columns[0]

# پاکسازی مقادیر ستون کلاس
df[class_column] = df[class_column].astype(str).str.strip()

# ----------------- انتخاب کلاس -----------------
classes = sorted(df[class_column].dropna().unique())

with st.sidebar:
    selected_class = st.selectbox(
        "انتخاب کلاس",
        ["همه کلاس‌ها"] + list(classes)
    )

if selected_class != "همه کلاس‌ها":
    df_filtered = df[df[class_column] == selected_class].copy()
else:
    df_filtered = df.copy()

# ----------------- شاخص‌های کلیدی -----------------
st.subheader("📊 شاخص‌های کلیدی")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("تعداد دانش‌آموزان", df_filtered.shape[0])

with col2:
    avg_score = df_filtered['میانگین نمرات'].mean()
    st.metric("میانگین نمرات", f"{avg_score:.2f}")

with col3:
    max_score = df_filtered['میانگین نمرات'].max()
    st.metric("بیشترین نمره", f"{max_score:.2f}")

with col4:
    min_score = df_filtered['میانگین نمرات'].min()
    st.metric("کمترین نمره", f"{min_score:.2f}")

st.markdown("---")

# ----------------- تحلیل تک‌تک دروس -----------------
st.subheader("📚 تحلیل تک‌تک دروس")

# میانگین هر درس
subject_avg = {}
for subject in subject_columns:
    subject_avg[subject] = df_filtered[subject].mean()

# تبدیل به DataFrame برای نمایش
subject_df = pd.DataFrame({
    'درس': list(subject_avg.keys()),
    'میانگین نمره': list(subject_avg.values())
}).sort_values('میانگین نمره', ascending=False)

# نمایش در دو ستون
col1, col2 = st.columns(2)

with col1:
    # نمودار میانگین دروس
    fig_subjects = px.bar(
        subject_df,
        x='درس',
        y='میانگین نمره',
        title='میانگین نمره هر درس',
        color='میانگین نمره',
        color_continuous_scale='viridis',
        text_auto='.1f'
    )
    fig_subjects.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_subjects, use_container_width=True)

with col2:
    # جدول میانگین دروس
    st.dataframe(
        subject_df.style.background_gradient(
            subset=['میانگین نمره'], 
            cmap='YlOrRd'
        ),
        use_container_width=True
    )

# ----------------- تب‌ها -----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 توزیع نمرات", "🏫 مقایسه کلاس‌ها", "🥇 رتبه‌بندی دانش‌آموزان", "📋 جدول کامل"]
)

# ---------- تب ۱: توزیع نمرات ----------
with tab1:
    fig_hist = px.histogram(
        df_filtered,
        x='میانگین نمرات',
        nbins=10,
        title='توزیع میانگین نمرات دانش‌آموزان',
        color_discrete_sequence=['#636EFA']
    )
    fig_hist.update_layout(
        xaxis_title='میانگین نمرات',
        yaxis_title='تعداد دانش‌آموزان'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------- تب ۲: مقایسه کلاس‌ها ----------
with tab2:
    avg_by_class = (
        df.groupby(class_column)['میانگین نمرات']
        .mean()
        .reset_index()
        .sort_values('میانگین نمرات', ascending=False)
    )
    
    fig_bar = px.bar(
        avg_by_class,
        x=class_column,
        y='میانگین نمرات',
        title='میانگین نمره هر کلاس',
        text_auto='.2f',
        color='میانگین نمرات',
        color_continuous_scale='plasma'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------- تب ۳: رتبه‌بندی ----------
with tab3:
    # رتبه‌بندی دانش‌آموزان
    ranking_df = df_filtered.copy()
    
    # ایجاد ستون نام کامل
    name_cols = ['نام', 'نام خانوادگی']
    name_columns = []
    for col in ranking_df.columns:
        col_str = str(col).strip()
        if 'نام' in col_str:
            name_columns.append(col)
    
    if len(name_columns) >= 2:
        ranking_df['نام کامل'] = ranking_df[name_columns[0]].astype(str) + ' ' + ranking_df[name_columns[1]].astype(str)
    elif name_columns:
        ranking_df['نام کامل'] = ranking_df[name_columns[0]].astype(str)
    else:
        ranking_df['نام کامل'] = 'دانش‌آموز ' + (ranking_df.index + 1).astype(str)
    
    # مرتب‌سازی بر اساس نمره
    ranking_df = ranking_df.sort_values('میانگین نمرات', ascending=False)
    ranking_df['رتبه'] = range(1, len(ranking_df) + 1)
    
    # انتخاب ستون‌های نمایش
    display_cols = ['رتبه', 'نام کامل', 'میانگین نمرات'] + subject_columns[:5]
    st.dataframe(
        ranking_df[display_cols].head(20),
        use_container_width=True
    )
    
    # نمودار رتبه‌بندی
    fig_rank = px.bar(
        ranking_df.head(10),
        x='نام کامل',
        y='میانگین نمرات',
        title='ده دانش‌آموز برتر',
        color='میانگین نمرات',
        text='میانگین نمرات',
        color_continuous_scale='RdYlGn'
    )
    fig_rank.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_rank, use_container_width=True)

# ---------- تب ۴: جدول کامل ----------
with tab4:
    # انتخاب ستون‌های مهم برای نمایش
    important_cols = [class_column]
    for col in ['نام', 'نام خانوادگی', 'میانگین نمرات']:
        if col in df_filtered.columns:
            important_cols.append(col)
    
    display_df = df_filtered[important_cols + subject_columns]
    st.dataframe(display_df, use_container_width=True)

# ----------------- دانلود خروجی -----------------
st.markdown("---")
st.subheader("📥 خروجی")

col1, col2 = st.columns(2)

with col1:
    # دانلود داده‌های فیلتر شده
    csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "⬇️ دانلود داده‌های فیلتر شده (CSV)",
        data=csv,
        file_name=f"کارنامه_{selected_base}_{selected_class}.csv",
        mime="text/csv",
        help="دانلود اطلاعات کامل دانش‌آموزان"
    )

with col2:
    # دانلود خلاصه آمار
    summary_data = {
        'کلاس': [selected_class],
        'تعداد دانش‌آموز': [len(df_filtered)],
        'میانگین کل': [avg_score],
        'بیشترین نمره': [max_score],
        'کمترین نمره': [min_score]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_csv = summary_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "⬇️ دانلود خلاصه آمار (CSV)",
        data=summary_csv,
        file_name=f"خلاصه_آمار_{selected_base}_{selected_class}.csv",
        mime="text/csv",
        help="دانلود خلاصه آمار کلاس"
    )

st.success("✅ داشبورد با موفقیت ساخته شد!")
