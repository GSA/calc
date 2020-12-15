# CALC Maintenance Page

This directory contains a simple static application to show a maintenance
page when CALC is down for a planned outage (such as a deployment).

To show the maintenance page you will need to manually route CALC's production
URL to this application. You can do that with:

```sh
cf map-route calc-maintenance calc.gsa.gov
```

If you need to re-deploy this app:

1. `cd` into this directory
2. run `cf push`
