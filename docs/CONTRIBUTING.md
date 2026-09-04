# Contributing to BQEB

## Research Contributions

The BQEB project welcomes contributions that advance reproducibility, benchmarking, and energy AI research.

### Accepted Contribution Areas

- **Reproducibility improvements:** Enhanced validation mechanisms, deterministic execution enhancements
- **Benchmark extensions:** New datasets, additional forecasting scenarios, expanded evaluation frameworks
- **Validation workflows:** Additional checksum procedures, integrity validation methods, evidence documentation
- **Documentation improvements:** Clarity enhancements, methodology explanations, usage guidance
- **Scientific tooling:** Analysis utilities, validation scripts, visualization tools
- **Research lineage:** Documentation connecting new work to established BQEB phases

### Non-Acceptable Changes

- Modifications to historical manuscript content
- Changes to published Zenodo DOI records
- Modifications to the ForecastBench DOI (10.5281/zenodo.21735978)
- Repository renaming or structural reorganization affecting release history

---

## Contribution Requirements

All contributions must include:

### Clear Description

- Summary of proposed change
- Motivation and research context
- Connection to BQEB's reproducibility mission

### Reproducibility Information

- Steps to reproduce or validate the contribution
- Dependencies and environment specifications
- Test procedures demonstrating functionality

### Validation Evidence

- Test results demonstrating correctness
- Checksum validation for data contributions
- Evidence documentation following BQEB governance procedures

### Documentation Updates

- Updates to relevant documentation sections
- Citation guide updates if introducing new artifacts
- Research lineage updates if introducing new research phases

---

## Contribution Process

1. **Fork** the repository
2. **Create a feature branch** from `main`
3. **Implement changes** following the requirements above
4. **Validate** using provided tools (see Validation section)
5. **Document** all changes in supplementary materials or docs/
6. **Submit a pull request** with comprehensive description
7. **Engage** in review discussion ensuring research integrity

---

## Scientific Integrity

All contributors agree to:

### Preserve Research Lineage

- Maintain DOI separation between architecture and benchmarks
- Document connections to existing BQEB phases
- Create new DOIs only for distinct research contributions
- Acknowledge prior work and dependencies

### Maintain Citation Accuracy

- Use correct DOI references in citations and documentation
- Guide users to appropriate citation based on their usage
- Avoid conflating architecture and benchmark citations
- Preserve historical DOI references unchanged

### Avoid DOI Duplication

- Do not create duplicate Zenodo records
- Do not modify existing published DOIs
- Coordinate with maintainers before proposing new Zenodo submissions
- Use version numbers and branches for experimental work

---

## Validation Checklist

Before submitting contributions:

- [ ] No modifications to historical manuscript content
- [ ] No changes to published DOI records
- [ ] Documentation is complete and accurate
- [ ] Reproducibility procedures are documented
- [ ] Citation references are correct
- [ ] Code syntax is valid (`python -m compileall code/`)
- [ ] Research lineage is preserved
- [ ] Commit message is descriptive

---

## Support and Questions

- Review `docs/PUBLICATION_ROADMAP.md` for research phases
- Consult `docs/CITATION_GUIDE.md` for citation questions
- Reference `docs/RESEARCH_LINEAGE.md` for understanding connections
- Check `CITATION.cff` for current version and metadata

Thank you for contributing to BQEB!
