# Migrate ECR Images Between AWS Accounts

A shell script to pull Docker images from one AWS ECR registry and push them to another, preserving repository names and tags.

## Prerequisites

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) configured with profiles for both accounts
- [Docker](https://docs.docker.com/get-docker/) with [buildx](https://docs.docker.com/buildx/working-with-buildx/) (included in Docker Desktop; on Linux install the `docker-buildx-plugin` package)
- Source account: IAM permissions `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`
- Destination account: IAM permissions `ecr:GetAuthorizationToken`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`
- Target repositories must already exist in the destination account

## Usage

```bash
./migrate-ecr-images.sh [OPTIONS] -s SOURCE_ACCOUNT -d DEST_ACCOUNT -r REGION repo:tag [repo:tag ...]
```

### Required arguments

| Argument | Description |
|---|---|
| `-s SOURCE_ACCOUNT` | AWS account ID of the source |
| `-d DEST_ACCOUNT` | AWS account ID of the destination |
| `-r REGION` | AWS region (e.g. `us-east-1`) |
| `repo:tag [...]` | One or more `repository:tag` pairs to migrate |

### Options

| Option | Default | Description |
|---|---|---|
| `--src-profile PROFILE` | `default` | AWS CLI profile for the source account |
| `--dst-profile PROFILE` | `default` | AWS CLI profile for the destination account |
| `-h` | | Show help |

## Examples

Migrate a single image using default AWS profiles:

```bash
./migrate-ecr-images.sh \
  -s 111122223333 \
  -d 444455556666 \
  -r us-east-1 \
  myapp:latest
```

Migrate multiple images with named profiles:

```bash
./migrate-ecr-images.sh \
  -s 111122223333 --src-profile prod-readonly \
  -d 444455556666 --dst-profile staging-admin \
  -r us-east-1 \
  myapp:latest myapp:v1.2.3 worker:v3.1
```

## How it works

1. Authenticates Docker to both ECR registries using `aws ecr get-login-password`
2. For each `repo:tag` pair, copies the manifest directly between registries using `docker buildx imagetools create` — no local pull or disk usage
3. Reports any failures at the end and exits with code `1` if any image failed

## Notes

- Repository names must be identical in both accounts
- Multi-platform (multi-arch) images are preserved — the manifest list is copied as-is, not re-assembled from a single local platform
- The script continues on individual image failures and reports a summary at the end, making it suitable for batch migrations
- Because `imagetools create` works registry-to-registry, no local disk space is consumed
