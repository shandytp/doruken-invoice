import streamlit as st
from weasyprint import CSS
from src.utils.helper import (insert_data, get_user_options, update_payment_status,
                              fetch_invoice_data, get_users, generate_json_invoice,
                              render_template_to_pdf, get_qty_data, get_revenue_data,
                              format_currency, get_paid_user_data)


st.title("Invoice Doruken Data Generator (for internal)")

DORUKEN_LOGO = "assets/doruken_logo.png"

TEMPLATE_HTML_PATH = "template/invoice_template_001.html"

TEMPLATE_CSS = [
    CSS("static/invoice_template_001.css"),
    CSS("https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"),
    CSS("https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css")
]


def main():

    st.logo(DORUKEN_LOGO, icon_image = DORUKEN_LOGO, size = "large")
    
    # st.sidebar.image(DORUKEN_LOGO)

    selected_box = st.sidebar.selectbox(
        label = "Menu",
        options = ("Generate Invoice Data", "Update Status Payment",
                   "Show Data", "Generate Invoice File", "Dashboard")
    )
    
    if selected_box == "Generate Invoice Data":

        with st.form(key = "invoice_form", clear_on_submit = True):
            total_price = 0
            upsize_price = 0
            
            nama = st.text_input(
                label = "Nama Customer",
                help = "Nama customer yang ingin dimasukkan pada Invoice"
            )
            
            email = st.text_input(
                label = "Email Customer",
                help = "Email customer yang ingin dimasukkan pada Invoice"
            )
            
            phone = st.text_input(
                label = "Nomor HP Customer",
                help = "Nomor HP customer yang ingin dimasukkan ke Invoice"
            )
            
            apparel_package = st.selectbox(
                label = "Package yang dipilih Customer",
                options = ("Harris Gothic", "Ayyis Dino", "Bundle Gothic and Ayyis"),
                help = "Apparel Package yang dipilih oleh Customer"
            )
            
            if apparel_package == "Harris Gothic":
                total_price += 150_000
                
            elif apparel_package == "Ayyis Dino":
                total_price += 150_000
                
            elif apparel_package == "Bundle Gothic and Ayyis":
                total_price += 280_000
                
            apparel_size = st.selectbox(
                label = "Size Apparel Customer",
                options = ("S", "M", "L", "XL", "2XL", "3XL", "4XL"),
                help = "Size Apparel yagn dipilih oleh Customer"
            )
            
            if apparel_size == "2XL":
                total_price += 5000
                upsize_price += 5000
                
            elif apparel_size == "3XL":
                total_price += 10_000
                upsize_price += 10_000
                
            elif apparel_size == "4XL":
                total_price += 15_000
                upsize_price += 15_000
                
            qty = st.number_input(
                label = "Qty Apparel",
                min_value = 1,
                help = "Jumlah qty yang dibeli customer"
            )
                
            address = st.text_area(
                label = "Alamat Customer",
                help = "Alamat customer yang ingin dimasukkan ke Invoice"
            )
            
            shipping_cost = st.number_input(
                label = "Biaya Ongkir",
                min_value = 0,
                help = "Masukkan biaya ongkir yang dibayar oleh customer"
            )
            
            due_date = st.date_input(
                label = "Tanggal pelunasan akhir Customer",
                value = "today",
                help = "Masukkan tanggal akhir pelunasan customer"
            )
            
            total_price = (total_price * qty) + shipping_cost
            
            submit_button = st.form_submit_button("Submit")
            
        if submit_button:
            if nama and email and phone and apparel_package and apparel_size and address:
                insert_data(table_name = "invoice_table",
                            nama = nama,
                            email = email,
                            phone = phone,
                            apparel_package = apparel_package,
                            apparel_size = apparel_size,
                            upsize_price = upsize_price,
                            qty = qty,
                            address = address,
                            shipping_cost = shipping_cost,
                            due_date = due_date,
                            total_price = total_price)

            else:
                st.error("Isi semua data!")

    elif selected_box == "Update Status Payment":
        customer_names = get_user_options()
        
        if customer_names:
            with st.form(key = "update_payment_form", clear_on_submit = True):
                selected_name = st.selectbox(
                    label = "Customer Name",
                    options = customer_names,
                    help = "Pilih Customer yang ingin di update Status Payment"
                )
                
                submit_button = st.form_submit_button("Update Payment Status")
                
            if submit_button:
                success = update_payment_status(name = selected_name)
                
                if success:
                    st.success(f"Payment Status customer: {selected_name} berhasil di update")
                    
                else:
                    st.error("Failed to update payment status.")
                    
        else:
            st.error("Tidak ada customer")

    elif selected_box == "Show Data":
        invoice_data = fetch_invoice_data()
        
        if invoice_data is not None and not invoice_data.empty:
            st.header("Invoice Doruken Data")
            st.dataframe(invoice_data)
            
        else:
            st.warning("Data Invoice tidak ada yang bisa diambil dari Database!")
            
    elif selected_box == "Generate Invoice File":
        users_data = get_users()
        
        selected_name = st.selectbox(
            label = "Customer Name",
            options = users_data
        )

        if st.button("Generate Invoice"):
            invoice_data = generate_json_invoice(nama = selected_name)
            
            with open(TEMPLATE_HTML_PATH) as template_file:
                template_html = template_file.read()
                
            pdf_buffer = render_template_to_pdf(template_file = template_html,
                                                context = invoice_data,
                                                styles = TEMPLATE_CSS)
            
            st.download_button(
                label = "Download Invoice PDF",
                data = pdf_buffer,
                file_name = f"invoice-doruken-{invoice_data['invoiceNumber']}-{invoice_data['client']['firstName']}.pdf",
                mime = "application/pdf"
            )
            
            st.success(f"Invoice for {selected_name} success generate!")

    elif selected_box == "Dashboard":
        a, b, c, d = st.columns(4)
        e, f, g, h = st.columns(4)
        i, j = st.columns(2)
        
        a.metric("Total Order QTY", value = get_qty_data(data = "total"), border = True)
        b.metric("Order QTY Ayyis", value = get_qty_data(data = "ayyis"), border = True)
        c.metric("Order QTY Gothic", value = get_qty_data(data = "gothic"), border = True)
        d.metric("Order QTY Bundle", value = get_qty_data(data = "bundle"), border = True)
        
        e.metric("Total Revenue", value = format_currency(get_revenue_data(data="total")), border=True)
        f.metric("Total Revenue Ayyis", value = format_currency(get_revenue_data(data="ayyis")), border=True)
        g.metric("Total Revenue Gothic", value = format_currency(get_revenue_data(data="gothic")), border=True)
        h.metric("Total Revenue Bundle", value = format_currency(get_revenue_data(data="bundle")), border=True)
        
        i.metric("Total Paid Users", value = get_paid_user_data(data = "paid"), border = True)
        j.metric("Total Not Paid Users", value = get_paid_user_data(data = "not_paid"), border = True)


if __name__ == "__main__":
    main()
