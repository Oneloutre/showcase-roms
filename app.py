from flask import Flask, render_template, request, abort, redirect
import xml.etree.ElementTree as ET
import json
import os
import cloudscraper
from bs4 import BeautifulSoup

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
BUCKET     = os.getenv("R2_BUCKET")

DOWNLOADS_PREFIX = os.getenv("R2_DOWNLOADS_PREFIX", "downloads/")
TESTERS_PREFIX   = os.getenv("R2_TESTERS_PREFIX", "testers/")

if not all([ACCOUNT_ID, ACCESS_KEY, SECRET_KEY, BUCKET]):
    raise RuntimeError("R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY / R2_BUCKET manquants.")

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="auto",
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

def _norm_relpath(p: str) -> str:
    p = (p or "").replace("\\", "/")
    parts = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    return "/".join(parts)

def _ensure_trailing_slash(p: str) -> str:
    return p if p.endswith("/") else (p + "/")

def _join_prefix(base_prefix: str, user_rel: str) -> str:
    base = _ensure_trailing_slash(base_prefix.lstrip("/"))
    rel = _norm_relpath(user_rel)
    return base + rel

def _prefix_for_dir(base_prefix: str, user_rel: str) -> str:
    return _ensure_trailing_slash(_join_prefix(base_prefix, user_rel))

def _is_dir(prefix: str) -> bool:
    pref = _ensure_trailing_slash(prefix)
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=pref, Delimiter="/", PaginationConfig={"PageSize": 1000}):
        if page.get("CommonPrefixes"):
            return True
        for obj in page.get("Contents", []):
            if obj["Key"] != pref:
                return True
    return False

def _file_exists(key: str) -> bool:
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404 or e.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
            return False
        return False

def _list_dir(prefix: str):
    pref = _ensure_trailing_slash(prefix)
    dirs, files = [], []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=pref, Delimiter="/", PaginationConfig={"PageSize": 1000}):
        for cp in page.get("CommonPrefixes", []):
            dirs.append(cp["Prefix"])
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/") or key == pref:
                continue
            files.append({"Key": key, "Size": obj.get("Size", 0)})
    return dirs, files

def _sum_size(prefix: str) -> int:
    total = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix, PaginationConfig={"PageSize": 1000}):
        for obj in page.get("Contents", []):
            if not obj["Key"].endswith("/"):
                total += obj.get("Size", 0)
    return total

def _human(nbytes: int) -> str:
    if nbytes < 1000:
        return f"{nbytes} B"
    if nbytes < 1_000_000:
        return f"{nbytes/1_000:.2f} KB"
    if nbytes < 1_000_000_000:
        return f"{nbytes/1_000_000:.2f} MB"
    return f"{nbytes/1_000_000_000:.2f} GB"

def _presign_get(key: str, filename=None, expires: int = 300) -> str:
    params = {"Bucket": BUCKET, "Key": key}
    if filename:
        params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
    return s3.generate_presigned_url("get_object", Params=params, ExpiresIn=expires)

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
    "Xiaomi Redmi Note 10 lite": {"codename": "curtana (MiAtoll serie)", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1588937747.86846999!400x400!85.png", "download": "https://evolution-x.org/downloads/miatoll"},
    "Redmi Note 11 Pro 5G": {"codename": "Veux", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1648199221.0063088.png", "download": "https://evolution-x.org/downloads/veux"}

}

unofficial_devices = {
    "Motorola G30\n(Work in progress.)": {"codename": "caprip", "image": "https://storage.comprasmartphone.com/smartphones/motorola-moto-g30.png", "download": "https://evox.onelots.fr/download"},
    "Oneplus Nord N10 5G\n(Work in progress.)": {"codename": "billie", "image": "https://oasis.opstatics.com/content/dam/oasis/page/billie/N10-Frame11.png", "download": "https://evox.onelots.fr/download"},
    "Redmi Note 11S\n(Work in progress.)": {"codename": "fleur", "image": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1643013636.25845935.png", "download": "https://evox.onelots.fr/download"},
    "Samsung S9+\n(Work in progress.)": {"codename": "star2lte", "image": "https://www.thekase.com/on/demandware.static/-/Sites-tk-product/default/dw95aa7775/38937129/132901_large.png", "download": "https://evox.onelots.fr/download"},
}

@app.route('/')
def home():
    return render_template('index.html', official_devices=official_devices, unofficial_devices=unofficial_devices)

def check_size_r2(prefix: str) -> str:
    return _human(_sum_size(prefix))

@app.route('/downloads')
def downloads():
    path = request.args.get('path', '')
    key_dir = _prefix_for_dir(DOWNLOADS_PREFIX, path)

    if not _is_dir(key_dir):
        file_key = _join_prefix(DOWNLOADS_PREFIX, path)
        if _file_exists(file_key):
            filename = os.path.basename(file_key.rstrip("/"))
            url = _presign_get(file_key, filename=filename, expires=300)
            return redirect(url, code=302)
        abort(404)

    dirs, files = _list_dir(key_dir)
    items = []

    for d in dirs:
        name = d[len(_ensure_trailing_slash(DOWNLOADS_PREFIX)):]
        name = name.rstrip("/").split("/")[-1]
        rel_path = _norm_relpath(path)
        item_rel = f"{rel_path}/{name}" if rel_path else name
        items.append({"name": name, "is_dir": True, "path": item_rel})

    for f in files:
        key = f["Key"]
        name = os.path.basename(key)
        rel_path = _norm_relpath(path)
        item_rel = f"{rel_path}/{name}" if rel_path else name
        items.append({"name": name, "is_dir": False, "path": item_rel})

    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    parent_path = "/".join(_norm_relpath(path).split("/")[:-1]) if path else None
    total_size = check_size_r2(_ensure_trailing_slash(DOWNLOADS_PREFIX))
    folder_size = check_size_r2(key_dir)

    return render_template('downloads.html',
                           items=items,
                           current_path=_norm_relpath(path),
                           parent_path=parent_path,
                           total_size=total_size,
                           folder_size=folder_size)

@app.route('/testers')
def testers():
    path = request.args.get('path', '')
    key_dir = _prefix_for_dir(TESTERS_PREFIX, path)

    if not _is_dir(key_dir):
        file_key = _join_prefix(TESTERS_PREFIX, path)
        if _file_exists(file_key):
            filename = os.path.basename(file_key.rstrip("/"))
            url = _presign_get(file_key, filename=filename, expires=300)
            return redirect(url, code=302)
        abort(404)

    dirs, files = _list_dir(key_dir)
    items = []

    for d in dirs:
        name = d[len(_ensure_trailing_slash(TESTERS_PREFIX)):]
        name = name.rstrip("/").split("/")[-1]
        rel_path = _norm_relpath(path)
        item_rel = f"{rel_path}/{name}" if rel_path else name
        items.append({"name": name, "is_dir": True, "path": item_rel})

    for f in files:
        key = f["Key"]
        name = os.path.basename(key)
        rel_path = _norm_relpath(path)
        item_rel = f"{rel_path}/{name}" if rel_path else name
        items.append({"name": name, "is_dir": False, "path": item_rel})

    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    parent_path = "/".join(_norm_relpath(path).split("/")[:-1]) if path else None
    total_size = check_size_r2(_ensure_trailing_slash(TESTERS_PREFIX))
    folder_size = check_size_r2(key_dir)

    return render_template('testers.html',
                           items=items,
                           current_path=_norm_relpath(path),
                           parent_path=parent_path,
                           total_size=total_size,
                           folder_size=folder_size)

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

def parse_xml(xml_content):
    root = ET.fromstring(xml_content)
    repositories = []
    for project in root.findall('project'):
        repo_info = {
            "repository": project.get('name'),
            "target_path": project.get('path'),
            "remote": project.get('remote'),
            "branch": project.get('revision', '')
        }
        repositories.append(repo_info)
    return repositories

def convert_to_dependencies(repositories, branch_mapping, remote_mapping):
    dependencies = []
    for repo in repositories:
        dep = {
            "remote": remote_mapping.get(repo["repository"], repo["remote"]),
            "repository": repo["repository"],
            "target_path": repo["target_path"],
            "branch": branch_mapping.get(repo["repository"], repo["branch"] or '')
        }
        dependencies.append(dep)
    return json.dumps(dependencies, indent=2)

@app.route('/manifest_to_dependencies', methods=['GET', 'POST'])
def manifest_to_deps():
    device_codename = ""
    xml_content = ""
    error_message = ""

    if request.method == 'POST':
        if 'xml_content' in request.form and 'convert' not in request.form:
            xml_content = request.form.get('xml_content', '')
            device_codename = request.form.get('device_codename', "")
            if xml_content.strip():
                try:
                    repositories = parse_xml(xml_content)
                except ET.ParseError as e:
                    return render_template(
                        'tools/manifest_to_deps.html',
                        output=f"XML parse error: {e}",
                        repositories=[],
                        repositories_json="[]",
                        device_codename=device_codename,
                        xml_content=xml_content,
                        error_message="Invalid XML"
                    )
                repositories_json = json.dumps(repositories)
                return render_template('tools/manifest_to_deps.html',
                                       repositories=repositories,
                                       repositories_json=repositories_json,
                                       device_codename=device_codename,
                                       xml_content=xml_content,
                                       error_message=error_message)
            return render_template('tools/manifest_to_deps.html',
                                   repositories=[],
                                   repositories_json="[]",
                                   device_codename=device_codename,
                                   xml_content=xml_content,
                                   error_message="No XML provided")

        if 'convert' in request.form:
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
                    repositories_json="[]",
                    repositories=[]
                )

            for k in request.form:
                if k.startswith('branch_'):
                    repo_name = k.split('_', 1)[1]
                    branch_mapping[repo_name] = request.form[k].strip()
                elif k.startswith('remote_'):
                    repo_name = k.split('_', 1)[1]
                    remote_mapping[repo_name] = request.form[k].strip()

            remote_for_all = request.form.get('remoteForAll', '').strip()
            branch_for_all = request.form.get('branchForAll', '').strip()
            if remote_for_all:
                for repo in repositories:
                    remote_mapping[repo["repository"]] = remote_for_all
            if branch_for_all:
                for repo in repositories:
                    branch_mapping[repo["repository"]] = branch_for_all

            for repo in repositories:
                repo_name = repo["repository"]
                if not remote_mapping.get(repo_name, "").strip() or not branch_mapping.get(repo_name, "").strip():
                    return render_template(
                        'tools/manifest_to_deps.html',
                        repositories=repositories,
                        repositories_json=json.dumps(repositories),
                        device_codename=device_codename,
                        xml_content=xml_content,
                        error_message="All Remote and Branch fields must be filled out."
                    )


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

    return render_template('tools/manifest_to_deps.html',
                           output='',
                           repositories=[],
                           repositories_json="[]",
                           device_codename='',
                           xml_content='',
                           error_message='')

objectifs = {
    "objectif1": {
        "nom": "New screen for the Sony Xperia 10 IV",
        "description": "My Sony Xperia 10 IV's screen is broken, so I need to replace it with a new one. But it costs around $90.",
        "pourcentage": 1
    }
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
