import zipfile
import os
import re
import requests
import json
import math
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def unzip_and_map(main_zip_path, extract_to):
    # Unzip the main zip file
    unzip_file(main_zip_path, extract_to)

    proposal_paths = {}
    index = 1  # Start an index for each unzipped directory

    # Unzip nested zip files and collect file paths
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.endswith('.zip'):
                # Unzip this nested zip file
                zip_file_path = os.path.join(root, file)
                subdirectory_path = os.path.join(root, os.path.splitext(file)[0])
                os.makedirs(subdirectory_path, exist_ok=True)
                unzip_file(zip_file_path, subdirectory_path)

                # Collect file paths after unzipping
                for sub_root, sub_dirs, sub_files in os.walk(subdirectory_path):
                    for sub_file in sub_files:
                        # Use regular expressions to match files starting with 'PROPOSAL' followed by a number
                        match = re.match(r'PROPOSAL(\d+)', sub_file)
                        if match:
                            proposal_num = int(match.group(1))
                            # Now we're using a combination of index and proposal number for uniqueness
                            key = (index * 1000) + proposal_num

                            if key not in proposal_paths:
                                proposal_paths[key] = [None, None]

                            if sub_file.endswith('.3D.json'):
                                proposal_paths[key][1] = os.path.join(sub_root, sub_file)
                            elif sub_file.endswith('.json'):
                                proposal_paths[key][0] = os.path.join(sub_root, sub_file)

                index += 1  # Increment the index after processing each zip file

    return proposal_paths


def fetch_3d_particles(building_id):
    # URL of the API endpoint
    url = 'https://livekluster.ehr.ee/api/3dtwin/v1/rest-api/particles'

    # Headers to specify that we accept JSON
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Data payload with the building ID
    payload = [building_id]

    # Making the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        # Handle errors or unsuccessful responses
        print(f"Error fetching data: {response.status_code}")
        return None


def adjust_data(data):
    # Find the minimum values for x0 and y0
    min_x0 = min(item['x0'] for item in data)
    min_z0 = min(item['z0'] for item in data)
    min_y0 = min(item['y0'] for item in data)
    min_x1 = min(item['x1'] for item in data)
    min_y1 = min(item['y1'] for item in data)
    min_z1 = min(item['z1'] for item in data)
    min_x2 = min(item['x2'] for item in data)
    min_y2 = min(item['y2'] for item in data)
    min_z2 = min(item['z2'] for item in data)

    # Adjust the coordinates relative to the minimum values found
    for item in data:
        item['x0'] -= min_x0
        item['y0'] -= min_y0
        item['z0'] -= min_z0
        item['x1'] -= min_x1
        item['y1'] -= min_y1
        item['z1'] -= min_z1
        item['x2'] -= min_x2
        item['y2'] -= min_y2
        item['z2'] -= min_z2

    return data


def calculate_attributes(data):
    # Reinitialize variables for calculations
    total_area = 0
    nr_of_particles = len(data)
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

    # Iterate through each particle to perform calculations
    for particle in data:
        # Update total area
        total_area += particle['area']

        # Update min and max coordinates for all three corners of the triangle
        coords = [(particle['x0'], particle['y0'], particle['z0']),
                  (particle['x1'], particle['y1'], particle['z1']),
                  (particle['x2'], particle['y2'], particle['z2'])]

        for x, y, z in coords:
            min_x, min_y, min_z = min(min_x, x), min(min_y, y), min(min_z, z)
            max_x, max_y, max_z = max(max_x, x), max(max_y, y), max(max_z, z)

    # Calculate dimensions
    length = max_x - min_x
    width = max_y - min_y
    height = max_z - min_z

    volume = total_area * height

    return {"area": total_area, "particles": nr_of_particles, "length": length, "width": width, "height": height,
            "volume": volume}


def building_attributes(mapping):
    attributes = {}
    for key in mapping:
        if mapping[key][1] == None:
            continue
        try:
            with open(mapping[key][1], 'r') as file:
                data = json.load(file)[0]['particles']

            attributes[key] = calculate_attributes(data)
        except:
            continue

    return attributes


def euclidean_distance(attributes1, attributes2):
    area = math.pow(attributes1['area'] - attributes2['area'], 2)
    particles = math.pow(attributes1['particles'] - attributes2['particles'], 2)
    length = math.pow(attributes1['length'] - attributes2['length'], 2)
    width = math.pow(attributes1['width'] - attributes2['width'], 2)
    height = math.pow(attributes1['height'] - attributes2['height'], 2)
    volume = math.pow(attributes1['volume'] - attributes2['volume'], 2)
    return math.sqrt(area + particles + length + width + height + volume)


def calculate_distances(param, new_building_data):
    distances = {}
    for key in param.keys():
        attributes1 = param[key]
        attributes2 = calculate_attributes(new_building_data)
        distance = euclidean_distance(attributes1, attributes2)
        distances[key] = distance
    return distances


def find_volume(proposal_house_dimensions):
    total_area = 0
    z_coordinates = []

    # Iterate through each particle to perform calculations
    for particle in proposal_house_dimensions:
        z_coordinates.append(particle['z0'])
        z_coordinates.append(particle['z1'])
        z_coordinates.append(particle['z2'])

        total_area += particle['area']

    max_c = max(z_coordinates)
    min_c = min(z_coordinates)

    if min_c == 0:
        height = max_c
    else:
        height = max_c / min_c

    return total_area * height


def rescale(proposal_files, new_dimensions):
    with open(proposal_files[1], 'r') as file2:
        proposal_house_dimensions = json.load(file2)[0]['particles']
    with open(proposal_files[0], 'r') as file1:
        proposal = json.load(file1)
    proposal_house_volume = find_volume(proposal_house_dimensions)
    new_house_volume = find_volume(new_dimensions)
    index = new_house_volume / proposal_house_volume
    total_cost = 0
    for costItem in proposal['costItems']:
        if costItem['unit'] == "m²" or costItem['unit'] == "m2" or costItem['unit'] == "m3":
            quant = round(float(costItem['quantity']) * index, 2)
            costItem['quantity'] = quant
            cost = round(float(costItem['totalUnitPrice']) * quant, 2)
            costItem['totalCost'] = cost
            total_cost += cost
    proposal['totalCostExclVAT'] = round(total_cost, 2)
    proposal['VAT'] = round(total_cost * 0.22, 2)
    proposal['totalCost'] = round(total_cost * 1.22, 2)
    return proposal

def generate_pdf(proposal, filename):
    # Define your document's header details
    company_name = "<b>Company XYZ</b>"
    company_contact_info = "1234 Business Rd., Business City | +123 456 7890 | contact@companyxyz.com"
    document_title = "Price Quote / Proposal for Exterior Renovation"
    quote_number = "<b>Quote No:</b> 123456"
    customer_name = "<b>Customer Name:</b> John Doe"
    object_address = "<b>Object Address:</b> 1234 Main St, Anytown"
    quote_date = "<b>Quote Date:</b> 2023-02-02"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # Custom styles
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle('CustomStyle', parent=styles['Normal'], fontSize=10, leading=12)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=12, leading=14)

    # Add company and document details
    elements.append(Paragraph(company_name, header_style))
    elements.append(Paragraph(company_contact_info, custom_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(document_title, header_style))
    elements.append(Paragraph(quote_number, custom_style))
    elements.append(Spacer(1, 12))

    # Add customer and project details
    elements.append(Paragraph(customer_name, custom_style))
    elements.append(Paragraph(object_address, custom_style))
    elements.append(Paragraph(quote_date, custom_style))
    elements.append(Spacer(1, 12))

    # Generate table data from the JSON
    table_data = [['Description', 'Quantity', 'Unit', 'Unit Price', 'Total Cost']]
    for item in proposal['costItems']:
        row = [item['description'], item['quantity'], item['unit'], item['totalUnitPrice'], item['totalCost']]
        table_data.append(row)

    # Append the total cost information with merging setup
    table_data.append(['Total Cost Excl. VAT:', '', '', '', proposal['totalCostExclVAT']])
    table_data.append(['VAT (22%):', '', '', '', proposal['VAT']])
    table_data.append(['Total Cost:', '', '', '', proposal['totalCost']])

    # Create and style the table
    table = Table(table_data)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -4), 'LEFT'),  # Align the description column text to the left for all but the last 3 rows
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -4), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Merge cells for the last three rows
        ('SPAN', (0, -3), (-2, -3)),  # Merge description cells for "Total Cost Excl. VAT:"
        ('SPAN', (0, -2), (-2, -2)),  # Merge description cells for "VAT (22%):"
        ('SPAN', (0, -1), (-2, -1)),  # Merge description cells for "Total Cost:"
        ('ALIGN', (0, -3), (-1, -1), 'RIGHT'),  # Ensure right alignment for the last 3 rows
    ])
    table.setStyle(table_style)
    elements.append(table)

    # Footer information
    footer_elements = [
        Paragraph("Thank you for considering our services. We look forward to the opportunity to work with you.",
                  custom_style),
        Spacer(1, 12),
        Paragraph("For any questions or further information, please do not hesitate to contact us.", custom_style),
        Paragraph("This proposal is valid for 30 days from the date of issuance.", custom_style)
    ]
    # Add footer elements
    elements.extend(footer_elements)
    # Build the PDF
    doc.build(elements)


def make_proposal(house_id):
    zip_path = '/Users/maarjahoop/PycharmProjects/bigdata4digitalconstruction/16/02_04_2024_andmestik.zip'  # Replace with the path to your zip file
    extract_to = '/Users/maarjahoop/PycharmProjects/bigdata4digitalconstruction/16'  # Replace with the path where you want to extract the files
    mapping = unzip_and_map(zip_path, extract_to)
    attributes = building_attributes(mapping)


    data = fetch_3d_particles(house_id)
    new_building_data = adjust_data(data[0]['particles'])

    distances = calculate_distances(attributes, new_building_data)
    minimum = 10000000000000
    min_key = 0
    for k, v in distances.items():
        if v < minimum:
            minimum = v
            min_key = k
    new_proposal = rescale(mapping[min_key], new_building_data)

    return new_proposal




# house = "120242890"
# proposal = make_proposal(house)
#
# pdf_name = "Renovation_Proposal_" + house + ".pdf"
#
# generate_pdf(proposal, pdf_name)


