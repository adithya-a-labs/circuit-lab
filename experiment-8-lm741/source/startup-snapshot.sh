#!/usr/bin/env bash
set -euo pipefail
retained_env=/workspace/circuit-tools/python-env
test -x "$retained_env/bin/python"
if [ ! -e /tmp/circuit-env ] && [ ! -L /tmp/circuit-env ]; then
    ln -s "$retained_env" /tmp/circuit-env
    echo 'Restored /tmp/circuit-env symlink'
fi
test "$(readlink -f /tmp/circuit-env)" = "$retained_env"
export PATH="/workspace/circuit-tools/ngspice/usr/bin:$PATH"
command -v ngspice
ngspice --version
/tmp/circuit-env/bin/python - <<'PY'
import tempfile
import numpy, scipy, matplotlib
assert matplotlib.get_backend().lower() == 'agg', matplotlib.get_backend()
with tempfile.TemporaryFile(dir=matplotlib.get_cachedir()) as probe:
    probe.write(b'cache-write-check')
    probe.flush()
print('PASS: numpy', numpy.__version__, 'scipy', scipy.__version__, 'matplotlib', matplotlib.__version__)
print('PASS: Agg and writable cache', matplotlib.get_cachedir())
PY
