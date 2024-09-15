import asyncio

import streamlit as st

from todoist import Todoist

async def main() -> None:
    todoist = Todoist()
    task_objs = await todoist.get_tracked_task_objs()

    st.set_page_config(page_title="Milestone Maven", layout="wide")
    st.markdown(
        r"""
        <style>
        .stDeployButton {
                visibility: hidden;
            }
        </style>
        """, unsafe_allow_html=True
    )

    row1 = st.columns(3)
    row2 = st.columns(3)

    ele_count = 0

    for col in row1 + row2:
        tile = col.container(height=160)
        if (ele_count < len(task_objs)):
            tile.subheader(task_objs[ele_count].title)
            tile.progress(task_objs[ele_count].progress)
            tile.empty().text(f"Progress: {task_objs[ele_count].progress * 100:.2f}%")
            ele_count += 1


if __name__ == "__main__":
    asyncio.run(main())