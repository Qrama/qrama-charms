import os
from charmhelpers.core import hookenv
from charms.reactive import remove_state


def update_fqdns():
    remove_state('lets-encrypt.registered')


def live(fqdns=None):
    """live returns a dict containing the paths of certificate and key files
    for the configured FQDN."""
    if fqdns:
        registered = [p for p in os.listdir('/etc/letsencrypt/live')
                      if os.path.isdir('/etc/letsencrypt/live/{}'.format(p))]
        if registered is []:
            return None
        common = list(set(registered).intersection(fqdns))
        return {
            'fullchain': '/etc/letsencrypt/live/{}/fullchain.pem'.format(common[0]),
            'chain': '/etc/letsencrypt/live/{}/chain.pem'.format(common[0]),
            'cert': '/etc/letsencrypt/live/{}/cert.pem'.format(common[0]),
            'privkey': '/etc/letsencrypt/live/{}/privkey.pem'.format(common[0]),
            'dhparam': '/etc/letsencrypt/dhparam.pem',
        }
    else:
        fqdn = hookenv.config().get('fqdn')
        if not fqdn:
            return None
        return {
            'fullchain': '/etc/letsencrypt/live/%s/fullchain.pem' % (fqdn),
            'chain': '/etc/letsencrypt/live/%s/chain.pem' % (fqdn),
            'cert': '/etc/letsencrypt/live/%s/cert.pem' % (fqdn),
            'privkey': '/etc/letsencrypt/live/%s/privkey.pem' % (fqdn),
            'dhparam': '/etc/letsencrypt/dhparam.pem',
        }

