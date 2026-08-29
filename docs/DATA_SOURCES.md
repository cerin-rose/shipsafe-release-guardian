# Data Sources - Solo, Compliant

This project was completed as a **solo project** using public and synthetic test data only.

## 1. Spring PetClinic

**Source:**  
https://github.com/spring-projects/spring-petclinic

**License:** MIT

**Type:** Public sample Java application

The repository was cloned into:

`src/`

It was used as a realistic test application for ShipSafe's **16 release-safety checks**.

## 2. Synthetic Test Data

All additional test cases were created specifically for this project.

Synthetic examples included:

- `VAULT_ID` bug injected at:
  `OwnerController.java:50`

- Missing deployment configuration case:
  `deploy/codeengine.yaml`
  - Simulated `C16` missing configuration

- React dependency test:
  `frontend/package.json`
  - Used `lodash 4.17.10` as a dependency test case

- Placeholder values:
  - Used `xxx` and other dummy values
  - No real customer or employee information

## Data Compliance

The project uses:

- Public open-source code
- Synthetic test data
- Dummy configuration values

The project does **not** use:

- Personally identifiable information (PII)
- Client/customer data
- Company-confidential information
- Private production data
- Social media user data