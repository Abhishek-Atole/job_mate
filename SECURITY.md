# Security Policy

## Reporting a Vulnerability

Open an issue on GitHub for any security concerns. Do not post sensitive details publicly.

## Best Practices

- Never commit `.env` files or API keys
- JWT tokens expire after 24 hours
- Role-based access enforced on all API endpoints
- SQL injection and XSS protection via Django ORM and DRF serializers
