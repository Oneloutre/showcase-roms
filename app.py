from flask import Flask, render_template, request, abort, send_file
import os
import cloudscraper
from bs4 import BeautifulSoup

DOWNLOAD_DIR = ('test')

app = Flask(__name__)

official_devices = {
    "Xiaomi Mi Mix 2S": {"codename": "polaris", "image": "https://raw.githubusercontent.com/Evolution-X/www_gitres/refs/heads/udc/devices/images/polaris.png", "download": "https://sourceforge.net/projects/evolution-x/files/polaris"},
    "Google Pixel 3a": {"codename": "sargo", "image": "https://github.com/Evolution-X/www_gitres/blob/main/devices/images/sargo.png", "download": "https://sourceforge.net/projects/evolution-x/files/sargo"},
    "Google Pixel 3a XL": {"codename": "bonito", "image": "https://github.com/Evolution-X/www_gitres/blob/main/devices/images/bonito.png", "download": "https://sourceforge.net/projects/evolution-x/files/bonito"},
    "Google Pixel 3": {"codename": "blueline", "image": "https://github.com/Evolution-X/www_gitres/blob/main/devices/images/blueline.png", "download": "https://sourceforge.net/projects/evolution-x/files/blueline"},
    "Google Pixel 3 XL": {"codename": "crosshatch", "image": "https://github.com/Evolution-X/www_gitres/blob/main/devices/images/crosshatch.png", "download": "https://sourceforge.net/projects/evolution-x/files/crosshatch"},
}

unofficial_devices = {
    "Xiaomi Redmi 5 Plus\n(Under work.)": {"codename": "vince", "image": "https://images.frandroid.com/wp-content/uploads/2019/04/xiaomi-redmi-5-plus-2018.png", "download": "https://evox.onelots.fr/downloads"},
    "Oneplus Nord N10 5G\n(Under work.)": {"codename": "billie", "image": "https://oasis.opstatics.com/content/dam/oasis/page/billie/N10-Frame11.png", "download": "https://evox.onelots.fr/download"},
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



@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error="403 Forbidden: You don't have permission to access this resource."), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="404 Not Found: The requested resource could not be found."), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)