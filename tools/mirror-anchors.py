#!/usr/bin/env python3
"""Mirror the receipts repository's anchor listing into this site, at BUILD time.

WHY THIS EXISTS (2026-09-02). /record/ is the page this product's whole argument rests on:
a public record a stranger can check. It read the listing with an unauthenticated fetch to
api.github.com FROM THE VISITOR'S BROWSER, and GitHub allows 60 of those an hour per IP,
shared by everyone behind one carrier NAT. Measured that day: the API answered 403 and the
page rendered "Could not read the repository" to a reader who had come to check our honesty.
The one page that must never look broken was the one page whose content we did not own.

  🔒 A PAGE THAT PROMISES IT MAKES NO THIRD-PARTY REQUEST MAY NOT MAKE ONE. The stylesheet's
  own header says this site talks to no host but its own, and the CSP had api.github.com in
  connect-src to permit exactly the call that contradicted it. Both are gone.

  🔒 MIRRORING IS NOT HIDING. The repository link stays on the page, in prose, so anyone can
  read the source of this file for themselves and find the same roots. What changes is who
  pays for the request: us, once, at build time, instead of every visitor, on every load.

    python3 tools/mirror-anchors.py            write record/anchors.json from the live repo
    python3 tools/mirror-anchors.py --offline  rewrite the file's stamp without a network call

Commit record/anchors.json alongside each new anchor. A stale mirror is visible: the page
prints the date it was taken.
"""
import json, os, sys, urllib.request, urllib.error, datetime

REPO = 'jeremiah2060/orderedstrength-receipts'
API  = 'https://api.github.com/repos/%s/contents/anchors' % REPO
OUT  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'record', 'anchors.json')


def fetch():
    req = urllib.request.Request(API, headers={'accept': 'application/vnd.github+json',
                                               'user-agent': 'orderedstrength-site-mirror'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 'ok', json.load(r)
    except urllib.error.HTTPError as e:
        # 404 is the honest current state, not a failure: the folder does not exist yet.
        if e.code == 404:
            return 'no-folder', []
        return 'unreachable', []
    except Exception:
        return 'unreachable', []


def fetch_document(url):
    """Read one published anchor file and hand back what it actually claims.

    🔒 IT VALIDATES BEFORE IT MIRRORS. A root that is not 64 hex characters, or a count that
    is not a positive integer, is refused rather than copied onto the page. This site prints
    these values as fact; mirroring a malformed one would republish somebody else's mistake in
    our own voice.
    """
    if not url:
        return 'unreachable', {}
    req = urllib.request.Request(url, headers={'user-agent': 'orderedstrength-site-mirror'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            doc = json.load(r)
    except Exception:
        return 'unreachable', {}
    root = doc.get('root')
    count = doc.get('count')
    if not isinstance(root, str) or len(root) != 64 or any(c not in '0123456789abcdef' for c in root):
        return 'unreachable', {}
    if not isinstance(count, int) or count < 1:
        return 'unreachable', {}
    return 'ok', doc


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    if '--offline' in sys.argv:
        prev = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
        state, listing = prev.get('state', 'no-folder'), []
        anchors = prev.get('anchors', [])
    else:
        state, listing = fetch()
        if state == 'unreachable':
            # 🔒 REFUSE TO OVERWRITE A GOOD MIRROR WITH A FAILED READ. A network hiccup here
            # must never empty a published record; that is the failure this whole file exists
            # to stop, moved from the visitor's browser to ours.
            print('mirror: the API was unreachable. record/anchors.json left as it is.')
            return 1
        # 🔒 THE ROOT COMES OUT OF THE FILE, NEVER OUT OF THE LISTING. Until 2026-09-05 this
        # stored `f['sha']`, which is GIT'S BLOB HASH of the file: a hash OF the document, not
        # the Merkle root INSIDE it. /record/ then printed it under the words "the root hash
        # covering every prediction sealed that day". Both halves were working correctly and
        # the sentence was false, and it was invisible only because no anchor had ever been
        # published: the first real one would have shipped a number a checking stranger could
        # not reproduce, on the single page whose whole purpose is that they can.
        anchors = []
        for f in sorted(listing, key=lambda f: f.get('name', ''), reverse=True):
            if f.get('type') != 'file' or not f['name'].endswith('.json'):
                continue
            state, doc = fetch_document(f.get('download_url'))
            if state != 'ok':
                # Same law as a failed listing: a half-read mirror is worse than yesterday's
                # good one, because the page cannot tell the difference.
                print('mirror: could not read %s. record/anchors.json left as it is.' % f['name'])
                return 1
            anchors.append({'date': f['name'].rsplit('.', 1)[0],
                            'root': doc.get('root'),
                            'count': doc.get('count'),
                            'url': f['html_url']})
        anchors.sort(key=lambda a: a['date'], reverse=True)
        if state == 'ok' and not anchors:
            state = 'empty'

    doc = {'mirrored': stamp, 'repo': REPO, 'state': state, 'anchors': anchors}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print('mirror: %s, %d anchor(s), stamped %s -> record/anchors.json'
          % (state, len(anchors), stamp))
    return 0


if __name__ == '__main__':
    sys.exit(main())
