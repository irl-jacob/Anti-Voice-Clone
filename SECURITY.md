# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions of AvC:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

We take the security of AvC and the underlying neural inference pipeline very seriously.

If you discover a security vulnerability or sensitive exploit vector (such as an audio deserialization flaw, denial of service in the ONNX runtime or WebSocket stream, or data exposure):

1. **Do not disclose the issue publicly.** Please refrain from creating public GitHub issues or discussions.
2. **Email the maintainers**: Send details directly to [itsmejam07@outlook.com](mailto:itsmejam07@outlook.com).
3. **Include the following details**:
   - Description of the vulnerability and attack vector
   - Steps or audio payload to reproduce the behavior
   - Potential impact on inference servers or user sessions
   - Any proposed remediations or patches

### Response Timeline
- **Initial Acknowledgement**: Within 48 hours.
- **Triage & Status Assessment**: Within 5 business days.
- **Fix & Public Disclosure**: Coordinated following fix validation and deployment.
