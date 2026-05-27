# Quality Risk Analysis - One Page Overview

---

## 🎯 The Problem

**Teams discover risks too late** → Schedule slips, technical debt, production incidents

| Current State ❌ | Desired State ✅ |
|-----------------|-----------------|
| Risks found during development | Risks identified during planning |
| Late-stage design changes | Informed upfront decisions |
| Rushed mitigation under pressure | Proactive mitigation strategies |
| Production incidents from blind spots | Downstream impacts anticipated |
| "We didn't know it would be this complex" | "We planned for the complexity" |

---

## 💡 The Solution

**Early-stage Quality Risk Analysis tool** that analyzes documentation and codebase to identify risks before coding starts.

Run via QualityForge:

```
/qforge → Option 2: Quality Risk Analysis (BETA)
```

---

## 🔄 How It Works

```
┌─────────────────┐
│ 1. INPUT        │
│ Documentation   │
│ - PRD           │
│ - Jira Tickets  │
│ - Figma Designs │
│ - Repo Context  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. ANALYZE      │
│ Codebase        │
│ - Map features  │
│ - Find files    │
│ - Identify deps │
│ - Check quality │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. IDENTIFY     │
│ Risks           │
│ - Technical     │
│ - Integration   │
│ - Downstream    │
│ - Team/Process  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. REPORT       │
│ Comprehensive   │
│ - Severity      │
│ - Mitigations   │
│ - Spikes needed │
│ - Questions     │
└─────────────────┘
```

---

## 📊 What You Get

### Risk Report Includes:

| Section | What It Tells You |
|---------|------------------|
| **Summary** | Risk count by severity, top 3 concerns, key requirements |
| **Codebase Touch Points** | Which areas are affected + why |
| **Risks** | Grouped by severity — inline evidence + mitigations |
| **Open Questions** | Prioritized unknowns (blockers, high-priority, nice-to-have) |
| **Recommended Spikes** | Research/POC work needed before implementation |
| **Sources** | Links to PRD, Jira, Figma, repo |

---

## 🎭 Risk Categories

### 🔴 Critical Risks
- Breaking API changes
- Large data migrations (100M+ records)
- Legacy code with low test coverage
- Security vulnerabilities

**Impact:** Could cause major production incidents or block deployment

---

### 🟠 High Risks
- Third-party API rate limiting
- Performance bottlenecks
- Cross-team coordination needs
- Complex error scenarios

**Impact:** Could extend timeline or cause user-facing issues

---

### 🟡 Medium Risks
- Audit trail requirements
- Cost implications
- Missing monitoring
- Documentation gaps

**Impact:** Should address but won't block deployment

---

### 🟢 Low Risks
- UI/UX changes
- Minor enhancements
- Cosmetic issues

**Impact:** Track but low priority

---

## ✨ Key Features

### 1. Documentation Ingestion
✅ PRD content (Confluence, Google Docs)  
✅ Jira tickets via Atlassian MCP  
✅ Figma designs via Figma MCP  
✅ GitHub repository context  

### 2. Intelligent Analysis
✅ Maps requirements to code  
✅ Identifies affected components  
✅ Finds likely downstream dependencies (best-effort; evidence-backed)  

### 3. Risk Detection
✅ 4 risk categories (Technical, Integration, Downstream, Team)  
✅ Severity scoring (Critical, High, Medium, Low)  
✅ Common pattern recognition  

### 4. Actionable Output
✅ Specific mitigation strategies  
✅ Spike work recommendations  
✅ Prioritized open questions  
✅ Google Docs-compatible export  

---

## 🚀 Usage Example

### Step 1: Invoke
```
/qforge → Option 2: Risk Analysis (BETA)
```

### Step 2: Provide Info
```
PRD URL: https://confluence.example.com/display/HELIX/SMS-Scheduling
PRD Content: [Full text...]
Jira: HELIX-5432
Repository: nova-corp/helix-api
```

### Step 3: Review Report
```
📊 Risk Analysis Complete!

Total Risks: 14
🔴 Critical: 3
🟠 High: 6
🟡 Medium: 4
🟢 Low: 1

Top Concerns:
1. Breaking API change → Mitigation: Version API
2. 500M record migration → Mitigation: Online schema change
3. Legacy SMS service → Mitigation: Increase test coverage first
```

### Step 4: Take Action
- Review risks with stakeholders
- Choose mitigation strategies
- Create spike tickets
- Update timeline
- Adjust scope if needed

---

## 📈 Success Metrics

Risk Analysis ROI is real, but **exact targets vary** by team and feature.

Suggested metrics (define locally):
- Adoption: % of features analyzed before coding
- Effectiveness: % of identified high-severity risks mitigated before implementation
- Process improvement: reduction in late-stage requirement/design changes
- Operational impact: reduction in production incidents attributable to missed planning risks
- Efficiency: time to generate a report (depends heavily on input completeness)

---

## 🎯 When to Use

### ✅ Perfect For:
- Early planning phase (have PRD, haven't coded yet)
- Architecture review preparation
- Sprint planning and estimation
- Technical spike planning
- Cross-team coordination planning

### ⚠️ Not For:
- Features already in development (use code review)
- Simple bug fixes
- Changes to familiar, well-tested code

---

## 👥 Who Benefits?

### Product Managers
- Understand complexity before committing to timelines
- Make informed scope/timeline trade-offs
- Get questions answered early

### Tech Leads
- Identify architectural concerns upfront
- Plan spike work before sprints
- Design better solutions with full context

### Engineering Managers
- Allocate resources appropriately
- Coordinate cross-team dependencies
- Communicate realistic timelines

### Architects
- Review integration impacts
- Suggest patterns and best practices
- Prevent architecture erosion

---

## 🛠️ Technical Requirements

### Required
- **GitHub MCP**: Codebase search and analysis
- **Cursor**: QualityForge environment

### Optional (Enhanced)
- **Atlassian MCP**: Auto-fetch Jira ticket details
- **Figma MCP**: Design analysis
- **Bugsnag MCP**: Historical error data

---

## 💰 ROI Calculation
Risk Analysis ROI is real, but **exact time-saved numbers vary** by team and feature. Treat any time/ROI estimates as **illustrative**, not tool-verified output.

---

## 🎓 Learning Resources

| Resource | Purpose |
|----------|---------|
| [Risk Analysis Guide](./GUIDE.md) | Complete usage instructions |
| [Content Accuracy Rubric](./CONTENT-ACCURACY-RUBRIC.md) | How to keep risks evidence-based |
| [Example Risk Report](../templates/EXAMPLE-RISK-REPORT.md) | See what reports look like |

---

## 🚦 Getting Started

### Step 1: Review Examples
Read the [Example Risk Report](../templates/EXAMPLE-RISK-REPORT.md) to understand output

### Step 2: Try It
Run on a current project in planning phase

### Step 3: Share Results
Present to stakeholders, gather feedback

### Step 4: Iterate
Use feedback to improve requirements

### Step 5: Make It Standard
Include in Definition of Ready for new features

---

## 💬 Common Questions

**Q: How long does analysis take?**  
A: Varies by feature complexity and how complete the provided documentation is (PRD/Jira/Figma + repo context).

**Q: Is it accurate?**  
A: The report is only as accurate as the evidence available. Use the **Content Accuracy Rubric** and the quality gate to enforce evidence + confidence (and treat unknowns as questions/spikes).

**Q: What if it misses a risk?**  
A: Risk reports are starting point, not replacement for team expertise

**Q: Do we need all the MCPs?**  
A: Only GitHub MCP required; others enhance but not necessary

**Q: Can we customize risk detection?**  
A: Future enhancement; currently uses standard patterns

---

## 🎉 Key Differentiators

| Other Tools | QualityForge Risk Identification |
|-------------|----------------------------|
| Generic checklists | Actual codebase analysis |
| Vague warnings | Specific mitigation strategies |
| Standalone reports | Integrated with test generation |
| Hours of manual work | Automated in minutes |
| After-the-fact | Shift-left planning |

---

## 📞 Questions or Feedback?

- File issues under: Risk Analysis (BETA) / `/qforge` Feature 2
- Share success stories
- Request features
- Report bugs

---

*Quality Risk Analysis - Shift Testing Left, Ship with Confidence* 🚀

