# github_webhook

cat /var/log/webhook.log


sudo systemctl restart webhook.service

sudo visudo
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn.service
