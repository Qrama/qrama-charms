from charmhelpers.core import unitdata
from charms.reactive import remove_state


db = unitdata.kv()


def request_fqdns(array_fqdns):
    db.set('fqdns', db.get('fqdns').update(array_fqdns))
    remove_state('lets-encrypt.registered')


def delete_fqdns(array_fqdns):
    db.set('fqdns', db.get('fqdns') - set(array_fqdns))
    remove_state('lets-encrypt.registered')


def live(fqdns):
    """live returns a dict containing the paths of certificate and key files
    for the configured FQDN."""
    try:
        fqdn = fqdns[0]
    except (IndexError, TypeError):
        return None
    return {
        'fullchain': '/etc/letsencrypt/live/%s/fullchain.pem' % (fqdn),
        'chain': '/etc/letsencrypt/live/%s/chain.pem' % (fqdn),
        'cert': '/etc/letsencrypt/live/%s/cert.pem' % (fqdn),
        'privkey': '/etc/letsencrypt/live/%s/privkey.pem' % (fqdn),
        'dhparam': '/etc/letsencrypt/dhparam.pem',
    }
