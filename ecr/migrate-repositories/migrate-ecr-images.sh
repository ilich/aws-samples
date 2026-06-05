#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [OPTIONS] -s SOURCE_ACCOUNT -d DEST_ACCOUNT -r REGION repo:tag [repo:tag ...]

Migrate ECR images from one AWS account to another.

Required:
  -s SOURCE_ACCOUNT   AWS account ID of the source
  -d DEST_ACCOUNT     AWS account ID of the destination
  -r REGION           AWS region (e.g. us-east-1)
  repo:tag [...]      One or more repository:tag pairs to migrate

Options:
  --src-profile PROFILE   AWS CLI profile for the source account (default: default)
  --dst-profile PROFILE   AWS CLI profile for the destination account (default: default)
  -h                      Show this help message

Examples:
  $0 -s 111122223333 -d 444455556666 -r us-east-1 myapp:latest myapp:v1.2.3
  $0 -s 111122223333 --src-profile prod -d 444455556666 --dst-profile staging -r us-east-1 myapp:latest
EOF
}

SRC_ACCOUNT=""
DST_ACCOUNT=""
REGION=""
SRC_PROFILE="default"
DST_PROFILE="default"

# Parse flags; collect remaining args as repo:tag pairs
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -s) SRC_ACCOUNT="$2"; shift 2 ;;
    -d) DST_ACCOUNT="$2"; shift 2 ;;
    -r) REGION="$2"; shift 2 ;;
    --src-profile) SRC_PROFILE="$2"; shift 2 ;;
    --dst-profile) DST_PROFILE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 1 ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [[ -z "$SRC_ACCOUNT" || -z "$DST_ACCOUNT" || -z "$REGION" || ${#POSITIONAL[@]} -eq 0 ]]; then
  echo "Error: -s, -d, -r and at least one repo:tag are required." >&2
  usage
  exit 1
fi

SRC_REGISTRY="${SRC_ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
DST_REGISTRY="${DST_ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"

log() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] $*"; }

ecr_login() {
  local registry="$1" profile="$2"
  log "Authenticating Docker to ${registry} (profile: ${profile})"
  aws ecr get-login-password --region "$REGION" --profile "$profile" \
    | docker login --username AWS --password-stdin "$registry"
}

ecr_login "$SRC_REGISTRY" "$SRC_PROFILE"
ecr_login "$DST_REGISTRY" "$DST_PROFILE"

FAILED=()

for repo_tag in "${POSITIONAL[@]}"; do
  # Split on the last colon so image names with colons in the repo path still work
  repo="${repo_tag%:*}"
  tag="${repo_tag##*:}"

  if [[ "$repo" == "$tag" ]]; then
    log "WARNING: no tag found in '${repo_tag}', skipping (use repo:tag format)"
    FAILED+=("$repo_tag")
    continue
  fi

  src_image="${SRC_REGISTRY}/${repo}:${tag}"
  dst_image="${DST_REGISTRY}/${repo}:${tag}"

  log "Copying  ${src_image} -> ${dst_image}"
  # imagetools create copies the manifest list directly between registries,
  # preserving multi-platform (multi-arch) images without a local pull/push.
  if ! docker buildx imagetools create --tag "$dst_image" "$src_image"; then
    log "ERROR: failed to copy ${src_image}"
    FAILED+=("$repo_tag")
    continue
  fi

  log "Done     ${repo}:${tag}"
done

echo ""
if [[ ${#FAILED[@]} -gt 0 ]]; then
  log "Migration completed with errors. Failed images:"
  for item in "${FAILED[@]}"; do
    echo "  - $item"
  done
  exit 1
else
  log "All images migrated successfully."
fi
