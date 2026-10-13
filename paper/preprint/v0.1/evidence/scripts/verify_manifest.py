from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[1]
manifest=root/'SHA256SUMS'
listed=set()
for line in manifest.read_text().splitlines():
 expected,rel=line.split('  ',1);p=root/rel
 if p.is_symlink() or '..' in Path(rel).parts or not p.is_file():raise ValueError('Invalid manifest member '+rel)
 if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Hash mismatch '+rel)
 listed.add(rel)
actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p!=manifest and 'generated' not in p.relative_to(root).parts and '__pycache__' not in p.relative_to(root).parts}
assert listed==actual, 'Unlisted/missing payload files'
print(f'PASS: {len(listed)} payload files verified; manifest excludes only itself, generated verification outputs and Python bytecode caches.')
