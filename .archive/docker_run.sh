#!/bin/sh -e

set -o pipefail

# if FLASK_DEBUG is defined, we'll run via flask with dynamic reloading of
# code changes to disk. This is helpful for debugging something already in k8s

CERTS_DIR=${CERTS_DIR-/certs}

assert_file() {
	if [ ! -f ${CERTS_DIR}/$1 ] ; then
		echo ERROR: Missing file: ${CERTS_DIR}/$1
		exit 1
	fi
}

assert_file factory_ca.pem
assert_file local-ca.pem
assert_file local-ca.key
assert_file tls-crt

dns=$(openssl x509 -text -noout -in ${CERTS_DIR}/tls-crt | grep -o "DNS:[[:print:]]*.ota-lite.foundries.io" | sed -e 's/^DNS://')
ostree_hostname=$(openssl x509 -ext subjectAltName -noout -in ${CERTS_DIR}/tls-crt | grep -o "DNS:[^,]*ostree.foundries.io" | sed -e 's/^DNS://')
export DEVICE_GATEWAY_SERVER=https://${dns}:8443
export OSTREE_SERVER=https://${ostree_hostname}:8443
export ROOT_CRT=$(cat ${CERTS_DIR}/factory_ca.pem)
export CA_CRT=$(cat ${CERTS_DIR}/local-ca.pem)
export CA_KEY=$(cat ${CERTS_DIR}/local-ca.key)

if [ -z "$FLASK_DEBUG" ] ; then
	exec /usr/bin/gunicorn -n intel-esh -w4 -b 0.0.0.0:8000 $FLASK_APP
fi

exec flask run -h 0.0.0.0 -p 8000
