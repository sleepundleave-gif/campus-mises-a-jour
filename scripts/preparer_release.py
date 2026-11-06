#!/usr/bin/env python3
"""Prepare a Campus update manifest from a signed GitHub release asset."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import quote

PACKAGE = 'ci.campus.etudes'
# Public certificate fingerprint of the Campus v1.3 debug APK, NOT a private key.
SIGNER = 'b5dac27f335bc98f85f299d961d7007fbdf62f731ebbe63df98e1f6576af0bcf'

def fail(message):
    raise SystemExit(message)

def command(name):
    p = shutil.which(name)
    if p: return p
    home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if home:
        matches = sorted((Path(home) / 'build-tools').glob('*/' + name), reverse=True)
        if matches: return str(matches[0])
    fail(f'Outil Android {name} introuvable.')

def run(cmd):
    try: return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError: fail('L’APK ne peut pas être inspecté ou sa signature est invalide.')

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''): digest.update(chunk)
    return digest.hexdigest()

def main():
    parser = argparse.ArgumentParser(description='Prépare update.json depuis un APK Campus signé.')
    parser.add_argument('apk', type=Path)
    parser.add_argument('--repo', required=True, help='Compte/dépôt GitHub, ex. nom/campus-mises-a-jour')
    parser.add_argument('--tag', required=True, help='Tag de la release, ex. v1.3.0')
    parser.add_argument('--notes', default='')
    parser.add_argument('--output', type=Path, default=Path('update.json'))
    args = parser.parse_args()
    if not args.apk.is_file() or args.apk.suffix.lower() != '.apk': fail('Un fichier APK existant est nécessaire.')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo): fail('Nom de dépôt GitHub invalide.')
    if not re.fullmatch(r'[A-Za-z0-9._-]+', args.tag): fail('Tag invalide. Utilisez par exemple v1.3.0.')
    if len(args.notes) > 2000: fail('Les notes dépassent 2 000 caractères.')
    info = run([command('aapt'), 'dump', 'badging', str(args.apk)])
    signature = run([command('apksigner'), 'verify', '--print-certs', str(args.apk)])
    first = next((line for line in info.splitlines() if line.startswith('package:')), '')
    pkg = re.search(r"name='([^']+)'", first)
    code = re.search(r"versionCode='(\d+)'", first)
    version = re.search(r"versionName='([^']+)'", first)
    cert = re.search(r'Signer #1 certificate SHA-256 digest:\s*([0-9a-fA-F]+)', signature)
    if not (pkg and code and version and cert): fail('Métadonnées de l’APK incomplètes.')
    if pkg.group(1) != PACKAGE: fail('Ce fichier n’est pas un APK Campus.')
    if cert.group(1).lower() != SIGNER: fail('Signature différente de celle de Campus installé.')
    number = int(code.group(1))
    if number < 4: fail('Le numéro de version doit être au minimum celui de Campus 1.3.')
    if args.tag not in (version.group(1), 'v'+version.group(1)):
        fail('Le tag doit correspondre à la version de l’APK, par exemple v1.3.0.')
    native = next((line for line in info.splitlines() if line.startswith('native-code:')), '')
    if "'armeabi-v7a'" not in native or "'arm64-v8a'" not in native:
        fail('Cet APK doit inclure les versions Android ARM 32 et 64 bits.')
    digest = sha256_file(args.apk)
    if args.output.exists():
        try:
            old = json.loads(args.output.read_text(encoding='utf-8'))
            previous = int(old.get('versionCode', 0))
            if number < previous: fail('Cette release est plus ancienne que la version déjà publiée.')
            if number == previous and old.get('sha256') != digest:
                fail('Ce numéro de version est déjà publié avec un autre fichier APK.')
        except (ValueError, TypeError, OSError): fail('Le manifeste existant est invalide.')
    asset_url = 'https://github.com/' + args.repo + '/releases/download/' + quote(args.tag, safe='') + '/' + quote(args.apk.name, safe='')
    result = {'versionCode':number, 'versionName':version.group(1), 'apkUrl':asset_url, 'sha256':digest, 'notes':args.notes}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Manifeste préparé :', args.output)
    print('Version :', result['versionName'], '(code', result['versionCode'], ')')

if __name__ == '__main__': main()
