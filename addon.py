# -*- coding: utf-8 -*-
import os, re, json, urllib.request, urllib.parse, zipfile, shutil
import xbmc, xbmcgui, xbmcaddon, xbmcvfs

A = xbmcaddon.Addon()
ROOT = xbmcvfs.translatePath(A.getAddonInfo('path'))
PROFILE = xbmcvfs.translatePath(A.getAddonInfo('profile'))
STORE = os.path.join(PROFILE, 'games')
ART = os.path.join(PROFILE, 'artwork')
ICON = os.path.join(ROOT, 'resources', 'art', 'icon-1.0.4.png')
FANART = os.path.join(ROOT, 'resources', 'art', 'background-1.0.4.png')
os.makedirs(STORE, exist_ok=True)
os.makedirs(ART, exist_ok=True)

PLATFORMS = {
    'NES': {'core': 'game.libretro.fceumm', 'exts': ('.nes', '.fds', '.unf', '.unif')},
    'SNES': {'core': 'game.libretro.snes9x', 'exts': ('.sfc', '.smc', '.fig', '.swc')},
    'Sega Mega Drive': {'core': 'game.libretro.genplus', 'exts': ('.md', '.gen', '.bin', '.smd')},
    'GBA': {'core': 'game.libretro.mgba', 'exts': ('.gba',)},
    'Amiga': {'core': 'game.libretro.puae', 'exts': ('.adf', '.adz', '.ipf', '.dms', '.hdf')},
    'Arcade': {'core': 'game.libretro.fbneo', 'exts': ('.zip',)},
}
ORDER = ['NES', 'SNES', 'Sega Mega Drive', 'GBA', 'Amiga', 'Arcade']
ROM_EXTS = tuple(e for p in PLATFORMS.values() for e in p['exts'])


def dialog(text):
    xbmcgui.Dialog().ok('SorbettoGames', str(text))


def req(url):
    return urllib.request.Request(url, headers={'User-Agent': 'SorbettoGames/1.0.4'})


def read(url, timeout=25):
    with urllib.request.urlopen(req(url), timeout=timeout) as r:
        return r.read()


def release_assets():
    repo = A.getSetting('github_repo').strip() or 'HermesGR/SorbettoGames'
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Μη έγκυρο repository.')
    tag = A.getSetting('release_tag').strip()
    endpoint = 'tags/' + urllib.parse.quote(tag, safe='') if tag else 'latest'
    data = json.loads(read('https://api.github.com/repos/' + repo + '/releases/' + endpoint))
    return data.get('assets', [])


def classify(name):
    parts = name.replace('\\', '/').split('/')
    if len(parts) > 1:
        folder = parts[0].strip().lower()
        for platform in ORDER:
            if folder == platform.lower() or folder == platform.split()[0].lower():
                return platform
    low = name.lower()
    for platform in ORDER:
        if low.endswith(PLATFORMS[platform]['exts']):
            return platform
    return None


def build_games(assets):
    games = []
    for asset in assets:
        name = asset.get('name', '')
        if not name.lower().endswith(ROM_EXTS):
            continue
        platform = classify(name)
        if not platform:
            continue
        base = os.path.basename(name)
        title = os.path.splitext(base)[0].replace('_', ' ').strip()
        gid = re.sub(r'[^a-z0-9]+', '-', base.lower()).strip('-')
        games.append({
            'id': gid,
            'title': title,
            'platform': platform,
            'asset': name,
            'url': asset.get('browser_download_url', ''),
        })
    games.sort(key=lambda g: (ORDER.index(g['platform']), g['title'].lower()))
    return games


def folder(g):
    return os.path.join(STORE, g['id'])


def installed(g):
    exts = PLATFORMS[g['platform']]['exts']
    for root, _, names in os.walk(folder(g)):
        for name in names:
            if name.lower().endswith(exts):
                return os.path.join(root, name)
    return None


def image(g):
    path = os.path.join(ART, g['id'] + '.png')
    if os.path.isfile(path):
        return path
    return ICON


def download(g):
    if not g.get('url', '').startswith('https://'):
        dialog('Μη έγκυρος σύνδεσμος λήψης.')
        return None
    part = folder(g) + '.part'
    tmp = folder(g) + '.tmp'
    progress = xbmcgui.DialogProgress()
    progress.create('SorbettoGames', 'Λήψη: ' + g['title'])
    try:
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        with urllib.request.urlopen(req(g['url']), timeout=90) as r, open(part, 'wb') as f:
            total = int(r.headers.get('Content-Length') or 0)
            count = 0
            while True:
                if progress.iscanceled():
                    raise InterruptedError('Η λήψη ακυρώθηκε.')
                data = r.read(262144)
                if not data:
                    break
                f.write(data)
                count += len(data)
                progress.update(min(99, int(count * 100 / total)) if total else 0, '%.1f MB' % (count / 1048576))
        if g['url'].lower().endswith('.zip'):
            with zipfile.ZipFile(part) as z:
                root = os.path.abspath(tmp)
                for member in z.infolist():
                    target = os.path.abspath(os.path.join(tmp, member.filename))
                    if os.path.commonpath([root, target]) != root:
                        raise ValueError('Μη ασφαλής διαδρομή ZIP.')
                    if ((member.external_attr >> 16) & 0o170000) == 0o120000:
                        raise ValueError('Δεν επιτρέπονται symlinks.')
                z.extractall(tmp)
        else:
            shutil.copyfile(part, os.path.join(tmp, os.path.basename(g['url'])))
        if not installed_from(tmp, g):
            raise ValueError('Δεν βρέθηκε συμβατό αρχείο παιχνιδιού.')
        shutil.rmtree(folder(g), ignore_errors=True)
        os.replace(tmp, folder(g))
        return installed(g)
    except Exception as exc:
        xbmc.log('SorbettoGames download: ' + str(exc), xbmc.LOGERROR)
        dialog('Αποτυχία λήψης/εγκατάστασης.\n' + str(exc))
    finally:
        progress.close()
        shutil.rmtree(tmp, ignore_errors=True)
        if os.path.isfile(part):
            os.remove(part)
    return None


def installed_from(path, g):
    exts = PLATFORMS[g['platform']]['exts']
    for root, _, names in os.walk(path):
        for name in names:
            if name.lower().endswith(exts):
                return os.path.join(root, name)
    return None


def rpc(method, params):
    result = json.loads(xbmc.executeJSONRPC(json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})))
    if 'error' in result:
        raise RuntimeError(result['error'].get('message', 'Kodi JSON-RPC error'))
    return result.get('result', {})


def core_status(core):
    return rpc('Addons.GetAddonDetails', {'addonid': core, 'properties': ['enabled']}).get('addon', {}).get('enabled', False)


def ready_core(core):
    try:
        enabled = core_status(core)
    except Exception:
        xbmc.executebuiltin('InstallAddon(' + core + ')')
        monitor = xbmc.Monitor()
        for _ in range(120):
            if monitor.waitForAbort(1):
                return False
            try:
                enabled = core_status(core)
                break
            except Exception:
                pass
        else:
            dialog('Δεν ολοκληρώθηκε η εγκατάσταση ' + core + '.')
            return False
    if not enabled:
        try:
            rpc('Addons.SetAddonEnabled', {'addonid': core, 'enabled': True})
            if not core_status(core):
                raise RuntimeError('Παραμένει απενεργοποιημένος.')
        except Exception as exc:
            dialog(str(exc))
            return False
    return True


def launch(g, rom):
    if not rom or not os.path.isfile(rom):
        dialog('Δεν βρέθηκε το αρχείο παιχνιδιού.')
        return False
    core = PLATFORMS[g['platform']]['core']
    if not ready_core(core):
        return False
    try:
        item = xbmcgui.ListItem(label=g['title'], path=rom)
        tag = item.getGameInfoTag()
        tag.setTitle(g['title'])
        tag.setGameClient(core)
        item.setProperty('gameclient', core)
        item.setArt({'icon': image(g), 'thumb': image(g), 'fanart': FANART})
        xbmc.Player().play(rom, item)
        return True
    except Exception as exc:
        xbmc.log('SorbettoGames RetroPlayer: ' + str(exc), xbmc.LOGERROR)
        dialog('Αποτυχία εκκίνησης.\n' + str(exc))
        return False


class Menu(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.heading = 'SorbettoGames'
        self.entries = []
        self.choice = -1

    def onInit(self):
        self.getControl(50).setImage(FANART)
        self.getControl(60).setLabel(self.heading)
        listing = self.getControl(100)
        listing.reset()
        listing.addItems(self.entries)
        self.setFocusId(100)

    def onClick(self, control):
        if control == 100:
            self.choice = self.getControl(100).getSelectedPosition()
            self.close()

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216, 247):
            self.close()


def choose(title, labels):
    entries = []
    for label in labels:
        item = xbmcgui.ListItem(label=label)
        item.setArt({'icon': ICON, 'thumb': ICON, 'fanart': FANART})
        entries.append(item)
    window = Menu('SorbettoMenu.xml', ROOT, 'Default', '1080i')
    window.heading = title
    window.entries = entries
    window.doModal()
    choice = window.choice
    del window
    return choice


def game_menu(g):
    rom = installed(g)
    action = choose(g['title'], ['Εκκίνηση' if rom else 'Λήψη και εγκατάσταση', 'Πληροφορίες', 'Διαγραφή εγκατάστασης'])
    if action == 0:
        if rom:
            return launch(g, rom)
        rom = download(g)
        if rom and xbmcgui.Dialog().yesno('SorbettoGames', 'Εγκαταστάθηκε. Να γίνει εκκίνηση;'):
            return launch(g, rom)
    elif action == 1:
        dialog(g['platform'] + '\nΕξομοιωτής: ' + PLATFORMS[g['platform']]['core'] + '\nΑρχείο: ' + g['asset'])
    elif action == 2 and rom and xbmcgui.Dialog().yesno('SorbettoGames', 'Διαγραφή τοπικής εγκατάστασης;'):
        shutil.rmtree(folder(g), ignore_errors=True)
    return False


class Browser(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.games = []
        self.category = None
        self.visible_games = []

    def onInit(self):
        self.getControl(50).setImage(FANART)
        self.fill()
        self.setFocusId(100)

    def fill(self):
        self.visible_games = [g for g in self.games if self.category is None or g['platform'] == self.category]
        items = []
        for g in self.visible_games:
            state = 'Εγκατεστημένο' if installed(g) else 'Διαθέσιμο για λήψη'
            item = xbmcgui.ListItem(label=g['title'], label2=g['platform'] + '  •  ' + state)
            item.setArt({'icon': image(g), 'thumb': image(g), 'fanart': FANART})
            items.append(item)
        listing = self.getControl(100)
        listing.reset()
        listing.addItems(items)
        self.getControl(200).setLabel('Κονσόλα: ' + (self.category or 'Όλες'))
        self.getControl(61).setLabel(str(len(items)) + ' παιχνίδια')

    def onClick(self, control):
        if control == 100:
            position = self.getControl(100).getSelectedPosition()
            if 0 <= position < len(self.visible_games):
                if game_menu(self.visible_games[position]):
                    self.close()
                else:
                    self.fill()
                    self.setFocusId(100)
        elif control == 200:
            selected = xbmcgui.Dialog().select('Φίλτρο κονσόλας', ['Όλες'] + ORDER)
            if selected >= 0:
                self.category = None if selected == 0 else ORDER[selected - 1]
                self.fill()
                self.setFocusId(100)
        elif control == 201:
            self.games = build_games(release_assets())
            self.fill()
        elif control == 203:
            A.openSettings()
        elif control == 204:
            self.close()

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216, 247):
            self.close()


def main():
    try:
        games = build_games(release_assets())
    except Exception as exc:
        games = []
        dialog('Το Release δεν είναι προσβάσιμο.\n' + str(exc))
    browser = Browser('SorbettoBrowser.xml', ROOT, 'Default', '1080i')
    browser.games = games
    browser.doModal()
    del browser


if __name__ == '__main__':
    main()
