import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import warnings
import random
import altair as alt

warnings.simplefilter("ignore")


def categorize_level(df, air_quality_level: str):
    """
    Categorizing the air quality index by mapping the level of air quality
    """
    aqi_conditions = [
        (df[air_quality_level] >= 0) & (df[air_quality_level] <= 50),
        (df[air_quality_level] > 50) & (df[air_quality_level] <= 100),
        (df[air_quality_level] > 100) & (df[air_quality_level] <= 150),
        (df[air_quality_level] > 150) & (df[air_quality_level] <= 200),
        (df[air_quality_level] > 200) & (df[air_quality_level] <= 300),
        (df[air_quality_level] > 300),
    ]

    labels = [
        "Good",
        "Moderate",
        "Unhealthy",
        "Unhealthy (Sensitive)",
        "Very Unhealthy",
        "Hazardous",
    ]

    df["Category"] = np.select(aqi_conditions, labels, default="Unknown")

    return df


def create_overall_aqi(df):
    aqi_df = df["AQI"].value_counts().reset_index()
    total = aqi_df["count"].sum()
    aqi_df["percentage"] = np.round((aqi_df["count"] / total) * 100, 2)

    return aqi_df


def create_pollution_by_station(df):
    polluted_station = (
        df.groupby(by="station")
        .agg(
            {
                "vehicle_pollution": "median",
                "industrial_pollution": "median",
                "Total_AQI": "median",
            }
        )
        .reset_index()
    )

    return polluted_station


def create_pollution_by_time(df):
    pollution_by_time = (
        df.groupby(by="time_group")
        .agg(
            {
                "vehicle_pollution": "median",
                "industrial_pollution": "median",
                "Total_AQI": "median",
            }
        )
        .reset_index()
    )

    return pollution_by_time


def create_pollution_tren(df):
    pollution_tren = (
        df.groupby(by="year")
        .agg(
            {
                "vehicle_pollution": "median",
                "industrial_pollution": "median",
                "Total_AQI": "median",
            }
        )
        .reset_index()
    )

    return pollution_tren


def create_pollution_by_month(df):
    num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    month = [
        "Jan",
        "Feb",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agu",
        "Sept",
        "Okt",
        "Nov",
        "Des",
    ]
    month_map = {num[i]: month[i] for i in range(12)}
    pollution_by_month = (
        df.groupby(by=["month"])["Total_AQI"]
        .median()
        .reset_index()
        .sort_values(by="Total_AQI", ascending=False)
    )

    pollution_by_month["month"] = pollution_by_month["month"].map(month_map)

    return pollution_by_month


def create_pollution_rain_year(df):
    pm_rain_by_year = (
        df.groupby(by="year")
        .agg(
            {
                "PM2.5": "median",
                "PM10": "median",
                "Total_AQI": "median",
                "RAIN": "sum",
                "TEMP": "median",
                "PRES": "median",
                "DEWP": "median",
            }
        )
        .reset_index()
    )

    pm_rain_by_year = pm_rain_by_year.rename(
        columns={
            "year": "year",
            "PM2.5": "PM2",
            "PM10": "PM10",
            "Total_AQI": "AQI",
            "RAIN": "RAIN",
        },
    )

    pm_rain_by_year["PM2_pct"] = np.round(
        pm_rain_by_year["PM2"].pct_change().fillna(0) * 100, 2
    )

    pm_rain_by_year["PM10_pct"] = np.round(
        pm_rain_by_year["PM10"].pct_change().fillna(0) * 100, 2
    )

    pm_rain_by_year["AQI_pct"] = np.round(
        pm_rain_by_year["AQI"].pct_change().fillna(0) * 100, 2
    )

    pm_rain_by_year["RAIN_pct"] = np.round(
        pm_rain_by_year["RAIN"].pct_change().fillna(0) * 100, 2
    )

    return pm_rain_by_year


def create_rain_by_month(df):
    num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    month = [
        "Jan",
        "Feb",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agu",
        "Sept",
        "Okt",
        "Nov",
        "Des",
    ]
    month_map = {num[i]: month[i] for i in range(12)}

    rain_by_month = (
        df.groupby(by=["month"])["RAIN"]
        .sum()
        .reset_index()
        .sort_values(by="RAIN", ascending=False)
    )

    rain_by_month["month"] = rain_by_month["month"].map(month_map)

    return rain_by_month


def create_pollution_wind(df):
    pollution_by_wd = (
        df.groupby(by="wd").agg({"Total_AQI": "median", "WSPM": "median"}).reset_index()
    )

    return pollution_by_wd


def dashboard():
    st.title("🍃Air Quality Analysis🍃")

    all_df = pd.read_csv(
        "https://raw.githubusercontent.com/Jimmm1290/Air-Quality-Analysis/refs/heads/main/Dashboard/main-data.csv"
    )
    all_df["date"] = pd.to_datetime(all_df["date"])

    min_date = all_df["date"].min()
    max_date = all_df["date"].max()

    with st.sidebar:
        st.image(
            "https://www.deq.ok.gov/wp-content/uploads/air-division/aqi_mini-768x432.png"
        )
        st.subheader("Parameter")
        start_date, end_date = st.date_input(
            label="Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date],
        )
        station = st.multiselect(
            label="Stasiun Pilihan",
            options=tuple(all_df["station"].unique()),
            default=["Aotizhongxin", "Changping"],
        )

    ## Filtering data berdasarkan rentang waktu dan stasiun pilihan pada sidebar
    main_df = all_df[
        (all_df["date"] >= str(start_date))
        & (all_df["date"] <= str(end_date))
        & (all_df["station"].isin(station))
    ]

    ## Membuat dataframe untuk memvisualisasikan hasil dari pertanyaan
    aqi_df = create_overall_aqi(main_df)
    pollution_by_station_df = create_pollution_by_station(main_df)
    pollution_by_time_df = create_pollution_by_time(main_df)
    pollution_tren_df = create_pollution_tren(main_df)
    pollution_by_month_df = create_pollution_by_month(main_df)
    pollution_rain_df = create_pollution_rain_year(main_df)
    rain_by_month_df = create_rain_by_month(main_df)
    pollution_wind_df = create_pollution_wind(main_df)

    def aqi_plot(df):
        """
        Merujuk ke Pertanyaan nomor 1:
        "Berapa persentase kualitas udara tertinggi secara keseluruhan berdasarkan tingkat bahayanya?"
        """

        st.subheader("Indeks Kualitas Udara Secara Keseluruhan")

        colors = ["#fa5252", "#ff6b6b", "#ff8787", "#ffa8a8", "#ffc9c9", "#ffe3e3"]

        fig, ax = plt.subplots()
        ax.pie(df["percentage"], labels=df["AQI"], autopct="%1.1f%%", colors=colors)
        ax.set_title("Persentase Kualitas Udara")

        st.pyplot(fig)

    def substances_plot(df):
        """
        Merujuk ke Pertanyaan nomor 1:
        "Apa zat polutan yang memiliki indeks konsentrasi tertingg berdasarkan waktu?"
        """

        st.subheader("Tingkat Keparahan Konsentrasi Zat Polutan")

        lst = [col for col in df.columns if col.find("_AQI") != -1]
        lst.remove("Total_AQI")

        fig, ax = plt.subplots(2, 3, figsize=(16, 7), dpi=200)

        index = 0
        for i in range(2):
            for j in range(3):
                sns.countplot(data=df, x=lst[index], hue="year", ax=ax[i, j])
                ax[i, j].set_ylabel(None)
                ax[i, j].set_xlabel(None)
                ax[i, j].set_title(f"{lst[index].split('_AQI')[0]}")
                ax[i, j].legend_.remove()

                index += 1

        fig.suptitle("Indeks Konsentrasi Zat Polutan Berdasarkan Tahun", fontsize=20)
        fig.tight_layout(rect=[0, 0, 1, 0.9])

        handles, labels = ax[i, j].get_legend_handles_labels()
        plt.figlegend(
            handles,
            labels,
            loc="upper center",
            ncol=len(labels),
            bbox_to_anchor=(0.5, 0.9),
        )

        st.pyplot(fig)

    def pollution_by_station_plot(df):
        """
        Merujuk ke Pertanyaan nomor 2:
        "Stasiun mana yang paling banyak terkena dampak polusi?"
        """

        st.subheader("Indeks Kualitas Udara Stasiun di China")
        sorted_df = df.sort_values(by="Total_AQI", ascending=False)
        chart = (
            alt.Chart(sorted_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "station", title="Station", sort=None, axis=alt.Axis(labelAngle=-90)
                ),
                y=alt.Y("Total_AQI", title="Total AQI"),
            )
        )

        st.altair_chart(chart, use_container_width=True)

    def detail_pollution_bystation_plot(df):
        """
        Merujuk ke Pertanyaan nomor 2:
        "Stasiun mana yang paling banyak terkena dampak polusi?"
        """

        vehicle_col, industrial_col = st.columns(2)

        with vehicle_col:
            st.write("Urutan Indeks Polusi Kendaraan Terburuk")

            sorted_df = df.sort_values(by="vehicle_pollution", ascending=False)

            chart = (
                alt.Chart(sorted_df)
                .mark_bar()
                .encode(
                    y=alt.Y("station", title=None, sort=None),
                    x=alt.X("vehicle_pollution", title=None),
                    color=alt.Color(
                        "vehicle_pollution",
                        legend=None,
                        scale=alt.Scale(scheme="oranges"),
                    ),
                )
            )

            st.altair_chart(chart, use_container_width=True)

        with industrial_col:
            st.write("Urutan Indeks Polusi Pabrik Terburuk")

            sorted_df = df.sort_values(by="industrial_pollution", ascending=False)

            chart = (
                alt.Chart(sorted_df)
                .mark_bar()
                .encode(
                    y=alt.Y("station", title=None, sort=None),
                    x=alt.X("industrial_pollution", title=None),
                    color=alt.Color(
                        "industrial_pollution",
                        scale=alt.Scale(scheme="oranges"),
                        legend=None,
                    ),
                )
            )

            st.altair_chart(chart, use_container_width=True)

    def pollution_by_time_plot(df):
        sorted_df = df.sort_values("Total_AQI", ascending=False)

        st.subheader("Indeks Kualitas Udara")

        chart_1 = (
            alt.Chart(sorted_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "time_group:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)
                ),
                y=alt.Y(
                    "Total_AQI:Q",
                    title=None,
                ),
            )
        )

        st.altair_chart(altair_chart=chart_1, use_container_width=True)

        vehicle, industrial = st.columns(2)

        with vehicle:
            st.write("Polusi Kendaraan Berdasarkan Waktu Aktivitas")
            vehicle_chart = (
                alt.Chart(df.sort_values("vehicle_pollution", ascending=False))
                .mark_bar()
                .encode(
                    x=alt.X(
                        "time_group:N",
                        title=None,
                        sort=None,
                        axis=alt.Axis(labelAngle=0),
                    ),
                    y=alt.Y(
                        "vehicle_pollution:Q",
                        title=None,
                    ),
                    color=alt.Color(
                        "vehicle_pollution:Q",
                        scale=alt.Scale(scheme="oranges"),
                        legend=None,
                    ),
                )
            )
            st.altair_chart(altair_chart=vehicle_chart, use_container_width=True)

        with industrial:
            st.write("Polusi Pabrik Berdasarkan Waktu Aktivitas")
            industrial_chart = (
                alt.Chart(df.sort_values("vehicle_pollution", ascending=False))
                .mark_bar()
                .encode(
                    x=alt.X(
                        "time_group:N",
                        title=None,
                        sort=None,
                        axis=alt.Axis(labelAngle=0),
                    ),
                    y=alt.Y(
                        "vehicle_pollution:Q",
                        title=None,
                    ),
                    color=alt.Color(
                        "vehicle_pollution:Q",
                        scale=alt.Scale(scheme="oranges"),
                        legend=None,
                    ),
                )
            )
            st.altair_chart(altair_chart=industrial_chart, use_container_width=True)

    def pollution_tren_plot(df):
        st.subheader(
            f"Tren Konsentrasi Polusi Tahun {start_date.year} - {end_date.year}"
        )

        tren_chart = (
            alt.Chart(df)
            .transform_fold(
                fold=["vehicle_pollution", "industrial_pollution", "Total_AQI"],
                as_=["Pollution Type", "pollution_level"],
            )
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "year:O",
                    title=f"Year ({start_date.year} - {end_date.year})",
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y("pollution_level:Q", title=None),
                color="Pollution Type:N",
            )
            .configure_legend(orient="bottom")
        )

        st.altair_chart(altair_chart=tren_chart, use_container_width=True)

    def pollution_by_month_plot(df):
        st.subheader("Tingkat Polusi Berdasarkan Bulan")

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                y=alt.Y("month:N", title=None, sort=None),
                x=alt.X(
                    "Total_AQI:Q",
                    title=None,
                ),
                color=alt.Color(
                    "Total_AQI:Q", scale=alt.Scale(scheme="viridis"), legend=None
                ),
            )
        )

        st.altair_chart(altair_chart=chart, use_container_width=True)

    def pollution_rain_plot(df):
        df = categorize_level(df, "AQI")
        st.subheader("Konsentrasi Curah Hujan Dari Tahun ke Tahun")

        with st.container():
            col1, col2, col3 = st.columns(3)

            # Temperature
            temp_val = np.round(df[df.year == end_date.year]["TEMP"].values[0], 2)
            col1.metric(label="Temperature", value=f"{temp_val} \u00b0C")

            # Pressure
            pres_val = np.round(df[df.year == end_date.year]["PRES"].values[0], 2)
            col2.metric(label="Pressure", value=f"{pres_val} mbar")

            # Dew Point
            dewp_val = np.round(df[df.year == end_date.year]["DEWP"].values[0], 2)
            col3.metric(label="Dew Point", value=f"{dewp_val} \u00b0C")

        tren_chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title=f"Year", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("RAIN:Q", title=None),
            )
        )
        st.altair_chart(tren_chart, use_container_width=True)

        st.subheader("Grafik Pergerakan Zat Polutan Dipengaruhi Curah Hujan")

        ## Rain Metrics
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                val_1 = df[df.year == end_date.year]["PM2"].values[0]
                delta_1 = df[df.year == end_date.year]["PM2_pct"].values[0]

                st.metric(
                    label="PM2.5",
                    value=f"{val_1} μg/m3",
                    delta=f"{delta_1}%",
                    delta_color="inverse",
                )

                val_2 = df[df.year == end_date.year]["PM10"].values[0]
                delta_2 = df[df.year == end_date.year]["PM10_pct"].values[0]

                st.metric(
                    label="PM10",
                    value=f"{val_2} μg/m3",
                    delta=f"{delta_2}%",
                    delta_color="inverse",
                )

            with col2:
                val_3 = df[df.year == end_date.year]["AQI"].values[0]
                delta_3 = df[df.year == end_date.year]["AQI_pct"].values[0]

                st.metric(
                    label="Air Quality Index",
                    value=f"{val_3}",
                    delta=f"{delta_3}%",
                    delta_color="inverse",
                )

                category = df[df.year == end_date.year]["Category"].values[0]
                st.metric(
                    label="Category",
                    value=f"{category}",
                )

        aqi_chart = (
            alt.Chart(df)
            .transform_fold(fold=["PM2", "PM10", "AQI"], as_=["Type", "Level"])
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Level:Q", title="AQI Level"),
                color=alt.Color("Type:N"),
                tooltip=["year:O", "Type:N", "Level:Q"],
            )
            .configure_legend(orient="bottom")
        )
        st.altair_chart(aqi_chart, use_container_width=True)

    def rain_by_month_plot(df):
        st.subheader("Akumulasi Konsentrasi Curah Hujan Berdasarkan Bulan")

        chart = (
            alt.Chart(df.sort_values("RAIN", ascending=False))
            .mark_bar()
            .encode(
                y=alt.Y("month:N", title=None, axis=alt.Axis(labelAngle=0), sort=None),
                x=alt.X("RAIN:Q", title="Rain"),
                color=alt.Color(
                    "RAIN:Q", scale=alt.Scale(scheme="viridis"), legend=None
                ),
            )
        )

        st.altair_chart(chart, use_container_width=True)

    def pollution_wind_plot(df):
        sorted_df = df.sort_values("Total_AQI", ascending=False)
        st.subheader("Distribusi Polusi Udara Berdasarkan Arah Mata Angin")

        colorlist = [color for color in range(17)]

        chart = (
            alt.Chart(sorted_df)
            .mark_bar(color="#3bc9db")
            .encode(
                y=alt.Y("wd:N", title=None, sort=None),
                x=alt.X("Total_AQI:Q", title="Total_AQI"),
            )
        )

        st.altair_chart(chart, use_container_width=True)

    ## Menampilkan visualisasi
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Quality", "Station", "Time", "Rain", "Wind"]
    )

    with tab1:
        aqi_plot(aqi_df)
        substances_plot(main_df)

    with tab2:
        pollution_by_station_plot(pollution_by_station_df)
        detail_pollution_bystation_plot(pollution_by_station_df)

    with tab3:
        pollution_by_time_plot(pollution_by_time_df)
        pollution_tren_plot(pollution_tren_df)
        pollution_by_month_plot(pollution_by_month_df)

    with tab4:
        pollution_rain_plot(pollution_rain_df)
        rain_by_month_plot(rain_by_month_df)

    with tab5:
        pollution_wind_plot(pollution_wind_df)


if __name__ == "__main__":
    dashboard()
