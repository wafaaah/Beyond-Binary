"""Patient transfer desk shown inside the Overflow page."""
import pandas as pd
import streamlit as st

from shared import cached_data, cached_forecast
from ml.referral import bed_status, place_patients, ward_positions


@st.cache_data
def starting_beds(week, horizon, multiplier):
    return bed_status(
        cached_forecast(week, horizon), cached_data(), week, multiplier
    )


def render_transfer_desk(week, horizon, multiplier):
    st.caption("When a ward has no free bed, send the patient to the nearest "
               "ward in the same city that has one.")
    start = starting_beds(week, horizon, multiplier)
    scenario = f"{week}_{horizon}_{multiplier:.1f}"
    # bed counts and the log are kept for each scenario
    beds = st.session_state.setdefault(
        f"beds_{scenario}", dict(zip(start["ward_id"], start["free_beds"]))
    )
    log = st.session_state.setdefault(f"log_{scenario}", [])

    left, middle, right = st.columns(3)
    city = left.selectbox("City", sorted(start["city"].unique()), key="desk_city")
    city_wards = sorted(start.loc[start["city"] == city, "ward_id"])
    ward = middle.selectbox("Patient arrived at", city_wards, key="desk_ward")
    patients = int(right.number_input("Number of patients", 1, 50, 1, key="desk_patients"))


    def set_beds(ward):
        beds[ward] = int(st.session_state[f"count_{scenario}_{ward}"])


    st.number_input(
        f"Free beds at {ward} now (update with the real count)", 0, 500,
        int(beds[ward]), key=f"count_{scenario}_{ward}",
        on_change=set_beds, args=(ward,),
    )

    positions, real = ward_positions(city_wards)
    city_beds = {w: beds[w] for w in city_wards}
    plan, unplaced = place_patients(city_beds, positions, ward, patients)
    distance_label = "Distance (km)" if real else "Demo distance (km)"

    st.subheader("Recommended placement")
    if city_beds[ward] == 0:
        st.warning(f"{ward} has no free bed. Transfer to the nearest ward below.")
    for target, count, distance in plan:
        if target == ward:
            st.success(f"Admit {count} patient(s) here at {ward}.")
        else:
            st.info(f"Send {count} patient(s) to **{target}** | "
                    f"{distance_label}: {distance} | Free beds there: {beds[target]}")
    if unplaced:
        st.error(f"No free bed in {city} for {unplaced} patient(s). "
                 "Escalate to the city control room or call 999.")


    def confirm():
        for target, count, distance in plan:
            # the widget keeps its own copy, so clear it to show the new count
            st.session_state.pop(f"count_{scenario}_{target}", None)
            beds[target] -= count
            log.append({
                "from_ward": ward, "to_ward": target, "patients": count,
                "action": "admitted" if target == ward else "transferred",
                "distance_km": distance,
            })


    def reset():
        for key in list(st.session_state):
            if key.startswith(f"count_{scenario}_"):
                del st.session_state[key]
        st.session_state.pop(f"beds_{scenario}", None)
        st.session_state.pop(f"log_{scenario}", None)


    a, b = st.columns(2)
    a.button("Confirm placement", type="primary", disabled=not plan,
             on_click=confirm, use_container_width=True)
    b.button("Reset beds and log", on_click=reset, use_container_width=True)

    st.subheader(f"Free beds in {city}")
    st.dataframe(
        pd.DataFrame({"ward_id": city_wards, "free_beds": [beds[w] for w in city_wards]}),
        hide_index=True, use_container_width=True,
    )

    st.subheader("Transfer log")
    if log:
        table = pd.DataFrame(log)
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.download_button("Download log CSV", table.to_csv(index=False),
                           "patient_transfers.csv", "text/csv")
    else:
        st.info("No placements confirmed yet.")

    note = "" if real else ("Ward positions are a schematic grid (the dataset has no "
                            "coordinates), so distances are for demonstration. ")
    st.caption(note + "Starting bed counts are estimates, not live hospital data. "
               "The log is kept only for this browser session.")
