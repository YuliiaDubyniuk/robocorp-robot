from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive



@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=100)
    open_robot_order_website()
    download_orders_file()
    fill_form_with_data()
    

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    close_annoying_modal()

def download_orders_file():
    """Downloads CSV file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def read_data_and_return():
    """reads data from file and returns table"""
    file_with_data = Tables()
    orders_table = file_with_data.read_table_from_csv("orders.csv")
    return orders_table

def fill_form_with_data():
    """fills the form for each order"""
    orders = read_data_and_return()

    for order in orders:
        fill_the_form_and_submit_order(order)

def close_annoying_modal():
    """closes modal on robot website"""
    page = browser.page()  
    page.click("text=OK")

def fill_the_form_and_submit_order(order):
    page = browser.page()
    head_number = str(order["Head"])
    page.select_option("#head", {head_number})
    body_number = order["Body"]
    page.check(f"input[name='body'][value='{body_number}']")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])   
    page.click("#order")
    order_another_btn = page.is_visible("#order-another")
    if order_another_btn:
        receipt_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshot_path, receipt_path)
        page.click("#order-another")
        close_annoying_modal()        

    else:
        print("Form submission failed. Retrying...")
        page.click("#order")


def store_receipt_as_pdf(order_number):
    """Saves receipt as pdf file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    receipt_path = pdf.html_to_pdf(receipt_html, "output/receipts/robot_receipt_{}.pdf".format(order_number))
    return receipt_path

def screenshot_robot(order_number):
    """Takes a screenshot of the robot"""
    page = browser.page()
    screenshot_path = "output/screenshots/robot_image_{}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the screenshot to the receipt"""
    pdf = PDF()    
    # pdf.add_watermark_image_to_pdf(image_path=screenshot, source_path=pdf_file, output_path=pdf_file)
    pdf.add_files_to_pdf(screenshot, pdf_file, append=True)


# def archive_receipts():
#     """Archives folder with all receipts in ZIP file"""
#     lib = Archive()
#     lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip')