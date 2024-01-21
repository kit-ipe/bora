# This is a manual trigger to the CPS pod at the OpenShift platform.
# Only run this when the webhook is not working.
curl -X POST -k https://kaas.kit.edu:8443/oapi/v1/namespaces/bora/buildconfigs/cps/webhooks/<SECRET>/generic
