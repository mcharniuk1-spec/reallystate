---
name: wordpress-development
description: WordPress implementation guide for theme/plugin customization, REST integration, security hardening, and deployment-safe updates. Use when building or integrating WordPress-based web surfaces.
---

# WordPress Development

## Use When

- Building WordPress pages/themes/plugins.
- Integrating data feeds into WordPress UI.
- Reviewing WordPress security and performance risks.

## Workflow

1. Decide mode: classic theme, block theme, or headless WordPress.
2. Define data contract (WP REST, custom endpoint, or external API).
3. Implement minimal plugin/theme changes with rollback path.
4. Validate permissions, nonces, input sanitization, and escaping.
5. Test staging path before production rollout.

## Security Checklist

- Sanitize all input (`sanitize_text_field`, etc.).
- Escape all output (`esc_html`, `esc_attr`, `wp_kses_post`).
- Validate capabilities (`current_user_can`).
- Use nonces for state-changing actions.

## Output

```text
WP mode:
Data contract:
Files changed:
Security checks:
Test plan:
Rollback plan:
```
