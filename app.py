from flask import Flask, render_template, request, abort, send_file
import xml.etree.ElementTree as ET
import json
import os
import cloudscraper
from bs4 import BeautifulSoup

DOWNLOAD_DIR = ('test')

app = Flask(__name__)

official_devices = {
    "Google Pixel 3": {"codename": "blueline", "image": "https://ipmobile.am/wp-content/uploads/2024/04/google_pixel_3_just_black_2.png", "download": "https://evolution-x.org/downloads/blueline"},
    "Google Pixel 3 XL": {"codename": "crosshatch", "image": "https://ipmobile.am/wp-content/uploads/2024/04/google_pixel_3_just_black_2.png", "download": "https://evolution-x.org/downloads/crosshatch"},
    "Google Pixel 3a": {"codename": "sargo", "image": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi6UERQz2Ii54OS7gGkUWjzegjcd7oP0KoK8-iLvo-NXLBkfnNSD019dtwmrwjbmSSF9GNq547tm35jzZl55NEu6MWqjhQSzj2UUWBAbekh3AAuY6bqzk-ZYjuwIFQUOu0Rb3W3Ubc7Vh8/s1600/Blackandwhite_01.png", "download": "https://evolution-x.org/downloads/sargo"},
    "Google Pixel 3a XL": {"codename": "bonito", "image": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi6UERQz2Ii54OS7gGkUWjzegjcd7oP0KoK8-iLvo-NXLBkfnNSD019dtwmrwjbmSSF9GNq547tm35jzZl55NEu6MWqjhQSzj2UUWBAbekh3AAuY6bqzk-ZYjuwIFQUOu0Rb3W3Ubc7Vh8/s1600/Blackandwhite_01.png", "download": "https://evolution-x.org/downloads/bonito"},
    "Oneplus 5": {"codename": "cheeseburger", "image": "https://cdn.opstatics.com/store/20170907/assets/images/support/support-list/model-specs-list/details/5-black.png", "download": "https://evolution-x.org/downloads/cheeseburger"},
    "Oneplus 5T": {"codename": "dumpling", "image": "https://cdn.opstatics.com/store/20170907/assets/images/support/support-list/model-specs-list/details/5-black.png", "download": "https://evolution-x.org/downloads/dumpling"},
    "Oneplus 7": {"codename": "guacamoleb","image": "https://media2.gsm55.com/media/device/4447/4447.png", "download": "https://evolution-x.org/downloads/guacamoleb"},
    "Oneplus 7 Pro": {"codename": "guacamole", "image": "https://cdn.revendo.com/media/08/63/34/1662390983/oneplus-7-pro-nebula-blue-guenstig-gebraucht-kaufen.png.png", "download": "https://evolution-x.org/downloads/guacamole"},
    "Oneplus 7T": {"codename": "hotdogb", "image": "https://cdn.revendo.com/media/86/84/34/1662392047/oneplus-7t-glacier-blue-guenstig-gebraucht-kaufen.png.png", "download": "https://evolution-x.org/downloads/hotdogb"},
    "Oneplus 7T Pro": {"codename": "hotdog", "image": "https://www.gizmochina.com/wp-content/uploads/2019/09/oneplus_7t_pro_1_3.png", "download": "https://evolution-x.org/downloads/hotdog"},
    "Poco M2 Pro": {"codename": "gram (MiAtoll serie)", "image": "https://c0.lestechnophiles.com/images.frandroid.com/wp-content/uploads/2020/07/xiaomi-poco-m2-pro-frandroid-2020-768x768.png", "download": "https://evolution-x.org/downloads/miatoll"},
    "Xiaomi Mi A3": {"codename": "laurel_sprout", "image": "https://i01.appmifile.com/webfile/globalimg/T/20190718094400.png", "download": "https://evolution-x.org/downloads/laurel_sprout"},
    "Xiaomi Mi Mix 2S": {"codename": "polaris", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1526037372.73933512.png", "download": "https://evolution-x.org/downloads/polaris"},
    "Xiaomi Mi Note 2": {"codename": "Scorpio", "image": "https://www.dpreview.com/files/p/E~C0x0S1200x900T600x450~articles/5706742151/mi_note2_thumbnail.png", "download": "https://evolution-x.org/downloads/scorpio"},
    "Xiaomi Redmi Note 9S": {"codename": "curtana (MiAtoll serie)", "image": "https://media2.gsm55.com/media/device/4575/4575.png", "download": "https://evolution-x.org/downloads/miatoll"},
    "Xiaomi Redmi Note 9 Pro": {"codename": "joyeuse (MiAtoll serie)", "image": "https://media2.gsm55.com/media/device/4572/4572.png", "download": "https://evolution-x.org/downloads/miatoll"},
    "Xiaomi Redmi Note 9 Pro (India)": {"codename": "curtana (MiAtoll serie)", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1595220196.89229402!400x400!85.png", "download": "https://evolution-x.org/downloads/miatoll"},
    "Xiaomi Redmi Note 9 Pro Max": {"codename": "excalibur (MiAtoll serie)", "image": "https://media2.gsm55.com/media/device/4572/4572.png", "download": "https://evolution-x.org/downloads/miatoll"},
    "Xiaomi Redmi Note 10 lite": {"codename": "curtana (MiAtoll serie)", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1588937747.86846999!400x400!85.png", "download": "https://evolution-x.org/downloads/miatoll"}
}


unofficial_devices = {
    "Motorola G30\n(Work in progress.)": {"codename": "caprip", "image": "https://storage.comprasmartphone.com/smartphones/motorola-moto-g30.png", "download": "https://evox.onelots.fr/download"},
    "Oneplus Nord N10 5G\n(Work in progress.)": {"codename": "billie", "image": "https://oasis.opstatics.com/content/dam/oasis/page/billie/N10-Frame11.png", "download": "https://evox.onelots.fr/download"},
    "Redmi Note 11 Pro 5G\n(Work in progress.)": {"codename": "Veux", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1648199221.0063088.png", "download": "https://evolution-x.org/downloads/veux"},
    "Redmi Note 11S\n(Work in progress.)": {"codename": "fleur", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1643013636.25845935.png", "download": "https://evox.onelots.fr/download"},
    "Samsung S9+\n(Work in progress.)": {"codename": "star2lte", "image": "https://www.thekase.com/on/demandware.static/-/Sites-tk-product/default/dw95aa7775/38937129/132901_large.png", "download": "https://evox.onelots.fr/download"},
}

@app.route('/')
def home():
    return render_template('index.html', official_devices=official_devices, unofficial_devices=unofficial_devices)

def check_size(directory_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    if total_size < 1000:
        return f"{total_size} B"
    elif total_size < 1000 * 1000:
        return f"{total_size / 1000:.2f} KB"
    elif total_size < 1000 * 1000 * 1000:
        return f"{total_size / 1000 / 1000:.2f} MB"
    else:
        return f"{total_size / 1000 / 1000 / 1000:.2f} GB"


@app.route('/downloads')
def downloads():
    path = request.args.get('path', '')
    base_dir = os.environ.get('DOWNLOAD_DIR', 'downloads')
    current_path = os.path.join(base_dir, path)

    try:
        if not os.path.exists(current_path):
            abort(404)

        if not os.path.realpath(current_path).startswith(os.path.realpath(base_dir)):
            abort(403)

        items = []
        if os.path.isdir(current_path):
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(item_path)
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'path': os.path.join(path, item) if path else item
                })

            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

            parent_path = os.path.dirname(path) if path else None
            total_size = check_size('downloads')
            folder_size = check_size(current_path)
            return render_template('downloads.html', items=items, current_path=path, parent_path=parent_path, total_size=total_size, folder_size=folder_size)
        else:
            return send_file(current_path, as_attachment=True, mimetype="application/octet-stream")
    except PermissionError:
        abort(403)


# Yes I'm lazy so I'll just copy/paste
@app.route('/testers')
def testers():
    path = request.args.get('path', '')
    base_dir = os.environ.get('DOWNLOAD_DIR', 'testers')
    current_path = os.path.join(base_dir, path)

    try:
        if not os.path.exists(current_path):
            abort(404)

        if not os.path.realpath(current_path).startswith(os.path.realpath(base_dir)):
            abort(403)

        items = []
        if os.path.isdir(current_path):
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(item_path)
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'path': os.path.join(path, item) if path else item
                })

            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

            parent_path = os.path.dirname(path) if path else None
            total_size = check_size('testers')
            folder_size = check_size(current_path)
            return render_template('testers.html', items=items, current_path=path, parent_path=parent_path, total_size=total_size, folder_size=folder_size)
        else:
            return send_file(current_path, as_attachment=True, mimetype="application/octet-stream")
    except PermissionError:
        abort(403)

@app.route('/eta')
def eta():
    return render_template('eta.html')


@app.route('/when')
def when():
    scraper = cloudscraper.create_scraper()

    url = 'https://hel-eu-1.ci.evolution-x.org/'

    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('div', {'id': 'view-message'}).find('table')

    head = table.find('thead')
    days = []
    devices = []
    for th in head.find_all('th'):
        days.append(th.text)

    for tr in table.find('tbody').find_all('tr'):
        device = {}
        for i, td in enumerate(tr.find_all('td')):
            if i == 0:
                device['hour'] = td.text
            else:
                device[days[i]] = td.text
        devices.append(device)
    return render_template('when.html', devices=devices)

@app.route('/tools')
def tools():
    tools_data = [
        {'name': 'Manifest to Dependencies', 'description': 'This tool will convert your device.xml to a clean evolution.dependencies file', 'link': '/manifest_to_dependencies', 'icon': 'file-text'},
        {'name': 'Mystery tool', 'description': 'Coming up later', 'link': '/second_tool', 'icon': 'message-square'},
    ]
    return render_template('tools.html', tools=tools_data)

# ------------------ KANGED TO AIDAN WARNER ------------------

def parse_xml(xml_content):
    root = ET.fromstring(xml_content)
    repositories = []

    for project in root.findall('project'):
        repo_info = {
            "repository": project.get('name'),
            "target_path": project.get('path'),
            "remote": project.get('remote'),  # Capture the remote
            "branch": project.get('revision', '')  # Use revision as branch
        }
        repositories.append(repo_info)
    
    return repositories

def convert_to_dependencies(repositories, branch_mapping, remote_mapping):
    dependencies = []
    for repo in repositories:
        dep = {
            "remote": remote_mapping.get(repo["repository"], repo["remote"]),  # Use the provided remote or default
            "repository": repo["repository"],
            "target_path": repo["target_path"],
            "branch": branch_mapping.get(repo["repository"], repo["branch"] or '')  # Use user branch or default revision
        }
        dependencies.append(dep)
    
    return json.dumps(dependencies, indent=2)

@app.route('/manifest_to_dependencies', methods=['GET', 'POST'])
def manifest_to_deps():
    device_codename = ""
    xml_content = ""
    error_message = ""

    if request.method == 'POST':
        if 'xml_content' in request.form:
            # Process XML
            xml_content = request.form.get('xml_content')  # Capture the XML content entered
            device_codename = request.form.get('device_codename', "")
            if xml_content:
                repositories = parse_xml(xml_content)  # Parse XML content
                repositories_json = json.dumps(repositories)  # Serialize repositories
                return render_template('tools/manifest_to_deps.html', repositories=repositories, repositories_json=repositories_json, device_codename=device_codename, xml_content=xml_content, error_message=error_message)  # Pass back xml_content

        elif 'convert' in request.form:
            branch_mapping = {}
            remote_mapping = {}
            device_codename = request.form.get('device_codename', "")
            xml_content = request.form.get('xml_content', "")

            try:
                repositories_json = request.form.get('repositories')
                if not repositories_json:
                    raise json.JSONDecodeError("No repositories JSON", "", 0)
                repositories = json.loads(repositories_json)
            except json.JSONDecodeError as e:
                return render_template(
                    'tools/manifest_to_deps.html',
                    output="Error decoding JSON: " + str(e),
                    device_codename=device_codename,
                    xml_content=xml_content,
                    repositories_json="[]"
                )

            # Collect user-defined branches and remotes
            for repo in request.form:
                if repo.startswith('branch_'):
                    repo_name = repo.split('_', 1)[1]
                    branch_value = request.form[repo].strip()
                    branch_mapping[repo_name] = branch_value

                elif repo.startswith('remote_'):
                    repo_name = repo.split('_', 1)[1]
                    remote_mapping[repo_name] = request.form[repo].strip()

            remote_for_all = request.form.get('remoteForAll', '').strip()
            branch_for_all = request.form.get('branchForAll', '').strip()

            # Apply to all if provided
            if remote_for_all:
                for repo in repositories:
                    remote_mapping[repo["repository"]] = remote_for_all

            if branch_for_all:
                for repo in repositories:
                    branch_mapping[repo["repository"]] = branch_for_all

            # --- Check for empty fields ---
            missing_fields = False
            for repo in repositories:
                repo_name = repo["repository"]
                remote_val = remote_mapping.get(repo_name, "").strip()
                branch_val = branch_mapping.get(repo_name, "").strip()
                if not remote_val or not branch_val:
                    missing_fields = True
                    break

            if missing_fields:
                error_message = "All Remote and Branch fields must be filled out."
                return render_template(
                    'tools/manifest_to_deps.html',
                    repositories=repositories,
                    repositories_json=json.dumps(repositories),
                    device_codename=device_codename,
                    xml_content=xml_content,
                    error_message=error_message
                )
            # --- End check ---

            # Generate dependencies based on user branches and remotes
            dependencies = convert_to_dependencies(repositories, branch_mapping, remote_mapping)
            return render_template(
                'tools/manifest_to_deps.html',
                output=dependencies,
                repositories=repositories,
                repositories_json=json.dumps(repositories),
                device_codename=device_codename,
                branches=branch_mapping,
                xml_content=xml_content,
                error_message=""
            )

    return render_template('tools/manifest_to_deps.html', output='', repositories=[], device_codename='', xml_content='', error_message='')

objectifs = {
    "objectif1": {
        "nom": "New screen for the Sony Xperia 10 IV",
        "description": "My Sony Xperia 10 IV's screen is broken, so I need to replace it with a new one. But it costs around $90.",
        "pourcentage": 1    }
}


@app.route('/goals')
def objectifs_func():
    return render_template('objectives.html', objectifs=objectifs)


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error="403 Forbidden: You don't have permission to access this resource."), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="404 Not Found: The requested resource could not be found."), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)