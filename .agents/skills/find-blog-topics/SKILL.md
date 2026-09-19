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
      closedIssues: search(query: "author:@me is:issue closed:<start-date>..<end-date>", type: ISSUE, first: 50) {
        issueCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          ... on Issue {
            title
            url
            repository { nameWithOwner }
            state
            createdAt
            closedAt
            body
          }
        }
      }
    }'
    ```

    - Check `pageInfo.hasNextPage` and `totalCount` / `issueCount`. If `hasNextPage` is true, explicitly report that results are truncated (e.g. `Showing 50 of <totalCount> PRs`), or paginate using `after: "<endCursor>"` if a complete scan is required.
    - `commitContributionsByRepository` is capped at 100 repositories by GitHub's API; if 100 repositories are returned, report that repository commit activity may be truncated.
    - Combine and deduplicate PRs by URL across `pullRequestContributions` and `mergedPRs` before categorizing and ranking, so PRs both opened and merged in the window are not counted twice.
    - Do the same for issues across `issueContributions` and `closedIssues`: `issueContributions` holds issues *opened* in the window, so an issue opened earlier and resolved during it only arrives via `closedIssues`.
    - Commit contributions give only per-repository counts and dates, never commit content, and cannot show whether a commit belongs to a PR. Fetch commit details for **every** repository reporting commit contributions — not only those without PR activity — then classify them against the PR set following [Attribution caveats](#attribution-caveats):
      - Via REST API (resolves GitHub account association): `gh api --paginate "repos/<owner>/<repo>/commits?author=<viewer>&since=<start>&until=<end>&per_page=100"`, repeated with `&sha=gh-pages` when the repository reports `gh-pages` activity, because `sha` defaults to the default branch
      - Via local clone: `git log --all --author="<author-pattern>" --since="<start>" --until="<end>"`, where `<author-pattern>` matches the user's Git name or email (`git config user.email`), not their GitHub login

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

## Attribution caveats

GitHub's attribution model does not map cleanly onto Git authorship, so a commit can be the user's real work and still be missed, or be one change counted twice. Report what can be verified, and label the rest **unverified** rather than presenting a guess as fact.

- **Squash and rebase merges rewrite SHAs.** A squash-merged PR lands one new commit on the base branch that appears in no PR commit listing, so plain SHA subtraction reports it as direct work and ranks the same change twice. Collect `mergeCommit.oid` (`gh pr view <pr-url> --json mergeCommit`) alongside each PR's commits, and treat a leftover commit whose message or patch matches a collected PR as that same work.
- **PR commit listings are capped.** `gh api --paginate ".../pulls/<number>/commits"` stops at 250 (`gh pr view --json commits` stops at 100). Beyond that, leftovers are unverified, not confirmed direct work.
- **The contribution graph covers only the default branch and `gh-pages`.** Work on an unmerged branch never appears, and commit search is built from the same index, so it cannot recover it either.
- **Opening a PR is the contribution, not updating one.** `pullRequestContributions` records PRs *opened* in the window, so an older open PR that received new commits during it appears in neither that connection nor `mergedPRs`. Search for those separately with `gh search prs --author=@me --state=open --updated=<start>..<end> --limit 100`, then check the commit dates on what comes back. `--limit` defaults to 30, and a full result set means the search was capped, so report it as truncated.
- **Only PR-less, unlisted branch work needs a local scan.** That is the real boundary of "already covered by the PR queries"; anything outside it must be scanned from a clone the user names, or disclosed as unscanned.
- **Co-authored commits credit the user in a trailer, not the author header.** A `Co-authored-by:` credit counts on the contribution graph, but both the REST `author=` filter and `git log --author` match the author header and drop it. When an aggregate reports activity the detail lookup cannot account for, re-scan without the author filter and match `Co-authored-by:` trailers against the viewer's known identities.

## Notes

- Focus on merged PRs (`state: MERGED`) for completed work; open PRs (`state: OPEN`) for "coming soon" ideas; ignore closed unmerged PRs (`state: CLOSED` without `mergedAt`)
- Cross-reference commit activity with PR context for richer descriptions
