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

st.info(f"📚 دروس شناسایی شده ({len(subject_columns)} درس): {subject_columns}")

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
df_clean = df.dropna(subset=['میانگین نمرات']).copy()

# ----------------- شناسایی ستون کلاس -----------------
class_keywords = ['کلاس', 'class', 'رده']
class_column = None

for col in df_clean.columns:
    col_str = str(col).strip().lower()
    for keyword in class_keywords:
        if keyword in col_str:
            class_column = col
            break
    if class_column:
        break

if class_column is None:
    # استفاده از اولین ستون غیرعددی
    for col in df_clean.columns:
        if col not in subject_columns and col != 'میانگین نمرات':
            class_column = col
            break

if class_column is None:
    class_column = df_clean.columns[0]

# پاکسازی مقادیر ستون کلاس
df_clean[class_column] = df_clean[class_column].astype(str).str.strip()

# ----------------- انتخاب کلاس -----------------
classes = sorted(df_clean[class_column].dropna().unique())

with st.sidebar:
    selected_class = st.selectbox(
        "انتخاب کلاس",
        ["همه کلاس‌ها"] + list(classes)
    )

if selected_class != "همه کلاس‌ها":
    df_filtered = df_clean[df_clean[class_column] == selected_class].copy()
else:
    df_filtered = df_clean.copy()

# ----------------- نمایش اطلاعات اولیه -----------------
with st.expander("📄 مشاهده ساختار فایل"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("تعداد کل سطرها", df.shape[0])
    with col2:
        st.metric("تعداد سطرهای تمیز", df_clean.shape[0])
    with col3:
        st.metric("تعداد دروس", len(subject_columns))
    
    st.write("نمونه‌ای از داده‌ها:")
    st.dataframe(df_filtered.head())

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
    # جدول میانگین دروس (بدون background_gradient)
    st.write("میانگین نمره هر درس:")
    st.dataframe(
        subject_df.round(2),
        use_container_width=True,
        hide_index=True
    )

# ----------------- تب‌ها -----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 توزیع نمرات", "🏫 مقایسه کلاس‌ها", "🥇 رتبه‌بندی", "📋 جدول کامل"]
)

# ---------- تب ۱: توزیع نمرات ----------
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            df_filtered,
            x='میانگین نمرات',
            nbins=10,
            title='توزیع میانگین نمرات',
            color_discrete_sequence=['#636EFA']
        )
        fig_hist.update_layout(
            xaxis_title='میانگین نمرات',
            yaxis_title='تعداد دانش‌آموزان'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        fig_box = px.box(
            df_filtered,
            y='میانگین نمرات',
            title='پراکندگی نمرات',
            points='all'
        )
        st.plotly_chart(fig_box, use_container_width=True)

# ---------- تب ۲: مقایسه کلاس‌ها ----------
with tab2:
    avg_by_class = (
        df_clean.groupby(class_column)['میانگین نمرات']
        .agg(['mean', 'count', 'min', 'max'])
        .round(2)
        .reset_index()
        .sort_values('mean', ascending=False)
    )
    
    avg_by_class.columns = ['کلاس', 'میانگین', 'تعداد', 'کمترین', 'بیشترین']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(
            avg_by_class,
            x='کلاس',
            y='میانگین',
            title='میانگین نمره هر کلاس',
            text='میانگین',
            color='میانگین',
            color_continuous_scale='plasma'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.write("آمار کلاس‌ها:")
        st.dataframe(avg_by_class, use_container_width=True, hide_index=True)

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
    
    # جدول رتبه‌بندی
    st.write("رتبه‌بندی دانش‌آموزان:")
    display_cols = ['رتبه', 'نام کامل', 'میانگین نمرات'] + subject_columns[:3]
    st.dataframe(
        ranking_df[display_cols],
        use_container_width=True,
        hide_index=True
    )
    
    # نمایش ۵ نفر برتر
    st.write("🏆 پنج دانش‌آموز برتر:")
    top_5 = ranking_df.head(5)
    fig_top = px.bar(
        top_5,
        x='نام کامل',
        y='میانگین نمرات',
        title='پنج دانش‌آموز برتر',
        text='میانگین نمرات',
        color='میانگین نمرات',
        color_continuous_scale='RdYlGn'
    )
    fig_top.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_top, use_container_width=True)

# ---------- تب ۴: جدول کامل ----------
with tab4:
    st.write(f"داده‌های کلاس: {selected_class}")
    
    # انتخاب ستون‌های مهم برای نمایش
    display_cols = [class_column, 'میانگین نمرات']
    
    # اضافه کردن ستون‌های نام
    for col in ['نام', 'نام خانوادگی']:
        if col in df_filtered.columns:
            display_cols.append(col)
    
    # اضافه کردن ۵ درس اول
    display_cols += subject_columns[:5]
    
    st.dataframe(
        df_filtered[display_cols],
        use_container_width=True
    )

# ----------------- دانلود خروجی -----------------
st.markdown("---")
st.subheader("📥 دانلود خروجی")

col1, col2, col3 = st.columns(3)

with col1:
    # دانلود داده‌های فیلتر شده
    csv_data = df_filtered.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "⬇️ دانلود داده‌های فیلتر شده",
        data=csv_data,
        file_name=f"کارنامه_{selected_base}_{selected_class}.csv",
        mime="text/csv"
    )

with col2:
    # دانلود آمار دروس
    subject_stats_csv = subject_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "⬇️ دانلود آمار دروس",
        data=subject_stats_csv,
        file_name=f"آمار_دروس_{selected_base}_{selected_class}.csv",
        mime="text/csv"
    )

with col3:
    # دانلود رتبه‌بندی
    ranking_csv = ranking_df[['رتبه', 'نام کامل', 'میانگین نمرات'] + subject_columns].to_csv(
        index=False, encoding='utf-8-sig'
    )
    st.download_button(
        "⬇️ دانلود رتبه‌بندی",
        data=ranking_csv,
        file_name=f"رتبه‌بندی_{selected_base}_{selected_class}.csv",
        mime="text/csv"
    )

# ----------------- نکات پایانی -----------------
st.markdown("---")
with st.expander("ℹ️ راهنمای استفاده"):
    st.markdown("""
    ### نحوه استفاده از داشبورد:
    
    1. **انتخاب پایه**: در نوار کناری، پایه مورد نظر را انتخاب کنید
    2. **انتخاب کلاس**: می‌توانید یک کلاس خاص یا "همه کلاس‌ها" را انتخاب کنید
    3. **تحلیل داده‌ها**: داده‌ها در ۴ تب مختلف تحلیل شده‌اند:
       - **تب ۱**: توزیع نمرات و نمودار جعبه‌ای
       - **تب ۲**: مقایسه عملکرد کلاس‌ها
       - **تب ۳**: رتبه‌بندی دانش‌آموزان
       - **تب ۴**: جدول کامل داده‌ها
    4. **دانلود**: می‌توانید نتایج را در قالب CSV دانلود کنید
    
    ### نکات:
    - میانگین نمرات از میانگین تمام دروس محاسبه می‌شود
    - مقادیر خالی در محاسبات در نظر گرفته نمی‌شوند
    - برای بهترین تجربه، از مرورگرهای مدرن استفاده کنید
    """)

st.success("✅ داشبورد با موفقیت بارگذاری شد!")
