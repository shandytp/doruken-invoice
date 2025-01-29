import streamlit as st
import datetime
from weasyprint import CSS
from src.utils.helper import (
    insert_data, get_user_options, update_payment_status, fetch_invoice_data,
    get_users, generate_json_invoice, render_template_to_pdf, get_qty_data,
    get_revenue_data, format_currency, get_paid_user_data, get_ongkir
)

st.title("Invoice Doruken Data Generator (for internal)")

DORUKEN_LOGO = "assets/doruken_logo.png"
TEMPLATE_HTML_PATH = "template/invoice_template_001.html"

TEMPLATE_CSS = [
    CSS("static/invoice_template_001.css"),
    CSS("https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"),
    CSS("https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css")
]


def main():
    st.logo(DORUKEN_LOGO, icon_image= DORUKEN_LOGO, size = "large")  # Fix logo display

    selected_box = st.sidebar.selectbox(
        label="Menu",
        options=["Generate Invoice Data", "Update Status Payment",
                 "Show Data", "Generate Invoice File", "Dashboard"]
    )
    
    if selected_box == "Generate Invoice Data":
        with st.form(key="invoice_form", clear_on_submit=True):
            total_price = 0
            upsize_price = 0
            
            nama = st.text_input("Nama Customer", help="Nama customer pada Invoice")
            email = st.text_input("Email Customer", help="Email customer pada Invoice")
            phone = st.text_input("Nomor HP Customer", help="Nomor HP customer ke Invoice")

            # Price Mapping for Packages
            package_prices = {
                "Harris Gothic": 150_000,
                "Ayyis Dino": 150_000,
                "Bundle Gothic and Ayyis": 280_000
            }
            
            apparel_package = st.selectbox(
                "Package yang dipilih Customer",
                options=list(package_prices.keys()),
                help="Apparel Package yang dipilih"
            )
            
            total_price += package_prices[apparel_package]

            # Price Mapping for Sizes
            size_prices = {"2XL": 5000, "3XL": 10_000, "4XL": 15_000}
            apparel_size = st.selectbox("Size Apparel Customer", ["S", "M", "L", "XL", "2XL", "3XL", "4XL"])
            
            if apparel_size in size_prices:
                upsize_price = size_prices[apparel_size]
                total_price += upsize_price
            
            qty = st.number_input("Qty Apparel", min_value=1, help="Jumlah qty yang dibeli customer")

            address = st.text_area("Alamat Customer", help="Alamat customer pada Invoice")
            origin = st.text_input("Kota Pengirim", value="depok")

            destination = st.text_input("Kota Customer", help="Kota Customer tujuan")
            
            if "shipping_cost" not in st.session_state:
                st.session_state.shipping_cost = 0

            # Shipping Cost Calculation
            shipping_cost = 0
            if st.form_submit_button("Calculate Shipping Cost") and destination:
                ongkir_data = get_ongkir(origin=origin, destination=destination)
                if not ongkir_data.empty:
                    st.session_state.shipping_cost = int(ongkir_data.iloc[0]["price"])
                else:
                    st.error("Gagal mendapatkan biaya ongkir! Periksa input.")
                    
            shipping_cost = st.number_input("Biaya Ongkir", value=st.session_state.shipping_cost, help="Masukkan biaya ongkir")
            
            due_date = st.date_input("Tanggal pelunasan akhir", value=datetime.date.today())

            total_price = (total_price * qty) + st.session_state.shipping_cost
            
            submit_button = st.form_submit_button("Submit")
        
            if submit_button:
                if nama and email and phone and address:
                    insert_data(
                        table_name="invoice_table",
                        nama=nama, email=email, phone=phone,
                        apparel_package=apparel_package, apparel_size=apparel_size,
                        upsize_price=upsize_price, qty=qty, address=address,
                        origin=origin, destination=destination,
                        shipping_cost=shipping_cost, due_date=due_date, total_price=total_price
                    )
                    st.success("Invoice berhasil disimpan!")
                else:
                    st.error("Isi semua data!")

    elif selected_box == "Update Status Payment":
        customer_names = get_user_options()
        if customer_names:
            with st.form(key="update_payment_form", clear_on_submit=True):
                selected_name = st.selectbox("Customer Name", customer_names, help="Pilih Customer untuk update")
                submit_button = st.form_submit_button("Update Payment Status")
            
            if submit_button:
                if update_payment_status(name=selected_name):
                    st.success(f"Status pembayaran {selected_name} berhasil diperbarui")
                else:
                    st.error("Gagal memperbarui status pembayaran.")
        else:
            st.error("Tidak ada customer")

    elif selected_box == "Show Data":
        invoice_data = fetch_invoice_data()
        if not invoice_data.empty:
            st.header("Invoice Doruken Data")
            st.dataframe(invoice_data)
        else:
            st.warning("Data Invoice tidak ditemukan!")

    elif selected_box == "Generate Invoice File":
        users_data = get_users()
        selected_name = st.selectbox("Customer Name", users_data)

        if st.button("Generate Invoice"):
            invoice_data = generate_json_invoice(nama=selected_name)
            
            with open(TEMPLATE_HTML_PATH) as template_file:
                template_html = template_file.read()
                
            pdf_buffer = render_template_to_pdf(template_file=template_html, context=invoice_data, styles=TEMPLATE_CSS)
            
            st.download_button(
                label="Download Invoice PDF",
                data=pdf_buffer,
                file_name=f"invoice-doruken-{invoice_data['invoiceNumber']}-{invoice_data['client']['firstName']}.pdf",
                mime="application/pdf"
            )
            st.success(f"Invoice untuk {selected_name} berhasil dibuat!")

    elif selected_box == "Dashboard":
        cols1 = st.columns(4)
        cols2 = st.columns(4)
        cols3 = st.columns(2)

        cols1[0].metric("Total Order QTY", get_qty_data("total"), border = True)
        cols1[1].metric("Order QTY Ayyis", get_qty_data("ayyis"), border = True)
        cols1[2].metric("Order QTY Gothic", get_qty_data("gothic"), border = True)
        cols1[3].metric("Order QTY Bundle", get_qty_data("bundle"), border = True)

        cols2[0].metric("Total Revenue", format_currency(get_revenue_data("total")), border = True)
        cols2[1].metric("Total Revenue Ayyis", format_currency(get_revenue_data("ayyis")), border = True)
        cols2[2].metric("Total Revenue Gothic", format_currency(get_revenue_data("gothic")), border = True)
        cols2[3].metric("Total Revenue Bundle", format_currency(get_revenue_data("bundle")), border = True)

        cols3[0].metric("Total Paid Users", get_paid_user_data("paid"), border = True)
        cols3[1].metric("Total Not Paid Users", get_paid_user_data("not_paid"), border = True)


if __name__ == "__main__":
    main()
