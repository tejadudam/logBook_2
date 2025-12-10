# app.py
import streamlit as st
import pandas as pd

from db import (
    init_db,
    get_all_clients,
    get_all_logs,
    get_log_by_id,
)
from views import to_df
from dialogs import (
    quick_add_log_dialog,
    quick_add_log_for_client_dialog,
    add_client_dialog,
    show_edit_client_dialog,
    show_client_detail_dialog,
    show_edit_log_dialog,
)


# ---------- PAGES ----------

def dashboard_page():
    # Notion-like page header
    st.markdown(
        """
        <div class="notion-page-header">
            <div class="notion-page-icon">📊</div>
            <div>
                <div class="notion-page-title">Dashboard</div>
                <div class="notion-page-subtitle">
                    High-level view of all your clients and work logs.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_row = st.columns([3, 1])
    with top_row[1]:
        if st.button("➕ Quick Add Log", use_container_width=True):
            quick_add_log_dialog()

    clients = get_all_clients()
    logs = get_all_logs()

    total_clients = len(clients)
    total_logs = len(logs)
    open_logs = [
        l for l in logs
        if (l["status"] or "").lower() not in ("completed", "done", "closed")
    ]
    open_count = len(open_logs)

    st.markdown(
        '<div class="notion-section-title">Key Metrics</div>',
        unsafe_allow_html=True,
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Clients", total_clients)
    m2.metric("Total Logs", total_logs)
    m3.metric("Open Logs", open_count)

    st.markdown(
        '<div class="notion-section-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="notion-section-title">Task Overview</div>',
        unsafe_allow_html=True,
    )
    if not logs:
        st.info("No logs yet.")
    else:
        lookup = {c["id"]: c["name"] for c in clients}
        for l in logs[:5]:
            client_name = lookup.get(l["client_id"], "Client")

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="notion-log-row">
                        <div class="notion-log-info">
                            <div class="notion-log-title">{l['title']}</div>
                            <div class="notion-log-meta">
                                {client_name} | {l['log_date'] or ''} | {l['status'] or ''}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.write("")  # small top padding
                if st.button("Edit", key=f"dash_edit_{l['id']}"):
                    show_edit_log_dialog(l["id"], get_log_by_id)

        st.caption("Showing latest 5 logs.")


def clients_page():
    st.markdown(
        """
        <div class="notion-page-header">
            <div class="notion-page-icon">👥</div>
            <div>
                <div class="notion-page-title">Clients</div>
                <div class="notion-page-subtitle">
                    Database of all implementation clients with quick actions.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    clients = get_all_clients()

    # Top bar: search + filter + add new
    bar1, bar2, bar3 = st.columns([3, 1.3, 1.2])
    with bar1:
        search = st.text_input(
            "",
            placeholder="Search clients by name, code, state or status...",
            label_visibility="collapsed",
        )
    with bar2:
        status_filter = st.selectbox(
            "Filter",
            ["All", "Not Started", "In Progress", "On Hold",
             "Completed", "Churned", "Other"],
            label_visibility="collapsed",
        )
    with bar3:
        if st.button("➕ New Client", use_container_width=True):
            add_client_dialog()

    def match(c):
        if status_filter != "All" and (c["status"] or "") != status_filter:
            return False
        if search:
            s = search.lower()
            return (
                s in (c["name"] or "").lower()
                or s in (c["code"] or "").lower()
                or s in (c["status"] or "").lower()
                or s in (c["state"] or "").lower()
            )
        return True

    filtered = [c for c in clients if match(c)]

    st.markdown(
        """
        <div class="notion-table-header">
            <div class="nt-col-id">ID</div>
            <div class="nt-col-name">Name</div>
            <div class="nt-col-status">Status</div>
            <div class="nt-col-actions">Actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            '<div class="notion-empty">'
            'No clients match your filters. Try clearing the search or status filter.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    for c in filtered:
        st.markdown('<div class="notion-table-row">', unsafe_allow_html=True)
        col_id, col_name, col_status, col_actions = st.columns([1, 3, 2, 3])

        with col_id:
            st.markdown(
                f"<div class='nt-cell-id'>{c['id']:03d}</div>",
                unsafe_allow_html=True,
            )

        with col_name:
            sub = " · ".join(
                x for x in [c["code"] or "", c["state"] or ""] if x
            )
            st.markdown(
                f"""
                <div class="nt-cell-name">
                    <div class="nt-name-main">{c['name']}</div>
                    <div class="nt-name-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_status:
            status = c["status"] or "—"
            st.markdown(
                f"<div class='nt-pill nt-pill-status'>{status}</div>",
                unsafe_allow_html=True,
            )

        with col_actions:
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Open", key=f"open_{c['id']}"):
                    show_client_detail_dialog(c["id"])
            with b2:
                if st.button("Edit", key=f"edit_{c['id']}"):
                    show_edit_client_dialog(c["id"])
            with b3:
                if st.button("Log", key=f"log_{c['id']}"):
                    quick_add_log_for_client_dialog(c["id"])

        st.markdown("</div>", unsafe_allow_html=True)


def logs_page():
    st.markdown(
        """
        <div class="notion-page-header">
            <div class="notion-page-icon">📝</div>
            <div>
                <div class="notion-page-title">Logs & Tasks</div>
                <div class="notion-page-subtitle">
                    Timeline of all activities across every client.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("➕ Quick Add Log", use_container_width=True):
        quick_add_log_dialog()

    clients = get_all_clients()
    lookup = {c["id"]: c["name"] for c in clients}

    f1, f2 = st.columns(2)
    with f1:
        options = ["All Clients"] + [f"{c['name']} (#{c['id']})" for c in clients]
        choice = st.selectbox("Filter by client", options)
        client_id = (
            None if choice == "All Clients"
            else int(choice.split("#")[-1].strip(")"))
        )
    with f2:
        status_filter = st.selectbox(
            "Status", ["All", "Not Started", "In Progress", "Blocked", "Completed"]
        )

    logs = get_all_logs(status_filter=status_filter, client_id=client_id)
    if not logs:
        st.info("No logs for the selected filters.")
        return

    df = to_df(logs)
    df["Client"] = df["client_id"].map(lookup)
    cols = ["id", "Client", "log_date", "title", "status", "owner", "remarks"]
    cols = [c for c in cols if c in df.columns]

    st.markdown(
        '<div class="notion-section-title">Logs Table</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(df[cols], use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="notion-section-divider"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="notion-section-title">Edit / Delete Log</div>',
        unsafe_allow_html=True,
    )

    log_map = {
        f"{l['id']} - {l['title']} ({lookup.get(l['client_id'], 'Client')})": l["id"]
        for l in logs
    }
    label = st.selectbox("Select log to edit", list(log_map.keys()))
    selected_log_id = log_map[label]

    if st.button("Edit Selected Log"):
        show_edit_log_dialog(selected_log_id, get_log_by_id)


def settings_page():
    st.markdown(
        """
        <div class="notion-page-header">
            <div class="notion-page-icon">⚙️</div>
            <div>
                <div class="notion-page-title">Settings & Info</div>
                <div class="notion-page-subtitle">
                    Lightweight configuration and help for this internal tool.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="notion-text-block">
          <p>This is your local <strong>Client & Project Tracker</strong> app.</p>
          <ul>
            <li>Data is stored in <code>client_tracker.db</code> (SQLite)</li>
            <li>You can back up that file to keep history safe</li>
            <li>
              If you used an older schema and see errors,
              delete <code>client_tracker.db</code> once and restart.
            </li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- MAIN ----------

def main():
    st.set_page_config(
        page_title="Client & Project Tracker",
        page_icon="📁",
        layout="wide",
    )

    # Global Notion-like theming + layout tweaks, dark-mode aware
    st.markdown(
        """
        <style>
        /* Hide Streamlit header bar */
        header, [data-testid="stHeader"] {
            display: none !important;
        }

        /* App & layout (use theme vars) */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2.5rem;
            max-width: 1100px;
        }

        /* Sidebar look */
        section[data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            margin-bottom: 0.4rem;
            color: var(--text-color);
        }

        /* Sidebar radio -> Notion-like nav */
        section[data-testid="stSidebar"] input[type="radio"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] > label {
            padding: 6px 10px !important;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.92rem;
            color: var(--text-color);
            margin-bottom: 2px;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
            background-color: rgba(148, 163, 184, 0.25) !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] > label[data-selected="true"] {
            background-color: var(--background-color) !important;
            font-weight: 600;
            box-shadow: 0 1px 3px rgba(0,0,0,0.24);
        }

        /* Page header */
        .notion-page-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        .notion-page-icon {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: var(--secondary-background-color);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 1px 3px rgba(15,23,42,0.3);
        }
        .notion-page-title {
            font-size: 1.9rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text-color);
        }
        .notion-page-subtitle {
            font-size: 0.9rem;
            color: rgba(148, 163, 184, 0.9);
            margin-top: 2px;
        }

        /* Sections */
        .notion-section-title {
            font-size: 1.05rem;
            font-weight: 600;
            margin: 1.0rem 0 0.4rem 0;
            color: var(--text-color);
        }
        .notion-section-divider {
            border-bottom: 1px solid rgba(148, 163, 184, 0.4);
            margin: 1.0rem 0;
        }

        /* Clients table (Notion-style database) */
        .notion-table-header {
            display: grid;
            grid-template-columns: 0.7fr 3fr 2fr 3fr;
            font-size: 0.75rem;
            text-transform: uppercase;
            color: rgba(148, 163, 184, 0.95);
            padding: 0.25rem 0.25rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.4);
            margin-top: 0.4rem;
        }
        .notion-table-row {
            padding: 0.15rem 0.25rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        }
        .notion-table-row:hover {
            background-color: rgba(148, 163, 184, 0.12);
        }
        .nt-col-id, .nt-col-name, .nt-col-status, .nt-col-actions {
            padding: 0.2rem 0.2rem;
        }
        .nt-cell-id {
            font-feature-settings: "tnum" 1;
            font-variant-numeric: tabular-nums;
            color: rgba(148, 163, 184, 0.95);
            font-size: 0.85rem;
            padding-top: 0.2rem;
        }
        .nt-cell-name {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .nt-name-main {
            font-size: 0.95rem;
            font-weight: 500;
            color: var(--text-color);
        }
        .nt-name-sub {
            font-size: 0.8rem;
            color: rgba(148, 163, 184, 0.95);
        }
        .nt-pill {
            display: inline-flex;
            align-items: center;
            padding: 1px 8px;
            border-radius: 999px;
            font-size: 0.78rem;
            border: 1px solid rgba(148, 163, 184, 0.5);
            background: rgba(148, 163, 184, 0.15);
            color: var(--text-color);
        }
        .notion-empty {
            padding: 0.8rem 0.4rem;
            color: rgba(148, 163, 184, 0.95);
            font-size: 0.9rem;
        }

        /* Recent logs on dashboard */
        .notion-log-row {
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, 0.4);
            padding: 12px 16px;
            margin-bottom: 12px;
            background: var(--secondary-background-color);
            display: flex;
            align-items: center;
        }
        .notion-log-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .notion-log-title {
            font-size: 0.98rem;
            font-weight: 600;
            color: var(--text-color);
        }
        .notion-log-meta {
            font-size: 0.78rem;
            color: rgba(148, 163, 184, 0.95);
        }

        /* Generic text block */
        .notion-text-block {
            font-size: 0.95rem;
            color: var(--text-color);
        }
        .notion-text-block ul {
            padding-left: 1.2rem;
        }
        .notion-text-block li {
            margin-bottom: 0.25rem;
        }
        .notion-text-block code {
            background: rgba(148, 163, 184, 0.18);
            padding: 2px 4px;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        /* Buttons – soften a bit */
        button[kind="primary"], button {
            border-radius: 999px !important;
            font-size: 0.82rem !important;
        }

        /* Dialogs wider */
        [data-testid="stDialog"] > div {
            align-items: center;
        }
        [data-testid="stDialog"] > div > div {
            width: 1000px !important;
            max-width: 95vw !important;
        }
        [data-testid="stDialog"] [data-testid="stVerticalBlock"] {
            max-width: 980px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Init DB
    init_db()

    # Sidebar: title + quick add
    st.sidebar.title("Workspace")

    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Clients", "Logs / Tasks", "Settings"],
        label_visibility="collapsed",
    )

    st.sidebar.title("Quick Actions")
    if st.sidebar.button("➕ Add Log"):
        quick_add_log_dialog()

    if page == "Dashboard":
        dashboard_page()
    elif page == "Clients":
        clients_page()
    elif page == "Logs / Tasks":
        logs_page()
    elif page == "Settings":
        settings_page()


if __name__ == "__main__":
    main()
