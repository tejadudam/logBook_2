# views.py
import streamlit as st
import pandas as pd
from db import (
    get_client_by_id,
    get_logs_for_client,
    get_modules_for_client,
    create_module,
    delete_module,
    update_module,
)


def to_df(rows):
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])


def client_detail_view(client_id: int):
    client = get_client_by_id(client_id)
    if not client:
        st.info("Client not found.")
        return

    st.markdown(f"### {client['name']}")
    bits = []
    if client["code"]:
        bits.append(client["code"])
    if client["state"]:
        bits.append(client["state"])
    if client["status"]:
        bits.append(f"Status: {client['status']}")
    if bits:
        st.caption(" · ".join(bits))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Manpower", client["initial_manpower"] or 0)
    c2.metric("Users", client["num_users"] or 0)
    c3.metric("Branches", client["num_branches"] or 0)
    c4.metric("Pocket FaME", "Yes" if client["pocket_fame"] else "No")

    c1, c2, c3 = st.columns(3)
    c1.write(f"PO Date: **{client['po_date'] or '—'}**")
    c2.write(f"Training: **{client['initial_training_date'] or '—'}**")
    c3.write(f"Go LIVE: **{client['go_live_date'] or '—'}**")

    if client["contact_name"]:
        st.write(
            f"Contact: **{client['contact_name']}**"
            + (f" ({client['contact_designation']})" if client["contact_designation"] else "")
        )
        cl = []
        if client["contact_phone"]:
            cl.append(f"📞 {client['contact_phone']}")
        if client["contact_email"]:
            cl.append(f"✉️ {client['contact_email']}")
        if cl:
            st.caption(" · ".join(cl))

    st.markdown("---")

    tabs = st.tabs(["Overview", "Project", "Contact", "Logs / Tasks", "Modules"])

    # Overview
    with tabs[0]:
        st.subheader("Overview")
        st.write(f"**FaME Version:** {client['fame_version'] or '—'}")
        st.write(f"**Status:** {client['status'] or '—'}")
        st.write(f"**State:** {client['state'] or '—'}")
        if client["psf"]:
            st.write(f"**PSF:** {client['psf']}")
        if client["notes"]:
            st.markdown("**Notes / Aspects:**")
            st.write(client["notes"])

    # Project
    with tabs[1]:
        st.subheader("Project Details")
        c1, c2, c3 = st.columns(3)
        c1.write(f"Initial Manpower: **{client['initial_manpower'] or 0}**")
        c2.write(f"Number of Users: **{client['num_users'] or 0}**")
        c3.write(f"Number of Branches: **{client['num_branches'] or 0}**")

        st.markdown("##### Integrations")
        c1, c2 = st.columns(2)

        def flag(v): return "✅ Yes" if v else "❌ No"

        with c1:
            st.write(f"Proforma: {flag(client['proforma_integration'])}")
            st.write(f"E-Invoice: {flag(client['einvoice_integration'])}")
            st.write(f"KYC – Aadhaar: {flag(client['kyc_aadhaar'])}")
            st.write(f"KYC – Bank: {flag(client['kyc_bank'])}")
        with c2:
            st.write(f"SMS: {flag(client['sms_integration'])}")
            st.write(f"Mail – Pay slips: {flag(client['sendmail_payslips'])}")
            st.write(f"Mail – Invoice: {flag(client['sendmail_invoice'])}")
            st.write(f"Bank Integration: {flag(client['bank_integration'])}")

    # Contact
    with tabs[2]:
        st.subheader("Contact Details")
        st.write(f"**Name:** {client['contact_name'] or '—'}")
        st.write(f"**Designation:** {client['contact_designation'] or '—'}")
        st.write(f"**Phone:** {client['contact_phone'] or '—'}")
        st.write(f"**Email:** {client['contact_email'] or '—'}")

    # Logs tab – read-only (no add form)
    with tabs[3]:
        logs = get_logs_for_client(client_id)
        st.subheader("Activity & Tasks")

        status_map = {
            "Not Started": "🔵 Not Started",
            "In Progress": "🟡 In Progress",
            "Blocked": "🔴 Blocked",
            "Completed": "🟢 Completed",
        }
        counts = {k: 0 for k in status_map}
        for l in logs:
            s = l["status"] or "Not Started"
            if s in counts:
                counts[s] += 1

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔵 Not Started", counts["Not Started"])
        c2.metric("🟡 In Progress", counts["In Progress"])
        c3.metric("🔴 Blocked", counts["Blocked"])
        c4.metric("🟢 Completed", counts["Completed"])

        st.markdown("---")
        st.markdown("#### Recent Activity")

        if not logs:
            st.info("No logs for this client yet.")
        else:
            recent = logs[:5]
            for l in recent:
                label = status_map.get(l["status"] or "Not Started", l["status"])
                st.markdown(
                    f"""
                    <div style="padding:0.5rem 0.75rem;border-radius:0.5rem;border:1px solid #eee;margin-bottom:0.35rem;">
                      <div style="font-size:0.8rem;color:#777;">{l['log_date'] or ''}</div>
                      <div style="font-weight:600;margin-bottom:0.1rem;">{l['title']}</div>
                      <div style="font-size:0.8rem;margin-bottom:0.15rem;">
                        {label or ''} | {(l['owner'] or '')}
                      </div>
                      <div style="font-size:0.8rem;color:#555;">
                        {(l['remarks'] or l['description'] or '')[:120]}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown("#### Full Log History")
        if not logs:
            st.info("No logs recorded yet.")
        else:
            with st.expander("View full log table", expanded=False):
                df = to_df(logs)
                cols = ["id", "log_date", "title", "status", "owner", "remarks"]
                cols = [c for c in cols if c in df.columns]
                st.dataframe(df[cols], use_container_width=True)

    # Modules
    with tabs[4]:
        modules = get_modules_for_client(client_id)
        total = len(modules)
        live = len([m for m in modules if m["is_live"]])
        not_live = total - live

        st.subheader("Module Wise Customizations")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Modules", total)
        c2.metric("LIVE Modules", live)
        c3.metric("Not Live", not_live)

        st.markdown("---")
        st.markdown("#### Add Module")
        with st.form(f"add_module_for_{client_id}", clear_on_submit=True):
            ctop1, ctop2 = st.columns([2, 1])
            with ctop1:
                m_name = st.text_input("Module Name *")
            with ctop2:
                m_live = st.checkbox("Module LIVE")

            m_custom = st.text_area(
                "Customizations / Notes", height=80,
                help="Example: extra fields, custom reports, approvals, etc."
            )
            submitted = st.form_submit_button("Add Module")
            if submitted:
                if not m_name.strip():
                    st.error("Module name is required.")
                else:
                    create_module(
                        client_id,
                        m_name.strip(),
                        m_custom.strip() or None,
                        m_live,
                    )
                    st.success("Module added.")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### Modules for this Client")

        # which module is currently in "edit mode"
        if "editing_module_id" not in st.session_state:
            st.session_state["editing_module_id"] = None

        if not modules:
            st.info("No modules recorded yet.")
        else:
            cols = st.columns(2)
            for idx, m in enumerate(modules):
                col = cols[idx % 2]
                with col:
                    is_editing = st.session_state["editing_module_id"] == m["id"]

                    if is_editing:
                        # --- EDIT MODE CARD ---
                        with st.form(f"edit_module_form_{m['id']}"):
                            top1, top2 = st.columns([2, 1])
                            with top1:
                                module_name = st.text_input(
                                    "Module Name *", value=m["module_name"]
                                )
                            with top2:
                                is_live = st.checkbox(
                                    "Module LIVE", value=bool(m["is_live"])
                                )

                            customizations = st.text_area(
                                "Customizations / Notes",
                                value=m["customizations"] or "",
                                height=80,
                            )

                            b1, b2, b3 = st.columns(3)
                            save_btn = b1.form_submit_button("Save")
                            cancel_btn = b2.form_submit_button("Cancel")
                            delete_btn = b3.form_submit_button("Delete", type="secondary")

                            if save_btn:
                                if not module_name.strip():
                                    st.error("Module name is required.")
                                else:
                                    data = {
                                        "module_name": module_name.strip(),
                                        "customizations": customizations.strip() or None,
                                        "is_live": is_live,
                                    }
                                    update_module(m["id"], data)
                                    st.success("Module updated.")
                                    st.session_state["editing_module_id"] = None
                                    st.rerun()

                            if cancel_btn:
                                st.session_state["editing_module_id"] = None
                                st.rerun()

                            if delete_btn:
                                delete_module(m["id"])
                                st.warning(f"Deleted module: {m['module_name']}")
                                st.session_state["editing_module_id"] = None
                                st.rerun()

                    else:
                        # --- VIEW MODE CARD ---
                        live_label = "LIVE" if m["is_live"] else "Not Live"
                        live_color = "#16a34a" if m["is_live"] else "#6b7280"

                        st.markdown(
                            f"""
                            <div style="
                                border: 1px solid #e5e7eb;
                                border-radius: 0.75rem;
                                padding: 0.75rem 0.9rem;
                                margin-bottom: 0.25rem;
                                background-color: #ffffff;
                            ">
                              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <div style="font-weight: 600;">{m['module_name']}</div>
                                <span style="
                                    font-size: 0.75rem;
                                    padding: 2px 8px;
                                    border-radius: 999px;
                                    background-color: {live_color}20;
                                    color: {live_color};
                                    border: 1px solid {live_color}40;
                                ">
                                  {live_label}
                                </span>
                              </div>
                              <div style="font-size: 0.85rem; color: #4b5563; min-height: 2.5rem;">
                                {(m['customizations'] or 'No specific notes').replace('\n','<br>')}
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("✏️ Edit", key=f"edit_module_{m['id']}"):
                                st.session_state["editing_module_id"] = m["id"]
                                st.rerun()
                        with b2:
                            if st.button("Delete", key=f"del_module_{m['id']}"):
                                delete_module(m["id"])
                                st.warning(f"Deleted module: {m['module_name']}")
                                st.rerun()


            with st.expander("View as table (for copy/export)", expanded=False):
                dfm = to_df(modules)
                dfm["is_live"] = dfm["is_live"].map(lambda x: "Yes" if x else "No")
                cols = ["id", "module_name", "customizations", "is_live"]
                cols = [c for c in cols if c in dfm.columns]
                st.dataframe(dfm[cols], use_container_width=True)
