# Repository Guidelines

## Environment

- Miniconda is installed at `~/miniconda3`.
- Use that installation for environment activation and package management.
- Prefer explicit environment setup over ad hoc local Python changes.

## Git

- The canonical remote repository is `git@github.com:Timothy914/MultiAgentResearchWithCodex.git`.
- Prefer SSH-based Git operations and keep the `origin` remote aligned with the canonical repository.
- Run `git status` before and after changes to confirm the working tree state.
- Pull and rebase or merge carefully before pushing when the remote branch has moved.
- Keep commits focused and descriptive; avoid bundling unrelated changes together.
- Do not rewrite shared history unless the task explicitly requires it and all collaborators are aware.
- Avoid destructive Git commands such as `git reset --hard` and forced pushes unless they are explicitly approved.

## Model and Dataset Downloads

- Store all models and datasets under `/Data/public`.
- Do not download large artifacts into the repository, home directory caches, or temporary project folders.
- Use the Hugging Face mirror at `https://hf-mirror.com` for CLI downloads.
- Always prefer resumable downloads for large files.

Example:

```bash
HF_ENDPOINT=https://hf-mirror.com huggingface-cli download \
  --resume-download model-name \
  --local-dir /Data/public/model-name \
  --local-dir-use-symlinks False
```

## Logging

- Record logs promptly for every training, inference, evaluation, or data-processing run.
- At minimum, log the start time, command, key arguments, output path, errors, and final status.
- If a script supports file logging, save logs to disk instead of relying only on terminal output.

## Memory and GPU Monitoring

- Check GPU memory and system memory before and after every script run.
- Monitor long-running jobs during execution if they may approach hardware limits.
- Stop and adjust the workload if memory usage becomes unsafe.

Recommended checks:

```bash
nvidia-smi
free -h
df -h /Data/public
```

## Execution Workflow

1. Verify available disk space in `/Data/public`.
2. Verify free system RAM and GPU memory.
3. Start the job with logging enabled.
4. Recheck memory usage after the job starts and after it finishes.
5. Keep the final logs and output paths for traceability.

## Operational Guardrails

- Reduce batch size, shard the job, or free occupied processes before running memory-intensive workloads.
- Treat resource checks and logging as mandatory steps, not optional cleanup.
