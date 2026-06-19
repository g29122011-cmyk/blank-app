import streamlit as st
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta


st.set_page_config(
    page_title="Мониторинг проблемного НДС",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
        border: 1px solid #e9edf3;
        padding: 14px 16px;
        border-radius: 16px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #667085;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #101828;
        font-weight: 700;
    }

    div[data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f5f7fa;
        border-radius: 12px 12px 0 0;
        padding: 10px 18px;
        border: 1px solid #e4e7ec;
        height: 52px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #175cd3;
        color: #175cd3;
        font-weight: 700;
    }

    div[data-testid="stDownloadButton"] > button {
        border-radius: 12px;
        border: 1px solid #d0d5dd;
        background: #ffffff;
        font-weight: 600;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        border-color: #175cd3;
        color: #175cd3;
    }

    .summary-card {
        background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
        border: 1px solid #e9edf3;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        min-height: 120px;
    }

    .summary-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #344054;
        margin-bottom: 8px;
    }

    .summary-text {
        font-size: 0.95rem;
        color: #475467;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# ТЕСТОВЫЕ ДАННЫЕ
# =========================================================
@st.cache_data
def create_demo_data():
    random.seed(42)

    companies = [
        "ООО Еврохим-Волгакалий",
        "АО НАК Азот",
        "ООО НРСС",
        "АО Еврохим-УКК",
        "АО БМЗ",
        "АО ЕХСЗ",
        "ООО ПГ Фосфорит",
        "ООО ГРК",
        "Ковдорский ГОК",
        "АО Невиномысский Азот"
    ]

    responsibles = [
        "Иванов И.И.",
        "Петрова А.С.",
        "Смирнов Д.В.",
        "Кузнецова Е.Н.",
        "Орлов М.П.",
        "Соколова Т.А."
    ]

    statuses = [
        "Новый кейс",
        "В работе",
        "Ожидает документы",
        "Эскалация",
        "Критичный риск",
        "Завершено"
    ]

    reasons = [
        "Расхождение по НДС",
        "Запрос дополнительных документов",
        "Подозрительная цепочка контрагентов",
        "Нагрузка на оборотный контур",
        "Риск налоговой претензии",
        "Несоответствие периода учета"
    ]

    periods = [
        "Q1 2026",
        "Q2 2026",
        "Q3 2026",
        "Q4 2026"
    ]

    base_date = date.today() - timedelta(days=180)

    rows = []
    for _ in range(260):
        status = random.choices(
            statuses,
            weights=[16, 28, 20, 14, 8, 14],
            k=1
        )[0]

        amount = round(random.uniform(2.5, 85.0), 1)

        if status in ["Эскалация", "Критичный риск"]:
            amount = round(amount * random.uniform(1.4, 2.2), 1)

        rows.append({
            "Дата": base_date + timedelta(days=random.randint(0, 180)),
            "Компания": random.choice(companies),
            "Период": random.choice(periods),
            "Причина": random.choice(reasons),
            "Ответственный": random.choice(responsibles),
            "Статус": status,
            "Сумма НДС. млн.руб.": amount
        })

    return pd.DataFrame(rows)


data = create_demo_data()
data["Дата"] = pd.to_datetime(data["Дата"])


# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================
def to_csv_download(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def fmt_mln(x):
    return f"{x:,.1f}"


def fmt_delta_abs(curr, prev):
    diff = curr - prev
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:,.1f}"


def status_cell_style(val):
    if pd.isna(val):
        return ""
    val_str = str(val).lower()

    if "эскала" in val_str or "крит" in val_str or "risk" in val_str:
        return "background-color: #FDECEC; color: #B42318; font-weight: 600;"
    if "в работе" in val_str:
        return "background-color: #FFF4E5; color: #B54708; font-weight: 600;"
    if "ожида" in val_str:
        return "background-color: #EEF4FF; color: #175CD3; font-weight: 600;"
    if "заверш" in val_str:
        return "background-color: #ECFDF3; color: #027A48; font-weight: 600;"
    if "нов" in val_str:
        return "background-color: #F2F4F7; color: #344054; font-weight: 600;"
    return "background-color: #F2F4F7; color: #344054;"


def style_registry(df: pd.DataFrame):
    return (
        df.style
        .format({"Сумма НДС. млн.руб.": "{:,.1f}"}, na_rep="-")
        .map(status_cell_style, subset=["Статус"])
    )


def build_vat_debt_bar(df: pd.DataFrame):
    if df.empty:
        return None

    company_reason_debt = (
        df.groupby(["Компания", "Причина"], as_index=False)
        .agg(Сумма_НДС=("Сумма НДС. млн.руб.", "sum"))
    )

    company_order = (
        company_reason_debt.groupby("Компания", as_index=False)["Сумма_НДС"]
        .sum()
        .sort_values("Сумма_НДС", ascending=True)["Компания"]
        .tolist()
    )

    totals = (
        company_reason_debt.groupby("Компания", as_index=False)["Сумма_НДС"]
        .sum()
        .sort_values("Сумма_НДС", ascending=True)
    )

    chart_height = max(480, len(company_order) * 44)

    color_map = {
        "Расхождение по НДС": "#175CD3",
        "Запрос дополнительных документов": "#36B37E",
        "Подозрительная цепочка контрагентов": "#F79009",
        "Нагрузка на оборотный контур": "#7A5AF8",
        "Риск налоговой претензии": "#F04438",
        "Несоответствие периода учета": "#12B76A",
    }

    fig = px.bar(
        company_reason_debt,
        x="Сумма_НДС",
        y="Компания",
        color="Причина",
        orientation="h",
        category_orders={"Компания": company_order},
        title="Задолженность по НДС по предприятиям",
        color_discrete_map=color_map
    )

    fig.add_trace(
        go.Scatter(
            x=totals["Сумма_НДС"],
            y=totals["Компания"],
            mode="text",
            text=[f"{v:,.1f}" for v in totals["Сумма_НДС"]],
            textposition="middle right",
            showlegend=False,
            hoverinfo="skip"
        )
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Причина: %{fullData.name}<br>Сумма НДС: %{x:.1f} млн руб.<extra></extra>"
    )

    fig.update_layout(
        barmode="stack",
        height=chart_height,
        margin=dict(l=20, r=90, t=60, b=20),
        xaxis_title="Сумма задолженности НДС, млн руб.",
        yaxis_title="Предприятие",
        legend_title="Причина",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig.update_xaxes(showgrid=True, gridcolor="#EAECF0", zeroline=False)
    fig.update_yaxes(showgrid=False)

    return fig


# =========================================================
# ЗАГОЛОВОК
# =========================================================
st.title("Мониторинг проблемного НДС")
st.caption("Executive dashboard для анализа проблемного НДС")


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("Фильтры")

    min_date = data["Дата"].min().date()
    max_date = data["Дата"].max().date()

    selected_dates = st.date_input(
        "Период",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        date_filtered_data = data[
            (data["Дата"].dt.date >= start_date) &
            (data["Дата"].dt.date <= end_date)
        ].copy()
    else:
        date_filtered_data = data.copy()
        start_date = min_date
        end_date = max_date

    companies = ["Все компании"] + sorted(date_filtered_data["Компания"].dropna().unique().tolist())
    selected_company = st.selectbox("Компания", companies)

    temp_for_status = date_filtered_data.copy()
    if selected_company != "Все компании":
        temp_for_status = temp_for_status[temp_for_status["Компания"] == selected_company]

    statuses = sorted(temp_for_status["Статус"].dropna().unique().tolist())
    selected_statuses = st.multiselect(
        "Статус",
        options=statuses,
        default=statuses
    )

    temp_for_responsible = temp_for_status.copy()
    if selected_statuses:
        temp_for_responsible = temp_for_responsible[
            temp_for_responsible["Статус"].isin(selected_statuses)
        ]

    responsible_options = sorted(temp_for_responsible["Ответственный"].dropna().unique().tolist())
    selected_responsibles = st.multiselect(
        "Ответственный",
        options=responsible_options,
        default=responsible_options
    )


# =========================================================
# ТЕКУЩИЙ ПЕРИОД
# =========================================================
filtered_data = date_filtered_data.copy()

if selected_company != "Все компании":
    filtered_data = filtered_data[filtered_data["Компания"] == selected_company]

if selected_statuses:
    filtered_data = filtered_data[filtered_data["Статус"].isin(selected_statuses)]
else:
    filtered_data = filtered_data.iloc[0:0]

if selected_responsibles:
    filtered_data = filtered_data[filtered_data["Ответственный"].isin(selected_responsibles)]
else:
    filtered_data = filtered_data.iloc[0:0]


# =========================================================
# ПРЕДЫДУЩИЙ ПЕРИОД
# =========================================================
period_days = (end_date - start_date).days + 1
prev_end_date = start_date - pd.Timedelta(days=1)
prev_start_date = prev_end_date - pd.Timedelta(days=period_days - 1)

previous_data = data[
    (data["Дата"].dt.date >= prev_start_date) &
    (data["Дата"].dt.date <= prev_end_date)
].copy()

if selected_company != "Все компании":
    previous_data = previous_data[previous_data["Компания"] == selected_company]

if selected_statuses:
    previous_data = previous_data[previous_data["Статус"].isin(selected_statuses)]

if selected_responsibles:
    previous_data = previous_data[previous_data["Ответственный"].isin(selected_responsibles)]


# =========================================================
# HEADER ACTIONS
# =========================================================
top1, top2, top3 = st.columns([2.2, 1.2, 1])

with top1:
    st.markdown("### Сводка для руководителя")

with top2:
    st.caption(f"Текущий период: {start_date} — {end_date}")
    st.caption(f"Предыдущий период: {prev_start_date} — {prev_end_date}")

with top3:
    st.download_button(
        label="Скачать CSV",
        data=to_csv_download(filtered_data),
        file_name="monitoring_cases_export.csv",
        mime="text/csv"
    )

if filtered_data.empty:
    st.warning("По выбранным фильтрам данные не найдены.")


# =========================================================
# KPI
# =========================================================
current_cases = len(filtered_data)
previous_cases = len(previous_data)

current_sum = filtered_data["Сумма НДС. млн.руб."].sum() if not filtered_data.empty else 0
previous_sum = previous_data["Сумма НДС. млн.руб."].sum() if not previous_data.empty else 0

current_companies = filtered_data["Компания"].nunique() if not filtered_data.empty else 0
previous_companies = previous_data["Компания"].nunique() if not previous_data.empty else 0

current_resp = filtered_data["Ответственный"].nunique() if not filtered_data.empty else 0
previous_resp = previous_data["Ответственный"].nunique() if not previous_data.empty else 0

current_avg = filtered_data["Сумма НДС. млн.руб."].mean() if not filtered_data.empty else 0
previous_avg = previous_data["Сумма НДС. млн.руб."].mean() if not previous_data.empty else 0

risk_current = filtered_data[
    filtered_data["Статус"].astype(str).str.contains("эскала|риск|крит", case=False, na=False)
] if not filtered_data.empty else filtered_data.iloc[0:0]

risk_previous = previous_data[
    previous_data["Статус"].astype(str).str.contains("эскала|риск|крит", case=False, na=False)
] if not previous_data.empty else previous_data.iloc[0:0]

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Всего кейсов",
    f"{current_cases}",
    delta=f"{current_cases - previous_cases:+}",
    delta_color="normal"
)

k2.metric(
    "Сумма НДС, млн руб.",
    fmt_mln(current_sum),
    delta=fmt_delta_abs(current_sum, previous_sum),
    delta_color="normal"
)

k3.metric(
    "Риск-кейсы",
    f"{len(risk_current)}",
    delta=f"{len(risk_current) - len(risk_previous):+}",
    delta_color="inverse"
)

k4.metric(
    "Компаний в контуре",
    f"{current_companies}",
    delta=f"{current_companies - previous_companies:+}",
    delta_color="off"
)

k5, k6, k7 = st.columns(3)

k5.metric(
    "Средняя сумма кейса",
    fmt_mln(current_avg),
    delta=fmt_delta_abs(current_avg, previous_avg),
    delta_color="normal"
)

k6.metric(
    "Ответственных",
    f"{current_resp}",
    delta=f"{current_resp - previous_resp:+}",
    delta_color="off"
)

k7.metric(
    "Сумма риск-кейсов, млн руб.",
    fmt_mln(risk_current["Сумма НДС. млн.руб."].sum() if not risk_current.empty else 0),
    delta=fmt_delta_abs(
        risk_current["Сумма НДС. млн.руб."].sum() if not risk_current.empty else 0,
        risk_previous["Сумма НДС. млн.руб."].sum() if not risk_previous.empty else 0
    ),
    delta_color="inverse"
)


# =========================================================
# SUMMARY CARDS
# =========================================================
sum1, sum2, sum3 = st.columns(3)

with sum1:
    text_1 = (
        f"В текущем периоде выявлено {len(risk_current)} риск-кейсов."
        if len(risk_current) > 0
        else "Критичные кейсы в текущем периоде не обнаружены."
    )
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">Риск-профиль</div>
        <div class="summary-text">{text_1}</div>
    </div>
    """, unsafe_allow_html=True)

with sum2:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">Сравнение с прошлым периодом</div>
        <div class="summary-text">
            Изменение по кейсам: {current_cases - previous_cases:+}.<br>
            Изменение по сумме: {current_sum - previous_sum:+,.1f} млн руб.
        </div>
    </div>
    """, unsafe_allow_html=True)

with sum3:
    if not filtered_data.empty:
        top_status_df = filtered_data["Статус"].value_counts().reset_index()
        top_status_name = top_status_df.iloc[0, 0]
        top_status_count = top_status_df.iloc[0, 1]
        top_status_text = f"Доминирующий статус: {top_status_name} ({top_status_count} кейсов)."
    else:
        top_status_text = "Нет данных для анализа структуры статусов."

    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">Структура портфеля</div>
        <div class="summary-text">{top_status_text}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# ВКЛАДКИ
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Сводка",
    "Риски",
    "Статусы",
    "Ответственные",
    "Реестр"
])


# =========================================================
# TAB 1 — СВОДКА
# =========================================================
with tab1:
    st.subheader("Сводная картина")

    col_left, col_right = st.columns([1.35, 1])

    with col_left:
        st.markdown("#### Динамика суммы по дням")
        if not filtered_data.empty:
            current_daily = (
                filtered_data
                .groupby(filtered_data["Дата"].dt.date, as_index=False)
                .agg(Сумма_НДС=("Сумма НДС. млн.руб.", "sum"))
            )
            st.line_chart(current_daily.set_index("Дата")["Сумма_НДС"], width="stretch")
        else:
            st.info("Нет данных для графика.")

    with col_right:
        st.markdown("#### Текущий период vs предыдущий")
        compare_table = pd.DataFrame({
            "Показатель": ["Кейсы", "Сумма НДС", "Средняя сумма", "Риск-кейсы"],
            "Текущий период": [
                current_cases,
                round(current_sum, 1),
                round(current_avg, 1),
                len(risk_current)
            ],
            "Предыдущий период": [
                previous_cases,
                round(previous_sum, 1),
                round(previous_avg, 1),
                len(risk_previous)
            ]
        })
        st.dataframe(compare_table, width="stretch", hide_index=True)

    st.markdown("#### Задолженность по НДС по предприятиям")
    debt_fig = build_vat_debt_bar(filtered_data)

    if debt_fig is not None:
        st.plotly_chart(debt_fig, width="stretch")
    else:
        st.info("Нет данных для построения графика по предприятиям.")


# =========================================================
# TAB 2 — РИСКИ
# =========================================================
with tab2:
    st.subheader("Мониторинг рисков")

    if filtered_data.empty:
        st.info("Нет данных для анализа рисков.")
    else:
        risk_candidates = filtered_data[
            filtered_data["Статус"].astype(str).str.contains("эскала|риск|крит", case=False, na=False)
        ].copy()

        if risk_candidates.empty:
            st.success("Критичных кейсов по текущим фильтрам не найдено.")
        else:
            r1, r2, r3 = st.columns(3)
            r1.metric("Риск-кейсы", f"{len(risk_candidates)}")
            r2.metric("Сумма риска, млн руб.", f"{risk_candidates['Сумма НДС. млн.руб.'].sum():,.1f}")
            r3.metric("Компаний в риске", f"{risk_candidates['Компания'].nunique()}")

            risk_by_company = (
                risk_candidates
                .groupby("Компания", as_index=False)
                .agg(
                    Количество=("Компания", "count"),
                    Сумма_НДС=("Сумма НДС. млн.руб.", "sum")
                )
                .sort_values("Сумма_НДС", ascending=False)
            )

            st.markdown("#### Компании с максимальным риском")
            st.dataframe(
                risk_by_company.style.format({
                    "Количество": "{:,.0f}",
                    "Сумма_НДС": "{:,.1f}"
                }),
                width="stretch",
                hide_index=True
            )

            st.markdown("#### Реестр риск-кейсов")
            st.dataframe(
                style_registry(risk_candidates.drop(columns=["Дата"], errors="ignore")),
                width="stretch",
                hide_index=True
            )


# =========================================================
# TAB 3 — СТАТУСЫ
# =========================================================
with tab3:
    st.subheader("Аналитика по статусам")

    if filtered_data.empty:
        st.info("Нет данных по статусам.")
    else:
        status_summary = (
            filtered_data
            .groupby("Статус", as_index=False)
            .agg(
                Количество=("Статус", "count"),
                Сумма_НДС=("Сумма НДС. млн.руб.", "sum")
            )
            .sort_values("Сумма_НДС", ascending=False)
        )

        left, right = st.columns([1, 1.2])

        with left:
            st.markdown("#### Сумма по статусам")
            st.bar_chart(status_summary.set_index("Статус")["Сумма_НДС"], width="stretch")

        with right:
            st.markdown("#### Таблица статусов")
            st.dataframe(
                status_summary.style.format({
                    "Количество": "{:,.0f}",
                    "Сумма_НДС": "{:,.1f}"
                }).map(status_cell_style, subset=["Статус"]),
                width="stretch",
                hide_index=True
            )


# =========================================================
# TAB 4 — ОТВЕТСТВЕННЫЕ
# =========================================================
with tab4:
    st.subheader("Количество инцидентов")

    if filtered_data.empty:
        st.info("Нет данных по ответственным.")
    else:
        resp_summary = (
            filtered_data
            .groupby("Ответственный", as_index=False)
            .agg(
                Количество_кейсов=("Ответственный", "count"),
                Сумма_НДС=("Сумма НДС. млн.руб.", "sum")
            )
            .sort_values("Сумма_НДС", ascending=False)
        )

        t1, t2 = st.columns([1, 1.2])

        with t1:
            st.markdown("#### Инциденты по ответственным")
            st.bar_chart(resp_summary.set_index("Ответственный")["Количество_кейсов"], width="stretch")

        with t2:
            st.markdown("#### Детализация по команде")
            st.dataframe(
                resp_summary.style.format({
                    "Количество_кейсов": "{:,.0f}",
                    "Сумма_НДС": "{:,.1f}"
                }),
                width="stretch",
                hide_index=True
            )


# =========================================================
# TAB 5 — РЕЕСТР
# =========================================================
with tab5:
    st.subheader("Полный реестр и выгрузка")

    reg1, reg2 = st.columns([3, 1])

    with reg1:
        st.markdown("#### Реестр кейсов")
    with reg2:
        st.download_button(
            label="Экспорт реестра",
            data=to_csv_download(filtered_data),
            file_name="registry_export.csv",
            mime="text/csv"
        )

    if filtered_data.empty:
        st.info("Нет данных для выгрузки.")
    else:
        registry_to_show = filtered_data.drop(columns=["Дата"], errors="ignore").copy()
        st.dataframe(
            style_registry(registry_to_show),
            width="stretch",
            hide_index=True
        )