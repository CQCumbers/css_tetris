pout = 'aluP'
gout = 'aluG'
cin = 'alu_cin'
n = 3

for i in range(1, n):
    for j in range(i):
        for k in range(-1, i - j):
            base = f'var(--{pout}_{j}p)' if j else f'var(--{cin}_0p)'
            resp = base if k < 0 else f'var(--{gout}_{j + k}p, {resp})'
        resp2 = f'{resp} {resp2}' if j else resp
    print(f'  --{cin}_{i}p: {resp2};')

print(f'  --{cin}_0n: var(--{gout}_0n) var(--{cin}_0n);')
for i in range(2, n + 1):
    for j in range(i):
        for k in range(i - j):
            base = f'var(--{gout}_{j}n)' if j else f'var(--{cin}_0n)'
            resp = base if k < 1 else f'var(--{pout}_{j + k}n, {resp})'
        resp2 = f'{resp} {resp2}' if j else resp
    print(f'  --{cin}_{i}n: {resp2};')
