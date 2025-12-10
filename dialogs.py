# dialogs.py
import streamlit as st
from datetime import date

from db import (
    get_all_clients,
    get_client_by_id,
    create_client,
    update_client,
    create_log,
    update_log,
    delete_log,
)
from views import client_detail_view


@st.dialog("Quick Add Log / Task")
def quick_add_log_dialog():
    clients = get_all_clients()
    if not clients:
        st.info("No clients yet. Add a client first.")
        return

    options = [f"{c['name']} (#{c['id']})" for c in clients]
    choice = st.selectbox("Client", options)
    client_id = int(choice.split("#")[-1].strip(")"))

    with st.form("quick_add_log_form", clear_on_submit=True):
        log_date = st.date_input("Log Date", value=date.today(), format="YYYY-MM-DD")
        title = st.text_input("Title *")
        status = st.selectbox(
            "Status",
            ["Not Started", "In Progress", "Blocked", "Completed"],
            index=1,
        )
        owner = st.text_input("Owner / Engineer")
        description = st.text_area("Description", height=80)
        remarks = st.text_area("Remarks", height=60)

        submitted = st.form_submit_button("Create Log")
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                payload = {
                    "client_id": client_id,
                    "log_date": log_date.isoformat(),
                    "title": title.strip(),
                    "status": status,
                    "owner": owner.strip() or None,
                    "description": description.strip() or None,
                    "remarks": remarks.strip() or None,
                }
                create_log(payload)
                st.success("Log created.")
                st.rerun()


def quick_add_log_for_client_dialog(client_id: int):
    client = get_client_by_id(client_id)
    if not client:
        st.error("Client not found.")
        return

    @st.dialog(f"Add Log – {client['name']}")
    def _dlg():
        with st.form(f"add_log_for_client_{client_id}", clear_on_submit=True):
            log_date = st.date_input("Log Date", value=date.today(), format="YYYY-MM-DD")
            title = st.text_input("Title *")
            status = st.selectbox(
                "Status",
                ["Not Started", "In Progress", "Blocked", "Completed"],
                index=1,
            )
            owner = st.text_input("Owner / Engineer")
            description = st.text_area("Description", height=80)
            remarks = st.text_area("Remarks", height=60)

            submitted = st.form_submit_button("Create Log")
            if submitted:
                if not title.strip():
                    st.error("Title is required.")
                else:
                    payload = {
                        "client_id": client_id,
                        "log_date": log_date.isoformat(),
                        "title": title.strip(),
                        "status": status,
                        "owner": owner.strip() or None,
                        "description": description.strip() or None,
                        "remarks": remarks.strip() or None,
                    }
                    create_log(payload)
                    st.success("Log created.")
                    st.rerun()

    _dlg()


def show_edit_log_dialog(log_id: int, get_log_by_id_fn):
    log = get_log_by_id_fn(log_id)
    if not log:
        st.error("Log not found.")
        return

    client = get_client_by_id(log["client_id"])
    client_name = client["name"] if client else f"Client #{log['client_id']}"

    @st.dialog(f"Edit Log – {client_name} (#{log_id})")
    def _dlg():
        from datetime import date as _date

        log_date_val = (
            _date.fromisoformat(log["log_date"])
            if log["log_date"]
            else _date.today()
        )

        with st.form(f"edit_log_{log_id}"):
            log_date = st.date_input("Log Date", value=log_date_val, format="YYYY-MM-DD")
            title = st.text_input("Title *", value=log["title"])
            description = st.text_area("Description", value=log["description"] or "")
            status = st.selectbox(
                "Status",
                ["Not Started", "In Progress", "Blocked", "Completed"],
                index=(
                    ["Not Started", "In Progress", "Blocked", "Completed"].index(
                        log["status"]
                    )
                    if log["status"] in ["Not Started", "In Progress", "Blocked", "Completed"]
                    else 1
                ),
            )
            owner = st.text_input("Owner", value=log["owner"] or "")
            remarks = st.text_area("Remarks", value=log["remarks"] or "")

            c1, c2 = st.columns(2)
            save = c1.form_submit_button("Save Changes")
            delete = c2.form_submit_button("Delete", type="secondary")

            if save:
                if not title.strip():
                    st.error("Title is required.")
                else:
                    payload = {
                        "log_date": log_date.isoformat(),
                        "title": title.strip(),
                        "description": description.strip() or None,
                        "status": status,
                        "owner": owner.strip() or None,
                        "remarks": remarks.strip() or None,
                    }
                    update_log(log_id, payload)
                    st.success("Log updated.")
                    st.rerun()

            if delete:
                delete_log(log_id)
                st.warning("Log deleted.")
                st.rerun()

    _dlg()


@st.dialog("Add New Client")
def add_client_dialog():
    from datetime import date as _date

    st.write("Fill the details to create a new client.")
    basic_tab, project_tab, contact_tab = st.tabs(
        ["Basic Client Details", "Project Details", "Contact Details"]
    )

    if "new_client_data" not in st.session_state:
        st.session_state["new_client_data"] = {}

    data = st.session_state["new_client_data"]

    with basic_tab:
        name = st.text_input("Client Name *", value=data.get("name", ""))
        code = st.text_input("Client Code / Short Name", value=data.get("code", ""))
        status = st.selectbox(
            "Status",
            ["Not Started", "In Progress", "On Hold", "Completed", "Churned", "Other"],
            index=1,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            po_date = st.date_input(
                "PO Received Date",
                value=data.get("po_date") or _date.today(),
                format="YYYY-MM-DD",
            )
        with c2:
            training_date = st.date_input(
                "Initial Training Date",
                value=data.get("initial_training_date") or _date.today(),
                format="YYYY-MM-DD",
            )
        with c3:
            go_live_date = st.date_input(
                "Go LIVE Date",
                value=data.get("go_live_date") or _date.today(),
                format="YYYY-MM-DD",
            )

        fame_version = st.text_input("FaME Version", value=data.get("fame_version", ""))
        pocket_fame = st.checkbox(
            "Pocket FaME Enabled", value=data.get("pocket_fame", False)
        )
        state = st.text_input("State", value=data.get("state", ""))

    with project_tab:
        c1, c2, c3 = st.columns(3)
        with c1:
            initial_manpower = st.number_input(
                "Initial Manpower",
                min_value=0,
                value=int(data.get("initial_manpower", 0)),
            )
        with c2:
            num_users = st.number_input(
                "Number of Users",
                min_value=0,
                value=int(data.get("num_users", 0)),
            )
        with c3:
            num_branches = st.number_input(
                "Number of Branches",
                min_value=0,
                value=int(data.get("num_branches", 0)),
            )

        st.markdown("##### Integrations")
        c1, c2 = st.columns(2)
        with c1:
            proforma_integration = st.checkbox(
                "Proforma Integration", value=data.get("proforma_integration", False)
            )
            einvoice_integration = st.checkbox(
                "E-Invoice Integration",
                value=data.get("einvoice_integration", False),
            )
            kyc_aadhaar = st.checkbox(
                "KYC – Aadhaar", value=data.get("kyc_aadhaar", False)
            )
            kyc_bank = st.checkbox(
                "KYC – Bank Account", value=data.get("kyc_bank", False)
            )
        with c2:
            sms_integration = st.checkbox(
                "SMS Integration", value=data.get("sms_integration", False)
            )
            sendmail_payslips = st.checkbox(
                "Mail – Pay slips", value=data.get("sendmail_payslips", False)
            )
            sendmail_invoice = st.checkbox(
                "Mail – Invoice", value=data.get("sendmail_invoice", False)
            )
            bank_integration = st.checkbox(
                "Bank Integration", value=data.get("bank_integration", False)
            )

        psf = st.text_input("PSF (Count / Status / Note)", value=data.get("psf", ""))
        notes = st.text_area(
            "Project Notes / Aspects",
            value=data.get("notes", ""),
        )

    with contact_tab:
        contact_name = st.text_input(
            "Primary Contact Name", value=data.get("contact_name", "")
        )
        contact_designation = st.text_input(
            "Designation", value=data.get("contact_designation", "")
        )
        contact_phone = st.text_input(
            "Phone Number", value=data.get("contact_phone", "")
        )
        contact_email = st.text_input(
            "Email ID", value=data.get("contact_email", "")
        )

    data.update(
        {
            "name": name,
            "code": code,
            "status": status,
            "po_date": po_date,
            "initial_training_date": training_date,
            "go_live_date": go_live_date,
            "fame_version": fame_version,
            "pocket_fame": pocket_fame,
            "state": state,
            "initial_manpower": initial_manpower,
            "num_users": num_users,
            "num_branches": num_branches,
            "proforma_integration": proforma_integration,
            "einvoice_integration": einvoice_integration,
            "kyc_aadhaar": kyc_aadhaar,
            "kyc_bank": kyc_bank,
            "sms_integration": sms_integration,
            "sendmail_payslips": sendmail_payslips,
            "sendmail_invoice": sendmail_invoice,
            "bank_integration": bank_integration,
            "psf": psf,
            "notes": notes,
            "contact_name": contact_name,
            "contact_designation": contact_designation,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
        }
    )
    st.session_state["new_client_data"] = data

    if st.button("Create Client", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Client Name is required.")
            return

        payload = data.copy()
        for k in ["po_date", "initial_training_date", "go_live_date"]:
            if isinstance(payload[k], _date):
                payload[k] = payload[k].isoformat()
        create_client(payload)
        st.success(f"Client '{name}' created.")
        st.session_state["new_client_data"] = {}
        st.rerun()


def show_edit_client_dialog(client_id: int):
    from datetime import date as _date

    client = get_client_by_id(client_id)
    if not client:
        st.error("Client not found.")
        return

    @st.dialog(f"Edit Client – {client['name']}")
    def _dlg():
        basic_tab, project_tab, contact_tab = st.tabs(
            ["Basic Details", "Project Details", "Contact Details"]
        )

        with basic_tab:
            name = st.text_input("Client Name *", value=client["name"])
            code = st.text_input("Client Code / Short Name", value=client["code"] or "")
            status = st.selectbox(
                "Status",
                ["Not Started", "In Progress", "On Hold", "Completed", "Churned", "Other"],
                index=(
                    ["Not Started", "In Progress", "On Hold", "Completed", "Churned", "Other"].index(
                        client["status"]
                    )
                    if client["status"] in
                    ["Not Started", "In Progress", "On Hold", "Completed", "Churned", "Other"]
                    else 1
                ),
            )
            po_val = (
                _date.fromisoformat(client["po_date"])
                if client["po_date"]
                else _date.today()
            )
            tr_val = (
                _date.fromisoformat(client["initial_training_date"])
                if client["initial_training_date"]
                else _date.today()
            )
            go_val = (
                _date.fromisoformat(client["go_live_date"])
                if client["go_live_date"]
                else _date.today()
            )
            c1, c2, c3 = st.columns(3)
            with c1:
                po_date = st.date_input("PO Received Date", value=po_val, format="YYYY-MM-DD")
            with c2:
                training_date = st.date_input("Initial Training Date", value=tr_val, format="YYYY-MM-DD")
            with c3:
                go_live_date = st.date_input("Go LIVE Date", value=go_val, format="YYYY-MM-DD")

            fame_version = st.text_input(
                "FaME Version", value=client["fame_version"] or ""
            )
            pocket_fame = st.checkbox(
                "Pocket FaME Enabled", value=bool(client["pocket_fame"])
            )
            state = st.text_input("State", value=client["state"] or "")

        with project_tab:
            initial_manpower = st.number_input(
                "Initial Manpower",
                min_value=0,
                value=int(client["initial_manpower"] or 0),
            )
            num_users = st.number_input(
                "Number of Users",
                min_value=0,
                value=int(client["num_users"] or 0),
            )
            num_branches = st.number_input(
                "Number of Branches",
                min_value=0,
                value=int(client["num_branches"] or 0),
            )

            st.markdown("##### Integrations")
            c1, c2 = st.columns(2)
            with c1:
                proforma_integration = st.checkbox(
                    "Proforma Integration", value=bool(client["proforma_integration"])
                )
                einvoice_integration = st.checkbox(
                    "E-Invoice Integration", value=bool(client["einvoice_integration"])
                )
                kyc_aadhaar = st.checkbox(
                    "KYC – Aadhaar", value=bool(client["kyc_aadhaar"])
                )
                kyc_bank = st.checkbox(
                    "KYC – Bank Account", value=bool(client["kyc_bank"])
                )
            with c2:
                sms_integration = st.checkbox(
                    "SMS Integration", value=bool(client["sms_integration"])
                )
                sendmail_payslips = st.checkbox(
                    "Mail – Pay slips", value=bool(client["sendmail_payslips"])
                )
                sendmail_invoice = st.checkbox(
                    "Mail – Invoice", value=bool(client["sendmail_invoice"])
                )
                bank_integration = st.checkbox(
                    "Bank Integration", value=bool(client["bank_integration"])
                )

            psf = st.text_input("PSF", value=client["psf"] or "")
            notes = st.text_area("Project Notes / Aspects", value=client["notes"] or "")

        with contact_tab:
            contact_name = st.text_input(
                "Primary Contact Name", value=client["contact_name"] or ""
            )
            contact_designation = st.text_input(
                "Designation", value=client["contact_designation"] or ""
            )
            contact_phone = st.text_input(
                "Phone Number", value=client["contact_phone"] or ""
            )
            contact_email = st.text_input(
                "Email ID", value=client["contact_email"] or ""
            )

        if st.button("Save Changes", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Client Name is required.")
                return

            payload = {
                "name": name.strip(),
                "code": code.strip() or None,
                "status": status,
                "po_date": po_date.isoformat(),
                "initial_training_date": training_date.isoformat(),
                "go_live_date": go_live_date.isoformat(),
                "fame_version": fame_version.strip() or None,
                "pocket_fame": pocket_fame,
                "state": state.strip() or None,
                "initial_manpower": int(initial_manpower),
                "num_users": int(num_users),
                "num_branches": int(num_branches),
                "proforma_integration": proforma_integration,
                "einvoice_integration": einvoice_integration,
                "kyc_aadhaar": kyc_aadhaar,
                "kyc_bank": kyc_bank,
                "sms_integration": sms_integration,
                "sendmail_payslips": sendmail_payslips,
                "sendmail_invoice": sendmail_invoice,
                "bank_integration": bank_integration,
                "psf": psf.strip() or None,
                "notes": notes.strip() or None,
                "contact_name": contact_name.strip() or None,
                "contact_designation": contact_designation.strip() or None,
                "contact_phone": contact_phone.strip() or None,
                "contact_email": contact_email.strip() or None,
            }
            update_client(client_id, payload)
            st.success("Client updated.")
            st.rerun()

    _dlg()


def show_client_detail_dialog(client_id: int):
    st.session_state["open_client_dialog"] = client_id  # <– store open dialog state

    @st.dialog("Client Details")
    def _dlg():
        client_detail_view(client_id)

    _dlg()

