# Introduction
This is the charm for User interface for the Tengu platform.

The User interface itself can be found <a href="https://github.com/IBCNServices/tengu-browser/tree/juju2.0">here</a>.

Since it is still in beta, any suggestions and bugs are welcome on <a href="https://github.com/Qrama/layer-tengu-ui/issues">Github</a>

# Installation
A relation between the Tengu UI and the Sojobo-API is required. When this is not present, the charm will remain in a blocked state. The relation can be added using the following command: `juju add-relation sojobo-api tengu-ui`.

There are 2 different setup options that can be specified in the config:
- letsencrypt (default)
- client
## letsencrypt
This is the default value. This means the client does not have it's own SSL certificates and free ones will be created with
LetsEncrypt. It setups the required nginx config to allow generation of the keys, and installs letsencrypt. Actual generating
of the certificates **requires that the Tengu-UI is exposed and accessable on it's FQDN (Full Qualified Domain Name)**. If this is the case, the certificates can be generated with the following command `sudo letsencrypt certonly -a webroot --webroot-path=[path_to_api] -d fqdn --rsa-key-size 4096`, with `fqdn` being the domain name. More info of the process can be found <a href="https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04">here</a>.
**Setting up the cronjob for automatic renewal of the certificates must also be done manually (see above url)!**
When the certificates are generated, one can continue setting up https by running the command `juju config setup=client`.

## client
This option is used if the client already has its own SSL certifcates, or if they have been generated using LetsEncrypt.

It also requires manual execution of `sudo openssl dhparam -out /etc/nginx/ssl/dhparam.pem 4096` to create a DH-group for extra security. At the time of writing, 4096 is sufficient enough, but as time goes by, this number should be increased.
The output location can be changed, but then this must be passed to the config accordingly in the dhparam value. The charm itself will set the required permissions of the file.
### Own SSL certificates
For this the correct path for fullchain and privatekey must be provided in the config and the Nginx-user (www-data) must have read access to them.
### LetsEncrypt
After the config option setup=httpsletsencrypt and manually generating the key, setup=httpsclient can be used, with fullchain and privatekey left to its default value (empty). The charm will then set the correct permissions and uses the default letsencrypt locations of the key.

# Bugs
Report bugs on <a href="https://github.com/Qrama/layer-tengu-ui/issues">Github</a>

# Author
User interface: Gregory Van Seghbroeck <a href="mailto:gregory.vanseghbroeck@qrama.io">gregory.vanseghbroeck@qrama.io</a>
Charm: Mathijs Moerman <a href="mailto:mathijs.moerman@qrama.io">mathijs.moerman@qrama.io</a>
