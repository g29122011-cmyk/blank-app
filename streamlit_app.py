import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="VAT Recovery Monitor", layout="wide")

st.title("VAT Recovery Monitor")
st.subheader("Мониторинг НДС, не принятого к вычету")
st.write(
    "Мониторинг мест и причин зависания сумм по НДС, с указанием зон ответственности и ответственных подразделений за своевременное урегулирование."
)

data = pd.DataFrame(
    [
        {
            "Компания": "ООО Еврохим-Волгакалий",
            "Период": "2026-04",
            "Причина": "Нет первичных документов",
            "Ответственный": "Иванов",
            "Статус": "В работе",
            "Сумма НДС. млн.руб.": 65.6,
        },
        {
            "Компания": "АО НАК Азот",
            "Период": "2026-04",
            "Причина": "Ошибка в счет-фактуре",
            "Ответственный": "Петров",
            "Статус": "Эскалация",
            "Сумма НДС. млн.руб.": 56.5,
        },
        {
            "Компания": "ООО НРСС",
            "Период": "2026-05",
            "Причина": "Риск по контрагенту",
            "Ответственный": "Сидорова",
            "Статус": "Ожидает документы",
            "Сумма НДС. млн.руб.": 2.6,
        },
        {
            "Компания": "АО Еврохим-УКК",
            "Период": "2026-05",
            "Причина": "Позднее поступление документов",
            "Ответственный": "Кузнецов",
            "Статус": "В работе",
            "Сумма НДС. млн.руб.": 224.3,
        },
    ]
)

companies = ["Все компании"] + sorted(data["Компания"].unique().tolist())
selected_company = st.selectbox("Выберите компанию", companies, width="stretch")

if selected_company == "Все компании":
    filtered_data = data.copy()
else:
    filtered_data = data[data["Компания"] == selected_company]

total_vat = filtered_data["Сумма НДС. млн.руб."].sum()
critical_cases = filtered_data[filtered_data["Статус"] == "Эскалация"].shape[0]
risk_companies = filtered_data["Компания"].nunique()

c1, c2, c3 = st.columns(3)
c1.metric("НДС не принят к вычету", f"{total_vat:.1f} млн руб.")
c2.metric("Критичные кейсы", str(critical_cases))
c3.metric("Компании в риске", str(risk_companies))

chart_data = (
    filtered_data.groupby("Причина", as_index=False)["Сумма НДС. млн.руб."]
    .sum()
    .sort_values("Сумма НДС. млн.руб.", ascending=False)
)

fig = px.bar(
    chart_data,
    x="Причина",
    y="Сумма НДС. млн.руб.",
    title="Сумма непринятого НДС по причинам",
    text_auto=".1f",
)

fig.update_layout(
    xaxis_title="",
    yaxis_title="млн руб.",
)

st.plotly_chart(fig, width="stretch")

st.markdown("### Критичные кейсы")
st.dataframe(filtered_data, width="stretch")