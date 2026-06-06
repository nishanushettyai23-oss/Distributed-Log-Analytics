# HTTPS Deployment

The public application is served by Caddy on ports 80 and 443. Caddy obtains and renews the TLS certificate, then forwards requests to the internal Nginx frontend. Nginx serves React and proxies `/api` requests to Flask.

## Public address

The current Compute Engine IP is `34.61.207.159`. Reserve it before using it in a hostname:

```bash
gcloud compute addresses create log-analytics-static-ip \
  --project=distributed-log-analytics \
  --region=us-central1 \
  --addresses=34.61.207.159
```

For a demonstration without purchasing a domain, use:

```text
34-61-207-159.nip.io
```

For a permanent deployment, create an `A` record such as `logs.example.com` pointing to `34.61.207.159` and use that hostname instead.

## Firewall

Open only the standard web ports:

```bash
gcloud compute firewall-rules create allow-log-analytics-https \
  --project=distributed-log-analytics \
  --network=default \
  --direction=INGRESS \
  --allow=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0
```

## Start the secure deployment

On the Compute Engine VM:

```bash
cd ~/Distributed-Log-Analytics
git pull origin main

cat > .env <<'EOF'
DOMAIN=34-61-207-159.nip.io
EOF

docker compose down
docker compose pull caddy
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 caddy
```

Verify the redirect and certificate:

```bash
curl -I http://34-61-207-159.nip.io
curl -I https://34-61-207-159.nip.io
curl https://34-61-207-159.nip.io/api/health
```

The external deployment link is:

```text
https://34-61-207-159.nip.io
```

After HTTPS works, remove the old public port `3000` rule:

```bash
gcloud compute firewall-rules delete allow-log-analytics-web \
  --project=distributed-log-analytics
```

Ports `3000` and `8080` remain available only through localhost on the VM for diagnostics.
