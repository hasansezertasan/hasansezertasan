---
name: find-blog-topics
description: Scan GitHub activity (PRs, issues, commits) for a time period and identify blog-worthy topics. Use when the user asks for blog ideas, content inspiration, or wants to find topics from their recent work. Triggers on "find blog topics", "what should I write about", "blog ideas from my GitHub", "scan my activity for content".
---

# Find Blog Topics

Scan the user's GitHub activity and identify topics worth writing about.

## Workflow

1. **Determine time range** — Default to last 14 days. Accept user-specified ranges like "last month", "past 30 days", "since September 1st". If the requested range exceeds 1 year, split it into consecutive windows of at most 1 year and merge results, as GitHub's `contributionsCollection(from:, to:)` API rejects ranges exceeding 1 year.

2. **Fetch activity via GraphQL** — Query PRs (both created and merged), issues, and commits:

    ```bash
    gh api graphql -f query='
    {
      viewer {
        login
        contributionsCollection(from: "<start>", to: "<end>") {
          pullRequestContributions(first: 50) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              pullRequest {
                title
                url
                repository { nameWithOwner }
                state
                mergedAt
                createdAt
                body
              }
            }
          }
          issueContributions(first: 50) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              issue {
                title
                url
                repository { nameWithOwner }
                createdAt
                body
              }
            }
          }
          commitContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner }
            contributions(first: 10) {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                commitCount
                occurredAt
              }
            }
          }
        }
      }
      mergedPRs: search(query: "author:@me is:pr merged:<start-date>..<end-date>", type: ISSUE, first: 50) {
        issueCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          ... on PullRequest {
            title
            url
            repository { nameWithOwner }
            state
            mergedAt
            createdAt
            body
          }
        }
      }
    }'
    ```

    - Check `pageInfo.hasNextPage` and `totalCount` / `issueCount`. If `hasNextPage` is true, explicitly report that results are truncated (e.g. `Showing 50 of <totalCount> PRs`), or paginate using `after: "<endCursor>"` if a complete scan is required.
    - `commitContributionsByRepository` is capped at 100 repositories by GitHub's API; if 100 repositories are returned, report that repository commit activity may be truncated.
    - Combine and deduplicate PRs by URL across `pullRequestContributions` and `mergedPRs` before categorizing and ranking, so PRs both opened and merged in the window are not counted twice.
    - Commit contributions provide only per-repository counts and dates, which cannot show whether a commit belongs to a PR. Inspect commit details for **every** repository reporting commit contributions — not only those without PR activity, or direct commits made alongside a PR in the same repository are silently dropped — filtered to the viewer:
      - Via REST API (recommended, handles GitHub account associations automatically): `gh api --paginate "repos/<owner>/<repo>/commits?author=<viewer>&since=<start>&until=<end>&per_page=100"`
      - Via local clone: `git log --author="<author-pattern>" --since="<start>" --until="<end>"`, where `<author-pattern>` matches the user's Git author name or email (e.g. from `git config user.email` or `git config user.name`), not necessarily their GitHub login.
    - Deduplicate those commits against the PR set before ranking: collect each PR's commit SHAs with `gh api --paginate "repos/<owner>/<repo>/pulls/<number>/commits?per_page=100" --jq '.[].sha'` — not `gh pr view --json commits`, which stops at 100 — then drop commits whose SHA appears there and treat the remainder as direct-commit topics. GitHub caps that endpoint at 250 commits per PR, so if a PR reports more, report the leftover commits as unverified rather than as confirmed direct work.
    - `contributionsCollection` counts only commits that landed on a repository's default branch (or `gh-pages`), so work still living on an unmerged branch never appears here — and GitHub's commit search is built from the same default-branch index, so it cannot recover it either. Branch work that already has an open PR is still covered by `pullRequestContributions`; for branch work with no PR, scan local clones the user names with `git log --all --author="<author-pattern>" --since="<start>" --until="<end>"`, and state in the output that unmerged, PR-less branch work outside those clones was not scanned.

3. **Categorize topics** — Group findings into:
    - **Technical Deep-Dives** — Complex implementations, migrations, protocol work
    - **Patterns & Architecture** — Design decisions, abstractions, provider seams
    - **Tooling & Automation** — CI/CD, templates, developer experience
    - **Tutorials** — Step-by-step guides extracted from PRs

4. **Rank by blog potential** — Prioritize topics that are:
    - Reusable by others (not project-specific)
    - Underserved in existing content
    - Have concrete code/examples to reference

5. **Output format** — Present as a numbered list with:
    - Topic title (blog-ready)
    - One-line description
    - Source PRs/repos for reference
    - Target audience hint

## Example Output

```markdown
## Technical Deep-Dives

1. **"Migrating to PEP 691: The Simple Repository API"** — Content negotiation,
    version normalization, API 1.0 fallbacks. Source: peta#165, peta#173

2. **"Building a Concurrent HTTP Transport Layer"** — Pooled clients, disk caching,
    conditional requests, offline mode. Source: peta#156→#157→#158

## Tooling & Automation

3. **"Reusable Homebrew/Scoop Bucket Templates"** — Manifest scaffolding,
    update automation, cross-platform CI. Source: tap-template, bucket-template
```

## Notes

- Focus on merged PRs (`state: MERGED`) for completed work; open PRs (`state: OPEN`) for "coming soon" ideas; ignore closed unmerged PRs (`state: CLOSED` without `mergedAt`)
- Cross-reference commit activity with PR context for richer descriptions
