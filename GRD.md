# General Requirements Document (GRD)

## 1. General system requirements

- Browser-based, responsive application.
- Support desktop, tablet and mobile screen sizes.
- Modular codebase with clear separation of UI, domain logic, infrastructure and AI adapters.
- Secure authentication and server-side authorization.
- Organization/project-level data isolation.
- Private-by-default evidence storage.
- Traceable status transitions.
- Accessible, understandable error messages.
- Configurable workflows and evidence requirements.
- Localization-ready date, time and text handling.

## 2. Non-functional requirements

### Security
- TLS in transit and encryption at rest through infrastructure controls.
- Password hashing using a modern password hashing algorithm if local credentials are used.
- MFA support for privileged roles where feasible.
- RBAC and project-level authorization.
- Secure session and refresh-token handling.
- Rate limiting and abuse protection.
- Audit logging for privileged actions.

### Privacy
- Collect only required personal data.
- Obtain explicit camera/location permissions.
- Make location optional where policy allows and mark missing data clearly.
- Define lawful purpose, retention and deletion policy with the pilot organization.
- Restrict public verification fields.
- Avoid sending confidential evidence to third-party AI providers without authorization.

### Availability and resilience
- Health checks and monitored services.
- Automated backups.
- Documented recovery objectives.
- Queue retries and failed-job visibility.
- Graceful degradation when AI services are unavailable.

### Usability
- Low-friction capture and submission.
- Clear progress indicators.
- Accessible color contrast and keyboard navigation.
- Explain AI flags in plain language.
- Provide a clear route to correction and resubmission.

### Maintainability
- Type hints and strict TypeScript.
- Linting, formatting and automated tests.
- API schema documentation.
- Database migrations.
- ADRs for major decisions.
- No hard-coded secrets or environment-specific URLs.

## 3. Constraints

- AI performance is limited by image quality, dataset coverage, camera angle, lighting and domain shift.
- Device GPS and EXIF values can be absent, altered or spoofed.
- SHA-256 proves byte-level consistency only after hashing.
- A photograph alone cannot establish hidden construction quality or structural safety.
- Applicable engineering standards and acceptance thresholds must be supplied and validated by qualified domain experts.

## 4. Compliance and policy

The pilot owner must determine applicable privacy, public-records, procurement, infrastructure-security, retention and accessibility obligations. Do not claim legal or standards compliance until reviewed by qualified personnel.
