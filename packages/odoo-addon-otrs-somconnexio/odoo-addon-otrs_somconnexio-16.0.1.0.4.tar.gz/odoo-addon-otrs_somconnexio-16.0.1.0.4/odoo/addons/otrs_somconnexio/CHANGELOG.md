# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [16.0.1.0.4] - 2025-06-02
### Fixed
- [#1510](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1510) Add origin to virtual records mobile tariff change

## [16.0.1.0.3] - 2025-05-28
### Added
- [#1500](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1500) Add code field in crm team

### Fixed
- [#1501](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1501) Only create OTRS tickets after lead validation, not edition
- [#1497](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1497) Always assign `will_force_other_mobiles_to_quit-pack` field in their computation

## [16.0.1.0.2] - 2025-05-28
### Added
- [#1492](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1492) Execute method create_additional_data_otrs_ticket as queue.job

## [16.0.1.0.1] - 2025-05-27
### Fixed
- [#1470](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1470) Call super() within otrs.crm.lead.listener `on_record_write` method

## [16.0.1.0.0] - 2025-05-26
### Added
- Migrate otrs_somconnexio module to ODOO v16
