# {{ project.title }}

{{ project.description }}

## Authors

{% for author in project.authors -%}
- {{ author }}
{% endfor %}

## Data Availability and Provenance Statements

### Statement about Rights

- [ ] I certify that the author(s) of the manuscript have legitimate access to and permission to use the data used in this manuscript.
- [ ] I certify that the author(s) of the manuscript have documented permission to redistribute/publish the data contained within this replication package.

### Summary of Availability

- [ ] All data **are** publicly available.
- [ ] Some data **cannot be made** publicly available.
- [ ] **No data can be made** publicly available.

## Computational Requirements

### Software Requirements

- `bead` for data dependency management
- Stata version {{ project.stata_version | default("18") }}
- Make for running code in proper order

### Memory, Runtime, Storage Requirements

Approximate time needed to reproduce the analyses on a standard desktop machine:

- [ ] <10 minutes
- [ ] 10-60 minutes
- [ ] 1-2 hours
- [ ] 2-8 hours
- [ ] 8-24 hours
- [ ] 1-3 days
- [ ] > 3 days

## Instructions to Replicators

- Run `make init` to initialize data dependencies
- Run `make all` to run all analysis steps

## References
