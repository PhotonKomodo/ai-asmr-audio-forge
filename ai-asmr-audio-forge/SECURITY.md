# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | yes       |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@ai-asmr-forge.dev` with a description, repro steps, and the
affected module. We respond within 72 hours.

Do **not** open a public issue for security problems.

## Threat model

This is a local desktop tool. It does not listen on a network socket. The
attack surface we care about:

1. **Model checkpoint loading** — we use `safetensors` only. Pickle-based
   `.pt` / `.ckpt` files are rejected at load time. If you find a path that
   still calls `torch.load` without `weights_only=True`, that's a P1.
2. **Prompt-to-file path traversal** — the render queue writes to
   `renders/`. Any prompt or preset that can escape that directory is a P1.
3. **Plugin loading** — third-party trigger plugins execute Python. We
   require an explicit `--allow-plugins` flag and a hash allowlist in
   `config/local.toml`. Bypassing either is a P1.
4. **Audio decoder** — `soundfile` / `libsndfile` is our only decoder.
   Malformed WAV files that crash the process are a P2.

## Out of scope

- Output that "sounds bad." That's a feature request, not a vuln.
- GPU driver crashes on unsupported cards.
- Anything requiring physical access to the host.