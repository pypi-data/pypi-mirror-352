# Git Clone Group (gcg)

A command-line tool to clone or update all projects from a GitLab group and its subgroups.

## Features

- Clone/update all repositories in a GitLab group and its subgroups
- Specify branch to clone/pull
- Parallel processing with progress bars
- Smart retry mechanism
- Empty repository detection
- Detailed statistics

## Installation

You can install git-clone-group using pip:

```bash
pip install git-clone-group
```

## Usage

Basic usage:

```bash
gcg -g GITLAB_ADDR -t TOKEN -i GROUP_ID [-d DEST_DIR] [-b BRANCH]
```

Show help:

```bash
gcg -h
```

Examples:

```bash
# Clone all projects from group ID 123 to current directory
gcg -g gitlab.com -t glpat-xxxxxxxxxxxx -i 123

# Clone to a specific directory
gcg -g gitlab.com -t glpat-xxxxxxxxxxxx -i 123 -d /path/to/repos

# Clone specific branch from private GitLab instance
gcg -g git.company.com -t glpat-xxxxxxxxxxxx -i 456 -d ./projects -b develop

# Clone default branches
gcg -g gitlab.com -t glpat-xxxxxxxxxxxx -i 123 -d ./repos
```

## Getting a GitLab Access Token

1. Log in to your GitLab instance
2. Go to Settings > Access Tokens
3. Create a new personal access token with `api` scope
4. Copy the token and use it with the `--token` argument

## Getting a Group ID

You can find the group ID in GitLab:

1. Go to your group's page
2. The group ID is shown in the group information panel
3. Or look at the URL: `https://gitlab.com/groups/your-group-name` - the group ID will be visible in the group details

## Notes

- The tool will automatically handle nested subgroups
- For existing repositories, it will perform a git pull
- Progress bars show real-time cloning/pulling status
- Both HTTP and SSH URLs are supported (SSH recommended)
