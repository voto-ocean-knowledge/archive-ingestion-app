from pathlib import Path
import datetime
import json
import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium, folium_static

st.set_page_config(page_title='Ocean Archive Ingest', page_icon="🌊")
st.title("Upload Photos to Ocean Archive")

runnable = False
fmt_colors = {
    'WARNING': 'orange',
    'ERROR': 'red',
}

show_map = False
upload_accept = False
project_name = None
user_entered_location = None
coords = None
info = None
operator_name = st.selectbox(
    "Operator",
    (None, "Micke", "Per", "Callum"),
)
if operator_name:
    st.write(f"Welcome back {operator_name} 👋 (this is where we'd ask an ambassador for a password)")
    project_name = st.selectbox(
        "Select Project",
        (None, "Baltic bonanza", "Gotland 1980", "Terrifying ice caves"),
    )


if project_name:

    st.write(f"Use the tools on the left hand side of the map to select the point/area where these photos were taken. You can delete an incorrect shape with the trashcan icon")
    m = folium.Map(location=[56, 15], zoom_start=6)
    Draw(export=True).add_to(m)
    output = st_folium(m, width=700, height=600)
    user_entered_location = output["last_active_drawing"]
    if user_entered_location:
        coords = user_entered_location["geometry"]["coordinates"]

num_photos = 0
if coords:
    uploaded_files = st.file_uploader(
        "Upload images", accept_multiple_files="directory", type=["jpg", "png"]
    )
    for uploaded_file in uploaded_files:
        num_photos += 1
        st.image(uploaded_file)
    info = st.text_input("addional information (optional)")


if num_photos > 0:
    st.markdown("-------------")
    st.subheader("Check details and upload")
    st.markdown(f"You will upload the {num_photos} photos above to the project **{project_name}**")
    st.write(f"These photos were collected at {coords}")

    m = folium.Map(location=[56, 15], zoom_start=6)
    folium.GeoJson(
        user_entered_location
    ).add_to(m)
    folium_static(m)

    if st.button("Upload Photos", type="primary"):
        photo_names = []
        archive_dir = Path("uploaded_files")
        existing_dirs = list(archive_dir.glob("upload_*"))
        if len(existing_dirs) > 0:
            existing_dirs.sort()
            max_num = int(existing_dirs[-1].parts[-1].split('_')[-1])
        else:
            max_num = 0
        upload_num = max_num + 1
        upload_id = f"upload_{upload_num}"
        upload_dir = archive_dir / upload_id
        if not upload_dir.exists():
            upload_dir.mkdir(parents=True)
        for i, uploaded_file in enumerate(uploaded_files):
            bytes_data = uploaded_file.getvalue()
            filename = uploaded_file.name.split('/')[-1]
            photo_names.append(filename)
            with open(upload_dir / filename, 'wb') as f:
                f.write(bytes_data)
            st.write(f"{i+1}. Uploaded {filename}")
        result = True
        info_dict = {'operator': operator_name,
                     'project': project_name,
                     'datetime': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     'photos': num_photos,
                     'photo_names': photo_names,
                     'location': user_entered_location,
                     }
        if info:
            info_dict["uploader_information"] = info
        with open(upload_dir / "meta.json", 'w') as f:
            json.dump(info_dict, f, indent=2)
        if result:
            st.subheader(f":green[Photos uploaded to upload_{upload_num} successfully!]")
            st.subheader(f":green[Thank you for your service 🙏]")
            st.write(f":green[Reload the page to start a new upload]")
        else:
            st.subheader(":red[Something went wrong 😢 contact Callum]")


st.markdown("-------------")
st.markdown(
    "Source code at [https://github.com/voto-ocean-knowledge/archive-ingestion-app](https://github.com/voto-ocean-knowledge/archive-ingestion-app)")
